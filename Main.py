import InputFile as InputFile

DataSegment = []


def MakeDataSegment():
    Size = 4096
    while Size > 0:
        Size -= 1
        DataSegment.append(0)


def FillDataSegment(Data):
    pass


MakeDataSegment()
Instructions, Data = InputFile.InputFile()

FillDataSegment(Data)
