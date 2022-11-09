# import argparse
# import sys
from enum import Enum

# _SHOULD_LOG_SCOPE = False  # see '--scope' command line option
# _SHOULD_LOG_STACK = False  # see '--stack' command line option


class ErrorCode(Enum):
    UNEXPECTED_TOKEN = 'Unexpected token'
    ID_NOT_FOUND = 'Identifier not found'
    DUPLICATE_ID = 'Duplicate id found'


class Error(Exception):
    def __init__(self, error_code=None, token=None, message=None):
        self.error_code = error_code
        self.token = token
        # add exception class name before the message
        self.message = f'{self.__class__.__name__}: {message}'


class LexerError(Error):
    pass


class ParserError(Error):
    pass


class SemanticError(Error):
    pass

# luaX_tokens = (
#     "and", "break", "do", "else", "elseif",
#     "end", "false", "for", "function", "goto", "if",
#     "in", "local", "nil", "not", "or", "repeat",
#     "return", "then", "true", "until", "while",
#     "//", "..", "...", "==", ">=", "<=", "~=",
#     "<<", ">>", "::", "<eof>",
#     "<number>", "<integer>", "<name>", "<string>")


class TokenType(Enum):
    # block of reserved words
    AND = 'and'
    BREAK = 'break'
    DO = 'do'
    ELSE = 'else'
    ELSEIF = 'elseif'
    END = 'end'
    FALSE = 'false'
    FOR = 'for'
    FUNCTION = 'function'
    GOTO = 'goto'
    IF = 'if'
    IN = 'in'
    LOCAL = 'local'
    NIL = 'nil'
    NOT = 'not'
    OR = 'or'
    REPEAT = 'repeat'
    RETURN = 'return'
    THEN = 'then'
    TRUE = 'true'
    UNTIL = 'until'
    WHILE = 'while'

    # single-character token types
    PLUS = '+'
    MINUS = '-'
    MUL = '*'
    FLOAT_DIV = '/'
    PERCENT = '%'
    EXP = '^'
    SH = '#'
    EQUAL = '=='
    NOTEQUAL = '~='
    LEQ = '<='
    GEQ = '>='
    LT = '<'
    GT = '>'
    ASSIGN = '='
    LPAREN = '('
    RPAREN = ')'
    LBRACE = '{'
    RBRACE = '}'
    LBRACKET = '['
    RBRACKET = ']'
    DCOLON = '::'
    SEMIC = ';'
    COLON = ':'
    COMMA = ','
    DOT = '.'
    DDOT = '..'
    ELLIPSIS = '...'
    DLT = '<<'
    DGT = '>>'
    AMPERSAND = '&'
    PIPE = '|'
    DSLASH = '//'
    TILDE = '~'

    EOF = '<eof>'
    NUMBER = '<number>'
    INTEGER = '<integer>'
    IDENTIFIER = '<identifier>'
    STRING = '<string>'


class Token:
    def __init__(self, type, value, lineno=None, column=None):
        self.type = type
        self.value = value
        self.lineno = lineno
        self.column = column

    def __str__(self):
        """String representation of the class instance.
        Example:
            >>> Token(TokenType.INTEGER, 7, lineno=5, column=10)
            Token(TokenType.INTEGER, 7, position=5:10)
        """
        return 'Token({type}, {value}, position={lineno}:{column})'.format(
            type=self.type,
            value=repr(self.value),
            lineno=self.lineno,
            column=self.column,
        )

    def __repr__(self):
        return self.__str__()


def _build_reserved_keywords():
    """Build a dictionary of reserved keywords.
    The function relies on the fact that in the TokenType
    enumeration the beginning of the block of reserved keywords is
    marked with 'AND' and the end of the block is marked with
    the 'WHILE' keyword.
    """
    # enumerations support iteration, in definition order
    tt_list = list(TokenType)
    start_index = 0
    end_index = tt_list.index(TokenType.WHILE)
    reserved_keywords = {
        token_type.value: token_type
        for token_type in tt_list[start_index:end_index + 1]
    }
    return reserved_keywords


