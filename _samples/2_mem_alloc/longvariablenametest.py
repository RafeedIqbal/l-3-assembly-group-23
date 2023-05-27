n012345678 = int(input())        # .BLOCK 2
a012345678 = 0                   # .WORD 0
b012345678 = 1                   # .WORD 1
i012345678 = 0                   # .WORD 1
while i012345678 < n012345678:
    tmp012345678 = a012345678 + b012345678        # .BLOCK 2 (optimized: .WORD 1 as we know statically a and b)
    a012345678 = b012345678
    b012345678 = tmp012345678
    i012345678 = i012345678 + 1

print(a012345678)
