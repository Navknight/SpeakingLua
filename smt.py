import lexer as lx
import astt


def bool(expr):
    return expr != lx.TokenType.NIL and expr != False


class Semantiff:
    def __init__(self, parser):
        self.parser = parser
        self.symtab = {}

    def create_variable(self, varname, value):
        self.symtab[varname] = value

    def flush(self, varname):
        del self.symtab[varname]

    def find(self):
        self.astt = self.parser.parse()
        return self.evaluate(self.astt)

    def evaluate(self, node):
        # print(node)

        if type(node)==int or type(node)==float:
            return node

        if node is None:  # 3
            return lx.TokenType.NIL

        if type(node) == list:
            a=self.evaluate(node[0])
            for child in node[1:]:
                self.evaluate(child)
            return a

        if type(node) == astt.Num:
            return node.value

        if type(node) == astt.BoolVal:
            return node.value

        elif type(node) == astt.Var:  # RHS variable
            if node.value in self.symtab:  # The 'value' is the variable name here
                return self.symtab[node.value]
            else:
                return lx.TokenType.NIL

        elif type(node) == astt.Assign:
            self.create_variable(node.left.value, self.evaluate(node.right))

            if self.symtab[node.left.value] == lx.TokenType.NIL:  # Clear unnecessary space
                self.flush(node.left.value)
            return lx.TokenType.NIL

        elif type(node) == astt.UnaryOp:
            if node.token == lx.TokenType.PLUS:
                return self.evaluate(node.expr)
            elif node.token == lx.TokenType.MINUS:
                return -self.evaulate(node.expr)
            if node.token == lx.TokenType.NOT:
                return not bool(self.evaluate(node.expr))
            else:
                raise Exception("Unrecognised unary operator: " + str(node.token))


        # Binary operation
        elif type(node) == astt.BinOp:
            if type(node.token)!=lx.TokenType:
                node.token = node.token.type
            # SCC Booleans
            if node.token == lx.TokenType.OR:
                cond = self.evaluate(node.left)
                if bool(cond):
                    return cond
                else:
                    return self.evaluate(node.right)
            if node.token == lx.TokenType.AND:
                cond = self.evaluate(node.left)
                if bool(cond):
                    return cond
                else:
                    return self.evaluate(node.right)

            # Arithmetic expressions
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            if left == lx.TokenType.NIL or right == lx.TokenType.NIL:
                return lx.TokenType.NIL

            if node.token == lx.TokenType.EXP:
                return self.evaluate(left) ** self.evaluate(right)

            if node.token == lx.TokenType.MUL:
                return self.evaluate(right) * self.evaluate(left)
            if node.token == lx.TokenType.FLOAT_DIV:
                return self.evaluate(left) / self.evaluate(right)

            if node.token == lx.TokenType.PLUS:
                return self.evaluate(right) + self.evaluate(left)
            if node.token == lx.TokenType.MINUS:
                return self.evaluate(left) - self.evaluate(right)

            else:
                raise Exception("Unrecognised binary operator: " + str(node.token))


        # While loop
        elif type(node) == astt.While:
            a = 0
            while self.evaluate(node.test):
                a = self.evaluate(node.body)
            return a

        if type(node) == astt.Compare:
            if (type(node.left) == astt.Var):
                left = self.symtab[node.left.token.value]

            if (type(node.right) == astt.Var):
                right = self.symtab[node.right.token.value]

            if (type(node.left) == astt.Num):
                left = node.left.value
            if (type(node.right) == astt.Num):
                right = node.right.value

            if (node.left == lx.TokenType.NIL or node.right == lx.TokenType.NIL):
                return lx.TokenType.NIL
            else:
                if node.op.type == lx.TokenType.GT:
                    return left > right
                elif node.op.type == lx.TokenType.LT:
                    return left < right
                elif node.op.type == lx.TokenType.GEQ:
                    return left >= right
                elif node.op.type == lx.TokenType.LEQ:
                    return left <= right
                elif node.op.type == lx.TokenType.EQUAL:
                    return left == right
                elif node.op.type == lx.TokenType.NOTEQUAL:
                    return left != right
                else:
                    raise Exception("Unrecognised compare operator: " + str(node.op))

        # If-elif-else ladder
        elif type(node) == astt.If:
            if self.evaluate(node.test):
                return self.evaluate(node.body)
            else:
                return self.evaluate(node.alt)

        if type(node) == astt.Compound:
            a = self.evaluate(node.children[0])
            for stmt in node.children[1:]:
                self.evaluate(stmt)
            return a

        if type(node) == astt.Block:
            return self.evaluate(node.compound_statement)

        if type(node) == astt.Program:
            return self.evaluate(node.block)
        # Find weird tokens    
        else:
            raise Exception("Unexpected token error: " + str(type(node)))