RESERVED_KEYWORDS = _build_reserved_keywords()


class Lexer:
    def __init__(self, text):
        # client string input, e.g. "4 + 2 * 3 - 6 / 2"
        self.text = text
        # self.pos is an index into self.text
        self.pos = 0
        self.current_char = self.text[self.pos]
        # token line number and column number
        self.lineno = 1
        self.column = 1

    def error(self):
        s = "Lexer error on '{lexeme}' line: {lineno} column: {column}".format(
            lexeme=self.current_char,
            lineno=self.lineno,
            column=self.column,
        )
        raise LexerError(message=s)

    def advance(self):
        """Advance the `pos` pointer and set the `current_char` variable."""
        if self.current_char == '\n':
            self.lineno += 1
            self.column = 0

        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]
            self.column += 1

    def peek1(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    #to be commented
    def peek2(self , s : str):
        peek_pos = self.pos+1
        if self.text[self.peek_pos] in s:
            self.current_char += self.text[self.peek_pos]
            self.advance()
            return True
        else: return False


    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        while self.current_char != ']' and self.peek1() != ']':
            self.advance()
        self.advance()  # the closing curly brace

    def number(self):
        """Return a (multidigit) integer or float consumed from the input."""

        # Create a new token with current line and column number
        token = Token(type=None, value=None,
                      lineno=self.lineno, column=self.column)

        result = ''
        if self.current_char == '0' and self.peek1() in 'xX':
            # hexadecimal number
            result += self.current_char
            self.advance()
            result += self.current_char
            self.advance()
            while self.current_char is not None and ((self.current_char.isdigit() or self.current_char in 'abcdefABCDEF') or (self.current_char == '.' and '.' not in result)):
                result += self.current_char
                self.advance()
        else: 
            while self.current_char is not None and self.current_char in '0123456789.':
                result += self.current_char
                self.advance()

        if self.current_char == '.':
            result += self.current_char
            self.advance()

            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()

            token.type = TokenType.REAL_CONST
            token.value = float(result)
        else:
            token.type = TokenType.INTEGER_CONST
            token.value = int(result)

        return token

    def _id(self):
        """Handle identifiers and reserved keywords"""

        # Create a new token with current line and column number
        token = Token(type=None, value=None,
                      lineno=self.lineno, column=self.column)

        value = ''
        while self.current_char is not None and self.current_char.isalnum():
            value += self.current_char
            self.advance()

        token_type = RESERVED_KEYWORDS.get(value.upper())
        if token_type is None:
            token.type = TokenType.ID
            token.value = value
        else:
            # reserved keyword
            token.type = token_type
            token.value = value.upper()

        return token

    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)
        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '{':
                self.advance()
                self.skip_comment()
                continue

            if self.current_char.isalpha():
                return self._id()

            if self.current_char.isdigit():
                return self.number()

            if self.current_char == ':' and self.peek1() == '=':
                token = Token(
                    type=TokenType.ASSIGN,
                    value=TokenType.ASSIGN.value,  # ':='
                    lineno=self.lineno,
                    column=self.column,
                )
                self.advance()
                self.advance()
                return token

            # single-character token
            try:
                # get enum member by value, e.g.
                # TokenType(';') --> TokenType.SEMI
                token_type = TokenType(self.current_char)
            except ValueError:
                # no enum member with value equal to self.current_char
                self.error()
            else:
                # create a token with a single-character lexeme as its value
                token = Token(
                    type=token_type,
                    value=token_type.value,  # e.g. ';', '.', etc
                    lineno=self.lineno,
                    column=self.column,
                )
                self.advance()
                return token

        # EOF (end-of-file) token indicates that there is no more
        # input left for lexical analysis
        return Token(type=TokenType.EOF, value=None)
