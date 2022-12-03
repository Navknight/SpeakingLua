# This file is meant to test smt.py

import lexer as lx
import astt as syn
import smt as tiff


def main():
    with open('code.txt') as f:
        text = f.read()
    lex = lx.Lexer(text)
    par = syn.Parser(lex)
    smtff = tiff.Semantiff(par)
    smtff.find()
    print(smtff.symtab)
    """while True:
        tok = lex.get_next_token()
        if tok.value is None:
            break
        print(tok)"""


if __name__ == '__main__':
    main()
