import lexer as lx
import ast

def bool(expr):
    return expr!=lx.TokenType.NIL and expr!=False

class Semantiff:
    def __init__(self, parser):
        self.parser=parser
        self.ast=parser.parse() #Directly storing the AST
        self.symtab={}
    
    def create_variable(varname, value):
        symtab[varname]=value
    
    def flush(varname):
        del symtab[varname]
        
    def evaluate(node):
        if node==None: #3
            return lx.TokenType.NIL
        
        if type(node)==ast.Num:
            return node.value
        
        if type(node)==ast.BoolVal:
            return node.value
        
        elif type(node)==ast.Var: #RHS variable
            if symtab.has_key(node.value): #The 'value' is the variable name here
                return symtab[node.value]
            else: return lx.TokenType.NIL
        
        elif type(node)==ast.VarDecl:
            return node.value
        
        elif type(node)==ast.Assign:
            self.create_variable(node.left.value, self.evaluate(node.right))
            
            if symtab[node.left.value]==lx.TokenType.NIL: #Clear unnecessary space
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
                raise Exception("Unrecognised unary operator: "+node)
                
                
        #Binary operation
        elif type(node)==ast.BinOp:
            
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
                raise Exception("Unrecognised binary operator: "+node)
                
         
        #While loop
        elif type(node)==ast.While:
            a = 0
            while self.evaluate(node.test):
                a=self.evaluate(node.body)
            return a
        
        
        #If-elif-else ladder
        elif type(node)==ast.Else:
            return self.evaluate(node.body)
        
        elif type(node)==ast.If:
            if self.evaluate(node.test):
                return self.evaluate(node.body)
            else:
                return self.evaluate(node.alt)
            
        # Find weird tokens    
        else:
            raise Exception("Unexpected token error: "+node)
