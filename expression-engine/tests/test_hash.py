import hashlib
import pytest
from src.hashing import CanonicalHasher


class TestCanonicalHasher:
    def setup_method(self):
        self.hasher = CanonicalHasher(rename_variables=False)

    def test_same_expression_deterministic(self):
        h1 = self.hasher.hash("2x+5")
        h2 = self.hasher.hash("2x+5")
        assert h1 == h2

    def test_commutative_addition_same_hash(self):
        h1 = self.hasher.hash("2x+5")
        h2 = self.hasher.hash("5+2x")
        assert h1 == h2

    def test_commutative_multiplication_same_hash(self):
        h1 = self.hasher.hash("x*2")
        h2 = self.hasher.hash("2x")
        assert h1 == h2

    def test_variable_reordering_same_hash(self):
        h1 = self.hasher.hash("y+x")
        h2 = self.hasher.hash("x+y")
        assert h1 == h2

    def test_constant_folding_same_hash(self):
        h1 = self.hasher.hash("2+3")
        h2 = self.hasher.hash("5")
        assert h1 == h2

    def test_different_expressions_different_hash(self):
        h1 = self.hasher.hash("2x+5")
        h2 = self.hasher.hash("3x+5")
        assert h1 != h2

    def test_different_constants_different_hash(self):
        h1 = self.hasher.hash("x+1")
        h2 = self.hasher.hash("x+2")
        assert h1 != h2

    def test_equation_same_hash(self):
        h1 = self.hasher.hash("2x+5=17")
        h2 = self.hasher.hash("5+2x=17")
        assert h1 == h2

    def test_different_equations_different_hash(self):
        h1 = self.hasher.hash("x+1=5")
        h2 = self.hasher.hash("x+2=5")
        assert h1 != h2

    def test_parentheses_no_change(self):
        h1 = self.hasher.hash("(x)")
        h2 = self.hasher.hash("x")
        assert h1 == h2

    def test_double_parens(self):
        h1 = self.hasher.hash("((x))")
        h2 = self.hasher.hash("x")
        assert h1 == h2

    def test_mult_ordering(self):
        h1 = self.hasher.hash("x*5")
        h2 = self.hasher.hash("5x")
        assert h1 == h2

    def test_unary_minus_preserved(self):
        h1 = self.hasher.hash("-x")
        h2 = self.hasher.hash("-x")
        assert h1 == h2

    def test_unary_minus_different_from_positive(self):
        h_pos = self.hasher.hash("x")
        h_neg = self.hasher.hash("-x")
        assert h_pos != h_neg

    def test_constant_folding_multiplication(self):
        h1 = self.hasher.hash("2*3*x")
        h2 = self.hasher.hash("6x")
        assert h1 == h2

    def test_whitespace_irrelevant(self):
        h1 = self.hasher.hash("2x+5")
        h2 = self.hasher.hash("  2x  +  5  ")
        assert h1 == h2

    def test_hash_is_sha256(self):
        h = self.hasher.hash("x")
        assert len(h) == 64  # SHA-256 hex digest
        all_hex = all(c in "0123456789abcdef" for c in h)
        assert all_hex

    def test_canonical_string(self):
        s = self.hasher.canonical_string("5+2x")
        assert s is not None
        assert isinstance(s, str)

    def test_skip_variable_rename(self):
        """Without variable renaming, different variable names produce
        different hashes (strict equivalence)."""
        h1 = self.hasher.hash("a+b")
        h2 = self.hasher.hash("a+c")
        assert h1 != h2

    def test_hash_across_complex_expression(self):
        h1 = self.hasher.hash("2x+3+4")
        h2 = self.hasher.hash("7+2x")
        assert h1 == h2
