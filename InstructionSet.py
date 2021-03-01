instructions = ["add", "li", "sub", "lw", "sw",
                "bne", "beq", "addi", "lui", "j", "jr"]
pc = 0
for i in range(0, 3):
    code = input().split()
    if (code[0] == "add"):
        registers[code[1]] = int(registers[code[2]])+int(registers[code[3]])
        pc += 1
    elif (code[0] == "li"):
        registers[code[1]] = int(code[2])
        pc += 1
    elif (code[0] == "sub"):
        registers[code[1]] = int(registers[code[2]]) - int(registers[code[3]])
        pc += 1
    elif (code[0] == "lw"):
        registers[code[1]] = int(registers[code[2]])
        pc += 1
    elif (code[0] == "sw"):
        registers[code[2]] = int(registers[code[1]])
        pc += 1
    elif (code[0] == "addi"):
        registers[code[1]] = int(registers[code[2]]) + int(code[3])
        pc += 1
    elif (code[0] == "bne"):
        if registers[code[1]] == registers[code[2]]:
            pc = x  # pc will be updated to the label
        else:
            pc += 1
    elif (code[0] == "beq"):
        if registers[code[1]] == registers[code[2]]:
            pc = x  # pc will be updated to the label of code[3]
        else:
            pc += 1
    elif (code[0] == "lui"):
        registers[code[1]] = int(code[2][2:]+"0000", 16)
        pc += 1
    elif (code[0] == "j"):
        pc = x  # pc will be updated to the label of code[1]
    elif (code[0] == "jr"):
        break
print(registers)


"""
string = 'F'
# converting hexadecimal string to decimal
res = int(string, 16)
"""
