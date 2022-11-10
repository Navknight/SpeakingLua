import lexer as lx
import ast as syn

def main():
    with open('test_lexer.txt') as f:
        text = f.read()
    lex = lx.Lexer(text)
    par = syn.Parser(lex)
    result = par.parse()
    print(result)
    """while True:
        tok = lex.get_next_token()
        if tok.value is None:
            break
        print(tok)"""

if __name__ == '__main__':
    main()