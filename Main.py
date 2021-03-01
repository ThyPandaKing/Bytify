import InputFile as InputFile
import re

Addres = {}
PC = 0


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
    "$t1": 0x0,
    "$t2": 0x0,
    "$t3": 0x0,
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


def InstructionFetch(PC):
    inst = Instructions[PC]
    PC += 1
    return inst, PC


def InstructionDecode(inst):
    idx = 0
    instType = ""
    if inst[0] == 'j' and inst[1] != 'r':
        instType = 'j'
        inst = inst[1:]
        inst = inst.strip()
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
    if instType == "add" or instType == "sub" or instType == "mul" or instType == "div" or instType == 'addi':
        return instType, arr
    elif instType == "beq" or instType == "bne":
        return instType, arr
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
        return instType, arr
    elif instType == "jr":
        return instType, ["$ra"]
    elif instType == 'j':
        return instType, arr
    elif instType == 'li':
        return instType, arr

    else:
        print("ERROR: cmd not found")
        return -1, -1


while 1:
    # print(PC)
    inst, PC = InstructionFetch(PC)
    # print(PC)
    instType, arguments = InstructionDecode(inst)
    if instType != -1:
        print(instType, " ", arguments)
    else:
        print(inst)
    # for k in arguments:
    #     print(k)

    if PC == len(Instructions):
        break
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
