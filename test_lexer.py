import lexer as lx


def main():
    with open('test_lexer.txt') as f:
        text = f.read()
    lex = lx.Lexer(text)
    while True:
        tok = lex.get_next_token()
        if tok.value is None:
            break
        print(tok)

if __name__ == '__main__':
    main()
