import ply.yacc as yacc
from lex2 import *
from re import *
import sys
import os

# -----------------------------------
#
# Program : Decls 
#         | Decls Body
#         | Body
#
# -----------------------------------

def p_program_decls(p):
    '''Program : Decls'''
    parser.assembly = f"{p[1]}"

def p_program_declsBody(p):
    '''Program : Decls Body'''
    parser.assembly = f"{p[1]}\nSTART\n{p[2]}STOP"
    
def p_program_body(p):
    '''Program : Body'''
    parser.assembly = f"START\n{p[1]}STOP"
    
# -----------------------------------
#
# Decls : Declaration Decls
#       | Declaration
#
# -----------------------------------

def p_declAss_recCall(p):
    '''Decls : Declaration Decls'''
    p[0] = f"{p[1]}{p[2]}"

def p_declAss_term(p):
    '''Decls : Declaration'''
    p[0] = p[1]

# -------------------------------
#
# Body : Assignment Body
#      | Statement Body
#      | Assignment
#      | Statement
#
# -------------------------------

def p_body_ASB(p):
    '''Body : Assignment Body
            | Statement Body'''
    p[0] = f"{p[1]}{p[2]}"
    
def p_body_AS(p):
    '''Body : Assignment
            | Statement'''
    p[0] = f"{p[1]}"

# ---------------------------------------------------------
#
# Declaration : INT ID
#             | INT ID KEEPS Expression
#             | ARRAY ID 
#             | ARRAY ID LPAREN Num RPAREN       
#             | ARRAY ID KEEPS LBRACKET List RBRACKET  
#             | ARRAY ID KEEPS ID                                     
#             | ARRAY ID KEEPS SEARCH ID LPAREN Expression RPAREN    
#             | MATRIX ID 
#             | MATRIX ID LPAREN Num COMMA Num RPAREN   
#             | MATRIX ID KEEPS LBRACKET Matrix RBRACKET 
#             | MATRIX ID KEEPS ID                     
# 
# ---------------------------------------------------------

def p_declaration_int(p):
    '''Declaration : INT ID'''
    nameVar = p[2]
    if nameVar not in parser.vars:
        parser.vars[nameVar] = (parser.stackPointer, None)
        p[0] = "PUSHI 0\n"
        parser.stackPointer +=1
    else:
        parser.success = False
        parser.error += f"\n>> The Variable {nameVar} already exists\n"
        parser.error += f"{currLinetxt}{parser.currLine}\n"
    parser.currLine +=1

def p_declaration_intExpression(p):
    '''Declaration : INT ID KEEPS Expression'''
    nameVar = p[2]
    value = p[4]
    if nameVar not in parser.vars:
        parser.vars[nameVar] = (parser.stackPointer, None)
        p[0] = f"{value}"
        parser.stackPointer += 1
    else:
        parser.error += f"\n>> The Variable {nameVar} already exists\n"
        parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False
    parser.currLine += 1

def p_declaration_emptyArray(p):
    '''Declaration : ARRAY ID '''
    nameVar = p[2]
    if nameVar not in parser.vars:
        parser.vars[nameVar] = (parser.stackPointer, 0)
        p[0] = f"PUSHN 0\n"
        parser.stackPointer += 1
    else:
        parser.error += f"\n>> The Variable {nameVar} already exists\n"
        parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.exito = False
    parser.currLine +=1

def p_declaration_array(p):
    '''Declaration : ARRAY ID LPAREN Num RPAREN '''
    nameVar = p[2]
    size = int(p[4])
    if nameVar not in parser.vars:
        if size >= 0:
            parser.vars[nameVar] = (parser.stackPointer, size)
            p[0] = f"PUSHN {size}\n"
            parser.stackPointer += size
        else:
            parser.error += f"\n>> Array size must be greater or equal than 0\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
            parser.success = False
    else:
        parser.error += f"\n>>The Variable {nameVar} already exists\n"
        parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False
    parser.currLine += 1

def p_declarations_arrayList(p):
    '''Declaration : ARRAY ID KEEPS LBRACKET List RBRACKET'''
    nameVar = p[2]
    list = p[5]
    size = len(list)
    temp = ""
    if nameVar not in parser.vars:
        if (size == 0):
            parser.error += f"\n>> To declare an Empty ARRAY try: ARRAY {nameVar}\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
            parser.success = False
        elif(size > 0):
            parser.vars[nameVar] = (parser.stackPointer, size)
            temp += f"\nPUSHN {size}\n"
            parser.stackPointer += size
            sPointer = parser.vars[nameVar][0]
            for i in range(size):
                temp += f"PUSHGP\nPUSHI {sPointer}\nPADD\nPUSHI {i}\nPUSHI {list[i]}\nSTOREN\n"
        else:
            parser.error += f"\n>> List Size Must be Greater than 0\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
            parser.success = False
    else:
        parser.error += f"\n>> The Variable {nameVar} already exists\n"
        parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False
    parser.currLine += 1
    p[0] = temp

def p_declaration_arrayId(p):
    '''Declaration : ARRAY ID KEEPS ID'''
    nameVar1 = p[2]
    nameVar2 = p[4]
    temp = "\n"
    if nameVar1 not in parser.vars:
        if nameVar2 not in parser.vars:
            parser.error += f"\n>> {nameVar2} has not beed declared\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
            parser.success = False

        else:
            
            sPointer2 = parser.vars[nameVar2][0]
            size2 = parser.vars[nameVar2][1]
            parser.vars[nameVar1] = (parser.stackPointer, size2)
            parser.stackPointer += size2
                
            sPointer1 = parser.vars[nameVar1][0]

            temp += f"PUSHN {size2}\n"

            for s in range(size2):
                temp += f"\nPUSHG {sPointer2 + s}\n"
                temp += f"STOREG {sPointer1 + s}\n"
            
    else:
        parser.error += f"\n>> {nameVar1} already exists\n"
        parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False
    p[0] = temp
    parser.currLine += 1

