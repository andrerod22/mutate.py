"""
Mutation Program for Testing Quality of Given Test Suites
Using FuzzyWuzzy.py, PublicTest-Full.py, PublicTest-Half.py, etc
"""
import sys
import pdb
import ast
import astor
from pprint import pprint
import random
import copy
def mutate_src(src_py, num_mutants):
    """Mutates Given Source File"""
    # TODO Create ASTs: DONE
    tree = None
    with open(src_py, "r") as source:
        tree = ast.parse(source.read())
    track_mutants = ReadTree()
    track_mutants.visit(tree)
    # print(vars(track_mutants))
    m = 0
    x = 0
    mutants = []
    a_avoid = []
    b_avoid = []
    f_avoid = []
    c_avoid = []
    # TODO Manipulate AST (Generate Mutants): DONE
    while(m < int(num_mutants)):
        random.seed(x)
        a = random.randint(1, track_mutants.assignments) if track_mutants.assignments > 0 else 0
        a = 0 if a in a_avoid else a
        f = random.randint(1, track_mutants.calls) if track_mutants.calls > 0 else 0
        f = 0 if f in f_avoid else f
        b = random.randint(1, track_mutants.binaries) if track_mutants.binaries > 0 else 0
        b = 0 if b in b_avoid else b
        c = random.randint(1, track_mutants.comparisons) if track_mutants.comparisons > 0 else 0
        c = 0 if c in c_avoid else c
        # breakpoint()
        if [a,f,b,c] not in mutants:
            mutants.append([a,f,b,c])
            # breakpoint()
            mutated_tree = copy.deepcopy(tree)
            invoke_bmutation = mutateBinOp(b)
            invoke_cmutation = mutateCompare(c)
            invoke_fmutation = mutateFunctCall(a, f)
            if b != 0:
                invoke_bmutation.visit(mutated_tree)
                if invoke_bmutation.b_avoid: 
                    b_avoid.append(invoke_bmutation.b_avoid)
            elif c != 0:
                invoke_cmutation.visit(mutated_tree)
                if invoke_cmutation.c_avoid: 
                    c_avoid.append(invoke_cmutation.c_avoid)
            elif f != 0 or a!= 0:
                invoke_fmutation.visit(mutated_tree)
                if invoke_fmutation.f_avoid: 
                    f_avoid.append(invoke_fmutation.f_avoid)
                if invoke_fmutation.a_avoid:
                    a_avoid.append(invoke_fmutation.a_avoid)
            if b != 0 or c != 0 or f != 0 or a != 0:
                filename = "{}.py".format(m)
                with open(filename, 'w') as source:
                    source.write(astor.to_source(mutated_tree))
                m += 1       
        x += 1
    
    # TODO Run Tests Against Mutated Program: In-Process

    # TODO Check Where Test Failed: In-Process





# Source1: https://www.mattlayman.com/blog/2018/decipher-python-ast/
# Source2: https://stackoverflow.com/questions/4947783/visiting-nodes-in-a-syntax-tree-with-python-ast-module
class mutateBinOp(ast.NodeTransformer):
    def __init__(self, b_mutant):
        self.visits = 0
        self.b_mutant = b_mutant
        self.b_avoid = None

    def visit_BinOp(self, node):
        # breakpoint()
        self.visits += 1
        if self.visits == self.b_mutant:
            self.b_avoid = self.b_mutant
            return self.swap(node)
        return node

    def swap(self, node):
        if(type(node.op) == ast.Add):
            node.op = ast.Sub()
        elif(type(node.op) == ast.Sub):
            node.op = ast.Add()
        elif(type(node.op) == ast.Mult):
            node.op = ast.FloorDiv()
        elif(type(node.op) == ast.Div):
            node.op = ast.Mult()
        return node

