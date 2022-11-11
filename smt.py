import lexer as lx
import ast

class Semantiff:
    def __init__(self, parser, code):
        self.parser=parser
        self.ast=parser.parse(code) #Directly storing the AST
        self.symtab={}
    
    def create_variable(varname, value):
        symtab[varname]=value
    
    def flush(varname):
        del symtab[varname]
        
    def evaluate(node):
        if type(node)==ast.Num:
            return node.value
        
        elif type(node)==ast.Var: #RHS variable
            if symtab.has_key(node.value): #The 'value' is the variable name here
                return symtab[node.value]
            else: return lx.NIL
        
        elif type(node)==ast.VarDecl:
            return node.value
        
        elif type(node)==ast.Assign:
            symtab[node.left.value]=self.evaluate(node.right)
            
            if symtab[node.left.value]==lx.NIL: #Clear unnecessary space
                self.flush(node.left.value)
            return lx.NIL
        
        elif type(node)==ast.UnaryOp:
            if node.token==lx.TokenType.PLUS:
                return self.evaluate(node.expr)
            elif node.token==lx.TokenType.MINUS:
                return -self.evaulate(node.expr)
            else:
                raise Exception("Unrecognised unary operator")
        elif type(node)==ast.BinOp:
            if node.right.value==lx.NIL or node.right.value==lx.NIL:
                return lx.NIL
            
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
                raise Exception("Unrecognised binary operator")
        else:
            raise Exception("Unexpected token error: "+node)
