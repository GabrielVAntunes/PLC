import ply.lex as lex
import sys

# Tokens
tokens = (

    'INT',
    'ARRAY',
    'MATRIX',
    'ID',

    'NUM',
    'NEGATIVE',
    'TEXT',

    'KEEPS',
    'SWAP',

    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'LBRACKET',
    'RBRACKET',
    'COMMA',
    'SEMICOLON',

    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDED_BY',
    'REMAINDER',

    'INPUT',
    'OUTPUT',

    'SEARCH',

    'IF',
    'ELSE',
    'WHILE',
    'DO',
    'REPEAT',
    'UNTIL',
    'FOR',
    'END',

    'NOT',
    'EQUAL',
    'NOT_EQUAL',
    'GREATER',
    'GREATER_EQUAL',
    'LOWER',
    'LOWER_EQUAL',
    'AND',
    'OR'
)

reserved = {

    'INT': 'INT',
    'ARRAY': 'ARRAY',
    'MATRIX': 'MATRIX',

    'KEEPS':'KEEPS',
    'SWAP': 'SWAP',

    'PLUS': 'PLUS',
    'MINUS': 'MINUS',
    'TIMES': 'TIMES',
    'DIVIDEDBY': 'DIVIDED_BY',
    'REMAINDER': 'REMAINDER',

    'INPUT': 'INPUT',
    'OUTPUT': 'OUTPUT',

    'SEARCH': 'SEARCH',

    'IF': 'IF',
    'ELSE': 'ELSE',
    'WHILE': 'WHILE',
    'DO': 'DO',
    'REPEAT': 'REPEAT',
    'UNTIL': 'UNTIL',
    'FOR': 'FOR',
    'END': 'END',

    'NOT': 'NOT',
    'EQUAL': 'EQUAL',
    'NOTEQUAL': 'NOT_EQUAL',
    'GREATER': 'GREATER',
    'GREATEREQUAL': 'GREATER_EQUAL',
    'LOWER': 'LOWER',
    'LOWEREQUAL': 'LOWER_EQUAL',
    'AND':'AND',
    'OR':'OR'
}

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_SEMICOLON = r';'
t_COMMA = r','
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_NEGATIVE = r'-'

def t_ID(t):
    r'[a-zA-Z_][\w_]*'
    t.type = reserved.get(t.value, 'ID')  
    return t

def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_TEXT(t):
    r'\".*\"' 
    t.value = t.value
    return t

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Erro lexical: {t.value[0]} na linha {t.lineno}")
    sys.exit()
    t.lexer.skip(len(t.value))

lexer = lex.lex()