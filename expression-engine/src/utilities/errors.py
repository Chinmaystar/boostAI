class ExpressionError(Exception):
    """Base exception for all expression engine errors."""


class TokenizerError(ExpressionError):
    """Raised when the tokenizer encounters an invalid character."""


class LexerError(ExpressionError):
    """Raised when the lexer detects an invalid token sequence."""


class ParserError(ExpressionError):
    """Raised when the parser encounters an unexpected token or incomplete input."""
