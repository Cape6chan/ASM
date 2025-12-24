import sys

EXTENSION = '.txt'

CHARACTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMOPQRSTUVWXYZ0123456789\n\t "

ID = "id"
NUMBER = "number"
OPERATOR = "operator"
BALISE = "balise"
ADDRESS = "address"
COMMA = "comma"
IMPORT = "import"

MOV = "mov"
ADD = "add"
REM = "rem"
INC = "inc"
DEC = "dec"
CMP = "cmp"
JMP = "jmp"
CALL = "call"
RET = "ret"
INT = "int"
PUSH = "push"
POP = "pop"

DBG = "dbg"
EOF = "eof"

"""
mov r v
add r v
rem r v
inc r
dec r
cmp a op b
jmp n°
int:
    exit:
        ra 0
        rb 0
        rc 0
        rd 0
    stdout:
        ra 1
        dbg all register:
            rb 0
            rc 0
            rd 0
        dbg ra:
            rb 1
            rc 0
            rd 0
        dbg rb:
            rb 2
            rc 0
            rd 0
        dbg rc:
            rb 3
            rc 0
            rd 0
        dbg rd:
            rb 4
            rc 0
            rd 0
        dbg ri:
            rb 5
            rc 0
            rd 0


"""

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def tokenize(source):
    def make_pos(p, sub=(0, 0)):
        return (p[0]-sub[0], p[1]-sub[1])
    source = list(source)
    i = 0
    tokens = []
    p = [1, 1]
    while i < len(source):
        if source[i] == '\n':
            i += 1; p[0] = 1; p[1] += 1
        elif i+1 < len(source) and source[i] == 'x' and source[i+1].isdigit():
            i += 1; p[0] += 1
            s = ""
            start = make_pos(p, (1, 0))
            while i < len(source) and source[i].isdigit():
                s += source[i]
                i += 1; p[0] += 1
            end = make_pos(p, (1, 0))
            tokens.append(((start, end), ADDRESS, int(s)))
        elif source[i].isalpha() or source[i] == '_':
            s = ""
            start = make_pos(p)
            while i < len(source) and (source[i].isalpha() or source[i] == '_'):
                s += source[i]
                i += 1; p[0] += 1
            end = make_pos(p, (1, 0))
            tokens.append(((start, end), ID, s))
        elif source[i].isdigit() or source[i] == '-':
            s = ""
            start = make_pos(p)
            if source[i] == '-':
                s = "-"
                i += 1; p[0] += 1
            while i < len(source) and source[i].isdigit():
                s += source[i]
                i += 1; p[0] += 1
            end = make_pos(p, (1, 0))
            if s == '-': s = "0"
            tokens.append(((start, end), NUMBER, int(s)))
        elif source[i] in '=<>!':
            s = ""
            start = make_pos(p)
            while i < len(source) and source[i] in '=<>!':
                s += source[i]
                i += 1; p[0] += 1
            end = make_pos(p, (1, 0))
            tokens.append(((start, end), OPERATOR, s))
        elif source[i] == ',':
            pop = make_pos(p)
            tokens.append(((pop, pop), COMMA))
            i += 1; p[0] += 1

        elif source[i] == '&':
            while i < len(source) and source[i] != '\n':
                i += 1; p[0] += 1

        elif source[i] == '#':
            s = ""
            start = make_pos(p)
            i += 1; p[0] += 1
            while i < len(source) and source[i] != '\n':
                s += source[i]
                i += 1; p[0] += 1
            end = make_pos(p, (1, 0))
            tokens.append(((start, end), IMPORT, s))

        else:
            i += 1; p[0] += 1

    return tokens + [((p, p), EOF)]


def error(message, pos=None, source=None):
    print(bcolors.FAIL + message)
    if pos and source:
        source = source.split('\n')
        sx, ex, sy, ey = pos[0][0], pos[1][0], pos[0][1], pos[1][1]
        ss = f'>>> '
        print(f'ln {sy}, col {sx}\n' + ss + source[pos[0][1]-1] + '\n' + ' '*(sx+len(ss)-1) + '^'*(ex-sx+1))
        print(bcolors.ENDC, end='')
    sys.exit(1)
def matchT(tok, type):
    return tok[1] == type
def matchV(tok, value):
    return tok[2] == value


