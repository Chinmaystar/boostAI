from __future__ import annotations

from src.ast import ASTNode
from .structural_hasher import StructuralHasher
from .structural_comparator import StructuralComparator
from .template_signature import TemplateSignature


class TemplateConfidenceScorer:
    """Scores how confidently an AST belongs to a given template.

    Confidence ranges from ``0.0`` (no match) to ``1.0`` (perfect
    match).  An exact structural match always yields ``1.0``.
    Near-match similarity between two live ASTs is available via
    ``compare_trees``.
    """

    @staticmethod
    def score(ast: ASTNode, signature: TemplateSignature) -> float:
        """Exact-match confidence: ``1.0`` if the AST's structural hash
        matches the template's, ``0.0`` otherwise.

        Args:
            ast: A canonicalised AST.
            signature: A template signature.

        Returns:
            ``1.0`` or ``0.0``.
        """
        return 1.0 if StructuralHasher.hash(ast) == signature.structural_hash else 0.0

    @staticmethod
    def compare_trees(a: ASTNode, b: ASTNode) -> float:
        """Structural similarity between two live ASTs.

        This is a direct delegate to
        ``StructuralComparator.similarity``.

        Args:
            a: First canonicalised AST.
            b: Second canonicalised AST.

        Returns:
            A float in ``[0.0, 1.0]``.
        """
        return StructuralComparator.similarity(a, b)

    @staticmethod
    def score_best(
        ast: ASTNode,
        registry: "TemplateRegistry",  # noqa: F821
    ) -> tuple[TemplateSignature | None, float]:
        """Find the best-matching template in a registry.

        First tries an exact structural-hash lookup.  If no exact
        match exists, the best near match is returned with its
        similarity score.

        Args:
            ast: A canonicalised AST.
            registry: A ``TemplateRegistry`` instance.

        Returns:
            A ``(signature, confidence)`` tuple.  ``signature`` is
            ``None`` when the registry is empty.
        """
        h = StructuralHasher.hash(ast)
        sig = registry.lookup_by_hash(h)
        if sig is not None:
            return sig, 1.0

        best_sig: TemplateSignature | None = None
        best_score = 0.0

        for candidate in registry.get_all():
            ref_fp = candidate.structural_hash
            if len(ref_fp) == 64:
                try:
                    bytes.fromhex(ref_fp)
                except ValueError:
                    pass
                else:
                    continue

            ref_sig_ast = _reconstruct_from_fingerprint(ref_fp)
            if ref_sig_ast is not None:
                s = StructuralComparator.similarity(ast, ref_sig_ast)
                if s > best_score:
                    best_score = s
                    best_sig = candidate

        return best_sig, best_score


def _reconstruct_from_fingerprint(fp: str) -> ASTNode | None:
    """Build a minimal dummy AST from a structural fingerprint string.

    Returns ``None`` if the fingerprint looks like a hex hash rather than
    a structural pattern.
    """
    if len(fp) == 64:
        try:
            bytes.fromhex(fp)
            return None
        except ValueError:
            pass

    from src.ast.nodes import (
        ConstantNode, VariableNode, BinaryOpNode,
        UnaryOpNode, EquationNode,
    )

    fp = fp.strip()
    if not fp:
        return None

    pos = [0]

    def parse() -> ASTNode | None:
        if pos[0] >= len(fp):
            return None
        ch = fp[pos[0]]
        pos[0] += 1

        if ch == "C":
            return ConstantNode(0)
        if ch == "V":
            return VariableNode("x")
        if ch == "U":
            if pos[0] < len(fp) and fp[pos[0]] == "(":
                pos[0] += 1
                op = parse()
                if pos[0] < len(fp) and fp[pos[0]] == ")":
                    pos[0] += 1
                return UnaryOpNode("-", op) if op is not None else None
            return None
        if ch == "B":
            if pos[0] < len(fp) and fp[pos[0]] == "(":
                pos[0] += 1
                left = parse()
                if pos[0] < len(fp) and fp[pos[0]] == ",":
                    pos[0] += 1
                right = parse()
                if pos[0] < len(fp) and fp[pos[0]] == ")":
                    pos[0] += 1
                if left is not None and right is not None:
                    return BinaryOpNode("+", left, right)
            return None
        if ch == "E":
            if pos[0] < len(fp) and fp[pos[0]] == "(":
                pos[0] += 1
                left = parse()
                if pos[0] < len(fp) and fp[pos[0]] == ",":
                    pos[0] += 1
                right = parse()
                if pos[0] < len(fp) and fp[pos[0]] == ")":
                    pos[0] += 1
                if left is not None and right is not None:
                    return EquationNode(left, right)
            return None
        return None

    return parse()
