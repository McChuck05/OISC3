# OISC3
Obfuscated Indirect Subleq with Coprocessor: 3 word instructions

Positive and negative memory both exist in the same save file.  Instructions are restricted to positive memory.  Indirect addressing is accomplished through the use of real/float/decimal numbers ("121.0").  This is the key to unlocking useful negative addressing and simplifying everything.

The assembler will work with raw numbers, names, and even with the built in instruction macro names (in italics below).  And yes, I have a working assembler and interpreter.  It even can output an executable raw numbers file.

The assembler/interpreter is written in Python.  It will optionally produce a compiled code file.
Usage: python oisc3.py infile.o3a [outfile.o3c]

Instruction formats:

  A B C    [C] = [B] - [A]                 /sub
  A B 0    [B] = [B] - A                   /lit-
  A 0 C    if [A] <= 0, call C             /call  (pushes NextIP onto the return stack)               
  0 B C    if [B] <= 0, jump to C          /jump
  A 0 0    push [A] onto the stack         /push
  0 B 0    pop the top of stack to B       /pop
  0 0 C    execute instruction [C]         /exec  (operates on the stack)               
  0 0 0    return                          /ret  (pops the top of return stack to NextIP)

Assembler formats:

 \#            comment
 %            data
 name:        naming a memory word
 name         using a named word
 \*name        indirect reference [[name]] (if N is 23, \*N is 23.0)
 @            this word
 ?            next word
 % --NEGATIVE: --NEGATIVE--     mandatory memory separator
 !            0
 ;            end of instruction
 ,            separator
 " or '       string delimiters
 ZERO         automatically created word containing 0
 
 /sub can be called with 1, 2 or 3 words
    A B C    [C] = [B] - [A]    
    A B      [B] = [B] - [A]   
    A        [A] = 0  
     
 /lit- must be called with 2 words
    A B      [B] = [B] - A
     
 /call and /jump can be called with 1 or 2 words.
    A B      if [A] <= 0, branch to B   
    A        unconditional branch to A
      
 /push, /pop and /exec are called with 1 word
    A        push [A] / pop to [A] / execute instruction [A]
      
 /ret takes no arguments.  If the return stack is empty, the program will halt.  Branching to a negative address will also halt.

Stack instructions:

      Positive                      Negative 
 1    input char ( -- a)            output char (a -- )
 2    input digit  ( -- a)          output number (a -- )
 3    DUP (a -- aa)                 DROP (a -- )
 4    OVER (ab -- aba)              SWAP (ab -- ba)
 5    roll left N (abcd1 -- bcda)   roll right N (abcd2 -- cdab)
 6    reverse stack (abcd -- dcba)  clear stack (abcd -- )
 7    depth of stack ( -- a)        pick N (abcd3 -- abcdb)
 8    bitwise true ( -- -1)         bitwise false ( -- 0)
 9    bitwise AND (ab -- a&b)       bitwise NOT (a -- ~a)
 10   bitwise OR (ab -- a|b)        bitwise XOR (ab -- a^b)
 11   shift left N bits (aN -- a)   shift right N bits (aN -- a)
 12   times (ab -- a\*b)             divide (ab -- a/b)
 13   int division (ab -- a//b)     remainder (ab -- a%b)
 14   exponent e (a -- exp(a))      natural log (a -- log(a))
 15   convert to integer (a -- a)   convert to float (a -- a)
 16   alloc N words (sign matters)  free N words (sign matters)
 17   plus (ab -- a+b)              minus (ab -- a-b)
 18   sin (a -- sin(a))             asin (a -- asin(a))
 19   cos (a -- cos(a))             acos (a -- acos(a))
 20   tan (a -- tan(a))             atan (a -- atan(a)) 
 21   sinh (a -- sinh(a))           asinh (a -- asinh(a)) 
 22   cosh (a -- cos(a))            acosh (a -- acosh(a)) 
 23   tanh (a -- cos(a))            atanh (a -- atanh(a)) 

