import lexer as lx


class AST(object):
    pass

class While(AST):
    def __init__(self, test, body):
        self.test = test
        self.body = body

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class If(AST):
    def __init__(self, test, body, elseif_body, orelse):
        self.test = test
        self.elseif_body = elseif_body
        self.body = body
        
        self.orelse = orelse
    
class ElseIf(AST):
    def __init__(self, test, body):
        self.test = test
        self.body = body

class Compare(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.right = right
        self.op = op

class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr


class Compound(AST):
    """Represents a 'BEGIN ... END' block"""
    def __init__(self):
        self.children = []


class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Var(AST):
    """The Var node is constructed out of IDENTIFIER token."""
    def __init__(self, token):
        self.token = token
        self.value = token.value


class NoOp(AST):
    pass


class Program(AST):
    def __init__(self, block):
        self.block = block


class Block(AST):
    def __init__(self, compound_statement):
        self.compound_statement = compound_statement


class VarDecl(AST):
    def __init__(self, var_node):
        self.var_node = var_node


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def program(self):
        #program : PROGRAM variable SEMI block DOT
        block_node = self.block()
        program_node = Program(block_node)
        return program_node

    def block(self):
        """block : declarations compound_statement"""
        #declaration_nodes = self.declarations()
        compound_statement_node = self.compound_statement()
        node = Block(compound_statement_node)
        return node
    """
    def declarations(self):
        declarations : VAR (variable_declaration SEMI)+
                        | empty
        
        declarations = []
        if self.current_token.type == VAR:
            self.eat(VAR)
            while self.current_token.type == IDENTIFIER:
                var_decl = self.variable_declaration()
                declarations.extend(var_decl)

        return declarations

    def variable_declaration(self):
        variable_declaration : IDENTIFIER (COMMA IDENTIFIER)* COLON type_spec
        var_nodes = [Var(self.current_token)]  # first IDENTIFIER
        self.eat(IDENTIFIER)

        while self.current_token.type == COMMA:
            self.eat(COMMA)
            var_nodes.append(Var(self.current_token))
            self.eat(IDENTIFIER)

        var_declarations = [
            VarDecl(var_node)
            for var_node in var_nodes
        ]
        return var_declarations

    def type_spec(self):
        type_spec : INTEGER
                     | REAL
        
        token = self.current_token
        if self.current_token.type == INTEGER:
            self.eat(INTEGER)
        else:
            self.eat(REAL)
        node = Type(token)
        return node
    """

    def compound_statement(self):
        
        #compound_statement: BEGIN statement_list END
        nodes = self.statement_list()

        root = Compound()
        for node in nodes:
            root.children.append(node)

        return root

    def statement_list(self):
        """
        statement_list : statement
                       | statement SEMI statement_list
        """
        node = self.statement()

        results = [node]

        while (self.current_token.type != lx.TokenType.EOF and self.current_token.type != lx.TokenType.END) :
            results.append(self.statement())

        return results

    def statement(self):
        """
        statement : compound_statement
                  | assignment_statement
                  | empty
        """
        if self.current_token.type == lx.TokenType.IDENTIFIER:
            node = self.assignment_statement()
        elif self.current_token.type == lx.TokenType.IF:
            node = self.if_statement()
        elif self.current_token.type == lx.TokenType.WHILE:
            node = self.while_statement()
        elif self.current_token.type == lx.TokenType.NIL:
            node = self.empty()
        else:
            node = self.conditional_statement()
        return node

    ##def decider(self):
    ###token = self.

####################################
####### ASSIGNMENT STATEMENT #######
####################################
    def assignment_statement(self):
        """
        assignment_statement : variable ASSIGN expr
        """

        left = self.variable()
        token = self.current_token
        self.eat(lx.TokenType.ASSIGN)
        right = self.expr()
        node = Assign(left, token, right)
        return node

####################################
########## IF STATEMENT ############
####################################

    def if_statement(self):
        if (self.current_token.type == lx.TokenType.IF):
            self.eat(lx.TokenType.IF)
        if (self.current_token.type == lx.TokenType.LPAREN):
            self.eat(lx.TokenType.LPAREN)
        condition = self.conditional_statement()
        if (self.current_token.type == lx.TokenType.RPAREN):
            self.eat(lx.TokenType.RPAREN)
        self.eat(lx.TokenType.THEN)
        body = self.statement_list()
        elifs = []
        while (self.current_token.type == lx.TokenType.ELSEIF):
            self.eat(lx.TokenType.ELSEIF)
            if (self.current_token.type == lx.TokenType.LPAREN):
                self.eat(lx.TokenType.LPAREN)
            elseif_condition = self.conditional_statement()
            if (self.current_token.type == lx.TokenType.RPAREN):
                self.eat(lx.TokenType.RPAREN)
            self.eat(lx.TokenType.THEN)
            elseif_body = self.statement_list() 
            elifnode = ElseIf(elseif_condition, elseif_body)
            elifs.append(elifnode)
        orbody = []
        if (self.current_token.type == lx.TokenType.ELSE):
            self.eat(lx.TokenType.ELSE)
            orbody = self.statement_list()
        self.eat(lx.TokenType.END)
        node = If(condition, body, elifs, orbody)
        return node


####################################
########## WHILE STATEMENT #########
####################################

    def while_statement(self):
        if (self.current_token.type == lx.TokenType.WHILE):
            self.eat(lx.TokenType.WHILE)
        if (self.current_token.type == lx.TokenType.LPAREN):
            self.eat(lx.TokenType.LPAREN)
        condition = self.conditional_statement()
        if (self.current_token.type == lx.TokenType.RPAREN):
            self.eat(lx.TokenType.RPAREN)
        self.eat(lx.TokenType.DO)
        body = self.statement_list()
        self.eat(lx.TokenType.END)
        node = While(condition, body)
        return node

####################################
###### CONDITIONAL STATEMENT #######
####################################


    def conditional_statement(self):
        """
        conditional_statement : expr COMPARISON_OP expr
        """
        COMPARISON_OP = {
        lx.TokenType.EQUAL : '==',
        lx.TokenType.NOTEQUAL : '~=',
        lx.TokenType.LEQ : '<=',
        lx.TokenType.GEQ : '>=',
        lx.TokenType.LT : '<',
        lx.TokenType.GT : '>',
        }
        left = self.expr()
        token = self.current_token
        if (self.current_token.type in COMPARISON_OP):
            self.eat(token.type)
        right = self.expr()
        node = Compare(left, token, right)
        return node



#####################################
#####################################
#####################################

    def variable(self):
        """
        variable : IDENTIFIER
        """
        node = Var(self.current_token)
        self.eat(lx.TokenType.IDENTIFIER)
        return node

    def empty(self):
        """An empty production"""
        return NoOp()

    def expr(self):
        """
        expr : term (( PLUS | MINUS) term)*
        """
        node = self.term()

        while self.current_token.type in (lx.TokenType.PLUS, lx.TokenType.MINUS):
            token = self.current_token
            if token.type == lx.TokenType.PLUS:
                self.eat(lx.TokenType.PLUS)
            elif token.type == lx.TokenType.MINUS:
                self.eat(lx.TokenType.MINUS)

            node = BinOp(left=node, op=token, right=self.term())

        return node

    def term(self):
        """term : factor ((MUL |33 FLOAT_DIV) factor)*"""
        node = self.factor()

        while self.current_token.type in (lx.TokenType.MUL, lx.TokenType.FLOAT_DIV):
            token = self.current_token
            if token.type == lx.TokenType.MUL:
                self.eat(lx.TokenType.MUL)
            elif token.type == lx.TokenType.FLOAT_DIV:
                self.eat(lx.TokenType.FLOAT_DIV)

            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def factor(self):
        """factor : PLUS factor
                  | MINUS factor
                  | _CONST
                  | NUMBER
                  | LPAREN expr RPAREN
                  | variable
        """
        token = self.current_token
        if token.type == lx.TokenType.PLUS:
            self.eat(lx.TokenType.PLUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == lx.TokenType.MINUS:
            self.eat(lx.TokenType.MINUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == lx.TokenType.INTEGER:
            self.eat(lx.TokenType.INTEGER)
            return Num(token)
        elif token.type == lx.TokenType.NUMBER:
            self.eat(lx.TokenType.NUMBER)
            return Num(token)
        elif token.type == lx.TokenType.LPAREN:
            self.eat(lx.TokenType.LPAREN)
            node = self.expr()
            self.eat(lx.TokenType.RPAREN)
            return node
        else:
            node = self.variable()
            return node

    def parse(self):
        """
        program : PROGRAM variable SEMI block DOT
        block : declarations compound_statement
        declarations : VAR (variable_declaration SEMI)+
                     | empty
        variable_declaration : IDENTIFIER (COMMA IDENTIFIER)* COLON type_spec
        type_spec : INTEGER | REAL
        compound_statement : BEGIN statement_list END
        statement_list : statement
                       | statement SEMI statement_list
        statement : compound_statement
                  | assignment_statement
                  | empty
        assignment_statement : variable ASSIGN expr
        empty :
        expr : term ((PLUS | MINUS) term)*
        term : factor ((MUL | INTEGER_DIV | FLOAT_DIV) factor)*
        factor : PLUS factor
               | MINUS factor
               | INTEGER
               | NUMBER
               | LPAREN expr RPAREN
               | variable
        variable: IDENTIFIER
        """
        node = self.program()
        if self.current_token.type != lx.TokenType.EOF:
            self.error()

        return node


def main():
    with open('test_lexer.txt') as f:
        text = f.read()
    lex = lx.Lexer(text)
    par = Parser(lex)
    result = par.parse()
    print(result)
    """while True:
        tok = lex.get_next_token()
        if tok.value is None:
            break
        print(tok)"""

if __name__ == '__main__':
    main()
