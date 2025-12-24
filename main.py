import sys

ID = "id"
NUMBER = "number"
OPERATOR = "operator"
BALISE = "balise"

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
        elif source[i].isalpha() or source[i] == '_':
            s = ""
            start = make_pos(p)
            while i < len(source) and (source[i].isalpha() or source[i] == '_'):
                s += source[i]
                i += 1; p[0] += 1
            end = make_pos(p, (1, 0))
            tokens.append(((start, end), ID, s))
        elif source[i].isdigit():
            s = ""
            start = make_pos(p)
            while i < len(source) and source[i].isdigit():
                s += source[i]
                i += 1; p[0] += 1
            end = make_pos(p, (1, 0))
            tokens.append(((start, end), NUMBER, int(s)))
        elif source[i] in '=<>!':
            s = ""
            start = make_pos(p)
            while i < len(source) and source[i] in '=<>!':
                s += source[i]
                i += 1; p[0] += 1
            end = make_pos(p, (1, 0))
            tokens.append(((start, end), OPERATOR, s))
        elif source[i] == '&':
            while i < len(source) and source[i] != '\n':
                i += 1; p[0] += 1
        else:
            i += 1; p[0] += 1

    return tokens + [((p, p), EOF)]


def error(message):
    print(message)
    sys.exit(1)
def matchT(tok, type):
    return tok[1] == type
