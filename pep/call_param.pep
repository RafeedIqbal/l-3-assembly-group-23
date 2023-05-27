         BR      program
x:       .BLOCK 2
result:  .BLOCK 2                        
_UNIV:   .EQUATE 42          
value:   .EQUATE 2           ;value #2d
my_func: LDWA 2,s
         ADDA _UNIV,i
         STWA result,d 
         DECO result,d
         RET
program: SUBSP 2,i           ;Allocate #value 
         DECI x,d
         LDWA x,d
         STWA 0,s
         CALL my_func
         .END