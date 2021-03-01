import InputFile as InputFile
import re

DataSegment = []
Addres = {}


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


def MakeDataSegment():
    Size = 1024
    while Size > 0:
        Size -= 1
        DataSegment.append(0)


def FillDataSegment(Data):
    pass


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


MakeDataSegment()

Instructions, Data = InputFile.InputFile()

FillDataSegment(Data)  # filling data segment
improveInstructions(Instructions)  # for branch instructions


PC = 0
while 1:
    # instruction fetch -> increase pc , send inst to next guy
    # Instruction decode/ RF -> for every inst , find what it is and to whom it is
    # Execution (Class) -> just execute whatever is given by ID/RF
    # Mem -> SW , DATA segment work
    # WB -> Concerned regisers
    # Print current Registers
    break
