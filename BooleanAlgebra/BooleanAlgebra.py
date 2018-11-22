import itertools

# Input set for later
PossibleInputs = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def convert(statement:str):
    '''
    Convert function will take a user inputted function and convert it
    into an easier to manipulate string. This will happen primarily
    by converting things like AB into A*B allowing for easier construction
    of operator tree.
    '''
    
    # First char will be skipped in iteration so init with first char
    newStatement = statement[0]
    
    # Iterate through remaining characters of expression
    for i,char in enumerate(statement[1:]):
        
        '''
        Loop will function by iterating through characters in the expr
        and checking the previous char to determine if a * needs to be
        placed
        '''
        if char in PossibleInputs or char == "(":
            # Character is a letter or (
            if statement[i] in PossibleInputs or statement[i] == "'" or statement[i] == ")":
                
                # Instances checked require * inserted
                newStatement+="*"
        
        # Reconstruct initial statement appropriately
        newStatement+=char
        
    # Return the reconstructed statement
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
        
def constructTree(statement:str):
    
    '''
    Tree construction is a recursive operation that constructs an operator tree from the
    given expression. Function will first remove redundant brackets (if any) and then 
    locate the first, highest priority node that is free. Then it will call itself
    on the left and right expressions. Any expression that is a length of 1 is a fully
    constructed branch.
    '''
    
    if len(statement) == 1:
        # Length of 1 means that the branch is full evaluated
        return statement
    
    # Remove redundant brackets from expression, ie (A+B) is A+B
    while statement[0] == "(" and statement[-1] == ")":
        # Skip first char as it's already known as ( and init depth of 1
        depth = 1
        for i,char in enumerate(statement[1:]):
            if char == "(": # Handle depth
                depth+=1
            elif char == ")":
                depth-=1
                
            # If depth of 0 is reached at the end then return the statement 
            # with outer brackets removed
            if depth == 0 and i == len(statement)-2:
                statement = statement[1:-1]
                break
            
            elif depth == 0:
                # Depth of 0 reached before end so edge case such as (A)+(B)
                break
    
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
        return Node("'", [constructTree(statement[:-1])])
        
# Node class will be used to structure the tree
class Node():
    def __init__(self, Operator:str, Children:list):
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
            return int(not self.Children[0].eval(inputs) if type(self.Children[0]) == Node else not inputs[self.Children[0]])    

def compare(statement1:str, statement2:str):
    
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
    statement1 = constructTree(statement1)
    statement2 = constructTree(statement2)
    
    # A list of combination(s)  
    combis = [list(i) for i in itertools.product([0, 1], repeat=len(inputChars))]
    
    # init failure count
    fails = 0
        
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
            print("Failure with parameters:")
            print(" ".join([char+"="+str(InputDict[char]) for char in InputDict.keys()]))
            
    # Testing complete, notify failure count or if success
    if fails == 0:
        print("Statements are identical")
    else:
        print("Statements are NOT identical")
        print("Failures encountered: {0:<5} ".format(fails))

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
        
    elif func == "table":
        statement = convert(input("Boolean Statement: "))
        truthTable(statement)