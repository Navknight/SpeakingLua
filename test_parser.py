import lexer as lx
import ast as syntree

def main():
    with open('test_lexer.txt') as f:
        text = f.read()
    lex = lx.Lexer(text)
    par = syntree.Parser(lex)
    result = par.parse()
    print(result)
    """while True:
        tok = lex.get_next_token()
        if tok.value is None:
            break
        print(tok)"""

if __name__ == '__main__':
    main()