def execution(instruct, reqRegisters):
    if (instruct == "add"):
        if len(reqRegisters) == 3:
                temp = int(Register[reqRegisters[1]]) + int(Register[reqRegisters[2]])
        else:
            if (reqRegisters[1].find('x') != -1):
                temp = int(reqRegisters[1], 16) + int(Register[reqRegisters[2]])
            else:
                temp = int(reqRegisters[1]) + int(Register[reqRegisters[2]])
        return temp
    elif (instruct == "sub"):
        temp = int(Register[reqRegisters[1]]) - int(Register[reqRegisters[2]])
        return temp
    elif (instruct == "mul"):
        temp = int(Register[reqRegisters[1]]) * int(Register[reqRegisters[2]])
        return temp
    elif (instruct == "div"):
        temp = int(Register[reqRegisters[1]]) / int(Register[reqRegisters[2]])
        return temp
    elif (instruct == "andi"):
        if (reqRegisters[2].find('x') != -1):
            temp = int(reqRegisters[2], 16) + int(Register[reqRegisters[1]])
        else:
            temp = int(reqRegisters[2]) + int(Register[reqRegisters[1]])
        return temp
    elif (instruct == "subi"):
        if (reqRegisters[2].find('x') != -1):
            temp = int(Register[reqRegisters[1]]) -  int(reqRegisters[2], 16)
        else:
            temp = int(Register[reqRegisters[1]]) -  int(reqRegisters[2])
        return temp
    elif (instruct == "and"):
        temp = int(Register[reqRegisters[1]]) & int(reqRegisters[2])
        return temp
    elif (instruct == "or"):
        temp = int(Register[reqRegisters[1]]) | int(reqRegisters[2])
        return temp
    elif (instruct == "not"):
        temp = ~ int(Register[reqRegisters[1]])
        return temp
    elif (instruct == "bne"):
        if Register[reqRegisters[0]] !=  Register[reqRegisters[1]] :
           PC = Addres[reqRegisters[2]]
           return True
        else :
            return False
    elif (instruct == "beq"):
        if Register[reqRegisters[0]] ==  Register[reqRegisters[1]] :
           PC = Addres[reqRegisters[2]]
           return True
        else :
            return False
    elif (instruct == "j"):
           PC = Addres[reqRegisters[1]]
           return True
    elif (instruct == "jr"):
           return "BREAK"
    elif (instruct == "li"):
        temp = int(reqRegisters[1])
    elif (instruct == "li"):
        if (reqRegisters[1].find('x') != -1):
            temp = int(reqRegisters[1],16)
        else:
            temp = int(reqRegisters[1])
        return mem(instruct, reqRegisters, temp)
    elif (instruct == "lui"):
        number = reqRegisters[1] + "0000"
        temp= int(number , 16)
        return mem(instruct, reqRegisters,temp)
    elif (instruct == "la"):
        temp = dataAddress[reqRegisters[1]]
        return mem(instruct, reqRegisters, temp)
    elif (instruct == "move"):
        temp = int(Register[reqRegisters[1]],16)
        return mem(instruct, reqRegisters, temp)
    elif (instruct == "srl"):
        temp = int(Register[reqRegisters[1]])>> int(reqRegisters[2])
        return mem(instruct, reqRegisters, temp)
    elif (instruct == "sll"):
        temp = int(Register[reqRegisters[1]])<< int(reqRegisters[2])
        return mem(instruct, reqRegisters, temp)
    elif (instruct == "andi"):
        if (reqRegisters[2].find('x') != -1):
            temp = int(Register[reqRegisters[1]],16) & int(reqRegisters[2], 16)
        else:
            temp = int(Register[reqRegisters[1]],16) & int(reqRegisters[2])
        return mem(instruct, reqRegisters,temp)

"""
Register = {
    "$zero": 0x0,      # Hard-wired to 0
    "$at": 0x0,        # Reserved for pseudo-instructions
    "$v0": 0x0,
    "$v1": 0x0,        # Return values from functions
    "$a0": 0x0,         # Arguments to functions - not preserved by subprograms
    "$a1": 0x0,
    "$a2": 0x0,
    "$a3": 0x0,
    "$t0": 0x0,         # Temporary data, not preserved by subprograms
    "$t1": 0xa,
    "$t2": 0x1,
    "$t3": 0xa,
    "$t4": 0x0,
    "$t5": 0x0,
    "$t6": 0x0,
    "$t7": 0x0,
    "$s0": 0x0,         # Saved registers, preserved by subprograms
    "$s1": 0x0,
    "$s2": 0x0,
    "$s3": 0x0,
    "$s4": 0x0,
    "$s5": 0x0,
    "$s6": 0x0,
    "$s7": 0x0,
    "$t8": 0x0,         # More temporary registers, not preserved by subprograms
    "$t9": 0x0,
    "$k0": 0x0,
    "$k1": 0x0,         # Reserved for kernel. Do not use.
    "$gp": 0x0,         # Global Area Pointer(base of global data segment)
    "$sp": 0x0,         # Stack Pointer
    "$fp": 0x0,         # Frame Pointer
    "$ra": 0x0          # Return Address
}
print(execution("addi",['$t0','$t3','0x4','sw']))
"""
"""
def add(x,y):
   return sub(x,y)
def sub(x,y):
    return x-y
print(add(6,5))
TELL ABOUT THIS
"""