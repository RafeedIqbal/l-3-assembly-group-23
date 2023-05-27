         BR      program
a:       .BLOCK 2
b:       .BLOCK 2
gcd:     LDWA a,d
         CPWA b,d
         BREQ end
         BRLE else
if:      SUBA b,d
         STWA a,d
         BR gcd
else:    LDWA b,d
         SUBA a,d
         STWA b,d
         BR gcd
end:     RET
program: DECI a,d
         DECI b,d
         CALL gcd
         DECO a,d
         .END
         
   
         
         