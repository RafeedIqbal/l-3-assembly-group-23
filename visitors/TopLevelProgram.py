import ast
from generators.SymbolTable import eight_chars

LabeledInstruction = tuple[str, str]

class TopLevelProgram(ast.NodeVisitor):
    """We supports assignments and input/print calls"""
    
    def __init__(self, entry_point) -> None:
        super().__init__()
        self.__instructions = list()
        self.assignable = list()
        self.__should_save = True
        self.__current_variable = None
        self.__elem_id = 0
        self.__record_instruction('NOP1', label=entry_point)

    def finalize(self):
        self.__instructions.append((None, '.END'))
        return self.__instructions

    ####
    ## Handling Assignments (variable = ...)
    ####

    def visit_Assign(self, node):
        # remembering the name of the target
        self.__current_variable = eight_chars(node.targets[0].id)
        # constant variables should not be assigned any value
        if self.__current_variable[0] == "_": return 
        # if first assignment is a constant it is ignored
        # future constant assignments are allowed
        elif isinstance(node.value, ast.Constant) and not self.__current_variable in self.assignable:
            self.assignable.append(self.__current_variable) 
            return
        elif not self.__current_variable in self.assignable:
            self.assignable.append(self.__current_variable) 
        # visiting the left part, now knowing where to store the result
        self.visit(node.value)
        if self.__should_save:
            self.__record_instruction(f'STWA {self.__current_variable},d')
        else:
            self.__should_save = True
        self.__current_variable = None

    def visit_Constant(self, node):
        self.__record_instruction(f'LDWA {node.value},i')
    
    def visit_Name(self, node):
        self.__record_instruction(f'LDWA {eight_chars(node.id)},d')

    def visit_BinOp(self, node):
        self.__access_memory(node.left, 'LDWA')
        if isinstance(node.op, ast.Add):
            self.__access_memory(node.right, 'ADDA')
        elif isinstance(node.op, ast.Sub):
            self.__access_memory(node.right, 'SUBA')
        else:
            raise ValueError(f'Unsupported binary operator: {node.op}')

    def visit_Call(self, node):
        match node.func.id:
            case 'int': 
                # Let's visit whatever is casted into an int
                self.visit(node.args[0])
            case 'input':
                # We are only supporting integers for now
                self.__record_instruction(f'DECI {self.__current_variable},d')
                self.__should_save = False # DECI already save the value in memory
            case 'print':
                # We are only supporting integers for now
                self.__record_instruction(f'DECO {eight_chars(node.args[0].id)},d')
            case _:
                # allocate memory for variables
                self.__record_instruction(f'SUBSP {2 * len(node.args)},i\t; push {" ".join(["#" + arg.id + "_" + node.func.id for arg in node.args])}')

                #add variables to stack
                for i in range(len(node.args)):
                    self.visit(node.args[i])
                    self.__record_instruction(f'STWA {2 * (len(node.args) - i - 1)},s')
                
                # add return value to stack
                self.__record_instruction(f'SUBSP 2,i\t; push #{"retV_" + node.func.id}')
                
                # call function
                self.__record_instruction(f'CALL {node.func.id}')

                # output return value
                self.__record_instruction(f'LDWA 0,s')

                #delete allocated memory
                self.__record_instruction(f'ADDSP 2,i\t; pop #{"retV_" + node.func.id}')
                self.__record_instruction(f'ADDSP {2 * len(node.args)},i\t; pop {" ".join(["#" + arg.id + "_s" for arg in node.args])}')



    ####
    ## Handling While loops (only variable OP variable)
    ####

    def visit_While(self, node):
        loop_id = self.__identify()
        inverted = {
            ast.Lt:  'BRGE', # '<'  in the code means we branch if '>=' 
            ast.LtE: 'BRGT', # '<=' in the code means we branch if '>' 
            ast.Gt:  'BRLE', # '>'  in the code means we branch if '<='
            ast.GtE: 'BRLT', # '>=' in the code means we branch if '<'
            ast.Eq: 'BRNE', # '==' in the code means we branch if '!='
            ast.NotEq: 'BREQ', # '!=' in the code means we branch if '=='
        }
        # left part can only be a variable
        self.__access_memory(node.test.left, 'LDWA', label = f'while_{loop_id}')
        # right part can only be a variable
        self.__access_memory(node.test.comparators[0], 'CPWA')
        # Branching is condition is not true (thus, inverted)
        self.__record_instruction(f'{inverted[type(node.test.ops[0])]} end_{loop_id}')
        # Visiting the body of the loop
        for contents in node.body:
            self.visit(contents)
        self.__record_instruction(f'BR while_{loop_id}')
        # Sentinel marker for the end of the loop
        self.__record_instruction(f'NOP1', label = f'end_{loop_id}')

    ####
    ## Handling If statements (only variable OP variable)
    ####

    def visit_If(self, node):
        cond_id = self.__identify()
        inverted = {
            ast.Lt:  'BRGE', # '<'  in the code means we branch if '>=' 
            ast.LtE: 'BRGT', # '<=' in the code means we branch if '>' 
            ast.Gt:  'BRLE', # '>'  in the code means we branch if '<='
            ast.GtE: 'BRLT', # '>=' in the code means we branch if '<'
            ast.Eq: 'BRNE', # '==' in the code means we branch if '!='
            ast.NotEq: 'BREQ', # '!=' in the code means we branch if '=='
        }
        # left part can only be a variable
        self.__access_memory(node.test.left, 'LDWA', label = f'if_{cond_id}')
        # right part can only be a variable
        self.__access_memory(node.test.comparators[0], 'CPWA')
        # Branching is condition is not true (thus, inverted)
        self.__record_instruction(f'{inverted[type(node.test.ops[0])]} else_{cond_id}')
        # Visiting the body of the if
        for contents in node.body:
            self.visit(contents)
        self.__record_instruction(f'BR end_{cond_id}')
        # Sentinel marker for start of the else statement
        self.__record_instruction(f'NOP1', label = f'else_{cond_id}')
        # Visiting the body of the else statement
        for contents in node.orelse:
            self.visit(contents)
        # Sentinel marker for the end of the conditonal
        self.__record_instruction(f'NOP1', label = f'end_{cond_id}')

    ####
    ## Handling function calls 
    ####

    def visit_FunctionDef(self, node):
        # write function name
        self.__record_instruction(f'NOP1', label = f'{node.name}')

        #get variables from stack (they are in reverse order)
        for i in range(len(node.args.args)):
            self.__record_instruction(f'LDWA {2 * (len(node.args.args) - i)},s')
            self.__record_instruction(f'STWA {node.args.args[i].arg},d')

        # visit contents
        for contents in node.body:
            self.visit(contents)

        self.__record_instruction(f'RET')
    
    ####
    ## Handling returns 
    ####

    def visit_Return(self, node):
        # load value of node
        self.visit(node.value)
        # store in return value
        self.__record_instruction(f'STWA 2,s')
        self.__record_instruction(f'RET')


    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call) and not node.value.func.id in ['int', 'input', 'print']:
            # allocate memory for variables
            self.__record_instruction(f'SUBSP {2 * len(node.args)},i\t; push {" ".join(["#" + arg.id + "_" + node.func.id for arg in node.args])}')

            #add variables to stack
            for i in range(len(node.args)):
                self.visit(node.args[i])
                self.__record_instruction(f'STWA {2 * (len(node.args) - i - 1)},s')
            
            # add return value to stack
            self.__record_instruction(f'SUBSP 2,i\t; push #{"retV_" + node.func.id}')
            
            # call function
            self.__record_instruction(f'CALL {node.func.id}')

            # output return value
            self.__record_instruction(f'LDWA 0,s')

            #delete allocated memory
            self.__record_instruction(f'ADDSP 2,i\t; pop #{"retV_" + node.func.id}')
            self.__record_instruction(f'ADDSP {2 * len(node.args)},i\t; pop {" ".join(["#" + arg.id + "_s" for arg in node.args])}')
        else:
            self.visit(node.value)

    ####
    ## Helper functions to 
    ####

    def __record_instruction(self, instruction, label = None):
        self.__instructions.append((label, instruction))

    def __access_memory(self, node, instruction, label = None):
        if isinstance(node, ast.Constant):
            self.__record_instruction(f'{instruction} {node.value},i', label)
        elif node.id[0] == "_":
            self.__record_instruction(f'{instruction} {eight_chars(node.id)},i', label)
        else:
            self.__record_instruction(f'{instruction} {eight_chars(node.id)},d', label)

    def __identify(self):
        result = self.__elem_id
        self.__elem_id = self.__elem_id + 1
        return result
