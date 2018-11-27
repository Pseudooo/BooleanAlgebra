import itertools

# Input set for later
PossibleInputs = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def convert(statement:str):
    
    '''
    Conversion of a string function will take a user-inputted function
    that is potentially "messy" and convert it to something that is easier
    to manage when constructing the operator tree
    '''
    
    # Reconstruction of a statement should never influence the first character
    newStatement = statement[0]
    
    # Iterate through characters of statement and decide if * should be injected
    for i,char in enumerate(statement[1:]):
        if char in PossibleInputs or char == "(" or char in ["0","1"]:
            prevChar = statement[i]
            if prevChar in PossibleInputs or prevChar == "'" or prevChar == ")" or prevChar in ["0","1"]:
                # * should be injected
                newStatement+="*"
        newStatement+=char
    return newStatement
                
def constructInputsDict(statement:str):
    '''
    Constructing an input dictionary will mean making a dictionary where each
    key of the dictionary will return it's corresponding value.
    '''
    
    inputs = []
    InputDict = {}
    
    # First we construct an array containing all of the chars used (Each char is entered once)
    for char in statement:
        if char not in inputs and char in PossibleInputs:
            inputs.append(char)
            
    # Characters are then sorted to they're entered in nice order
    inputs.sort()
    
    # iterate through the inputs in the expression and prompt user to enter a value
    for char in inputs:
        InputDict[char] = bool(int(input("{} = ".format(char))))
    
    # Return the constructed dictionary
    return InputDict

def getFreeOperator(statement:str, operator):
    
    '''
    Calling for an operator that is free means calling for an operator that is not encased
    in any sets of brackets. In doing this it allows for handing of brackets and nested 
    brackets without a dedicated node.
    '''
    
    depth = 0 # Depth indicates how many brackets are currently encasing the index
    index = None # If not found "free" then none will be returned
    for i,val in enumerate(statement):
        if val == "(": # handling depth
            depth+=1
        elif val == ")":
            depth-=1
        elif val==operator and depth == 0:
            # Instance where the operator found is free
            index = i
            break
    
    # Return the found index or None if not found
    return index
        
def cleanBrackets(statement:str):
    '''
    Clean brackets function will remove any unrequired brackets
    from a boolean expression.
    '''
    
    run = True
    while statement[0] == "(" and statement[-1] == ")" and run == True:
            
            innerStatement = statement[1:-1]
            depth = 1
            for char in innerStatement:
                if char == "(":
                    depth+=1
                elif char == ")":
                    depth-=1;
                    
                if depth == 0:
                    break
                    
            if depth == 1:
                statement = innerStatement
            else:
                run = False
            # Once the depth at the end has been decided
            
    return statement
    
def constructTree(statement:str):
    
    '''
    Tree construction is a recursive operation that constructs an operator tree from the
    given expression. Function will first remove redundant brackets (if any) and then 
    locate the first, highest priority node that is free. Then it will call itself
    on the left and right expressions. Any expression that is a length of 1 is a fully
    constructed branch.
    '''
    
    # Remove redundant brackets from expression, ie (A+B) is A+B
    statement = cleanBrackets(statement)
    
    if len(statement) == 1:
        # Length of 1 means that the branch is full evaluated
        return Node("v", statement)
    
    # Order of operations is to be taken backwards to ensure appropriate
    # construction/evaluation of the tree
    
    # Call for the index of the first or operator
    OrIndex = getFreeOperator(statement, "+")
    
    if OrIndex != None:
        # If the or index was found then we return a node and set the children
        # to trees that are to be constructed from the split statement
        return Node("+", [constructTree(statement[:OrIndex]), constructTree(statement[OrIndex+1:])])
    
    # Repeat the process for other operators
    AndIndex = getFreeOperator(statement, "*")
    if AndIndex != None:
        return Node("*", [constructTree(statement[:AndIndex]), constructTree(statement[AndIndex+1:])])
    
    NotIndex = getFreeOperator(statement, "'")
    if NotIndex != None:
        # In the instance of a not operator it will only have one child
        # of which will be entirely to the left due to order of node
        # construction
        return Node("'", constructTree(statement[:-1]))
    
    print("end?")
    print(statement)
        
# Node class will be used to structure the tree
class Node():
    def __init__(self, Operator:str, Children):
        # One global node with a defined operator
        self.operator = Operator        
        self.Children = Children
    
    def getChildren(self):
        return self.Children
    
    def setChildren(self, Children:list):
        self.Children = Children
    
    def getOperator(self):
        return self.operator
    
    def eval(self, inputs:dict):
        # Evaluation is a recursive operation
        
        # Or operator
        if self.operator == "+":
            # Start with false to not influence outcome
            val = False
            for child in self.Children:
                # Iterate through children
                if type(child) == Node:
                    # Another node will be evaluated
                    val = val or child.eval(inputs)
                else:
                    # Node is a input
                    val = val or inputs[child]
            
            return int(val) 
        
        # Repeat process for other operators
        elif self.operator == "*":
            val = True
            for child in self.Children:
                if type(child) == Node:
                    val = val and child.eval(inputs)
                else:
                    val = val and inputs[child]
    
            return int(val)
        
        elif self.operator == "'":
            # Not should only ever have one child
            return int(not self.Children.eval(inputs))
        
        elif self.operator == "v":
            # The value of the child
            if self.Children.isdigit():
                return int(self.Children)
            else:
                return int(inputs[self.Children])