def p_declaration_arraySearch(p):
    '''Declaration : ARRAY ID KEEPS SEARCH ID LPAREN Expression RPAREN '''
    nameVar1 = p[2]
    nameVar2 = p[5]
    value = p[7]
    temp = "\n"
    if nameVar1 not in parser.vars:
        if nameVar2 not in parser.vars:
            parser.error += f"\n>> {nameVar1} has not been declared\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
            parser.success = False
        
        else:

            sPointer2 = parser.vars[nameVar2][0]
            size2 = parser.vars[nameVar2][2]
            parser.vars[nameVar1] = (parser.stackPointer, size2)
            parser.stackPointer += size2
                
            sPointer1 = parser.vars[nameVar1][0]

            temp += f"PUSHN {size2}\n"

            for s in range(size2):
                temp += f"PUSHGP\nPUSHI {sPointer2}\nPADD\n{value}PUSHI {size2}\nMUL\nPUSHI {s}\nADD\nLOADN\n"
                temp += f"STOREG {sPointer1 + s}\n"

    else:
        parser.error += f"\n>> {nameVar1} already exists\n"
        parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False
    p[0] = temp
    parser.currLine += 1

def p_declaration_emptyMatrix(p):
    '''Declaration : MATRIX ID'''
    nameVar = p[2]
    if nameVar not in parser.vars:
        parser.vars[nameVar] = (parser.stackPointer, 0, 0)
        p[0] = f"PUSHN 0\n"
        parser.stackPointer += 1
    else:
        parser.error += f"\n>>The Variable {nameVar} already exists\n"
        parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False
    parser.currLine +=1

def p_declaration_matrix(p):
    '''Declaration : MATRIX ID LPAREN Num COMMA Num RPAREN''' 
    nameVar = p[2]
    lines = int(p[4])
    cols = int(p[6])  
    if nameVar not in parser.vars:
        if lines >= 0 and cols >= 0:
            parser.vars[nameVar] = (parser.stackPointer, lines, cols)
            p[0] = f"PUSHN {lines*cols}\n"
            parser.stackPointer += lines*cols
        else:
            parser.success = False
            parser.error += f"\n>> Lines and cols' size must be greater or equal than 0\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
    else:
        parser.error += f"The Variable {nameVar} already exists\n"
        parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False
    parser.currLine += 1

def p_declaration_assignMatrix(p):
    '''Declaration : MATRIX ID KEEPS LBRACKET Matrix RBRACKET'''
    nameVar = p[2]
    matrix = p[5]
    temp = ""
    size = len(matrix)
    if nameVar not in parser.vars:
        if size == 0:
            parser.error += f"\n>> To declare an empty MATRIX try: MATRIX {nameVar}\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
            parser.success = False

        else:
            lins = len(matrix)
            cols = len(matrix[0])
            size = lins * cols
            if validMatrix(matrix, lins, cols):
                parser.vars[nameVar] = (parser.stackPointer, lins, cols)
                parser.stackPointer += size
                sPointer = parser.vars[nameVar][0]
                temp += f"\nPUSHN {size}\n"
                for l in range(lins):
                    for c in range(cols):
                        temp += f"\nPUSHGP\nPUSHI {sPointer}\nPADD\nPUSHI {l * cols + c}\nPUSHI {matrix[l][c]}\nSTOREN\n"
            else:
                parser.error += f"\n>> Invalid Matrix: All lines must be of the same size and cannot be 0\n"
                parser.error += f"{currLinetxt}{parser.currLine}\n"
                parser.success = False

    else:
        parser.error += f"\n>> The Variable {nameVar} already exists\n"
        parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False
    p[0] = temp
    parser.currLine += 1

def p_declaration_matrixId(p):
    '''Declaration : MATRIX ID KEEPS ID'''
    nameVar1 = p[2]
    nameVar2 = p[4]
    temp = "\n"
    if nameVar1 not in parser.vars:
        if nameVar2 not in parser.vars:
            parser.error += f"\n>> {nameVar2} has not beed declared/n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
            parser.success = False

        else:
            
            sPointer2 = parser.vars[nameVar2][0]
            lins2 = parser.vars[nameVar2][1]
            cols2 = parser.vars[nameVar2][2]
            size =  lins2 * cols2 
            parser.vars[nameVar1] = (parser.stackPointer, lins2, cols2)
            parser.stackPointer += size

            sPointer1 = parser.vars[nameVar1][0]

            temp += f"PUSHN {size}\n"

            for s in range(size):
                temp += f"\nPUSHG {sPointer2 + s}\n"
                temp += f"STOREG {sPointer1 + s}\n"

    else:
        parser.error += f"\n>> {nameVar1} already exists\n"
        parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False
    p[0] = temp
    parser.currLine += 1

# -----------------------------------------------------------------------------
#
# Assignment : ID KEEPS Expression     
#            | ID KEEPS LBRACKET List RBRACKET
#            | ID LPAREN Expression RPAREN KEEPS Expression   
#            | ID KEEPS LBRACKET Matrix RBRACKET 
#            | ID LPAREN Expression COMMA Expression RPAREN KEEPS Expression  
#            | ID LPAREN Expression RPAREN KEEPS LBRACKET List RBRACKET   
#            | ID PLUS PLUS
#            | ID MINUS MINUS
#            | ID LPAREN Expression RPAREN SWAP ID LPAREN Expression RPAREN
#            | ID LPAREN Expression COMMA Expression RPAREN SWAP ID LPAREN Expression COMMA Expression RPAREN
#            | ID LPAREN Expression RPAREN SWAP ID LPAREN Expression COMMA Expression RPAREN
#            | ID LPAREN Expression COMMA Expression RPAREN SWAP ID LPAREN Expression RPAREN
#
# -----------------------------------------------------------------------------     

def p_assignment_id(p):
    '''Assignment : ID KEEPS Expression'''
    nameVar1 = p[1]
    value = p[3]
    if nameVar1 not in parser.vars:
        parser.error += f"\n{nameVar1} has not been declared\n"
        parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False
    else: 
        temp = f"{value}"
        if len(parser.vars[nameVar1]) == 3:
            lins = parser.vars[nameVar1][1]
            cols = parser.vars[nameVar1][2]
            size = lins * cols
            for s in reversed(range(size)):
                temp += f"STOREG {parser.vars[nameVar1][0] + s}\n"
            p[0] = temp
        elif parser.vars[nameVar1][1]:
            size = parser.vars[nameVar1][1]
            for c in reversed(range(size)):
                temp += f"STOREG {parser.vars[nameVar1][0] + c}\n"
            p[0] = temp

        else:
            p[0] = f"{value}STOREG {parser.vars[nameVar1][0]}\n"

    parser.currLine +=1
              
