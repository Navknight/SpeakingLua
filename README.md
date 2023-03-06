# SpeakingLua
###### A project to interpret a subset of Lua.  
Lua is dynamically typed and needs no explicit casts for type. Check the [Lua reference manual](https://www.lua.org/manual/) for details.

##### How to Use
Run test_semantiff.py
The code in code.txt is run and the variables are outputted at program end.

The given example is the sum of cubes from 0 to 10.
The output should be:
a: 10
b: 3025
(Not the exact format)

The code file may be changed to check various files

## Lexer
#### Niraj and Abhinav
Input: A stream of characters i.e. string

Output: The next token(number/identifier/keyword/...)

## Parser
#### B Teja and Keshav
Input: A list of tokens one at a time, with a lookahead of 1 token.

Output: The AST(Abstract Syntax Tree)

## Semantic analyser
#### Arvind Srinivasan
Input: AST

Output: Execution


