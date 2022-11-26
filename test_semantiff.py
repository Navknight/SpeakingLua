#This file is meant to test smt.py

import lexer as lx
import ast as syn
import smt as tiff

def main():
    with open('test_lexer.txt') as f:
        text = f.read()
    lex = lx.Lexer(text)
    par = syn.Parser(lex)
    smtff = tiff.Semantiff(par)
    result = smtff.find()
    print(result)
    """while True:
        tok = lex.get_next_token()
        if tok.value is None:
            break
        print(tok)"""

if __name__ == '__main__':
    main()