def p_assignment_array(p):
    '''Assignment : ID KEEPS LBRACKET List RBRACKET'''
    nameVar = p[1]
    list = p[4]
    size = len(list)
    temp = "\n"
    if nameVar in parser.vars:
        sPointer = parser.vars[nameVar][0]
        if parser.vars[nameVar][1] and len(parser.vars[nameVar]) == 2:
            if (size == parser.vars[nameVar][1]):
                for i in range(size):
                    temp += f"PUSHGP\nPUSHI {sPointer}\nPADD\nPUSHI {i}\nPUSHI {list[i]}\nSTOREN\n"
            else:
                parser.error += f"\n>> List size must be equal to {p[1]} size: {parser.vars[nameVar][1]}\n"
                parser.error += f"{currLinetxt}{parser.currLine}\n"
                parser.success = False
        else:
            parser.error += f"\n>> {nameVar} is not an ARRAY\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
            parser.success = False
    else: 
        parser.error += f"\n>> {nameVar} has not been declared\n"
        parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False
    p[0] = temp
    parser.currLine += 1

def p_assignment_expressionArray(p):
    '''Assignment : ID LPAREN Expression RPAREN KEEPS Expression'''
    nameVar = p[1]
    temp = ""
    if nameVar in parser.vars:
        if parser.vars[nameVar][1] == None:
            parser.error += f"\n>> {nameVar} has no dimension\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
            parser.success = False
        elif len(parser.vars[nameVar]) == 2:
            sPointer = parser.vars[nameVar][0]
            temp += f"\nPUSHGP\nPUSHI {sPointer}\nPADD\n{p[3]}{p[6]}STOREN\n"
        else:
            lins = parser.vars[nameVar][1]
            cols = parser.vars[nameVar][2]
            sPointer = parser.vars[nameVar][0]
            temp += f"{p[6]}"
            for c in range(cols):
                temp += f"\nPUSHGP\nPUSHI {sPointer + c}\nPADD\n{p[3]}PUSHI {cols}\nMUL\nPUSHG {parser.stackPointer + c}\nSTOREN\n"
            temp += f"\nPOP {cols}"
    else:
        parser.error += f"\n>> {nameVar} has not been declared\n"
        parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False
    p[0] = temp
    parser.currLine += 1

def p_assignment_matrix(p):
    '''Assignment : ID KEEPS LBRACKET Matrix RBRACKET'''
    nameVar = p[1]
    matrix = p[4]
    temp = ""
    if nameVar not in parser.vars:
        parser.error += f"\n>> {nameVar} has not been declared\n"
        parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False
    else: 
        if len(parser.vars[nameVar]) == 3:
            lins = parser.vars[nameVar][1]
            cols = parser.vars[nameVar][2]
            
            if validMatrix(matrix, lins, cols):
                sPointer = parser.vars[nameVar][0]
                for l in range(lins):
                    for c in range(cols):
                        temp += f"\nPUSHGP\nPUSHI {sPointer}\nPADD\nPUSHI {l * cols + c}\nPUSHI {matrix[l][c]}\nSTOREN" 

            else:
                parser.error += f"\n>> Invalid Matrix: {nameVar} has {lins} lines and {cols} cols\n"
                parser.error += f"{currLinetxt}{parser.currLine}\n"
                parser.success = False
        else:
            parser.error += f"\n>> {nameVar} is not a MATRIX\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
            parser.success = False
    p[0] = temp
    parser.currLine += 1

def p_assignment_matrixExpression(p):
    '''Assignment : ID LPAREN Expression COMMA Expression RPAREN KEEPS Expression'''
    nameVar = p[1]
    temp = ""
    if nameVar not in parser.vars:
        parser.error += f"\n>> {nameVar} has not been declared\n"
        parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False
    else:
        if len(parser.vars[nameVar]) == 3:
            sPointer = parser.vars[nameVar][0]
            cols = parser.vars[nameVar][2]
            temp += f"\nPUSHGP\nPUSHI {sPointer}\nPADD\n{p[3]}PUSHI {cols}\nMUL{p[5]}ADD\n{p[8]}STOREN\n"
        else: 
            parser.error += f"\n>> {nameVar} must be a MATRIX\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
            parser.success = False
    p[0] = temp
    parser.currLine += 1

def p_assignment_matrixList(p):
    '''Assignment : ID LPAREN Expression RPAREN KEEPS LBRACKET List RBRACKET'''
    nameVar = p[1]
    temp = "\n"
    if nameVar not in parser.vars:
        parser.error += f"\n>> {nameVar} has not been declared\n"
        parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False
    else:
        if len(parser.vars[nameVar]) != 3:
            parser.error += f"\n>> {nameVar} must be a MATRIX\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
            parser.success = False
        else:
            temp = "\n"
            cols = parser.vars[nameVar][2]
            sPointer = parser.vars[nameVar][0]
            list = p[7]
            if len(list) == cols:
                for c in range(cols):
                    temp += f"PUSHGP\nPUSHI {sPointer}\nPADD\n{p[3]}PUSHI {cols}\nMUL\nPUSHI {c}\nADD\nPUSHI {list[c]}\nSTOREN\n"
            else:
                parser.error += f"\n>> List must have {cols} elements\n"
                parser.error += f"{currLinetxt}{parser.currLine}\n"
                parser.success = False
    p[0] = temp
    parser.currLine += 1

def p_assignment_increment(p):
    '''Assignment : ID PLUS PLUS
                  | ID MINUS MINUS'''    
    nameVar = p[1]
    if nameVar not in parser.vars:
        parser.error += f"\n>> {nameVar} has not been declared\n"
        parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False
    else:
        if p[2] == "PLUS":
            p[0] = f"\nPUSHG {parser.vars[nameVar][0]}\nPUSHI 1\nADD\nSTOREG {parser.vars[nameVar][0]}\n"
        else:
            p[0] = f"\nPUSHG {parser.vars[nameVar][0]}\nPUSHI 1\nSUB\nSTOREG {parser.vars[nameVar][0]}\n"
    parser.currLine += 1

