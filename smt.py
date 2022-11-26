import lexer as lx
import ast

def bool(expr):
    return expr!=lx.TokenType.NIL and expr!=False

class Semantiff:
    def __init__(self, parser):
        self.parser=parser
        self.ast=parser.parse() #Directly storing the AST
        self.symtab={}
    
    def create_variable(self, varname, value):
        self.symtab[varname]=value
    
    def flush(self, varname):
        del self.symtab[varname]

    def find(self):
        return self.evaluate(self.ast)
        
    def evaluate(self, node):
        print(node)

        if node==None: #3
            return lx.TokenType.NIL
        
        if type(node)==ast.Num:
            return node.value
        
        if type(node)==ast.BoolVal:
            return node.value
        
        elif type(node)==ast.Var: #RHS variable
            if node.value in self.symtab: #The 'value' is the variable name here
                return self.symtab[node.value]
            else: return lx.TokenType.NIL
        
        elif type(node)==ast.Assign:
            self.create_variable(node.left.value, self.evaluate(node.right))
            
            if self.symtab[node.left.value]==lx.TokenType.NIL: #Clear unnecessary space
                self.flush(node.left.value)
            return lx.TokenType.NIL
        
        elif type(node)==ast.UnaryOp:
            if node.token==lx.TokenType.PLUS:
                return self.evaluate(node.expr)
            elif node.token==lx.TokenType.MINUS:
                return -self.evaulate(node.expr)
            if node.token==lx.TokenType.NOT:
                return not bool(self.evaluate(node.expr))
            else:
                raise Exception("Unrecognised unary operator: "+str(node.token))
                
                
        #Binary operation
        elif type(node)==ast.BinOp:
            node.token=node.token.type
            # SCC Booleans
            if node.token==lx.TokenType.OR:
                cond = self.evaluate(node.left)
                if bool(cond):
                    return cond
                else:
                    return self.evaluate(node.right)            
            if node.token==lx.TokenType.AND:
                cond = self.evaluate(node.left)
                if bool(cond):
                    return cond
                else:
                    return self.evaluate(node.right)
                
             
            #Arithmetic expressions
            if node.right.value==lx.TokenType.NIL or node.right.value==lx.TokenType.NIL:
                return lx.TokenType.NIL
            
            if node.token==lx.TokenType.EXP:
                return self.evaluate(node.left)**self.evaluate(node.right)
            
            if node.token==lx.TokenType.MUL:
                return self.evaluate(node.right)*self.evaluate(node.left)
            if node.token==lx.TokenType.FLOAT_DIV:
                return self.evaluate(node.left)/self.evaluate(node.right)
            
            if node.token==lx.TokenType.PLUS:
                return self.evaluate(node.right)+self.evaluate(node.left)
            if node.token==lx.TokenType.MINUS:
                return self.evaluate(node.left)-self.evaluate(node.right)
            
            else:
                raise Exception("Unrecognised binary operator: "+str(node.token))
                
         
        #While loop
        elif type(node)==ast.While:
            a = 0
            while self.evaluate(node.test):
                a=self.evaluate(node.body)
            return a
        
        
        if type(node)==ast.Compare:
            if (type(node.left)==ast.Var):
                node.left=self.symtab[node.left.token.value]

            if (type(node.right)==ast.Var):
                node.right=self.symtab[node.right.token.value]

            if (type(node.left)==ast.Num):
                node.left=node.left.value
            if (type(node.right)==ast.Num):
                node.right=node.right.value

            if (node.left==lx.TokenType.NIL or node.right==lx.TokenType.NIL):
                return lx.TokenType.NIL
            else:
                if node.op.type==lx.TokenType.GT:
                    return node.left>node.right
                elif node.op.type==lx.TokenType.LT:
                    return node.left<node.right
                elif node.op.type==lx.TokenType.GEQ:
                    return node.left>=node.right
                elif node.op.type==lx.TokenType.LEQ:
                    return node.left<=node.right
                elif node.op.type==lx.TokenType.EQUAL:
                    return node.left==node.right
                elif node.op.type==lx.TokenType.NOTEQUAL:
                    return node.left!=node.right
                else:
                    raise Exception("Unrecognised compare operator: "+str(node.op))

        #If-elif-else ladder
        elif type(node)==ast.If:
            if self.evaluate(node.test):
                return self.evaluate(node.body)
            else:
                return self.evaluate(node.alt)
            

        if type(node)==ast.Compound:
            a=self.evaluate(node.children[0])
            for stmt in node.children[1:]:
                self.evaluate(stmt)
            return a

        if type(node)==ast.Block:
            return self.evaluate(node.compound_statement)

        if type(node)==ast.Program:
            return self.evaluate(node.block)
        # Find weird tokens    
        else:
            raise Exception("Unexpected token error: "+str(type(node)))
