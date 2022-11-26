import lexer as lx


class AST(object):
    pass

class While(AST): #while loop
    def __init__(self, test, body):
        self.test = test
        self.body = body

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

"""class BoolOp(AST):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right"""

class If(AST):
    def __init__(self, test, body, alt):
        self.test = test
        self.body = body
        self.alt = alt
    

class Compare(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.right = right
        self.op = op

class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class BoolVal(AST):
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

        while (self.current_token.type not in (lx.TokenType.EOF, lx.TokenType.END, lx.TokenType.ELSEIF, lx.TokenType.ELSE) ):
            results.append(self.statement())

        return results

    def statement(self):
        """
        statement : compound_statement
                  | assignment_statement
                  | empty
        """
        if self.current_token.type == lx.TokenType.PRINT:
            node = self.print_statement()
        elif self.current_token.type == lx.TokenType.IDENTIFIER:
            node = self.assignment_statement()
        elif self.current_token.type == lx.TokenType.IF:
            node = self.if_statement()
        elif self.current_token.type == lx.TokenType.WHILE:
            node = self.while_statement()
        elif self.current_token.type == lx.TokenType.NIL:
            node = self.empty()
        else:
            node = self.parent_expr()
        return node

    ##def decider(self):
    ###token = self.


####################################
######### PRINT STATEMENT ##########
####################################

    def print_statement(self):
        """
        print_statement : print LPAREN expr RPAREN
        """

        self.eat(lx.TokenType.PRINT)
        token = self.current_token
        self.eat(lx.TokenType.LPAREN)
        node = self.parent_expr()
        self.eat(lx.TokenType.RPAREN)
        return node    

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
        right = self.parent_expr()
        node = Assign(left, token, right)
        return node

####################################
########## IF STATEMENT ############
####################################

    def if_statement(self):
        #Stand-alone if part
        if (self.current_token.type == lx.TokenType.IF):
            self.eat(lx.TokenType.IF)
        if (self.current_token.type == lx.TokenType.LPAREN):
            self.eat(lx.TokenType.LPAREN)
        condition = self.parent_expr()
        if (self.current_token.type == lx.TokenType.RPAREN):
            self.eat(lx.TokenType.RPAREN)
        self.eat(lx.TokenType.THEN)
        body = Compound()
        body.children=self.statement_list()
        alt = None
        #Elseif Part
        flag = 0
        if (self.current_token.type == lx.TokenType.ELSEIF):
            alt = self.elseif_statement()
            flag=1

        if (flag ==0  and self.current_token.type == lx.TokenType.ELSE):
            self.eat(lx.TokenType.ELSE)
            alt = Compound()
            alt.children=self.statement_list()
        self.eat(lx.TokenType.END)
        node = If(condition, body, alt)
        return node

    def elseif_statement(self):
        self.eat(lx.TokenType.ELSEIF)
        if (self.current_token.type == lx.TokenType.LPAREN):
            self.eat(lx.TokenType.LPAREN)
        elseif_condition = self.conditional_statement()
        if (self.current_token.type == lx.TokenType.RPAREN):
            self.eat(lx.TokenType.RPAREN)
        self.eat(lx.TokenType.THEN)
        elseif_body = Compound()
        elseif_body.children=self.statement_list()
        alt= None
        while (self.current_token.type == lx.TokenType.ELSEIF):
            alt = self.elseif_statement()
        if (self.current_token.type == lx.TokenType.ELSE):
            self.eat(lx.TokenType.ELSE)
            alt = Compound()
            alt.children=self.statement_list()
        elifnode = If(elseif_condition, elseif_body,alt)

        return elifnode
    


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

    def parent_expr(self):
        """expr (( COMPARISON_OPERATOR ) expr)"""

        COMPARISON_OP = {
        lx.TokenType.EQUAL : '==',
        lx.TokenType.NOTEQUAL : '~=',
        lx.TokenType.LEQ : '<=',
        lx.TokenType.GEQ : '>=',
        lx.TokenType.LT : '<',
        lx.TokenType.GT : '>',
        }

        node = self.expr()

        while self.current_token.type in COMPARISON_OP:
            token = self.current_token
            self.eat(token.type)

            node = Compare(left=node, op=token, right=self.expr())

        return node

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
        while self.current_token.type in (lx.TokenType.AND, lx.TokenType.OR):
            token = self.current_token
            if token.type == lx.TokenType.AND:
                self.eat(lx.TokenType.AND)
            elif token.type == lx.TokenType.OR:
                self.eat(lx.TokenType.OR)

            node = Compare(left=node, op=token, right=self.expr())

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
        elif token.type == lx.TokenType.TRUE:
            self.eat(lx.TokenType.TRUE)
            return BoolVal(token)
        elif token.type == lx.TokenType.FALSE:
            self.eat(lx.TokenType.FALSE)
            return BoolVal(token)        
        else:
            node = self.variable()
            return node

    def parse(self):

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
