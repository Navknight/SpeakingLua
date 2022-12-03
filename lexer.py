from enum import Enum
import re


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
    # print(Error)
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
    PRINT = 'print'
    FUNCTION = 'function'

    # single-character token types
    PLUS = '+' # +
    MINUS = '-' # unary minus
    MUL = '*'  # multiplication
    FLOAT_DIV = '/' # float division
    PERCENT = '%' # modulo
    EXP = '^' # exponentiation
    SH = '#' # length operator
    EQUAL = '==' # equality
    NOTEQUAL = '~=' # inequality
    LEQ = '<=' # less than or equal to
    GEQ = '>=' # greater than or equal to
    LT = '<'    # less than
    GT = '>'   # greater than
    ASSIGN = '=' # assignment
    LPAREN = '(' # left parenthesis
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

    #keywords in lua
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
        print(s)
        exit()
        # raise LexerError(s)

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

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        if self.current_char == '[' and self.peek() == '[':
            self.advance()
            self.advance()
            while self.current_char is not None and (self.text[self.pos: self.pos+4] != '--]]'):
                self.advance()
            self.advance()
            self.advance()
            self.advance()
            self.advance()
        else:
            while self.current_char is not None and (self.current_char != '\n'):
                self.advance()
            self.advance()

    def read_string(self, delimit):
        """Read a string literal token from the input.
        The opening delimiter is passed as an argument.
        """

        token = Token(type=None, value=None,
                      lineno=self.lineno, column=self.column)

        string = '' if delimit == "'" else ""
        self.advance()
        while self.current_char is not None and self.current_char != delimit:
            if self.current_char == '\\':
                match self.peek():
                    case '"':
                        string += '\"'
                    case 'n':
                        string += '\n'
                    case '\\':
                        string += '\\'
                    case 'r':
                        string += '\r'
                    case "'":
                        string += "\'"
                    case "t":
                        string += '\t'
                    case "b":
                        string += '\b'
                    case "f":
                        string += '\f'
                self.advance()
                self.advance()
                continue
            string += self.current_char
            self.advance()
        if self.current_char is None:
            self.error()
        self.advance()
        try:
            token.value = string
            token.type = TokenType.STRING
        except ValueError:
            self.error()

        return token

    def number(self):
        """Return a (multidigit) integer or float consumed from the input."""

        # Create a new token with current line and column number
        token = Token(type=None, value=None,
                      lineno=self.lineno, column=self.column)

        result = ''
        if self.current_char == '0' and self.peek() in 'xX':
            # hexadecimal number
            result += self.current_char
            self.advance()
            result += self.current_char
            self.advance()
            while self.current_char is not None and ((self.current_char.isdigit() or self.current_char in 'abcdefABCDEF') or (self.current_char == '.' and '.' not in result)):
                result += self.current_char
                self.advance()
        else:
            while self.current_char is not None and (self.current_char in '0123456789' or self.current_char == '.' and '.' not in result):
                result += self.current_char
                self.advance()
            if self.current_char is not None and re.search("[a-zA-Z]", self.current_char):
                self.error()

        try:
            token.value = int(result,10) if 'x' not in result else int(result,16)
            token.type = TokenType.INTEGER
        except ValueError:
            #try:
                token.value = float(result) if 'x' not in result else float.fromhex(result)
                token.type = TokenType.NUMBER
            #except ValueError:
                # try:
                #     token.value = float.fromhex(
                #         result) if '.' in result else int.fromhex(result)
                #     token.type = TokenType.NUMBER if '.' in result else TokenType.INTEGER
                # except ValueError:
                #     self.error()
        return token

    def _id(self):
        """Handle identifiers and reserved keywords"""

        # Create a new token with current line and column number
        token = Token(type=None, value=None,
                      lineno=self.lineno, column=self.column)

        value = ''
        while self.current_char is not None and self.current_char.isalnum() or self.current_char == '_':
            value += self.current_char
            self.advance()

        token_type = RESERVED_KEYWORDS.get(value)
        if token_type is None:
            token.type = TokenType.IDENTIFIER
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
            if self.current_char == '\n' or self.current_char == '\r':
                self.advance()
                continue
            # can be made more effifient by using a function to skip chunks
            if self.current_char == '\f' or self.current_char == '\v' or self.current_char == '\t':
                self.advance()
                continue

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '-' and self.peek() == '-':
                self.advance()
                self.advance()
                self.skip_comment()
                continue

            if self.current_char == '"' or self.current_char == "'":
                return self.read_string(self.current_char)

            if self.current_char.isalpha() or self.current_char == '_':
                return self._id()

            if self.current_char.isdigit():
                return self.number()

            if self.text[self.pos: self.pos+3] == '...':
                token = Token(
                    type=TokenType.ELLIPSIS,
                    value=TokenType.ELLIPSIS.value,
                    lineno=self.lineno,
                    column=self.column,
                )
                self.advance()
                self.advance()
                self.advance()
                return token

            # single-character token
            try:
                # get enum member by value, e.g.
                # TokenType(';') --> TokenType.SEMI
                if len(self.text) > (self.pos + 1):
                    if self.current_char + self.text[self.pos + 1] in list(x.value for x in TokenType):
                        token_type = TokenType(
                            self.current_char + self.text[self.pos + 1])
                    else:
                        token_type = TokenType(self.current_char)
                else:
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
                if len(token.value) == 2:
                    self.advance()
                    self.advance()
                else:
                    self.advance()
                return token

        # EOF (end-of-file) token indicates that there is no more
        # input left for lexical analysis
        return Token(type=TokenType.EOF, value=None)
