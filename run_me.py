import lexer as lx
import astt as syn
import smt as tiff

def main():
    text=input()
    lex = lx.Lexer(text)
    par = syn.Parser(lex)
    smtff = tiff.Semantiff(par)
    while True:
        text=input()
        lex = lx.Lexer(text)
        par = syn.Parser(lex)
        smtff = tiff.Semantiff(par)
        smtff.find()
        print(smtff.symtab)

if __name__ == '__main__':
    main()