class Parser:
    def __init__(self, tokens, source, imported=[]):
        self.tokens = tokens
        self.ast = []
        self.source = source
        self.imported = imported

    def at(self):
        return self.tokens[0] if len(self.tokens)>0 else ()
    def eat(self):
        return self.tokens.pop(0)

    def parse_id(self):
        if matchV(self.at(), MOV):
            self.eat()
            r = self.parse_register()
            v = self.parse_value()
            return (MOV, r, v)


        elif matchV(self.at(), ADD):
            self.eat()
            r = self.parse_register()
            v = self.parse_value()
            return (ADD, r, v)

        elif matchV(self.at(), REM):
            self.eat()
            r = self.parse_register()
            v = self.parse_value()
            return (REM, r, v)


        elif matchV(self.at(), INC):
            self.eat()
            r = self.parse_register()
            return (INC, r)

        elif matchV(self.at(), DEC):
            self.eat()
            r = self.parse_register()
            return (DEC, r)


        elif matchV(self.at(), CMP):
            self.eat()
            a = self.parse_value()
            op = self.parse_operator()
            b = self.parse_value()
            return (CMP, a, op[1], b)


        elif matchV(self.at(), JMP):
            self.eat()
            i = self.parse_value()
            return (JMP, i)

        elif matchV(self.at(), CALL):
            self.eat()
            i = self.parse_value()
            return (CALL, i)

        elif matchV(self.at(), RET):
            self.eat()
            return RET


        elif matchV(self.at(), INT):
            self.eat()
            return INT


        elif matchV(self.at(), PUSH):
            self.eat()
            v = [self.parse_value()]
            while matchT(self.at(), COMMA):
                self.eat()
                v.append(self.parse_value())
            return (PUSH, v)

        elif matchV(self.at(), POP):
            self.eat()
            r = self.parse_register()
            return (POP, r)


        elif matchV(self.at(), DBG):
            self.eat()
            return DBG

        else:
            return (BALISE, self.eat()[2])

    def parse_value(self):
        tok = self.eat()
        if matchT(tok, ID):
            return (ID, tok[2])
        elif matchT(tok, ADDRESS):
            return (ADDRESS, tok[2])
        elif matchT(tok, NUMBER):
            return (NUMBER, tok[2])
        error(f"{tok[1]}{' '+tok[2] if tok[2] else ''} expected value", tok[0], self.source)
        return None

    def parse_operator(self):
        tok = self.eat()
        if matchT(tok, OPERATOR):
            return (OPERATOR, tok[2])
        error(f"{tok[1]}{' '+tok[2] if tok[2] else ''} expected operator", tok[0], self.source)
        return None

    def parse_register(self):
        tok = self.eat()
        if matchT(tok, ID):
            return (ID, tok[2])
        elif matchT(tok, ADDRESS):
            return (ADDRESS, tok[2])
        error(f"{tok[1]}{' '+tok[2] if tok[2] else ''} expected register or address", tok[0], self.source)
        return None

    def parse(self):
        while not matchT(self.at(), EOF):
            if self.at()[1] == ID:
                node = self.parse_id()
                if node: self.ast.append(node)

            elif self.at()[1] == IMPORT:
                if not self.at()[2] in self.imported:
                    self.imported.append(self.at()[2])
                    tokens, source = tokenizefile(self.at()[2]+EXTENSION)
                    parser = Parser(tokens, source, self.imported)
                    for n in parser.parse():
                        self.ast.append(n)
                    self.eat()
                else:
                    self.eat()

            else:
                print(self.eat())

        return self.ast