class mutateFunctCall(ast.NodeTransformer):
    def __init__(self, a_mutant, f_mutant):
        self.visits = 0
        self.a_mutant = a_mutant
        self.f_mutant = f_mutant
        self.f_avoid = None
        self.a_avoid = None
        self.found = False
   
    def visit_Call(self, node):
        # breakpoint()
        self.visits += 1
        if self.found:
            self.found = False
            return node
        elif self.visits == self.f_mutant:
            self.f_avoid = self.f_mutant
            self.a_avoid = None
            return ast.Pass()
        return node

    def visit_Assign(self, node):
        # breakpoint()
        self.visits += 1
        if self.visits == self.a_mutant:

            self.a_avoid = self.a_mutant
            if type(node.value) == ast.Name:
                return ast.copy_location(
                ast.Assign(
                    targets=node.targets,
                    value=ast.Name(id='None', ctx=None)),
                    node
                )
            elif type(node.value) == ast.NameConstant:
                return ast.copy_location(
                ast.Assign(
                    targets=node.targets,
                    value=ast.NameConstant(value=random.randint(1,999))),
                    node
                )
            elif type(node.value) == ast.Constant:
                if type(node.value.value) == str:
                    return ast.copy_location(
                        ast.Assign(
                            targets=node.targets,
                            value=ast.Constant(value="")),
                            node
                    )
                else:
                    return ast.copy_location(
                        ast.Assign(
                            targets=node.targets,
                            value=ast.Constant(value=random.randint(1,999))),
                            node
                    )
            elif type(node.value) == ast.Call:
                # self.f_avoid = self.a_mutant
                self.visits -= 1
                if(self.f_mutant == 0):
                    return ast.copy_location(
                        ast.Assign(
                            targets=node.targets,
                            value=ast.Name(id='None', ctx=None)),
                            node
                        )

                # return ast.Pass()
        return node

    def visit_If(self, node):
        # breakpoint()
        self.found = True
        self.generic_visit(node)
        return node

class mutateCompare(ast.NodeTransformer):
    def __init__(self, c_mutant):
        self.visits = 0
        self.c_mutant = c_mutant
        self.c_avoid = None
    def visit_Compare(self, node):
        # breakpoint()
        self.visits += 1
        if self.visits == self.c_mutant:
            self.c_avoid = self.c_mutant
            return self.negate(node)
        return node

    def negate(self, node):
        if (ast.Gt == type(node.ops[0])):
            return ast.Compare(
                left = node.left,
                ops = [ast.LtE()],
                comparators = node.comparators
            )
        elif (ast.LtE == type(node.ops[0])):
            return ast.Compare(
                left = node.left,
                ops = [ast.Gt()],
                comparators = node.comparators
            )
        elif (ast.Lt == type(node.ops[0])):
            return ast.Compare(
                left = node.left,
                ops = [ast.GtE()],
                comparators = node.comparators
            )
        elif (ast.GtE == type(node.ops[0])):
            return ast.Compare(
                left = node.left,
                ops = [ast.Lt()],
                comparators = node.comparators
            )
        return node

class ReadTree(ast.NodeVisitor):
    def __init__(self):
        self.found = False
        self.comparisons = 0
        self.binaries = 0
        self.assignments = 0
        self.calls = 0

    def visit_Call(self, node):
        # CHECK LATER
        if self.found:
            self.found = False
            return None
        self.calls += 1
        return None

    def visit_Assign(self, node):
        self.assignments += 1
        return None
    def visit_BinOp(self, node):
        if(
            type(node.op) == ast.Add or
            type(node.op) == ast.Sub or
            type(node.op) == ast.Mult or
            type(node.op) == ast.Div 
            ): 
            self.binaries += 1
        return None

    def visit_If(self, node):
        self.found = True
        self.generic_visit(node)
        return None
    
    def visit_Compare(self, node):
        if (
            ast.Gt == type(node.ops[0]) or
            ast.Lt == type(node.ops[0]) or
            ast.GtE == type(node.ops[0]) or
            ast.LtE == type(node.ops[0])
        ):
            self.comparisons += 1
        return None

if __name__ == "__main__":
    mutate_src(sys.argv[1], sys.argv[2])

