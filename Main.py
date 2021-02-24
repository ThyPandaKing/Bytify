import InputFile as InputFile
import re

DataSegment = []
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


MakeDataSegment()
Instructions, Data = InputFile.InputFile()

FillDataSegment(Data)
PC = 0
while 1:
    # instruction fetch -> increase pc , send inst to next guy
    # Instruction decode/ RF -> for every inst , find what it is and to whom it is
    # Execution (Class) -> just execute whatever is given by ID/RF
    # Mem -> SW , DATA segment work
    # WB -> Concerned regisers
    # Print current Registers
    break
