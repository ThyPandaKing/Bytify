import InputFile as InputFile
import re

Addres = {}
PC = 0

Register = {
    "$zero": '0x0',      # Hard-wired to 0
    "$at": '0x0',        # Reserved for pseudo-instructions
    "$v0": '0x0',
    "$v1": '0x0',        # Return values from functions
    "$a0": '0x0',         # Arguments to functions - not preserved by subprograms
    "$a1": '0x0',
    "$a2": '0x0',
    "$a3": '0x0',
    "$t0": '0x0',         # Temporary data, not preserved by subprograms
    "$t1": '0x0',
    "$t2": '0x0',
    "$t3": '0x0',
    "$t4": '0x0',
    "$t5": '0x0',
    "$t6": '0x0',
    "$t7": '0x0',
    "$s0": '0x0',         # Saved registers, preserved by subprograms
    "$s1": '0x0',
    "$s2": '0x0',
    "$s3": '0x0',
    "$s4": '0x0',
    "$s5": '0x0',
    "$s6": '0x0',
    "$s7": '0x0',
    "$t8": '0x0',         # More temporary registers, not preserved by subprograms
    "$t9": '0x0',
    "$k0": '0x0',
    "$k1": '0x0',         # Reserved for kernel. Do not use.
    "$gp": '0x0',         # Global Area Pointer(base of global data segment)
    "$sp": '0x0',         # Stack Pointer
    "$fp": '0x0',         # Frame Pointer
    "$ra": '0x0'          # Return Address
}


def improveInstructions(Instructions):
    pc = 0
    temp = []
    for inst in Instructions:

        if '.' in inst:
            temp.append(inst)
        elif ':' in inst:
            idx = inst.find(':')

            Addres[inst[:idx]] = pc
            if inst[-1] == ':':
                temp.append(inst)
            else:
                idx = inst.find(':')
                id2 = Instructions.index(inst)
                Instructions[id2] = inst[idx+1:].strip()
                pc += 1
        else:
            pc = pc+1

    for tep in temp:
        Instructions.remove(tep)


Instructions, Data = InputFile.InputFile()

improveInstructions(Instructions)  # for branch instructions
# for dta in Data:
#     print(dta)

# print(Addres)


PC=0
def InstructionFetch(inst):
 #   inst = Instructions[PC]
     global PC
     inst = inst
     PC = PC + 1
     return InstructionDecode(inst)


def InstructionDecode(inst):
    global PC
    if inst == "syscall":
        return execution("syscall", [])
    idx = 0
    instType = ""
    if inst[0] == 'j' and inst[1] != 'r' and inst[1] == ' ':
        instType = 'j'
        inst = inst[1:]
        inst = inst.strip()
    elif "jal" in inst:
        instType = "jal"
        inst = inst[4:]
        inst = inst.strip()
        return execution(instType, [inst])
    else:
        for ch in inst:

            if ch == '$':
                break
            instType += ch
            idx += 1

    instType = instType.strip()
    inst = inst[idx:]
    # print(inst)
    inst = inst.replace(",", " ")
    # print(inst)
    arr = inst.split()
    # arguments will depend upon instType
    # 1. add,sub,mul,div
    if instType == "add" or instType == "sub" or instType == "mul" or instType == "div" or instType == 'addi'or instType == 'subi':
        return execution(instType, arr)
    elif instType == "and" or instType == "or" or instType == "sll" or instType == "srl" or instType == "andi":
        return execution(instType, arr)
    elif instType == "beq" or instType == "bne":
        return execution(instType, arr)
    elif instType == "lw" or instType == "sw":
        tempInst = instType
        instType = "add"
        temp1 = arr[0]
        inst = arr[1]
        temp = ""
        idx = 0
        for ele in inst:
            if ele == '(':
                temp2 = inst[idx+1:]
                temp2 = temp2.replace(')', ' ')
                temp2 = temp2.strip()
                break
            else:
                temp += ele
                idx += 1

        arr = [temp1, temp, temp2, tempInst]
        return execution(instType, arr)
    elif instType == "jr":
        return execution(instType, ["$ra"])
    elif instType == 'j':
        return execution(instType, arr)
    elif instType == 'li':
        return execution(instType, arr)
    elif instType == 'la' or instType == "move" or instType == "lui":
        return execution(instType, arr)
    else:
        print("ERROR: cmd not found")
        return -1, -1