def compare(statement1:str, statement2:str, printFailures=True):
    
    '''
    Compare function will compare two inputted statements, generate a truth table for each
    and verify if the statements produce the same output(s) for their corresponding input(s).
    '''
    
    # Construct an input dictionary that is not populated by the user
    inputChars = []
        
    # statement1 is assumed to have more or equivalent inputs than statement2
    for char in statement1:
        if char not in inputChars and char in PossibleInputs:
            inputChars.append(char) 
        
    # Sort to make sure inputs are kept inline
    inputChars.sort()
        
    # Construct trees
    statement1 = constructTree(convert(statement1))
    statement2 = constructTree(convert(statement2))
    
    # A list of combination(s)  
    combis = [list(i) for i in itertools.product([0, 1], repeat=len(inputChars))]
    
    # init failure count
    fails = 0
    
    if printFailures == True:    
        print("Testing...")
        
    # Iterate through combinations
    for comb in combis:
        InputDict = {}
        
        # Construct input dictionary for combination
        for i,val in enumerate(inputChars):
            InputDict[val] = comb[i]
                
        # Compare statements for generated input
        if statement1.eval(InputDict) != statement2.eval(InputDict):
            # failed, notify users of failure values
            fails+=1
            if printFailures == True:
                print("Failure with parameters:")
                print(" ".join([char+"="+str(InputDict[char]) for char in InputDict.keys()]))
            
    # Testing complete, notify failure count or if success
    if fails == 0:
        if printFailures == True:
            print("Statements are identical")
        return True
    else:
        if printFailures == True:
            print("Statements are NOT identical")
            print("Failures encountered: {0:<5} ".format(fails))
        return False

def truthTable(statement:str):
    
    inputChars = []
    
    # statement1 is assumed to have more or equivalent inputs than statement2
    for char in statement:
        if char not in inputChars and char in PossibleInputs:
            inputChars.append(char) 
        
    # Sort to make sure inputs are kept inline
    inputChars.sort()
    
    statement = constructTree(statement)
    
    combis = [list(i) for i in itertools.product([0, 1], repeat=len(inputChars))]
    
    print(*inputChars,"|","X")
    
    for comb in combis:
        InputDict = {}
        
        # Construct input dictionary for combination
        for i,val in enumerate(inputChars):
            InputDict[val] = comb[i]
            
        print(*comb,"|",statement.eval(InputDict))
            
# Primary loop
run = True

# Initial message
print("Boolean Algebra Engine")
print("\nType help to get help\n")

while(run):
    # Input function
    
    func = input("> ")
        
    if func == "quit":
        # command to quit the application
        print("Goodbye!")
        run = False
        
    elif func == "eval":
        # Command allowing user to evaluate a boolean algebra statement
        # with defined inputs
        statement = convert(input("Boolean statement: "))
        inputs = constructInputsDict(statement)
        statementTree = constructTree(statement)
        print(statementTree.eval(inputs))
        
    elif func == "compare":
        # Command to compare if two statements are identical based on their
        # truth tables
        statement1 = convert(input("Boolean Statement 1: "))
        statement2 = convert(input("Boolean Statement 2: "))
        
        compare(statement1, statement2)
        
    elif func == "help":
        print("Commands:")
        print(" - quit")
        print("   ~quits")
        print(" - eval")
        print("   ~prompts for a boolean statement to be entered and will then")
        print("    evaluate it to a final value")
        print(" - compare")
        print("   ~prompts for two boolean statements to be entered and will then")
        print("    have their truth tables compared")
        print(" - table")
        print("   ~prompts the user to enter a boolean statement, the truth table")
        print("    for the defined expression will then be generated")
        print(" - checksteps")
        print("   ~prompts the user to enter a boolean expression, the user will")
        print("    the be required to enter n more statements and each will be checked")
        print("    and if an incorrect step is entered the user will be notified")
        print("    is useful to check working(s) out for a simplification.")
        
    elif func == "table":
        statement = convert(input("Boolean Statement: "))
        truthTable(statement)
        
    elif func == "checksteps":
        # Check steps will let the user enter all of their steps.
        
        print("Type break when you're finished entering steps")
        
        initExpr = input("Initial Expression: ")
        
        step = 1
        prevExpr = initExpr
        
        moreSteps = True
        while moreSteps:
            expr = input("Step {0}: ".format(step))
            
            if expr.lower() == "break":
                moreSteps = False
                print("All steps are were correct!")
            else:
                step+= 1
                
                if compare(initExpr, expr, False) == False:
                    print("Invalid Step!")
                    print(prevExpr,"!=",expr)
                    moreSteps = False
            prevExpr = expr
    else:
        print("Invalid Commmand!")
        print("Type help")