def p_assignment_swap1D(p):
    '''Assignment : ID LPAREN Expression RPAREN SWAP ID LPAREN Expression RPAREN'''
    nameVar1 = p[1]
    nameVar2 = p[6]
    temp = "\n"
    if nameVar1 not in parser.vars or nameVar2 not in parser.vars:
        if nameVar1 not in parser.vars:
            parser.error += f"\n>> {nameVar1} has not been declared\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
        if nameVar2 not in parser.vars:
            parser.error += f"\n>> {nameVar2} has not been declared\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False
    else:
        sPointer1 = parser.vars[nameVar1][0]
        sPointer2 = parser.vars[nameVar2][0]
        if len(parser.vars[nameVar1]) == 2 and len(parser.vars[nameVar2]) == 2 and parser.vars[nameVar1][1] and parser.vars[nameVar2][1]:   # Para ARRAYS
            temp += f"PUSHGP\nPUSHI {sPointer1}\nPADD\n{p[3]}PUSHGP\nPUSHI {sPointer2}\nPADD\n{p[8]}LOADN\n"
            temp += f"PUSHGP\nPUSHI {sPointer2}\nPADD\n{p[8]}PUSHGP\nPUSHI {sPointer1}\nPADD\n{p[3]}LOADN\n"
            temp += f"\nSTOREN\nSTOREN\n"

        elif len(parser.vars[nameVar1]) == 3 and len(parser.vars[nameVar2]) == 3:   # Para MATRIXS
            cols1 = parser.vars[nameVar1][2]
            cols2 = parser.vars[nameVar2][2]

            if cols1 != cols2:
                parser.error += f"\n>> To execute SWAP both lines must be of the same size\n"
                parser.error += f"{currLinetxt}{parser.currLine}\n"
                parser.success = False

            else:
                for c in range(cols1):
                    temp += f"PUSHGP\nPUSHI {sPointer1}\nPADD\n{p[3]}PUSHI {cols1}\nMUL\nPUSHI {c}\nADD\n"
                    temp += f"PUSHGP\nPUSHI {sPointer2}\nPADD\n{p[8]}PUSHI {cols2}\nMUL\nPUSHI {c}\nADD\nLOADN\n"
                    temp += f"PUSHGP\nPUSHI {sPointer2}\nPADD\n{p[8]}PUSHI {cols2}\nMUL\nPUSHI {c}\nADD\n"
                    temp += f"PUSHGP\nPUSHI {sPointer1}\nPADD\n{p[3]}PUSHI {cols1}\nMUL\nPUSHI {c}\nADD\nLOADN\n"
                    temp += f"\nSTOREN\nSTOREN\n"
                    if c != cols1 - 1:
                        temp += "\n"                    

        else:
            parser.error += f"\n>> SWAP only works with ARRAYS and MATRIXS \n"

            if not parser.vars[nameVar1][1]:
                parser.error += f">> {nameVar1} is an INT\n"
            if not parser.vars[nameVar2][1]:
                parser.error += f">> {nameVar2} is as INT\n"

            parser.error += f"{currLinetxt}{parser.currLine}\n"
            parser.success = False
    p[0] = temp
    parser.currLine += 1

def p_assignment_swap2D(p):
    '''Assignment : ID LPAREN Expression COMMA Expression RPAREN SWAP ID LPAREN Expression COMMA Expression RPAREN'''
    nameVar1 = p[1]
    nameVar2 = p[8]
    temp = "\n"
    if nameVar1 not in parser.vars or nameVar2 not in parser.vars:
        if nameVar1 not in parser.vars:
            parser.error += f"\n>> {nameVar1} has not been declared\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
        if nameVar2 not in parser.vars:
            parser.error += f"\n>> {nameVar2} has not been declared\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False

    else:
        if len(parser.vars[nameVar1]) == 3 and len(parser.vars[nameVar2]) == 3:
            sPointer1 = parser.vars[nameVar1][0]
            sPointer2 = parser.vars[nameVar2][0]
            cols1 = parser.vars[nameVar1][2]
            cols2 = parser.vars[nameVar2][2]
            temp += f"PUSHGP\nPUSHI {sPointer1}\nPADD\n{p[3]}PUSHI {cols1}\nMUL\n{p[5]}ADD\n"
            temp += f"PUSHGP\nPUSHI {sPointer2}\nPADD\n{p[10]}PUSHI {cols2}\nMUL\n{p[12]}ADD\nLOADN\n"
            temp += f"PUSHGP\nPUSHI {sPointer2}\nPADD\n{p[10]}PUSHI {cols2}\nMUL\n{p[12]}ADD\n"
            temp += f"PUSHGP\nPUSHI {sPointer1}\nPADD\n{p[3]}PUSHI {cols1}\nMUL\n{p[5]}ADD\nLOADN\n"
            temp += "\nSTOREN\nSTOREN\n"

        else:
            parser.error += f"\n>> Both variables must be MATRIXS\n"
            if len(parser.vars[nameVar1]) != 3:
                parser.error += f"\n>> {nameVar1} is not a MATRIX"
            if len(parser.vars[nameVar2]) != 3:
                parser.error += f"\n>> {nameVar2} is not a MATRIX"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
            parser.success = False
    p[0] = temp
    parser.currLine += 1

def p_assignment_swapAM(p):
    '''Assignment : ID LPAREN Expression RPAREN SWAP ID LPAREN Expression COMMA Expression RPAREN'''
    nameVar1 = p[1]
    nameVar2 = p[6]
    temp = "\n"
    if nameVar1 not in parser.vars or nameVar2 not in parser.vars:
        if nameVar1 not in parser.vars:
            parser.error += f"\n>> {nameVar1} has not been declared\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
        if nameVar2 not in parser.vars:
            parser.error += f"\n>> {nameVar2} has not been declared\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False

    else:
        if parser.vars[nameVar1][1] and len(parser.vars[nameVar1]) == 2 and len(parser.vars[nameVar2]) == 3:
            sPointer1 = parser.vars[nameVar1][0]
            sPointer2 = parser.vars[nameVar2][0]
            cols2 = parser.vars[nameVar2][2]
            temp += f"PUSHGP\nPUSHI {sPointer1}\nPADD\n{p[3]}PUSHGP\nPUSHI {sPointer2}\nPADD\n{p[8]}PUSHI {cols2}\nMUL\n{p[10]}ADD\nLOADN\n"
            temp += f"PUSHGP\nPUSHI {sPointer2}\nPADD\n{p[8]}PUSHI {cols2}\nMUL\n{p[10]}ADD\nPUSHGP\nPUSHI {sPointer1}\nPADD\n{p[3]}LOADN\n"
            temp += "\nSTOREN\nSTOREN\n"
        else:
            parser.error += f"\n>> The values you are trying to SWAP have different sizes\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
            parser.success = False
    p[0] = temp
    parser.currLine += 1

