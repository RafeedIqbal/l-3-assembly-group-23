         BR      program
_UNIV:   .EQUATE 42
value:   .EQUATE 0           ; value #2d
result:  .EQUATE 2           ; result #2d
my_func: SUBSP 4,i           ; push #result #value 
         DECI value,s
         LDWA value,s
         ADDA _UNIV,i
         STWA result,s
         DECO result,s
         ADDSP 4,i           ; pop #result #value
         RET
program: CALL my_func
         .END 
         