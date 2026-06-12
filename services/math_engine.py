import ast
import math
import operator as op
import re

_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
}

_ALLOWED_NAMES = {
    name: getattr(math, name)
    for name in [
        "sqrt", "sin", "cos", "tan", "log", "exp", "factorial",
        "acos", "asin", "atan", "ceil", "floor", "degrees", "radians", "pow",
        "fabs", "fsum", "gcd", "lcm", "prod", "dist", "hypot",
        "pi", "e", "tau", "inf", "nan",
    ]
    if hasattr(math, name)
}
_ALLOWED_NAMES.update({
    "abs": abs,
    "min": min,
    "max": max,
    "round": round,
    "sum": sum,
})


def _eval(node: ast.AST):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Constante invalida")
    if isinstance(node, ast.BinOp):
        if type(node.op) not in _OPERATORS:
            raise ValueError(f"Operador binario no soportado {type(node.op)}")
        return _OPERATORS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        if type(node.op) not in _OPERATORS:
            raise ValueError(f"Operador unario no soportado {type(node.op)}")
        return _OPERATORS[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Solo se permiten llamadas simples a funciones")
        func_name = node.func.id
        if func_name not in _ALLOWED_NAMES:
            raise ValueError(f"Funcion {func_name} no permitida")
        args = [_eval(arg) for arg in node.args]
        return _ALLOWED_NAMES[func_name](*args)
    if isinstance(node, ast.Name):
        if node.id not in _ALLOWED_NAMES:
            raise ValueError(f"Nombre {node.id} no permitido")
        return _ALLOWED_NAMES[node.id]
    raise ValueError(f"Expresion no soportada {type(node)}")


def safe_math_eval(expression: str) -> float:
    """Evalua una expresion matematica de forma segura usando AST."""
    tree = ast.parse(expression, mode="eval")
    result = _eval(tree.body)
    if not isinstance(result, (int, float)):
        raise ValueError("El resultado debe ser numerico")
    return float(result)


def resolver_matematica(pregunta: str) -> str | None:
    """Resuelve preguntas matematicas en espanol."""
    texto = pregunta.lower().strip()
    texto = (
        texto
        .replace("más", "+")
        .replace("mas", "+")
        .replace("menos", "-")
        .replace("por", "*")
        .replace("dividido", "/")
        .replace("raíz cuadrada de", "sqrt")
        .replace("raiz cuadrada de", "sqrt")
        .replace("seno de", "sin")
        .replace("coseno de", "cos")
        .replace("tangente de", "tan")
        .replace("logaritmo de", "log")
        .replace("exponencial de", "exp")
        .replace("factorial de", "factorial")
    )

    texto_limpio = re.sub(r"[^0-9+\-*/().\s]", "", texto)
    texto_limpio = re.sub(r"\s+", " ", texto_limpio).strip()

    if not texto_limpio or not re.search(r"\d", texto_limpio):
        return None

    try:
        resultado = safe_math_eval(texto_limpio)
        return f"El resultado es: {resultado}"
    except Exception:
        return None