def p_assignment_swapMA(p):
    '''Assignment : ID LPAREN Expression COMMA Expression RPAREN SWAP ID LPAREN Expression RPAREN'''
    nameVar1 = p[1]
    nameVar2 = p[8]
    temp = "\n"
    if nameVar1 not in parser.vars or nameVar2 not in parser.vars:
        if nameVar1 not in parser.vars:
            parser.error += f"\n>> {nameVar1} has not been declared\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
        if nameVar2 not in parser.vars:
            parser.error += f"\n>> {nameVar2} has not been declared\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False

    else:
        if parser.vars[nameVar2][1] and len(parser.vars[nameVar2]) == 2 and len(parser.vars[nameVar1]) == 3:
            sPointer1 = parser.vars[nameVar1][0]
            sPointer2 = parser.vars[nameVar2][0]
            cols1 = parser.vars[nameVar1][2]
            temp += f"PUSHGP\nPUSHI {sPointer1}\nPADD\n{p[3]}PUSHI {cols1}\nMUL\n{p[5]}ADD\nPUSHGP\nPUSHI {sPointer2}\nPADD\n{p[10]}LOADN\n"
            temp += f"PUSHGP\nPUSHI {sPointer2}\nPADD\n{p[10]}PUSHGP\nPUSHI {sPointer1}\nPADD\n{p[3]}PUSHI {cols1}\nMUL\n{p[5]}ADD\nLOADN\n"
            temp += "\nSTOREN\nSTOREN\n"

        else:
            parser.error += f"\n>> The values you are trying to SWAP have different sizes\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
            parser.success = False
    p[0] = temp
    parser.currLine += 1

# -----------------------------
#
# List : Num COMMA List
#      | Num
#      | 
#
# -----------------------------

def p_list_recCall(p):
    '''List : Num COMMA List'''
    p[0] = [int(p[1])] + p[3]
            
def p_list_end(p):
    '''List : Num'''
    p[0] = [int(p[1])]

def p_list_empty(p):
    '''List :'''
    p[0] = []

# --------------------------------------------------
#
# Matrix : LBRACKET List RBRACKET COMMA Matrix
#        | LBRACKET List RBRACKET
#        |
#
# --------------------------------------------------   
 
def p_matrix_recCall(p):
    '''Matrix : LBRACKET List RBRACKET COMMA Matrix'''
    p[0] = [p[2]] + p[5]

def p_matrix_end(p):
    '''Matrix : LBRACKET List RBRACKET '''
    p[0] = [p[2]]

def p_matrix_empty(p):
    '''Matrix :'''
    p[0] = []

# -----------------------
#
# Num : NUM
#     | NEGATIVE NUM
#
# -----------------------

