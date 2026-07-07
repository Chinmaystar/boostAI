from __future__ import annotations

from typing import Optional

from src.ast import ASTNode
from .structural_hasher import StructuralHasher
from .template_signature import TemplateSignature


class TemplateRegistry:
    """Stores and manages discovered template signatures.

    The registry is keyed by the structural hash of each template.
    Registering a template whose structural hash already exists will
    *not* create a duplicate — it returns ``False`` and the existing
    signature is preserved.

    Usage::

        registry = TemplateRegistry()
        registry.register(signature)
        sig = registry.lookup_by_hash("abc123...")
    """

    def __init__(self) -> None:
        self._by_hash: dict[str, TemplateSignature] = {}
        self._by_id: dict[str, TemplateSignature] = {}

    def register(self, signature: TemplateSignature) -> bool:
        """Register a template signature.

        Args:
            signature: The ``TemplateSignature`` to register.

        Returns:
            ``True`` if this is a new template (not previously seen),
            ``False`` if a template with the same structural hash
            already exists.
        """
        h = signature.structural_hash
        if h in self._by_hash:
            return False

        self._by_hash[h] = signature
        tid = signature.template_id
        if tid not in self._by_id:
            self._by_id[tid] = signature
        return True

    def lookup_by_hash(self, structural_hash: str) -> Optional[TemplateSignature]:
        """Look up a template by its structural hash.

        Args:
            structural_hash: The SHA-256 hex digest of the structural
                fingerprint.

        Returns:
            The matching ``TemplateSignature``, or ``None``.
        """
        return self._by_hash.get(structural_hash)

    def lookup_by_id(self, template_id: str) -> Optional[TemplateSignature]:
        """Look up a template by its human-readable ID.

        Args:
            template_id: The ``template_id`` field of the signature.

        Returns:
            The matching ``TemplateSignature``, or ``None``.
        """
        return self._by_id.get(template_id)

    def find_matches(self, ast: ASTNode) -> list[TemplateSignature]:
        """Find all templates that match the given AST's structural shape.

        Args:
            ast: A canonicalised AST.

        Returns:
            A list of matching ``TemplateSignature`` instances (typically
            zero or one, since each structural shape maps to one template).
        """
        h = StructuralHasher.hash(ast)
        sig = self._by_hash.get(h)
        if sig is not None:
            return [sig]
        return []

    def get_all(self) -> list[TemplateSignature]:
        """Return every registered template signature.

        Returns:
            A list of ``TemplateSignature`` objects (order is insertion
            order).  The list is a copy — mutating it does not affect
            the registry.
        """
        return list(self._by_hash.values())

    def count(self) -> int:
        """Return the number of unique templates in the registry."""
        return len(self._by_hash)

    def clear(self) -> None:
        """Remove all registered templates."""
        self._by_hash.clear()
        self._by_id.clear()
