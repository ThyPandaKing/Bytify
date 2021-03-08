import InputFile as InputFile
import memorySegment as FillMemory
from tkinter import *

Addres = {}
MemAddres = {}
PC = 0

dataSegment = 1024*[0]

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

changedRegisters = {
    "$zero": 0, "$at": 0, "$v0": 0, "$v1": 0, "$a0": 0, "$a1": 0, "$a2": 0, "$a3": 0, "$t0": 0, "$t1": 0, "$t2": 0, "$t3": 0, "$t4": 0,
    "$t5": 0, "$t6": 0, "$t7": 0, "$s0": 0, "$s1": 0, "$s2": 0, "$s3": 0, "$s4": 0, "$s5": 0, "$s6": 0, "$s7": 0, "$t8": 0, "$t9": 0, "$k0": 0, "$k1": 0,
    "$gp": 0, "$sp": 0, "$fp": 0, "$ra": 0
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


def InstructionFetch(inst):
 #   inst = Instructions[PC]
    global PC
    inst = inst
    PC = PC + 1
    if inst == "":
        return
    return InstructionDecode(inst)


def InstructionDecode(inst):
    global PC
    if inst == "syscall":
        return execution("syscall", [])
    idx = 0
    instType = ""
    # print(inst[0], inst[1])
    t = inst.split()
    # print(t)
    if "jal" in inst:
        instType = "jal"
        inst = inst[4:]
        inst = inst.strip()
        try:
            Addres[inst]
        except:
            return -1, -1
        return execution(instType, [inst])
    elif t[0] == 'j':
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
    if instType == "add" or instType == "sub" or instType == "mul" or instType == "div" or instType == 'addi' or instType == 'subi':
        if len(arr) != 3:
            return -2, -2
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
        return execution(instType, arr)
    elif instType == "and" or instType == "or" or instType == "sll" or instType == "srl" or instType == "andi":
        if len(arr) != 3:
            return -2, -2
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

        return execution(instType, arr)
    elif instType == "beq" or instType == "bne":
        if len(arr) != 3:
            return -2, -2
        try:
            for reg in arr:
                if reg != arr[-1]:
                    Register[reg]
                else:
                    Addres[reg]
        except:
            return -1, -1

        return execution(instType, arr)
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
        return execution(instType, arr)
    elif instType == "jr":
        return execution(instType, ["$ra"])
    elif instType == 'j':
        if len(arr) != 1:
            return -2, -2
        try:
            Addres[arr[0]]
        except:
            return -1, -1
        return execution(instType, arr)
    elif instType == 'li':
        if len(arr) != 2:
            return -2, -2
        try:
            int(arr[1])
            Register[arr[0]]
        except:
            return -1, -1
        return execution(instType, arr)
    elif instType == 'la' or instType == "move" or instType == "lui":
        if instType == "move":
            try:
                Register[arr[0]]
                Register[arr[1]]
            except:
                return -1, -1
        elif instType == "la":
            if len(arr) != 2:
                return -2, -2
            try:
                Register[arr[0]]

                MemAddres[arr[1]]
            except:
                return -1, -1
        else:
            try:
                Register[arr[0]]
                int(arr[1])
            except:
                return -1, -1
        return execution(instType, arr)
    elif instType == "slt":
        try:
            Register[arr[0]]
            Register[arr[1]]
            Register[arr[2]]
        except:
            return -1, -1
        return execution(instType, arr)
    else:
        print("ERROR: cmd not found")
        return -1, -1


def execution(instruct, reqRegisters):
    global PC
    if instruct != "sw" and instruct != "syscall":
        change(reqRegisters[0])
    if (instruct == "add"):
        if len(reqRegisters) == 3:
            temp = int(Register[reqRegisters[1]], 16) + \
                int(Register[reqRegisters[2]], 16)
        else:
            if (reqRegisters[1].find('x') != -1):
                temp = int(reqRegisters[1], 16) + \
                    int(Register[reqRegisters[2]], 16)
            else:
                temp = int(reqRegisters[1]) + \
                    int(Register[reqRegisters[2]], 16)
            # temp=str(temp)
        return mem(instruct, reqRegisters, temp)
    elif (instruct == "sub"):
        temp = int(Register[reqRegisters[1]], 16) - \
            int(Register[reqRegisters[2]], 16)
        return mem(instruct, reqRegisters, temp)
    elif (instruct == "mul"):
        temp = int(Register[reqRegisters[1]], 16) * \
            int(Register[reqRegisters[2]], 16)
        return mem(instruct, reqRegisters, temp)
    elif (instruct == "div"):
        temp = int(Register[reqRegisters[1]], 16) / \
            int(Register[reqRegisters[2]], 16)
        return mem(instruct, reqRegisters, temp)
    elif (instruct == "addi"):
        if (reqRegisters[2].find('x') != -1):
            temp = int(reqRegisters[2], 16) + \
                int(Register[reqRegisters[1]], 16)
        else:
            temp = int(reqRegisters[2]) + int(Register[reqRegisters[1]], 16)
        return mem(instruct, reqRegisters, temp)
    elif (instruct == "subi"):
        if (reqRegisters[2].find('x') != -1):
            temp = int(Register[reqRegisters[1]], 16) - \
                int(reqRegisters[2], 16)
        else:
            temp = int(Register[reqRegisters[1]], 16) - int(reqRegisters[2])
        return mem(instruct, reqRegisters, temp)
    elif (instruct == "and"):
        temp = int(Register[reqRegisters[1]], 16) & int(
            Register[reqRegisters[2]], 16)
        return mem(instruct, reqRegisters, temp)
    elif (instruct == "or"):
        temp = int(Register[reqRegisters[1]], 16) | int(reqRegisters[2])
        return mem(instruct, reqRegisters, temp)
    elif (instruct == "not"):
        temp = ~ int(Register[reqRegisters[1]], 16)
        return mem(instruct, reqRegisters, temp)
    elif (instruct == "bne"):
        if Register[reqRegisters[0]] != Register[reqRegisters[1]]:
            PC = Addres[reqRegisters[2]]
            return mem(instruct, reqRegisters, True)
        else:
            return mem(instruct, reqRegisters, False)
    elif (instruct == "beq"):
        if Register[reqRegisters[0]] == Register[reqRegisters[1]]:
            PC = Addres[reqRegisters[2]]
            print(Instructions[PC])
            return mem(instruct, reqRegisters, True)
        else:
            return mem(instruct, reqRegisters, False)
    elif (instruct == "j"):
        PC = Addres[reqRegisters[0]]
        return mem(instruct, reqRegisters, True)
    elif (instruct == "jr"):
        return "BREAK"
    elif (instruct == "li"):
        if (reqRegisters[1].find('x') != -1):
            temp = int(reqRegisters[1], 16)
        else:
            temp = int(reqRegisters[1])
        return mem(instruct, reqRegisters, temp)
    elif (instruct == "lui"):
        temp = int(reqRegisters[1])
        return mem(instruct, reqRegisters, temp)
    elif (instruct == "la"):
        temp = MemAddres[reqRegisters[1]]
        return mem(instruct, reqRegisters, temp)
    elif (instruct == "move"):
        temp = int(Register[reqRegisters[1]], 16)
        return mem(instruct, reqRegisters, temp)
    elif (instruct == "srl"):
        temp = int(Register[reqRegisters[1]], 16) >> int(reqRegisters[2])
        return mem(instruct, reqRegisters, temp)
    elif (instruct == "sll"):
        temp = int(Register[reqRegisters[1]], 16) << int(reqRegisters[2])
        return mem(instruct, reqRegisters, temp)
    elif (instruct == "andi"):
        if (reqRegisters[2].find('x') != -1):
            temp = int(Register[reqRegisters[1]],
                       16) & int(reqRegisters[2], 16)
        else:
            temp = int(Register[reqRegisters[1]], 16) & int(reqRegisters[2])
        return mem(instruct, reqRegisters, temp)
    elif instruct == "slt":
        # print(reqRegisters)
        temp = int(Register[reqRegisters[2]], 16) > int(
            Register[reqRegisters[1]], 16)
        return mem(instruct, reqRegisters, temp)
    elif (instruct == "syscall"):
        return mem(instruct, reqRegisters, 0)


def mem(instructType, reqRegisters, temp):
    global PC
    if(len(reqRegisters) == 4):
        if(reqRegisters[3] == "lw"):
            # print(type(dataSegment[temp//4]))
            if(type(dataSegment[temp//4]) == int):
                Register[reqRegisters[0]] = hex(dataSegment[temp//4])
            else:
                if dataSegment[temp//4].find('x') != -1:
                    Register[reqRegisters[0]] = hex(
                        int(dataSegment[temp//4], 16))
                else:
                    Register[reqRegisters[0]] = hex(int(dataSegment[temp//4]))
            # print(int(dataSegment[temp]))
            # lw s1 100(s0)
        else:
            dataSegment[temp//4] = Register[reqRegisters[0]]
    else:
        return writeBack(instructType, reqRegisters, temp)


def writeBack(instructType, reqRegisters, temp):
    global PC
    if instructType == "add" or instructType == "sub" or instructType == "subi" or instructType == "mul" or instructType == "div" or instructType == "addi" or instructType == "and" or instructType == "or" or instructType == "not" or instructType == "li" or instructType == "lui" or instructType == "la" or instructType == "move" or instructType == "srl" or instructType == "sll" or instructType == "andi":
        Register[reqRegisters[0]] = hex(temp)
    if instructType == "syscall":
        lastInstruct = Instructions[PC-2]
        lastInstruct = list(lastInstruct.split())
        # print(lastInstruct[0])
        if lastInstruct[0] == 'la':
            if (int(Register['$v0'], 16) == 1):
                values = list(MemAddres.values())
                position = values.index(int(Register['$a0'], 16))
                if position+1 < len(values):
                    toPrint = ""
                    for i in range(0, values[position + 1] - values[position]):
                        print(
                            int(dataSegment[int(Register['$a0'], 16) + i], 16), end=" ")
                        toPrint = toPrint + \
                            str(int(
                                dataSegment[int(Register['$a0'], 16) + i], 16))+" "
                    #toPrint += "\n"
                    label = Label(console, text=toPrint).pack()
                    print()
                else:
                    i = 0
                    toPrint = ""
                    while(dataSegment[int(Register['$a0'], 16) + i] != 0):
                        print(
                            int(dataSegment[int(Register['$a0'], 16) + i], 16), end=" ")
                        toPrint = toPrint + \
                            str(int(
                                dataSegment[int(Register['$a0'], 16) + i], 16))+" "
                        i += 1
                    #toPrint += "\n"
                    label = Label(console, text=toPrint).pack()
                    print()
                    # write try and catch for this...
            elif (int(Register['$v0'], 16) == 4):
                toPrint = ""
                values = list(MemAddres.values())
                position = values.index(int(Register['$a0'], 16))
                if position + 1 < len(values):
                    for i in range(0, values[position+1]-values[position]):
                        print(dataSegment[int(Register['$a0'], 16)+i], end="")
                        toPrint = toPrint + \
                            dataSegment[int(Register['$a0'], 16)+i]
                    #toPrint += "\n"
                    label = Label(console, text=toPrint).pack()
                    print()
                else:
                    i = 0
                    toPrint = ""
                    while (dataSegment[int(Register['$a0'], 16) + i] != 0):
                        print(
                            dataSegment[int(Register['$a0'], 16) + i], end="")
                        toPrint = toPrint + \
                            dataSegment[int(Register['$a0'], 16) + i]
                        i += 1
                    # toPrint+="\n"
                    label = Label(console, text=toPrint).pack()
                    print()
        else:
            print(int(Register["$a0"], 16))
            toPrint = str(int(Register["$a0"], 16))
            label = Label(console, text=toPrint).pack()


def change(register):
    changedRegisters[register] = 1


def restoreRegisters():
    keys = list(Register.keys())
    for j in range(0, 32):
        changedRegisters[keys[j]] = 0


def printRegisters():
    print("----------------------------------")
    print("|    REGISTERS    |     VALUE    |")
    keys = list(Register.keys())
    values = list(Register.values())
    print("|      $zero      |       0      |")
    for j in range(1, 32):
     #       print("|      ",keys[j],"      |       ",values[j][2:],"      |")
        #  print("|      ", keys[j], "      |       ", values[j], "      |")
        m = len(values[j])
        n = 16-m
        if n % 2 == 0:
            print("|      ", keys[j], "      |", end="")
            for i in range(0, n//2):
                print(" ", end="")
            print(values[j][2:], end="")
            for i in range(0, n//2):
                print(" ", end="")
            print("|", end="")
        else:
            print("|      ", keys[j], "      |", end="")
            for i in range(0, n // 2+1):
                print(" ", end="")
            print(values[j][2:], end="")
            for i in range(0, n // 2):
                print(" ", end="")
            print("|", end="")
        print()
    print("----------------------------------")


def printDataSegment():
    print("--------------------------------------------------")
    #print("------------------DATA SEGMENT--------------------")
    print("|                 DATA SEGMENT                   |")
    m = 0
    j = 0
    while 1:
        if m == 0:
            print("|", end="")
        if dataSegment[j] == 0:
            for k in range(m, 48):
                print(" ", end="")
            print("|")
            break
        else:
            if len(dataSegment[j])+m > 47:
                for k in range(m, 48):
                    print(" ", end="")
                print("|")
                m = 0
            else:
                print(dataSegment[j], end=" ")
                m = m + len(dataSegment[j]) + 1
                j += 1
        # print("\n",m,"\n")
    print("--------------------------------------------------")


class Table:

    def __init__(self, root):
        for i in range(1):
            """
           self.e = Entry(root, width=51, fg='black',
                       font=('Arial', 10, 'bold'))
           self.e.grid(row=i+1, column=0)
           self.e.configure(background="light blue")
           self.e.insert(END, " ")
           self.e = Entry(root, width=51, fg='black',
                          font=('Arial', 10, 'bold'))
           self.e.grid(row=i+1, column=1)
           self.e.configure(background="light blue")
           self.e.insert(END, " ")
           """
        self.e = Entry(root, width=45, fg='black',
                       font=('Arial', 10, 'bold'))
        self.e.grid(row=i+2, column=0)
        printPC = "PC = "+str(PC)
        self.e.insert(END, printPC)
        keys = list(Register.keys())
        values = list(Register.values())
        values1 = list(changedRegisters.values())
        # code for creating table
        for i in range(32):
            for j in range(2):
                if i == 0:
                    self.e = Entry(root, width=51, fg='black',
                                   font=('Arial', 10, 'bold'))
                    if j == 0:
                        self.e.grid(row=4, column=0)
                        self.e.insert(END, "REGISTERS")
                    if j == 1:
                        self.e.grid(row=4, column=1)
                        self.e.insert(END, "VALUES")

                self.e = Entry(root, width=51, fg='black',
                               font=('Arial', 10, 'bold'))
                if values1[i] == 1:
                    if j == 0:
                        self.e.grid(row=i+5, column=0)
                        self.e.configure(background="yellow")
                        self.e.insert(END, keys[i])
                    if j == 1:
                        self.e.grid(row=i + 5, column=1)
                        self.e.configure(background="yellow")
                        self.e.insert(END, values[i][2:])
                else:
                    if j == 0:
                        self.e.grid(row=i+5, column=0)
                        self.e.insert(END, keys[i])
                    if j == 1:
                        self.e.grid(row=i + 5, column=1)
                        self.e.insert(END, values[i][2:])
        restoreRegisters()


class Table1:
    def __init__(self, root):
        # """
        self.e = Entry(root, width=20, fg='black',
                       font=('Arial', 10, 'bold'))
        self.e.configure(background="light blue")
        self.e.grid(row=41, column=3)
        #self.e.insert(END, "")
        i = -1
        # """
        # """
        while 1:
            # for i in range(1000):
            if i == -1:
                self.e = Entry(root, width=25, fg='black',
                               font=('Arial', 10, 'bold'))
                self.e.grid(row=(i)+2, column=4)
                self.e.insert(END, "DATA SEGMENT ")
                i += 1
            elif dataSegment[i] != 0:
                # else:
                self.e = Entry(root, width=25, fg='black',
                               font=('Arial', 10, 'bold'))
                self.e.grid(row=(i % 37)+2, column=i//37+4)
                self.e.insert(END, dataSegment[i])
                i += 1
            else:
                break
            # """


"""
total_rows = len(Register)
total_columns = 2
root = Tk()
t = Table(root)
root.mainloop()
#print(dataSegment)
#print(MemAddres)
j=input("Enter 1 if you want to run the whole code at a time.\nEnter 2 if you want to print the code step by step.\n")
if j=='1':
"""


def press(num):
    global PC
    j = num
    if num == '1' and PC < len(Instructions):
        while 1:
            if PC == len(Instructions):
                break
            inst = Instructions[PC]
            # print(inst)
            ans = InstructionFetch(inst)

            # print(Register)
            # print()
            # for i in range(0, indx+10):
            #    print(dataSegment[i], end=" ")
            # print()
            # print(ans)
            if ans == (-2, -2):
             #   print("TOO LESS ARGUMENTS ERROR OCCURRED IN LINE : ",
             #         PC, " INSTRUCTION : \"", inst, "\"")
                root = Tk()
                root.geometry("500x300")
                root.title("ERROR")
                toPrint = ("TOO LESS ARGUMENTS ERROR OCCURRED IN LINE : " +
                           str(PC)+" INSTRUCTION : \"" + inst + "\"")
                label = Label(root, text=toPrint).pack()
                break
            elif ans == (-1, -1):
                root = Tk()
                root.geometry("500x300")
                root.title("ERROR")
                toPrint = ("SYNTAX ERROR OCCURRED IN LINE : " +
                           str(PC) + " INSTRUCTION : \"" + inst + "\"")
                label = Label(root, text=toPrint).pack()
                break
            elif ans == "BREAK":
                break
        t = Table(gui)
        t1 = Table1(gui)
        gui.mainloop()
        # printRegisters()
        # print(dataSegment)
        # print()
        # print()
        # printDataSegment()
        # print()
        # print()
    elif num == '2':
        if PC < len(Instructions):
            inst = Instructions[PC]
            # print(inst)
            ans = InstructionFetch(inst)

            # print(Register)
            # print()
            # for i in range(0, indx+10):
            #    print(dataSegment[i], end=" ")
            # print()
            if ans == (-2, -2):
                #   print("TOO LESS ARGUMENTS ERROR OCCURRED IN LINE : ",
                #        PC, " INSTRUCTION : \"", inst, "\"")
                root = Tk()
                root.geometry("500x300")
                root.title("ERROR")
                toPrint = ("TOO LESS ARGUMENTS ERROR OCCURRED IN LINE : " +
                           str(PC) + " INSTRUCTION : \"" + inst + "\"")
                label = Label(root, text=toPrint).pack()
            elif ans == (-1, -1):
                #   print("SYNTAX ERROR OCCURRED IN LINE : ",
                #         PC, " INSTRUCTION : \"", inst, "\"")
                root = Tk()
                root.geometry("500x300")
                root.title("ERROR")
                toPrint = ("SYNTAX ERROR OCCURRED IN LINE : " +
                           str(PC) + " INSTRUCTION : \"" + inst + "\"")
                label = Label(root, text=toPrint).pack()
            elif ans == "BREAK":
                PC = len(Instructions)
            # printRegisters()
            # print()
            # print()
            # printDataSegment()
            # print()
            # print()
            # print(dataSegment)
            t = Table(gui)
            t1 = Table1(gui)
            gui.mainloop()
            # printRegisters()
            if PC == len(Instructions):
                return


            # for (key, value) in Register.items():
            #     print(key, value)
# print(Register)
# print()
# for i in range(0, indx+10):
#    print(dataSegment[i], end=" ")
# if __name__ == "__main__":
gui = Tk()
gui.configure(background="light green")
gui.title("BYTIFY")
gui.geometry("1500x1300")
equation = StringVar()
onestep = Button(gui, text='ONE STEP EXECUTION', fg='white', bg='black',
                 command=lambda: press('1'), height=1, width=40)
onestep.grid(row=0, column=0)
stepbystep = Button(gui, text='STEP BY STEP EXECUTION', fg='white', bg='black',
                    command=lambda: press('2'), height=1, width=40)
stepbystep.grid(row=0, column=1)
t = Table(gui)
t1 = Table1(gui)
console = Tk()
#GUIFrame =Frame(console)
#GUIFrame.pack(expand=True, anchor=S)
#console.minsize(width=350, height=325)
#self.Button2 = Button(parent, text='exit', command= parent.quit)
#self.Button2.place(x=25, y=300)
# console.geometry("900x600")
console.title("Console")
gui.mainloop()
