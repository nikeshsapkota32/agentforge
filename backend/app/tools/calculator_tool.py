from __future__ import annotations

import ast
import math
import operator
from typing import Any

_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARYOPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}

_FUNCS: dict[str, Any] = {
    name: getattr(math, name)
    for name in ("sqrt", "log", "log10", "log2", "exp", "sin", "cos", "tan", "atan", "floor", "ceil")
}
_FUNCS.update({"abs": abs, "round": round, "min": min, "max": max})
_NAMES = {"pi": math.pi, "e": math.e}


def _eval(node: ast.AST) -> Any:
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("only numeric literals allowed")
    if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
        return _BINOPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARYOPS:
        return _UNARYOPS[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.Name) and node.id in _NAMES:
        return _NAMES[node.id]
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCS:
        return _FUNCS[node.func.id](*[_eval(a) for a in node.args])
    raise ValueError(f"disallowed expression: {ast.dump(node)}")


async def calculate(payload: dict[str, Any]) -> dict[str, Any]:
    expr = str(payload.get("expression") or "").strip()
    if not expr:
        return {"error": "missing expression"}
    if len(expr) > 256:
        return {"error": "expression too long"}
    try:
        tree = ast.parse(expr, mode="eval")
        result = _eval(tree)
        return {"expression": expr, "result": result}
    except Exception as exc:
        return {"expression": expr, "error": str(exc)}