class Interpreter:
    def __init__(self, ast):
        self.ast = ast
        self.ctx = {
            'register': {
                'ra': (NUMBER, 0),
                'rb': (NUMBER, 0),
                'rc': (NUMBER, 0),
                'rd': (NUMBER, 0),
                'ri': (NUMBER, 1),
            },
            'pile': [],
            'calls': [],
            'memory': [(NUMBER, 0) for i in range(256)]
        }

    def preprocessing(self):
        for i in range(len(self.ast)):
            n = self.ast[i]
            if n[0] == BALISE:
                self.set_register(n[1], (NUMBER, i+1))


    def eval_value(self, node):
        if node[0] == ID:
            return self.get_register(node[1])
        elif node[0] == ADDRESS:
            return self.get_memory(node[1])
        elif node[0] == NUMBER:
            return node

    def interpret(self, node):
        if node[0] == MOV:
            self.set_reg_mem(node[1], self.eval_value(node[2]))

        elif node[0] == ADD:
            self.set_reg_mem(node[1][1], (NUMBER, self.get_reg_mem(node[1], NUMBER)[1] + self.eval_value(node[2])[1]))
        elif node[0] == REM:
            self.set_reg_mem(node[1][1], (NUMBER, self.get_reg_mem(node[1], NUMBER)[1] - self.eval_value(node[2])[1]))

        elif node[0] == INC:
            self.set_reg_mem(node[1][1], (NUMBER, self.get_reg_mem(node[1], NUMBER)[1] + 1))
        elif node[0] == DEC:
            self.set_reg_mem(node[1][1], (NUMBER, self.get_reg_mem(node[1], NUMBER)[1] - 1))

        elif node[0] == CMP:
            if     (node[2] == '='  and not self.eval_value(node[1])[1] == self.eval_value(node[3])[1]) \
                or (node[2] == '<=' and not self.eval_value(node[1])[1] <= self.eval_value(node[3])[1]) \
                or (node[2] == '>=' and not self.eval_value(node[1])[1] >= self.eval_value(node[3])[1]) \
                or (node[2] == '<'  and not self.eval_value(node[1])[1] <  self.eval_value(node[3])[1]) \
                or (node[2] == '>'  and not self.eval_value(node[1])[1] >  self.eval_value(node[3])[1]) \
                or (node[2] == '!'  and not self.eval_value(node[1])[1] != self.eval_value(node[3])[1]):
                self.inc_ri(1)

        elif node[0] == JMP:
            self.mov_ri(self.eval_value(node[1])[1])
        elif node[0] == CALL:
            self.add_call(self.get_register('ri')[1])
            self.mov_ri(self.eval_value(node[1])[1])
        elif node == RET:
            self.mov_ri(self.pop_call())

        elif node == INT:
            if self.test_register(0,0,0,0):
                return -1

            elif self.test_register(1,0,0,0):
                for i in self.ctx['pile']:
                    print(i[1])

            elif self.test_register(1,1,0,0):
                for v in self.ctx['register']:
                    print(v, self.ctx['register'][v][1])
            elif self.test_register(1,1,1,0):
                print('ra', self.get_register('ra')[1])
            elif self.test_register(1,1,2,0):
                print('rb', self.get_register('rb')[1])
            elif self.test_register(1,1,3,0):
                print('rc', self.get_register('rc')[1])
            elif self.test_register(1,1,4,0):
                print('rd', self.get_register('rd')[1])
            elif self.test_register(1,1,5,0):
                print('ri', self.get_register('ri')[1])

            elif self.test_register(1,2,0):
                print(self.get_register('rd')[1], end='')
            elif self.test_register(1,2,1):
                if self.get_register('rd')[1]<len(CHARACTERS):
                    print(CHARACTERS[self.get_register('rd')[1]], end='')


        elif node[0] == PUSH:
            for i in node[1]:
                self.push_pile(self.eval_value(i))
        elif node[0] == POP:
            self.set_reg_mem(node[1], self.pop_pile())

        elif node == DBG:
            print('DEBUG PROCESS')

    def inc_ri(self, i):
        self.set_register('ri', (NUMBER, self.get_register('ri')[1] + i))
    def mov_ri(self, i):
        self.set_register('ri', (NUMBER, i))

    def set_reg_mem(self, nn, node):
        if nn[0] == ID:
            self.set_register(nn[1], node)
        elif nn[0] == ADDRESS:
            self.set_memory(nn[1], node)
    def get_reg_mem(self, nn, node, expected=None):
        if nn[0] == ID:
            return self.get_register(nn[1], node, expected)
        elif nn[0] == ADDRESS:
            return self.get_memory(nn[1], node, expected)

    def set_register(self, n, node):
        if node[0] == NUMBER or node[0] == ADDRESS:
            self.ctx['register'][n] = (node[0], node[1])
            return
        error(f"expected number or address")
        return
    def get_register(self, n, expected=None):
        if n in self.ctx['register']:
            if expected and self.ctx['register'][n][0] != expected:
                error(f"expected type {expected}")
            return self.ctx['register'][n]
        error(f"register {n} doesn't exist")
        return

    def set_memory(self, i, node):
        if 0 <= i < len(self.ctx['memory']):
            self.ctx['memory'][i] = (node[0], node[1])
            return
        error(f"memory {i} out of range")
        return
    def get_memory(self, i, expected=None):
        if 0 <= i < len(self.ctx['memory']):
            if expected and self.ctx['memory'][i][0] != expected:
                error(f"expected type {expected}")
            return self.ctx['memory'][i]
        error(f"memory {i} out of range")
        return

    def push_pile(self, node):
        self.ctx['pile'].append((node[0], node[1]))
    def pop_pile(self):
        return self.ctx['pile'].pop(-1)

    def test_register(self, ra, rb=None, rc=None, rd=None):
        return self.get_register('ra')[1] == ra \
            and (rb == None or self.get_register('rb')[1] == rb) \
            and (rc == None or self.get_register('rc')[1] == rc) \
            and (rd == None or self.get_register('rd')[1] == rd)

    def add_call(self, ri):
        self.ctx['calls'].append(ri)
    def pop_call(self):
        return self.ctx['calls'].pop(-1)

    def run(self):
        while self.get_register('ri')[1]-1<len(self.ast):
            i = self.get_register('ri')[1]
            node = self.ast[i-1]
            self.inc_ri(1)
            ret = self.interpret(node)
            if ret == -1: break

def tokenizefile(file):
    with open(file, 'r') as f:
        source = f.read()
    return tokenize(source), source

def main(file):
    tokens, source = tokenizefile(file)
    parser = Parser(tokens, source)
    ast = parser.parse()
    inter = Interpreter(ast)
    inter.preprocessing()
    inter.run()

if __name__ == "__main__":
    main("main.txt")