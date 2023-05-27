import ast
#https://docs.python.org/3/library/ast.html#ast.NodeVisitor.visit
#https://www.programiz.com/python-programming/methods/built-in/isinstance

class GlobalVariableExtraction(ast.NodeVisitor):
    """ 
        We extract all the left hand side of the global (top-level) assignments
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.results = {}

    def visit_Assign(self, node):
        if len(node.targets) != 1:
            raise ValueError("Only unary assignments are supported")

        id = node.targets[0].id
        value = None

        if isinstance(node.value, ast.Call) and not node.value.func.id in ['int', 'input', 'print']:
            for arg in node.value.args:
                if arg.id + "_s" not in self.results.keys():
                    # -1 indicates that it is part of a stack
                    self.results[arg.id + "_s"] = -1
                self.results["retV_" + node.value.func.id] = -1

        if id in self.results.keys() and self.results.get(id) != None:
            return
        elif isinstance(node.value, ast.Constant):
            value = node.value.value

        self.results[id] = value

    def visit_FunctionDef(self, node):
        for contents in node.body:
            self.visit(contents)

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call) and not node.value.func.id in ['int', 'input', 'print']:
            for arg in node.value.args:
                if arg.id + "_s" not in self.results.keys():
                    # -1 indicates that it is part of a stack
                    self.results[arg.id + "_s"] = -1
                self.results["retV_" + node.value.func.id] = -1
        else:
            self.visit(node.value)
   