def execution(instruct, reqRegisters):
    global PC
    if (instruct == "add"):
        if len(reqRegisters) == 3:
                temp = int(Register[reqRegisters[1]],16) + int(Register[reqRegisters[2]],16)
        else:
            if (reqRegisters[1].find('x') != -1):
                temp = int(reqRegisters[1], 16) + int(Register[reqRegisters[2]],16)
            else:
                temp = int(reqRegisters[1]) + int(Register[reqRegisters[2]],16)
            #temp=str(temp)
        return mem(instruct, reqRegisters,temp)
    elif (instruct == "sub"):
        temp = int(Register[reqRegisters[1]],16) - int(Register[reqRegisters[2]],16)
        return mem(instruct, reqRegisters,temp)
    elif (instruct == "mul"):
        temp = int(Register[reqRegisters[1]],16) * int(Register[reqRegisters[2]],16)
        return mem(instruct, reqRegisters,temp)
    elif (instruct == "div"):
        temp = int(Register[reqRegisters[1]],16) / int(Register[reqRegisters[2]],16)
        return mem(instruct, reqRegisters,temp)
    elif (instruct == "addi"):
        if (reqRegisters[2].find('x') != -1):
            temp = int(reqRegisters[2], 16) + int(Register[reqRegisters[1]],16)
        else:
            temp = int(reqRegisters[2]) + int(Register[reqRegisters[1]],16)
        return mem(instruct, reqRegisters,temp)
    elif (instruct == "subi"):
        if (reqRegisters[2].find('x') != -1):
            temp = int(Register[reqRegisters[1]],16) -  int(reqRegisters[2], 16)
        else:
            temp = int(Register[reqRegisters[1]],16) -  int(reqRegisters[2])
        return mem(instruct, reqRegisters,temp)
    elif (instruct == "and"):
        temp = int(Register[reqRegisters[1]],16) & int(Register[reqRegisters[2]],16)
        return mem(instruct, reqRegisters,temp)
    elif (instruct == "or"):
        temp = int(Register[reqRegisters[1]],16) | int(reqRegisters[2])
        return mem(instruct, reqRegisters,temp)
    elif (instruct == "not"):
        temp = ~ int(Register[reqRegisters[1]],16)
        return mem(instruct, reqRegisters,temp)
    elif (instruct == "bne"):
        if Register[reqRegisters[0]] !=  Register[reqRegisters[1]] :
           PC = Addres[reqRegisters[2]]
           return mem(instruct, reqRegisters,True)
        else :
            return mem(instruct, reqRegisters,False)
    elif (instruct == "beq"):
        if Register[reqRegisters[0]] ==  Register[reqRegisters[1]] :
           PC = Addres[reqRegisters[2]]
           return mem(instruct, reqRegisters, True)
        else :
            return mem(instruct, reqRegisters, False)
    elif (instruct == "j"):
           PC = Addres[reqRegisters[0]]
           return mem(instruct, reqRegisters, True)
    elif (instruct == "jr"):
        return mem(instruct, reqRegisters,"BREAK")
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

def mem(instructType,reqRegisters,temp):
    global PC
    if(len(reqRegisters)==4):
        if(reqRegisters[3] == "lw"):
            Register[reqRegisters[0]] = dataSegment[int(temp)]

            #lw s1 100(s0)
        else:
            memory[temp] = Register[reqRegisters[0]]
    else:
        return writeBack(instructType,reqRegisters,temp)

def writeBack(instructType,reqRegisters,temp):
    global PC
    if instructType=="add" or instructType=="sub" or  instructType=="subi" or instructType=="mul" or instructType=="div" or instructType=="addi" or instructType=="and" or instructType=="or" or instructType=="not" or instructType=="li" or instructType=="lui" or instructType=="la" or instructType=="move" or instructType=="srl" or instructType=="sll" or instructType=="andi":
         Register[reqRegisters[0]] = hex(temp)

while 1:
    if PC == len(Instructions):
        break
    print(PC)
    inst = Instructions[PC]
    InstructionFetch(inst)
    print(Register)
    # instruction fetch -> increase pc , send inst to next guy
    # Instruction decode/ RF -> for every inst , find what it is and to whom it is
    # Execution (Class) -> just execute whatever is given by ID/RF
    # Mem -> SW , DATA segment work
    # WB -> Concerned regisers
    # Print current Registers
    # break

# 1. execute -> given -> instruction Type , list of registers
# 2. mem address save

# 1. instruction fetch
# 2. Decode and rf -> string input