def p_num(p):
    '''Num : NUM     
           | NEGATIVE NUM'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = -p[2]
    
# -------------------------------------------------------------------
#
# Expression : Num
#            | ID
#            | INPUT
#            | Operation
#            | SEARCH ID LPAREN Expression RPAREN
#            | SEARCH ID LPAREN Expression COMMA Expression RPAREN
#
# -------------------------------------------------------------------

def p_expression_num(p):
    '''Expression : Num'''
    p[0] = f"PUSHI {p[1]}\n"

def p_expression_id(p):
    '''Expression : ID'''
    nameVar = p[1]
    if nameVar not in parser.vars:
        parser.error += f"\n>> The Variable {nameVar} has not been declared\n"
        parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False
    else:
        p[0] = f"PUSHG {parser.vars[nameVar][0]}\n"

def p_expression_input(p):
    '''Expression : INPUT
                  | Operation'''
    if(p[1] == 'INPUT'):
        p[0] = f"READ\nATOI\n"
    else:
        p[0] = p[1]

def p_expression_searchArrayID(p):
    '''Expression : SEARCH ID LPAREN Expression RPAREN'''
    nameVar = p[2]
    if nameVar not in parser.vars:
        parser.error += f"\n>> The Variable {nameVar} has not been declared\n"
        parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False
    else:
        if len(parser.vars[nameVar]) == 3:
            temp = "\n"
            cols = parser.vars[nameVar][2]
            for c in range(cols):
                temp += f"PUSHGP\nPUSHI {parser.vars[nameVar][0]}\nPADD\n{p[4]}PUSHI {cols}\nMUL\nPUSHI {c}\nADD\nLOADN\n"
            p[0] = temp
        elif parser.vars[nameVar][1]:
            p[0] = f"\nPUSHGP\nPUSHI {parser.vars[nameVar][0]}\nPADD\n{p[4]}LOADN\n"
        else:
            parser.error += f"\n>> {nameVar} must be an MATRIX or an ARRAY\n"
            parser.error += f"{currLinetxt}{parser.currLine}\n"
            parser.success = False
            p[0] = ""
            
    parser.currLine += 1
        

def p_expression_searchMatrixID(p):
    '''Expression : SEARCH ID LPAREN Expression COMMA Expression RPAREN'''
    nameVar = p[2]
    check = len(parser.vars[nameVar])
    if nameVar not in parser.vars:
        parser.error += f"\n>> The Variable {nameVar} has not been declared\n"
        parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False
    else:
        p[0] = f"PUSHGP\nPUSHI {parser.vars[nameVar][0]}\nPADD\n{p[4]}PUSHI {parser.vars[nameVar][2]}MUL\n{p[6]}ADD\nLOADN\n"
    parser.currLine += 1

# ----------------------------------------------
#
# Operation : Expression PLUS Expression
#           | Expression MINUS Expression
#           | Expression TIMES Expression
#           | Expression DIVIDEDBY Expression
#           | Expression REMAINDER Expression
#
# ----------------------------------------------

def p_operation(p):
    '''Operation : Expression PLUS Expression
                 | Expression MINUS Expression
                 | Expression TIMES Expression
                 | Expression DIVIDED_BY Expression
                 | Expression REMAINDER Expression'''
    if p[2] == 'PLUS':
        p[0] = f"{p[1]}{p[3]}ADD\n"
    elif p[2] == 'MINUS':
        p[0] = f"{p[1]}{p[3]}SUB\n"
    elif p[2] == 'TIMES':
        p[0] = f"{p[1]}{p[3]}MUL\n"
    elif p[2] == 'DIVIDEDBY':
        p[0] = f"{p[1]}{p[3]}DIV\n"
    else:
        p[0] = f"{p[1]}{p[3]}MOD\n"

# -----------------------------
#
# Statement : If
#           | While_Do
#           | Repeat_Until
#           | For_Do
#           | Output
#
# -----------------------------

def p_statement(p):
    '''Statement : If
                 | While_Do
                 | Repeat_Until
                 | For_Do
                 | Output''' 
    p[0] = p[1]  

# -------------------------------------------------------------------
#
# NOTA*: cPI  - CheckPoint IF
#        cPE  - CheckPoint ELSE
#        cPW  - CheckPoint WHILE (Volta ao Inicio)
#        cPEW - CheckPoint End While
#        cPR  - CheckPoint REPEAT (Volta ao Início)
#        cPU  - CheckPoint UNTIL (Sai do Ciclo)
#        cPF  - CheckPoint For (Volta ao Início)
#        cPEF - CheckPoint End For (Sai do Ciclo)
#
# -------------------------------------------------------------------
# 
# If : IF Comparison LBRACE Body RBRACE END  
#    | IF Comparison LBRACE Body RBRACE ELSE LBRACE Body RBRACE END
#
# -------------------------------------------------------------------

def p_if(p):
    '''If : IF Comparison LBRACE Body RBRACE END'''
    p[0] = f"\n{p[2]}\nJZ cPI{parser.checkPoint}\n{p[4]}cPI{parser.checkPoint}: NOP\n"
    parser.checkPoint += 1
    parser.currLine +=1

def p_ifElse(p):
    '''If : IF Comparison LBRACE Body RBRACE ELSE LBRACE Body RBRACE END'''
    temp = f"\n{p[2]}\nJZ cPE{parser.checkPoint}\n{p[4]}\nJUMP cPI{parser.checkPoint}\ncPE{parser.checkPoint}: NOP\n"
    temp += f"{p[8]}cPI{parser.checkPoint}: NOP\n"
    p[0] = temp
    parser.checkPoint += 1
    parser.currLine += 1

# ----------------------------------------------------------
#
# While_Do : WHILE Comparison DO LBRACE Body RBRACE END
#
# ----------------------------------------------------------

def p_whileDo(p):
    '''While_Do : WHILE Comparison DO LBRACE Body RBRACE END'''
    p[0] = f"\nCPW{parser.checkPoint}: NOP\n{p[2]}JZ cPEW{parser.checkPoint}\n{p[5]}JUMP cPW{parser.checkPoint}\ncPEW{parser.checkPoint}: NOP"
    parser.checkPoint +=1
    parser.currLine += 1

# --------------------------------------------------------------
#
# Repeat_Until : REPEAT LBRACE Body RBRACE UNTIL Comparison END
#
# --------------------------------------------------------------

def p_repeatUntil(p):
    '''Repeat_Until : REPEAT LBRACE Body RBRACE UNTIL Comparison END'''
    p[0] = f"\ncPR{parser.checkPoint}: NOP\n{p[3]}{p[6]}PUSHI 0\nEQUAL\nJZ cPU{parser.checkPoint}\nJUMP cPR{parser.checkPoint}\ncPU{parser.checkPoint}: NOP\n"
    parser.checkPoint += 1
    parser.currLine += 1

# ----------------------------------------------------------------------------------------------------------------
#
# For_Do : FOR LPAREN Assignment SEMICOLON Comparison SEMICOLON Assignment RPAREN DO LBRACE Body RBRACE END
#
# ----------------------------------------------------------------------------------------------------------------

def p_forDo(p):
    '''For_Do : FOR LPAREN Assignment SEMICOLON Comparison SEMICOLON Assignment RPAREN DO LBRACE Body RBRACE END'''
    temp = f"\n{p[3]}"
    temp += f"\ncPF{parser.checkPoint}: NOP\n{p[5]}JZ cPEF{parser.checkPoint}\n{p[11]}{p[7]}JUMP cPF{parser.checkPoint}\ncPEF{parser.checkPoint}: NOP\n"
    p[0] = temp
    parser.checkPoint += 1
    parser.currLine += 1

# ------------------------------------------------
#
# Output : OUTPUT TEXT
#        | OUTPUT ID
#        | OUTPUT Num
#        | OUTPUT LBRACKET List RBRACKET
#        | OUTPUT LBRACKET Matrix RBRACKET
#
# ------------------------------------------------

def p_output_text(p):
    '''Output : OUTPUT TEXT'''
    p[0] = f"PUSHS {p[2]}\nWRITES\n"
    parser.currLine += 1

def p_output_id(p):
    '''Output : OUTPUT ID'''
    nameVar = p[2]
    temp = ""
    if nameVar in parser.vars:
        sPointer = parser.vars[nameVar][0]
        if parser.vars[nameVar][1] == None:         # INTEIROS
            temp = f"\nPUSHG {sPointer}\nWRITEI\n"
        elif len(parser.vars[nameVar]) == 2:        # ARRAYS
            size = parser.vars[nameVar][1]
            temp += "\nPUSHS \"[\"\nWRITES"
            for i in range(size):
                temp += f"\nPUSHGP\nPUSHI {sPointer}\nPADD\nPUSHI {i}\nLOADN\nWRITEI\n"
                if i != size -1:
                    temp += "\nPUSHS \", \"\nWRITES\n"
            temp += "\nPUSHS \"]\"\nWRITES\n"
        else:                                       # MATRIXS
            lins = parser.vars[nameVar][1]
            cols = parser.vars[nameVar][2]
            temp += "\nPUSHS \"[\"\nWRITES\n"
            for l in range(lins):
                temp += "\nPUSHS \"[\"\nWRITES\n"
                for c in range(cols):
                    temp += f"PUSHGP\nPUSHI {sPointer}\nPADD\nPUSHI {l * cols + c}\nLOADN\nWRITEI\n"
                    if c != cols -1:
                        temp += "PUSHS \", \"\nWRITES\n"
                temp += "PUSHS \"]\"\nWRITES\n"
                if l != lins -1:
                    temp += "\nPUSHS \", \"\nWRITES\n"
            temp += "\nPUSHS \"]\"\nWRITES\n"
    else:
        parser.error += f"\n>> {nameVar} has not been declared\n" 
        parser.error += f"{currLinetxt}{parser.currLine}\n"
        parser.success = False
    p[0] = temp
    parser.currLine += 1
    
def p_output_num(p):
    '''Output : OUTPUT Num'''
    p[0] = f"\nPUSHI {p[2]}\nWRITEI\n"
    parser.currLine += 1

def p_output_array(p):
    '''Output : OUTPUT LBRACKET List RBRACKET'''
    temp = ""
    size = len(p[3])
    temp += "\nPUSHS \"[\"\nWRITES\n"
    for l in range(size):
        temp += f"\nPUSHI {p[3][l]}\nWRITEI\n"
        if l != size -1:
            temp += "\nPUSHS \", \"\nWRITES\n"
    temp += "\nPUSHS \"]\"\nWRITES\n"
    p[0] = temp
    parser.currLine += 1

def p_output_matrix(p):
    '''Output : OUTPUT LBRACKET Matrix RBRACKET'''
    temp = ""
    lins = len(p[3])
    cols = len(p[3][0])
    temp += "\nPUSHS \"[\"\nWRITES\n"
    for l in range(lins):
        temp += "\nPUSHS \"[\"\nWRITES\n"
        for c in range(cols):
            temp += f"PUSHI {p[3][l][c]}\nWRITEI\n"
            if c != cols - 1:
                temp += "PUSHS \", \"\nWRITES\n"
        temp += "PUSHS \"]\"\nWRITES\n"
        if l != lins - 1:
            temp += "\nPUSHS \", \"\nWRITES\n"
    temp += "\nPUSHS \"]\"\nWRITES\n"
    p[0] = temp
    parser.currLine += 1

# -----------------------------------------------------------------
# 
# Comparison : NOT Comparison 
#            | LPAREN Expression EQUAL Expression RPAREN
#            | LPAREN Expression NOT_EQUAL Expression RPAREN
#            | LPAREN Expression GREATER Expression RPAREN
#            | LPAREN Expression GREATER_EQUAL Expression RPAREN
#            | LPAREN Expression LOWER Expression RPAREN
#            | LPAREN Expression LOWER_EQUAL Expression RPAREN
#            | LPAREN Comparison AND Comparison RPAREN
#            | LPAREN Comparison OR Comparison RPAREN
#
# -----------------------------------------------------------------

def p_comparison_not(p):
    '''Comparison  : NOT Comparison''' 
    p[0] = f"{p[2]}PUSHI 0\nEQUALS\n"

def p_comparison(p):
    '''Comparison  : LPAREN Expression EQUAL Expression RPAREN
                   | LPAREN Expression NOT_EQUAL Expression RPAREN
                   | LPAREN Expression GREATER Expression RPAREN
                   | LPAREN Expression GREATER_EQUAL Expression RPAREN
                   | LPAREN Expression LOWER Expression RPAREN
                   | LPAREN Expression LOWER_EQUAL Expression RPAREN'''
    if p[3] == 'EQUAL':
        p[0] = f"{p[2]}{p[4]}EQUAL\n"
    elif p[3] == "NOT_EQUAL":
        p[0] = f"{p[2]}{p[4]}EQUAL\nPUSHI 0\nEQUAL\n"
    elif p[3] == 'GREATER':
        p[0] = f"{p[2]}{p[4]}SUP\n"
    elif p[3] == 'GREATER_EQUAL':
        p[0] = f"{p[2]}{p[4]}SUPEQ\n"
    elif p[3] == 'LOWER':
        p[0] = f"{p[2]}{p[4]}INF\n"
    else:
        p[0] = f"{p[2]}{p[4]}INFEQ\n"

def p_comparison_aO(p):
    '''Comparison  : LPAREN Comparison AND Comparison RPAREN
                   | LPAREN Comparison OR Comparison RPAREN'''
    if p[3] == 'AND':
        p[0] = f"{p[2]}{p[4]}AND\n"
    else:
        p[0] = f"{p[2]}{p[4]}OR\n"
    
def p_error(p):
    if p:
        print(f">> Syntax error at {p}")
    else:
        print(">> Syntax error at EOF")
    sys.exit()

# --------------------------------------------
#            Funções auxiliares:

def validMatrix(mat, lines, cols):

    check = True
    
    for l in range(lines):
        if len(mat[l]) != cols or len(mat[l]) == 0:
            check = False
            break
    return check

def nextCopy(numCopy, fileName):
    resp = int(numCopy[1:-1]) + 1
    return f"{fileName}({resp}).vm"   

# --------------------------------------------
#            Configuração do parser

parser = yacc.yacc()

parser.currLine = 1             # Indica a linha do código origem que está a ser lida
currLinetxt = f">> Error found at line "

parser.stackPointer = 0         # Indica a posição do topo da Stack no momento
parser.checkPoint = 0           # CheckPoint utilizado para diferenciar diferentes statements
parser.error = ""               # Regista a mensagem de erro a ser impressa ao utilizador 
parser.success = True           # Flag que Indica se ocorreu algum erro na execução do programa 
parser.vars = {}                # Dicionário que vai registar as variaveis utilizadas em conjunto com as informações necessárias

assembly = ""                   # Conversão Final do código em assembly

#
# ---------------------------------------------
#             Execução de Comandos

numArgs = len(sys.argv)

if numArgs == 1:                      # Caso o utilizador não especifique nem o ficheiro de entrada nem o de saída
    print(">>Press 'Enter' to Finish\n")    # Neste caso o utilizador introduz o código manualmente
    temp = input('>> ')
    code = temp

    while temp:
        temp = input('>> ')
        code += "\n" + temp

    parser.parse(code)

    if parser.success:
        assembly += parser.assembly
    else:
        if assembly == "":
            print("\n>> ERROR")
            print(parser.error)
            print(f">> Registed variables: {parser.vars}")
        sys.exit()

    flagSaveCode = input(">> Do you want the save the generated code? [Y/n]\n")
    flagSaveCode = search(r'(?i:no)|[Nn]\b', flagSaveCode)

    if flagSaveCode:
        print(">> Execution Finished")
    else:
        outputFile = input(">> Insert File Name: \n")

        if outputFile:
            if outputFile[-3:] != ".vm":
                outputFile = f"{outputFile}.vm"
            if outputFile[:9] != "./Testes/":
                outputFile = f"./Testes/{outputFile}"
            
        else:
            outputFile = ("./Testes/unnamed.vm")

        filesList = os.listdir("./Testes")

        while outputFile[9:] in filesList:

            flagReplace = input(f">> {outputFile[9:]} already exists, do you wish to replace it? [y/N]\n")
            flagReplace = search(r'(?i:yes)|[yY]\b', flagReplace)

            if flagReplace:
                break
        
            else:
                aux = search(r'([^\n]+?)(\([\d+]\))?\.vm\b', outputFile)
                fileName = aux.group(1)
                numCopy = aux.group(2)

                if numCopy:
                    outputFile = sub(escape(fileName+numCopy+'.vm'), nextCopy(numCopy, fileName), outputFile)
                else:
                    outputFile = outputFile[:-3] + "(1).vm"
        
        outputFileName = outputFile
        outputFile = open(outputFile, "w")
        outputFile.write(assembly)

        print(f">> File saved successfully as {outputFileName.split("/")[-1]}")
        outputFile.close()

elif numArgs == 2:                  # Caso o utilizador defina apenas o ficheiro de entrada

    inputFile = sys.argv[1]

    if inputFile[-4:] != ".ggo":

        print(f"\n>> Invalid file extension")
        print(">> File must be .ggo")

    else:

        file = open(inputFile, "r")
        code = file.read()
        parser.parse(code)

        if parser.success:
            assembly += parser.assembly
            print(f">> Registed variables: {parser.vars}")
        else:
            if assembly == "":
                print("\n>> ERROR")
                print(parser.error)
                print(f">> Registed variables: {parser.vars}")
            sys.exit()
        file.close()

        flagSaveCode = input(">> Do you want the save the generated code? [Y/n]\n")
        flagSaveCode = search(r'(?i:no)|[Nn]\b', flagSaveCode)

        if flagSaveCode:
            print(">> Execution Finished")

        else:
            print(f">> The generated code will be saved in this file: {inputFile[9:-4]}.vm\n")
            flagFileName = input(">> Do you want to change the file name? [y/N]\n")
            flagFileName = search(r'(?i:yes)|[Yy]\b', flagFileName)

            if flagFileName:
                outputFile = input(">> Insert File Name\n")
            else:
                outputFile = f"{inputFile[:-4]}"

            if outputFile[:9] != "./Testes/":
                print(outputFile[:9])
                outputFile = "./Testes/" + outputFile
            if outputFile[-3:] != ".vm":
                outputFile += ".vm"

            filesList = os.listdir("./Testes")

            while outputFile[9:] in filesList:

                flagReplace = input(f">> {outputFile[9:]} already exists, do you wish to replace it? [y/N]\n")
                flagReplace = search(r'(?i:yes)|[yY]\b', flagReplace)

                if flagReplace:
                    break
            
                else:
                    aux = search(r'([^\n]+?)(\([\d+]\))?\.vm\b', outputFile)
                    fileName = aux.group(1)
                    numCopy = aux.group(2)

                    if numCopy:
                        outputFile = sub(escape(fileName+numCopy+'.vm'), nextCopy(numCopy, fileName), outputFile)
                    else:
                        outputFile = outputFile[:-3] + "(1).vm"

            outputFileName = outputFile
            outputFile = open(outputFile, "w")
            outputFile.write(assembly)
            outputFile.close()

            print(f"\n>> File successfully saved as {outputFileName.split("/")[-1]}\n")

elif numArgs == 3:                  # Caso o utilizador defina tanto o ficheiro de entrada como de saída

    inputFile = sys.argv[1]
    outputFile = sys.argv[2]
    filesList = os.listdir("./Testes")

    if inputFile[-4:] != ".ggo" or outputFile[-3:] != ".vm":

        print(f"\n>> Invalid file extension\n")
        print(">> Files must be .ggo and .vm\n")

    else:

        if inputFile[9:] in filesList:
            file = open(inputFile, "r")
            code = file.read()
            parser.parse(code)
        else: 
            print(">> ERROR")
            print(">> Input File not in \"Testes\"")
            sys.exit()

        if parser.success:
            assembly += parser.assembly
        else:
            if assembly == "":
                print("\n>> ERROR")
                print(parser.error)
                print(f">> Registed variables: {parser.vars}")
            sys.exit()
        file.close()

        outputFileName = outputFile
        outputFileName = open(outputFile, "r")
        content = outputFileName.read()

        if content:

            flagRewrite = input(f">> {outputFile[9:]} already as content, do you wish to Rewrite it? [y/N]\n")
            flagRewrite = search(r'(?i:yes)|[yY]\b', flagRewrite)

            if flagRewrite:
                outputFileName = outputFile
                outputFile = open(outputFile, "w")
                outputFile.write(assembly)
                outputFile.close()

                print(f"\n>> File successefully saved as {outputFileName.split("/")[-1]}\n")

            else:

                print(">> Try again with another file")
                print(">> Execution Finished")

        else:
            outputFileName = outputFile
            outputFile = open(outputFile, "w")
            outputFile.write(assembly)
            outputFile.close()

            print(f"\n>> File successefully saved as {outputFileName.split("/")[-1]}\n")
else:
    print("\n>> ERROR")
    print(">> Invalid Format try one of the following:")
    print(">> python3 yacc.py")
    print(">> python3 yacc.py <Input File>.ggo")
    print(">> python3 yacc.py <Input File>.ggo <Output File>.vm")

print("")