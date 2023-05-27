         BR      program 
UNIV:            .WORD 42 
value:           .BLOCK 2
result:          .BLOCK 2
variable:        .BLOCK 2
program: DECI     value,d
         LDWA     value,d
         ADDA     UNIV,d
         STWA     result,d
         LDWA     3,i
         STWA     variable,d
         LDWA     result,d        
         SUBA     variable,d
         STWA     result,d
         LDWA     result,d
         SUBA     1,i
         STWA     result,d
         DECO     result,d
         LDBA     '\n',i
         STBA     charOut,d
         .END

