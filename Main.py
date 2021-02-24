import InputFile as InputFile
import re

DataSegment = []
Addres = {}


Register = {
    '$R1': 0x0,
    'R2': 0x0,
    'T1': 0x0
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
