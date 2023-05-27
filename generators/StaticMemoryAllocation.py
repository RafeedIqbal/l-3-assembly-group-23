from generators.SymbolTable import eight_chars


# https://www.w3schools.com/python/python_regex.asp
# https://www.programiz.com/python-programming/methods/built-in/isinstance


class StaticMemoryAllocation():

    def __init__(self, global_vars: dict()) -> None:
        self.__global_vars = global_vars

    def generate(self):
        print('; Allocating Global (static) memory')
        for n, v in self.__global_vars.items():
            m = eight_chars(n)
            if v == -1:
                print(f'{str(n+":"):<9}\t.EQUATE {str(0)}\t;#2d') # reserving memory)
            elif m[0] == "_":
                print(f'{str(m+":"):<9}\t.EQUATE {str(v)}') # reserving memory
            elif isinstance(v, int):
                print(f'{str(m+":"):<9}\t.WORD {str(v)}') # reserving memory
            else:
                print(f'{str(m+":"):<9}\t.BLOCK 2') # reserving memory