def matchV(tok, value):
    return tok[2] == value


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.ast = []

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

        elif matchV(self.at(), DBG):
            self.eat()
            return DBG

        else:
            return (BALISE, self.eat()[2])

    def parse_value(self):
        tok = self.eat()
        if matchT(tok, ID):
            return (ID, tok[2])
        if matchT(tok, NUMBER):
            return (NUMBER, tok[2])
        error(f"{tok[1]}{' '+tok[2] if tok[2] else ''} at col {tok[0][0][0]}, ln {tok[0][0][1]} expected value")
        return None

    def parse_operator(self):
        tok = self.eat()
        if matchT(tok, OPERATOR):
            return (OPERATOR, tok[2])
        error(f"{tok[1]}{' '+tok[2] if tok[2] else ''} at col {tok[0][0][0]}, ln {tok[0][0][1]} expected operator")
        return None

    def parse_register(self):
        tok = self.eat()
        if matchT(tok, ID):
            return (ID, tok[2])
        error(f"{tok[1]}{' '+tok[2] if tok[2] else ''} at col {tok[0][0][0]}, ln {tok[0][0][1]} expected register")
        return None

    def parse(self):
        while not matchT(self.at(), EOF):
            if self.at()[1] == ID:
                node = self.parse_id()
                if node: self.ast.append(node)

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
            'memory': [0 for i in range(256)]
        }

    def preprocessing(self):
        for i in range(len(self.ast)):
            n = self.ast[i]
            if n[0] == BALISE:
                self.ctx['register'][n[1]] = (NUMBER, i+1)


    def eval_value(self, node):
        if node[0] == ID:
            return self.ctx['register'][node[1]]
        elif node[0] == NUMBER:
            return node

    def interpret(self, node):
        if node[0] == MOV:
            self.ctx['register'][node[1][1]] = self.eval_value(node[2])

        elif node[0] == ADD:
            self.ctx['register'][node[1][1]] = (NUMBER, self.ctx['register'][node[1][1]][1] + self.eval_value(node[2])[1])
        elif node[0] == REM:
            self.ctx['register'][node[1][1]] = (NUMBER, self.ctx['register'][node[1][1]][1] - self.eval_value(node[2])[1])

        elif node[0] == INC:
            self.ctx['register'][node[1][1]] = (NUMBER, self.ctx['register'][node[1][1]][1] + 1)
        elif node[0] == DEC:
            self.ctx['register'][node[1][1]] = (NUMBER, self.ctx['register'][node[1][1]][1] - 1)

        elif node[0] == CMP:
            if (node[2] == '=' and not self.eval_value(node[1])[1] == self.eval_value(node[3])[1]) \
                or (node[2] == '<=' and not self.eval_value(node[1])[1] <= self.eval_value(node[3])[1]) \
                or (node[2] == '>=' and not self.eval_value(node[1])[1] >= self.eval_value(node[3])[1]) \
                or (node[2] == '<' and not self.eval_value(node[1])[1] < self.eval_value(node[3])[1]) \
                or (node[2] == '>' and not self.eval_value(node[1])[1] > self.eval_value(node[3])[1]) \
                or (node[2] == '!' and not self.eval_value(node[1])[1] != self.eval_value(node[3])[1]):
                self.inc_ri(1)

        elif node[0] == JMP:
            self.mov_ri(self.eval_value(node[1])[1])
        elif node[0] == CALL:
            self.add_call(self.ctx['register']['ri'][1])
            self.mov_ri(self.eval_value(node[1])[1])
        elif node == RET:
            self.mov_ri(self.pop_call())

        elif node == INT:
            if self.get_register('ra')[1] == 0 \
                and self.get_register('rb')[1] == 0 \
                and self.get_register('rc')[1] == 0 \
                and self.get_register('rd')[1] == 0:
                return -1
            elif self.get_register('ra')[1] == 1 \
                and self.get_register('rb')[1] == 0 \
                and self.get_register('rc')[1] == 0 \
                and self.get_register('rd')[1] == 0:
                for v in self.ctx['register']:
                    print(v, self.ctx['register'][v][1])
            elif self.get_register('ra')[1] == 1 \
                and self.get_register('rb')[1] == 1 \
                and self.get_register('rc')[1] == 0 \
                and self.get_register('rd')[1] == 0:
                print('ra', self.ctx['register']['ra'][1])
            elif self.get_register('ra')[1] == 1 \
                and self.get_register('rb')[1] == 2 \
                and self.get_register('rc')[1] == 0 \
                and self.get_register('rd')[1] == 0:
                print('rb', self.ctx['register']['rb'][1])
            elif self.get_register('ra')[1] == 1 \
                and self.get_register('rb')[1] == 3 \
                and self.get_register('rc')[1] == 0 \
                and self.get_register('rd')[1] == 0:
                print('rc', self.ctx['register']['rc'][1])
            elif self.get_register('ra')[1] == 1 \
                and self.get_register('rb')[1] == 4 \
                and self.get_register('rc')[1] == 0 \
                and self.get_register('rd')[1] == 0:
                print('rd', self.ctx['register']['rd'][1])
            elif self.get_register('ra')[1] == 1 \
                and self.get_register('rb')[1] == 5 \
                and self.get_register('rc')[1] == 0 \
                and self.get_register('rd')[1] == 0:
                print('ri', self.ctx['register']['ri'][1])

        elif node == DBG:
            print('DEBUG PROCESS')

    def inc_ri(self, i):
        self.ctx['register']['ri'] = (NUMBER, self.ctx['register']['ri'][1] + i)
    def mov_ri(self, i):
        self.ctx['register']['ri'] = (NUMBER, i)
    def get_register(self, n):
        return self.ctx['register'][n]
    def add_call(self, ri):
        self.ctx['calls'].append(ri)
    def pop_call(self):
        return self.ctx['calls'].pop(-1)

    def run(self):
        while self.ctx['register']['ri'][1]-1<len(self.ast):
            i = self.ctx['register']['ri'][1]
            node = self.ast[i-1]
            self.inc_ri(1)
            ret = self.interpret(node)
            if ret == -1: break


def main(file):
    with open(file, 'r') as f:
        tokens = tokenize(f.read())

    parser = Parser(tokens)
    ast = parser.parse()
    inter = Interpreter(ast)
    inter.preprocessing()
    inter.run()

if __name__ == "__main__":
    main("main.txt")