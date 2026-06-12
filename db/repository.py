import os
import random
import re
from pathlib import Path

from sqlalchemy import func, select

from db.engine import SessionLocal
from db.models import Feedback, KnowledgePair, QueryLog, Topic
from db.schemas import DashboardData, ThemeInfo, TopItem
from services.normalize import normalizar

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

TIPOS_RESPUESTA = ("embedding", "matematica", "ninguna")


def parse_data_file(filepath: str | Path) -> dict[str, str]:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    pairs: dict[str, str] = {}
    regex = re.compile(r"p:([\s\S]+?)\?r:([\s\S]+?)(?=\np:|$)")
    for match in regex.finditer(content):
        pairs[match.group(1).strip()] = match.group(2).strip()
    return pairs


def seed_from_files_if_empty() -> bool:
    """Lee archivos .txt y llena PostgreSQL si knowledge_pairs está vacía."""
    with SessionLocal() as session:
        existe = session.execute(select(KnowledgePair.id).limit(1)).scalar_one_or_none()
        if existe is not None:
            return False

        if not DATA_DIR.is_dir():
            print(f"[seed] Directorio de datos no encontrado: {DATA_DIR}")
            return False

        archivos = sorted(f for f in os.listdir(DATA_DIR) if f.endswith(".txt"))
        for filename in archivos:
            filepath = DATA_DIR / filename
            pairs = parse_data_file(filepath)
            if not pairs:
                continue

            slug = filename.replace(".txt", "")
            topic_name = slug.capitalize()
            topic = session.execute(
                select(Topic).where(Topic.slug == slug)
            ).scalar_one_or_none()
            if topic is None:
                topic = Topic(name=topic_name, slug=slug)
                session.add(topic)
                session.flush()

            for question, answer in pairs.items():
                session.add(
                    KnowledgePair(
                        topic_id=topic.id,
                        question=question,
                        answer=answer,
                        question_normalized=normalizar(question),
                    )
                )

        session.commit()
        print("[seed] Base de datos inicializada desde archivos .txt.")
        return True


def get_all_knowledge_pairs() -> list[tuple[str, str]]:
    with SessionLocal() as session:
        rows = session.execute(
            select(KnowledgePair.question, KnowledgePair.answer).order_by(
                KnowledgePair.id
            )
        ).all()
        return [(q, a) for q, a in rows]


def insert_knowledge_pair(topic_slug: str, question: str, answer: str) -> None:
    slug = topic_slug.replace(".txt", "").strip()
    with SessionLocal() as session:
        topic = session.execute(
            select(Topic).where(Topic.slug == slug)
        ).scalar_one_or_none()
        if topic is None:
            topic = Topic(name=slug.capitalize(), slug=slug)
            session.add(topic)
            session.flush()

        session.add(
            KnowledgePair(
                topic_id=topic.id,
                question=question,
                answer=answer,
                question_normalized=normalizar(question),
            )
        )
        session.commit()


def insert_query_log(question: str, response_type: str, similarity: float) -> None:
    with SessionLocal() as session:
        session.add(
            QueryLog(
                question=question,
                response_type=response_type,
                similarity=similarity,
            )
        )
        session.commit()


def insert_feedback(
    question: str,
    answer: str,
    rating: str,
    comment: str | None = None,
) -> None:
    with SessionLocal() as session:
        session.add(
            Feedback(
                question=question,
                answer=answer,
                rating=rating,
                comment=comment or "",
            )
        )
        session.commit()


def get_topics_with_stats() -> list[ThemeInfo]:
    with SessionLocal() as session:
        topics = session.execute(
            select(Topic.id, Topic.name, Topic.slug).order_by(Topic.name)
        ).all()

        temas: list[ThemeInfo] = []
        for topic_id, name, slug in topics:
            ejemplos = [
                q
                for (q,) in session.execute(
                    select(KnowledgePair.question)
                    .where(KnowledgePair.topic_id == topic_id)
                    .order_by(KnowledgePair.id)
                    .limit(3)
                ).all()
            ]
            cantidad = session.execute(
                select(func.count(KnowledgePair.id)).where(
                    KnowledgePair.topic_id == topic_id
                )
            ).scalar_one()
            temas.append(
                ThemeInfo(
                    nombre=name,
                    archivo=f"{slug}.txt",
                    cantidad=cantidad,
                    ejemplos=ejemplos,
                )
            )
        return temas


def get_random_question() -> str | None:
    with SessionLocal() as session:
        preguntas = [
            q for (q,) in session.execute(select(KnowledgePair.question)).all()
        ]
        if not preguntas:
            return None
        return random.choice(preguntas)


def get_answer_for_question(question: str) -> str | None:
    with SessionLocal() as session:
        row = session.execute(
            select(KnowledgePair.answer).where(KnowledgePair.question == question)
        ).first()
        return row[0] if row else None


def get_questions_by_topic(slug: str) -> list[str]:
    slug_limpio = slug.replace(".txt", "")
    with SessionLocal() as session:
        topic = session.execute(
            select(Topic).where(Topic.slug == slug_limpio)
        ).scalar_one_or_none()
        if not topic:
            return []
        return [
            q
            for (q,) in session.execute(
                select(KnowledgePair.question).where(
                    KnowledgePair.topic_id == topic.id
                )
            ).all()
        ]


def get_dashboard_metrics() -> DashboardData:
    with SessionLocal() as session:
        rows = session.execute(
            select(QueryLog.response_type, func.count(QueryLog.id)).group_by(
                QueryLog.response_type
            )
        ).all()

        metricas: dict[str, int] = {tipo: 0 for tipo in TIPOS_RESPUESTA}
        for tipo, count in rows:
            if tipo in metricas:
                metricas[tipo] = count
            else:
                metricas[tipo] = count

        total = sum(metricas.values())
        if total == 0:
            porcentajes = {k: 0.0 for k in metricas}
        else:
            porcentajes = {
                k: round((v / total) * 100, 1) for k, v in metricas.items()
            }

        return DashboardData(metricas=metricas, total=total, porcentajes=porcentajes)


def get_top_questions(limit: int = 10) -> list[TopItem]:
    with SessionLocal() as session:
        rows = session.execute(
            select(QueryLog.question, func.count(QueryLog.id).label("count"))
            .group_by(QueryLog.question)
            .order_by(func.count(QueryLog.id).desc())
            .limit(limit)
        ).all()
        return [TopItem(pregunta=q, count=c) for q, c in rows]
