file = open("input.txt", "r")
out = "program = ["
for line in file:
    stripped_line = line.strip()
    if (len(stripped_line) > 0):
        out += '\'' + line.strip() + '\',\n'
out = out[0:-2] + ']'
print(out)
