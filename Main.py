import InputFile as InputFile
import memorySegment as FillMemory

Addres = {}
MemAddres = {}
PC = 0

dataSegment = 1024*[0]

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

indx = FillMemory.FillMemory(Data, dataSegment, MemAddres)


def InstructionFetch(PC):
    inst = Instructions[PC]
    PC += 1
    return inst, PC


def InstructionDecode(inst):
    if inst == "syscall":
        return "syscall", []
    idx = 0
    instType = ""

    if "jal" in inst:
        instType = "jal"
        inst = inst[4:]
        inst = inst.strip()
        try:
            Addres[inst]
        except:
            return -1, -1
        return instType, [inst]
    elif inst[0] == 'j' and inst[1] != 'r':
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
        if instType != "addi":
            try:
                for reg in arr:
                    Register[reg]
            except:
                return -1, -1
        else:
            try:
                for reg in arr:
                    if reg != arr[-1]:
                        Register[reg]
                    else:
                        int(reg)
            except:
                return -1, -1
        if len(arr) != 3:
            return -2, -2
        else:
            return instType, arr
    elif instType == "and" or instType == "or" or instType == "sll" or instType == "srl" or instType == "andi":
        if instType == "and" or instType == "or":
            try:
                for reg in arr:
                    Register[reg]
            except:
                return -1, -1
        else:
            try:
                for reg in arr:
                    if reg != arr[-1]:
                        Register[reg]
                    else:
                        int(reg)
            except:
                return -1, -1

        if len(arr) != 3:
            return -2, -2
        else:
            return instType, arr
    elif instType == "beq" or instType == "bne":
        try:
            for reg in arr:
                if reg != arr[-1]:
                    Register[reg]
                else:
                    Addres[reg]
        except:
            return -1, -1

        if len(arr) != 3:
            return -2, -2
        else:
            return instType, arr
    elif instType == "lw" or instType == "sw":
        if inst.find('(') == -1:
            return -1, -1
        elif inst.find(')') == -1:
            return -1, -1

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

        try:
            int(temp)
            Register[temp1]
            Register[temp2]
        except:
            return -1, -1
        return instType, arr
    elif instType == "jr":
        return instType, ["$ra"]
    elif instType == 'j':
        try:
            Addres[arr[0]]
        except:
            return -1, -1
        if len(arr) != 1:
            return -2, -2
        else:
            return instType, arr
    elif instType == 'li':
        try:
            int(arr[1])
            Register[arr[0]]
        except:
            return -1, -1
        if len(arr) != 2:
            return -2, -2
        else:
            return instType, arr
    elif instType == 'la' or instType == "move" or instType == "lui":
        if instType == "move":
            try:
                Register[arr[0]]
                Register[arr[1]]
            except:
                return -1, -1
        elif instType == "la":
            try:
                Register[arr[0]]

                MemAddres[arr[1]]
            except:
                return -1, -1
        else:
            try:
                Register[arr[0]]

                MemAddres[arr[1]]
            except:
                return -1, -1
        if len(arr) != 2:
            return -2, -2
        else:
            return instType, arr

    else:
        print("ERROR: cmd not found")
        return -1, -1


while 1:
    inst, PC = InstructionFetch(PC)
    instType, arguments = InstructionDecode(inst)
    if instType == -2:
        print("TOO LESS ARGUMENTS ERROR OCCURRED IN LINE : ",
              PC, " INSTRUCTION : \"", inst, "\"")
        break
    elif instType == -1:
        print("SYNTAX ERROR OCCURRED IN LINE : ",
              PC, " INSTRUCTION : \"", inst, "\"")
        break
    else:
        print(instType, " ", arguments)

    if PC == len(Instructions):
        break
    # Execution (Class) -> just execute whatever is given by ID/RF
    # Mem -> SW , DATA segment work
    # WB -> Concerned regisers
    # Print current Registers
    # break
