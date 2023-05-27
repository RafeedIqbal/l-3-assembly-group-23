         BR      program 
_UNIV:   .EQUATE 42
x:       .BLOCK 2
result:  .BLOCK 2
retVal:  .EQUATE 2           ;return #2d
value:   .EQUATE 0           ;value #2d

my_func: LDWA 4,s
         ADDA _UNIV,i
         STWA retVal,s
         RET         
program: SUBSP 2,i           ; push #value 
         DECI x,d
         LDWA x,d
         STWA value,s
         SUBSP 2,i           ; push #retVal
         CALL my_func
         LDWA 0,s
         STWA result,d 
         ADDSP 4,i           ; pop #value #retVal
         DECO result,d
         .END
         