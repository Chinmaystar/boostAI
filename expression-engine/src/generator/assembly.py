from __future__ import annotations

import re
from typing import Any

from src.template_engine import TemplateSignature
from src.semantic_engine import SemanticTemplate, SolverType
from src.variable_engine import VariableGraph, VariableType
from src.symbolic import (
    BuiltinBackend, SymbolicExpr, EquationEngine, EvaluationEngine,
)

from .errors import QuestionAssemblyError, UnsolvedError


class QuestionAssemblyEngine:
    def __init__(self) -> None:
        self._backend = BuiltinBackend()
        self._eq_engine = EquationEngine(self._backend)
        self._eval_engine = EvaluationEngine(self._backend)

    def render(
        self,
        signature: TemplateSignature,
        assignments: dict[str, Any],
        template: SemanticTemplate,
    ) -> str:
        pattern = signature.canonical_pattern
        name_to_id = self._name_to_id_map(template)
        slot_to_val = self._slot_to_value_map(assignments, template)

        rendered = pattern
        for vname in signature.variable_slots:
            var_id = name_to_id.get(vname)
            if var_id is not None and var_id in assignments:
                val = assignments[var_id]
                formatted = self._format_value(val)
                rendered = re.sub(
                    r'\b' + re.escape(vname) + r'\b',
                    formatted, rendered,
                )
            elif vname in slot_to_val:
                val = slot_to_val[vname]
                formatted = self._format_value(val)
                rendered = re.sub(
                    r'\b' + re.escape(vname) + r'\b',
                    formatted, rendered,
                )

        rendered = self._clean_rendered(rendered)
        prefix = self._question_prefix(template)
        return f"{prefix}{rendered}"

    def compute_expected_answer(
        self,
        symbolic_expr: SymbolicExpr | None,
        assignments: dict[str, Any],
        template: SemanticTemplate,
        main_variable: str | None = None,
    ) -> Any:
        if symbolic_expr is None:
            return None

        solver = template.solver_type
        if solver == SolverType.NONE:
            return None

        try:
            if solver in (SolverType.LINEAR, SolverType.QUADRATIC,
                          SolverType.SIMULTANEOUS):
                return self._solve_equation(
                    symbolic_expr, assignments, template, main_variable)
            return self._evaluate_expression(
                symbolic_expr, assignments, template)
        except UnsolvedError:
            raise
        except Exception as exc:
            raise UnsolvedError(f"Cannot compute answer: {exc}") from exc

    def _solve_equation(
        self,
        symbolic_expr: SymbolicExpr,
        assignments: dict[str, Any],
        template: SemanticTemplate,
        main_variable: str | None = None,
    ) -> Any:
        var_name = main_variable or self._find_main_variable(template)
        if not var_name:
            return None
        substituted = self._substitute_assignments(
            symbolic_expr, assignments, template)
        if substituted.is_equal():
            result = self._eq_engine.solve(substituted, var_name)
            if result.has_solution:
                vals = result.solution_values()
                if len(vals) == 1:
                    return vals[0]
                return sorted(vals)
            raise UnsolvedError("Equation has no solution")
        return None

    def _evaluate_expression(
        self,
        symbolic_expr: SymbolicExpr,
        assignments: dict[str, Any],
        template: SemanticTemplate,
    ) -> Any:
        substituted = self._substitute_assignments(
            symbolic_expr, assignments, template)
        if substituted.is_equal():
            var_name = self._find_main_variable(template)
            if var_name:
                result = self._eq_engine.solve(substituted, var_name)
                if result.has_solution:
                    vals = result.solution_values()
                    if len(vals) == 1:
                        return vals[0]
                    if len(vals) > 1:
                        return sorted(vals)
            lhs = substituted.left()
            rhs = substituted.right()
            expr = self._backend._simplify(
                SymbolicExpr.sub(lhs, rhs))
            evaluated = self._eval_engine.evaluate(expr)
        else:
            evaluated = self._eval_engine.evaluate(substituted)
        if evaluated.is_number():
            v = evaluated.value
            if v == int(v):
                return int(v)
            return v
        return str(evaluated)

    def _collect_slot_values(
        self,
        assignments: dict[str, Any],
        template: SemanticTemplate,
    ) -> list[float]:
        g = self._get_graph(template)
        values: list[float] = []
        for n in g.all_nodes():
            if n.type in (
                VariableType.CONSTANT,
                VariableType.COEFFICIENT,
                VariableType.INTEGER,
            ) and n.id in assignments:
                val = assignments[n.id]
                if isinstance(val, (int, float)):
                    values.append(float(val))
        return values

    def _substitute_assignments(
        self,
        expr: SymbolicExpr,
        assignments: dict[str, Any],
        template: SemanticTemplate,
    ) -> SymbolicExpr:
        slot_values = self._collect_slot_values(assignments, template)

        def walk(node: SymbolicExpr, counter: list[int]) -> SymbolicExpr:
            if node.is_number() and counter[0] < len(slot_values):
                result = SymbolicExpr.number(slot_values[counter[0]])
                counter[0] += 1
                return result
            if node.children:
                return SymbolicExpr(
                    node.type, node.value,
                    tuple(walk(c, counter) for c in node.children),
                )
            return node

        return self._backend._simplify(walk(expr, [0]))

    def _find_main_variable(self, template: SemanticTemplate) -> str | None:
        g = self._get_graph(template)
        for var in g.all_nodes():
            if var.type.name in ("SYMBOL", "VARIABLE"):
                if not var.metadata.can_randomize:
                    return var.name
        for var in g.all_nodes():
            if var.type.name in ("SYMBOL", "VARIABLE"):
                return var.name
        return None

    def _get_graph(self, template: SemanticTemplate) -> VariableGraph:
        g = template.variable_graph
        if isinstance(g, VariableGraph):
            return g
        return VariableGraph()

    def _name_to_id_map(
        self, template: SemanticTemplate,
    ) -> dict[str, str]:
        g = self._get_graph(template)
        return {n.name: n.id for n in g.all_nodes()}

    def _slot_to_value_map(
        self,
        assignments: dict[str, Any],
        template: SemanticTemplate,
    ) -> dict[str, Any]:
        values = self._collect_slot_values(assignments, template)
        return {chr(ord("a") + i): val for i, val in enumerate(values)}

    def _format_value(self, value: Any) -> str:
        if isinstance(value, float):
            if value == int(value):
                return str(int(value))
            s = f"{value:.4f}".rstrip("0").rstrip(".")
            return s
        return str(value)

    def _clean_rendered(self, text: str) -> str:
        text = re.sub(r'\*', ' \u00d7 ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'\s*([+=])\s*', r' \1 ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _question_prefix(self, template: SemanticTemplate) -> str:
        if template.solver_type in (
            SolverType.LINEAR, SolverType.QUADRATIC,
            SolverType.SIMULTANEOUS,
        ):
            return "Solve: "
        if template.solver_type in (
            SolverType.EVALUATION, SolverType.ARITHMETIC_OP,
        ):
            return "Evaluate: "
        if template.solver_type == SolverType.GEOMETRIC_FORMULA:
            return "Find: "
        if template.solver_type == SolverType.STATISTICAL:
            return "Compute: "
        return ""
