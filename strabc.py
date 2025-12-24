CHARACTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMOPQRSTUVWXYZ0123456789\n\t "



def make_str(s):
    o = []
    for c in s:
        for i in range(len(CHARACTERS)):
            if c == CHARACTERS[i]:
                o.append(str(i))
    return '-1,'+','.join(o[::-1])

print(make_str("Welcome on the standard library\n"))