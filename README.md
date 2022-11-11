# SpeakingLua
###### A project to interpret a subset of Lua.  
Lua is dynamically typed and needs no explicit casts for type. Check the [Lua reference manual](https://www.lua.org/manual/) for details.  
The interfaces for our code and the meaning of each step can be found [here](https://ruslanspivak.com/lsbasi-part7/). The given is part 7, the bare minimum to get started.

##### Update!
We're done with our basic coding stuff, so let's go to the testing!  
Every file is tested using test_*.py

Lastly, we may want a dedicated handler program

## Lexer
#### Niraj and Abhinav
Input: A stream of characters i.e. string

Output: The next token(number/identifier/keyword/...)

## Parser
#### Teja and Keshav
Input: A list of tokens one at a time, with a lookahead of 1 token.

Output: The AST(Abstract Syntax Tree)

## Semantic analyser
#### Arvind Srinivasan
Input: AST

Output: Execution
