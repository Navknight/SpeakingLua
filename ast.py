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

class BoolOp(AST):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class If(AST):
    def __init__(self, test, body, orelse):
        self.test = test
        self.body = body
        self.orelse = orelse
    
class If(AST):
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


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lx.Lexer
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

        while self.current_token.type == #NEWLINE:
            #self.eat(TOKEN)
            results.append(self.statement())

        return results

    def statement(self):
        """
        statement : compound_statement
                  | assignment_statement
                  | empty
        """
        if self.current_token.type == IDENTIFIER:
            node = self.assignment_statement()
        elif self.current_token.type == IF:
            node = self.if_statement()
        elif self.current_token.type == WHILE:
            node = self.while_statement()
        elif self.current_token.type == NULL:
            node = self.empty()
        else:
            node = self.expr()
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
        self.eat(ASSIGN)
        right = self.expr()
        node = Assign(left, token, right)
        return node

####################################
########## IF STATEMENT ############
####################################

    def if_statement(self):
        if (self.current_token.type == IF):
            self.eat(IF)
        if (self.current_token.type == LPAREN):
            self.eat(LPAREN)
        condition = self.conditional_statement()
        if (self.current_token.type == RPAREN):
            self.eat(RPAREN)
        self.eat(THEN)
        body = self.statement_list()
        orbody = []
        if (self.current_token.type == ELSE):
            self.eat(ELSE)
            orbody = self.statement_list()
        self.eat(END)
        node = If(condition, body, orbody)
        return node


####################################
########## WHILE STATEMENT #########
####################################

    def while_statement(self):
        if (self.current_token.type == WHILE):
            self.eat(WHILE)
        if (self.current_token.type == LPAREN):
            self.eat(LPAREN)
        condition = self.conditional_statement()
        if (self.current_token.type == RPAREN):
            self.eat(RPAREN)
        self.eat(DO)
        body = self.statement_list()
        self.eat(END)
        node = If(condition, body)
        return node

####################################
###### CONDITIONAL STATEMENT #######
####################################


    def conditional_statement(self):
        """
        conditional_statement : expr COMPARISON_OP expr
        """
        COMPARISON_OP = {
        EQUAL : '==',
        NOTEQUAL : '~=',
        LEQ : '<=',
        GEQ : '>=',
        LT : '<',
        GT : '>',
        }
        left = self.expr()
        token = self.current_token
        if (self.current_token.type in COMPARISON_OP):
            self.eat(token)
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
        self.eat(IDENTIFIER)
        return node

    def empty(self):
        """An empty production"""
        return NoOp()

    def expr(self):
        """
        expr : term (( PLUS | MINUS) term)*
        """
        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)

            node = BinOp(left=node, op=token, right=self.term())

        return node

    def term(self):
        """term : factor ((MUL |33 FLOAT_DIV) factor)*"""
        node = self.factor()

        while self.current_token.type in (MUL, FLOAT_DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == FLOAT_DIV:
                self.eat(FLOAT_DIV)

            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def factor(self):
        """factor : PLUS factor
                  | MINUS factor
                  | _CONST
                  | REAL_CONST
                  | LPAREN expr RPAREN
                  | variable
        """
        token = self.current_token
        if token.type == PLUS:
            self.eat(PLUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == MINUS:
            self.eat(MINUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == INTEGER_CONST:
            self.eat(INTEGER_CONST)
            return Num(token)
        elif token.type == REAL_CONST:
            self.eat(REAL_CONST)
            return Num(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
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
               | INTEGER_CONST
               | REAL_CONST
               | LPAREN expr RPAREN
               | variable
        variable: IDENTIFIER
        """
        node = self.program()
        if self.current_token.type != EOF:
            self.error()

        return node