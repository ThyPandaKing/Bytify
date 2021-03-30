import InputFile as InputFile
import memorySegment as FillMemory
from tkinter import *
from tkinter import font as tkFont
from tkinter import ttk

Addres = {}
MemAddres = {}
PC = 0
lastinstruction = 0
space=-1
no_stalls=0
totalStalls=0
info=[]

class stall:
    def __init__(self, ck, pc):
        self.clock = ck
        self.at_instruction = pc


# variables used for pipelining
instructions_till_now = 0
is_data_forwarding_allowed = True
my_clock = 0
previous_registers = 2*[4*[0]]
stalls_list = []
data_forwarding_list = []
last_pc_value = 0

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
Registers1=Register.copy()

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

dataSegment1=dataSegment.copy()

def checkForStalls(instType, arr):
    global previous_registers
    global my_clock
    global PC
    global last_pc_value
    global space
    global no_stalls
    global info
    global totalStalls
    no_stalls = 0
    # in arithemetic or bitwise instructions
    if instType=="":
        a = []
        a.append(space)
        a.append(no_stalls)
        a.append(0)
        info.append(a)
        return[-1,-1]
    st = 1
    if checkBranch(instType):
        st = 0
    if checkBranch(previous_registers[1][0]):
        if last_pc_value+1 != PC - 1:
            if is_data_forwarding_allowed == False:
                my_clock += 3
                no_stalls = 3
                totalStalls+=3
                a = []
                a.append(space)
                a.append(no_stalls)
                a.append(0)
                info.append(a)
                space = space + 3
                stalls_list.append(
                    f'{4} , Due to Branch Statement for PC = {PC - 1} , clock = {my_clock - 4}')
                return [-1, -1]
            my_clock += 1
            totalStalls += 1
            no_stalls=1
            a = []
            a.append(space)
            a.append(no_stalls)
            a.append(1)
            info.append(a)
            space = space+1
            stalls_list.append(
                f'{1} , Due to Wrong Branch Prediction for PC = {PC - 1} , clock = {my_clock - 1}')
            data_forwarding_list.append(
                f'ID-EXE → IF-ID for PC = {PC - 1}, clock = {my_clock - 1}')
            return [-1, -1]
        a = []
        a.append(space)
        a.append(no_stalls)
        a.append(0)
        info.append(a)
        return [-1, -1]

    if (instructions_till_now > 2 and (
            previous_registers[0][1] in arr[st:] or previous_registers[1][1] in arr[st:])) or (
            instructions_till_now == 2 and previous_registers[0][1] in arr[st:]):

        if is_data_forwarding_allowed == False:

            my_clock += 3
            no_stalls = 3
            totalStalls += 3
            a = []
            a.append(space)
            a.append(no_stalls)
            a.append(0)
            info.append(a)
            space = space + 3
            stalls_list.append(
                f'{4} , Due to Data Dependency for PC = {PC - 1} , clock = {my_clock - 4}')
            return [-1, -1]
        else:
            # no stalls, data will be forwarded
            if previous_registers[0][1] in arr[st:]:
                if instructions_till_now > 2 and previous_registers[1][1] in arr[st:] and previous_registers[0][1] != \
                        previous_registers[1][1]:
                    data_forwarding_list.append(
                        f'EXE-MEM → ID-EXE AND MEM-WB → ID-EXE for PC = {PC - 1} , clock = {my_clock}')
                    if 'lw' in previous_registers[1][0]:
                        # print("my_clock")
                        my_clock += 1
                        no_stalls = 1
                        totalStalls += 1
                        a = []
                        a.append(space)
                        a.append(no_stalls)
                        a.append(0)
                        info.append(a)
                        space = space + 1
                        stalls_list.append(
                            f'{1} , Due to Data Dependency on LW/SW for PC = {PC - 1}, clock = {my_clock - 1}')
                        data_forwarding_list[-1] = f'MEM-WB → ID-EXE for PC = {PC - 1}, clock = {my_clock}'
                        return [previous_registers[0][1], -1]
                    a = []
                    a.append(space)
                    a.append(no_stalls)
                    a.append(0)
                    info.append(a)
                    return [previous_registers[0][1], previous_registers[1][1]]
                if 'lw' in previous_registers[1][0]:
                    my_clock += 1
                    no_stalls = 1
                    totalStalls += 1
                    a = []
                    a.append(space)
                    a.append(no_stalls)
                    a.append(0)
                    info.append(a)
                    space = space + 1
                    stalls_list.append(
                        f'{1} , Due to Data Dependency on LW/SW for PC = {PC - 1}, clock = {my_clock - 1}')
                    data_forwarding_list.append(
                        f'MEM-WB → ID-EXE for PC = {PC - 1}, clock = {my_clock}')
                    return [previous_registers[0][1], -1, -1]
                data_forwarding_list.append(
                    f'EXE-MEM → ID-EXE for PC = {PC - 1}, clock = {my_clock}')
                a = []
                a.append(space)
                a.append(no_stalls)
                a.append(0)
                info.append(a)
                return [previous_registers[0][1], -1]
            else:
                a = []
                a.append(space)
                a.append(no_stalls)
                a.append(0)
                info.append(a)
                data_forwarding_list.append(
                    f'MEM-WB → ID-EXE for PC = {PC - 1}, clock = {my_clock}')
                return [-1, previous_registers[1][1]]

    else:
        a = []
        a.append(space)
        a.append(no_stalls)
        a.append(0)
        info.append(a)
        return [-1, -1]
    a = []
    a.append(space)
    a.append(no_stalls)
    a.append(0)
    info.append(a)
    return [-1, -1]


def checkBranch(toCheck):
    if 'beq' in toCheck or 'bne' in toCheck or 'j' in toCheck:
        return True
    else:
        return False


def checkArithmetic(toCheck):
    if toCheck == "add" or toCheck == "sub" or toCheck == "mul" or toCheck == "div" \
            or toCheck == 'addi' or toCheck == "and" or toCheck == "or" or toCheck == "sll" \
            or toCheck == "srl" or toCheck == "andi" or toCheck == "not" or toCheck == "move" \
            or toCheck == 'slt' or toCheck == "li":
        return True
    else:
        return False


def InstructionFetch(inst):
 #   inst = Instructions[PC]
    global PC
    global ctr_left1
    global text
    global lastinstruction
    global my_clock
    global previous_registers
    global instructions_till_now
    global space

    k = str(str(PC+1)+'.0')
    l = str(str(PC+1)+'.50')
    text.tag_add("start", k, l)
    text.tag_config("start", background="orange")
    lastinstruction = inst
    PC = PC + 1
    if inst == "":
        return

    # previous_registers[0] contains the last instruction and [1] contains last to last inst

    my_clock += 1
    space+=1
    instructions_till_now += 1
    previous_registers[1][0] = previous_registers[0][0]
    previous_registers[0][0] = inst

    return InstructionDecode(inst)


def InstructionDecode(inst):
    global PC
    global last_pc_value
    if inst == "syscall":
        checkForStalls("syscall",[])
        return execution("syscall", [], [-1, -1])
    idx = 0
    instType = ""
    t = inst.split()

    if t[0] == 'j':
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

    inst = inst.replace(",", " ")

    arr = inst.split()
    # arguments will depend upon instType
    # 1. add,sub,mul,div
    if instType == "add" or instType == "sub" or instType == "mul" or instType == "div" or instType == 'addi':
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
    elif instType == "and" or instType == "or" or instType == "sll" or instType == "srl" or instType == "andi" or instType == "not":
        if instType != "not":
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
        else:
            if len(arr) != 2:
                return -2, -2

            try:
                for reg in arr:
                    Register[reg]
            except:
                return -1, -1
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
    elif instType == "jr":
        arr = ["$ra"]
    elif instType == 'j':
        if len(arr) != 1:
            return -2, -2
        try:
            Addres[arr[0]]
        except:
            return -1, -1
    elif instType == 'li':
        if len(arr) != 2:
            return -2, -2
        try:
            int(arr[1])
            Register[arr[0]]
        except:
            return -1, -1
    elif instType == 'la' or instType == "move":
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
    elif instType == "slt":
        try:
            Register[arr[0]]
            Register[arr[1]]
            Register[arr[2]]
        except:
            return -1, -1
    else:
        print("ERROR: cmd not found")
        return -1, -1

    # checking for dependencies and making decision according to the situation.
    dtaFor = checkForStalls(instType, arr)
    last_pc_value = PC - 1

    temp = previous_registers[1].copy()
    temp[1] = previous_registers[0][1]
    previous_registers[1] = temp
    if not checkBranch(instType):
        previous_registers[0][1] = arr[0]
    else:
        previous_registers[0][1] = "$dummy"

    return execution(instType, arr, dtaFor)


def execution(instruct, reqRegisters, dtaFor):
    global PC
    global previous_registers
    global my_clock
    global data_forwarding_list

    temp = 0
    if instruct != "sw" and instruct != "syscall":
        change(reqRegisters[0])

    # need data from mem-wb stage
    if dtaFor[0] != -1 or dtaFor[1] != -1:
        if 'MEM-WB' in data_forwarding_list[-1] and not checkBranch(previous_registers[1][0]):

            if dtaFor[0] != -1:
                adi = previous_registers[0].copy()
                adi[2] = adi[3]
                previous_registers[0] = adi
            if dtaFor[1] != -1:
                sow = previous_registers[1].copy()
                sow[2] = sow[3]
                previous_registers[1] = sow

    if (instruct == "add"):
        if len(reqRegisters) == 3:
            if dtaFor[0] == -1 and dtaFor[1] == -1:
                temp = int(Register[reqRegisters[1]], 16) + \
                    int(Register[reqRegisters[2]], 16)
            elif dtaFor[0] != -1 and dtaFor[1] != -1:
                temp = previous_registers[0][2]+previous_registers[1][2]
            else:
                if dtaFor[0] != -1:
                    if dtaFor[0] == reqRegisters[1]:
                        temp = int(Register[reqRegisters[2]],
                                   16) + previous_registers[0][2]
                    else:
                        temp = int(Register[reqRegisters[1]],
                                   16) + previous_registers[0][2]
                else:
                    if dtaFor[1] == reqRegisters[1]:
                        temp = int(Register[reqRegisters[2]],
                                   16) + previous_registers[1][2]
                    else:
                        temp = int(Register[reqRegisters[1]],
                                   16) + previous_registers[1][2]

        else:
            temp = int(reqRegisters[1]) + \
                int(Register[reqRegisters[2]], 16)

    elif (instruct == "sub"):
        if dtaFor[0] == -1 and dtaFor[1] == -1:
            temp = int(Register[reqRegisters[1]], 16) - \
                int(Register[reqRegisters[2]], 16)
        elif dtaFor[0] != -1 and dtaFor[1] != -1:
            if dtaFor[0] == reqRegisters[1]:
                temp = previous_registers[0][2]-previous_registers[1][2]
            else:
                temp = previous_registers[1][2]-previous_registers[0][2]
        else:
            if dtaFor[0] != -1:
                if dtaFor[0] == reqRegisters[1]:
                    temp = previous_registers[0][2] - int(Register[reqRegisters[2]],
                                                          16)
                else:
                    temp = int(Register[reqRegisters[1]],
                               16) - previous_registers[0][2]
            else:
                if dtaFor[1] == reqRegisters[1]:
                    temp = previous_registers[1][2] - int(Register[reqRegisters[2]],
                                                          16)
                else:
                    temp = int(Register[reqRegisters[1]],
                               16) - previous_registers[1][2]

    elif (instruct == "mul"):
        if dtaFor[0] == -1 and dtaFor[1] == -1:
            temp = int(Register[reqRegisters[1]], 16) * \
                int(Register[reqRegisters[2]], 16)
        elif dtaFor[0] != -1 and dtaFor[1] != -1:
            if dtaFor[0] == reqRegisters[1]:
                temp = previous_registers[0][2]*previous_registers[1][2]
            else:
                temp = previous_registers[1][2]*previous_registers[0][2]
        else:
            if dtaFor[0] != -1:
                if dtaFor[0] == reqRegisters[1]:
                    temp = previous_registers[0][2] * int(Register[reqRegisters[2]],
                                                          16)
                else:
                    temp = int(Register[reqRegisters[1]],
                               16) * previous_registers[0][2]
            else:
                if dtaFor[1] == reqRegisters[1]:
                    temp = previous_registers[1][2] * int(Register[reqRegisters[2]],
                                                          16)
                else:
                    temp = int(Register[reqRegisters[1]],
                               16) * previous_registers[1][2]
    elif (instruct == "div"):
        if int(Register[reqRegisters[2]], 16) == 0:
            return "BREAK"
        if dtaFor[0] == -1 and dtaFor[1] == -1:
            temp = int(Register[reqRegisters[1]], 16) // \
                int(Register[reqRegisters[2]], 16)
        elif dtaFor[0] != -1 and dtaFor[1] != -1:
            if dtaFor[0] == reqRegisters[1]:
                temp = previous_registers[0][2] // previous_registers[1][2]
            else:
                temp = previous_registers[1][2] // previous_registers[0][2]
        else:
            if dtaFor[0] != -1:
                if dtaFor[0] == reqRegisters[1]:
                    temp = previous_registers[0][2] // int(Register[reqRegisters[2]],
                                                           16)
                else:
                    temp = int(Register[reqRegisters[1]],
                               16) // previous_registers[0][2]
            else:
                if dtaFor[1] == reqRegisters[1]:
                    temp = previous_registers[1][2] // int(Register[reqRegisters[2]],
                                                           16)
                else:
                    temp = int(Register[reqRegisters[1]],
                               16) // previous_registers[1][2]
    elif (instruct == "addi"):
        if reqRegisters[1] in dtaFor:
            if reqRegisters[1] == dtaFor[0]:
                temp = int(reqRegisters[2]) + \
                    previous_registers[0][2]
            else:
                temp = int(reqRegisters[2]) + previous_registers[1][2]
        else:
            temp = int(reqRegisters[2]) + int(Register[reqRegisters[1]], 16)

    elif (instruct == "and"):
        if dtaFor[0] == -1 and dtaFor[1] == -1:
            temp = int(Register[reqRegisters[1]], 16) & \
                int(Register[reqRegisters[2]], 16)
        elif dtaFor[0] != -1 and dtaFor[1] != -1:
            if dtaFor[0] == reqRegisters[1]:
                temp = previous_registers[0][2] & previous_registers[1][2]
            else:
                temp = previous_registers[1][2] & previous_registers[0][2]
        else:
            if dtaFor[0] != -1:
                if dtaFor[0] == reqRegisters[1]:
                    temp = previous_registers[0][2] & int(Register[reqRegisters[2]],
                                                          16)
                else:
                    temp = int(Register[reqRegisters[1]],
                               16) & previous_registers[0][2]
            else:
                if dtaFor[1] == reqRegisters[1]:
                    temp = previous_registers[1][2] & int(Register[reqRegisters[2]],
                                                          16)
                else:
                    temp = int(Register[reqRegisters[1]],
                               16) & previous_registers[1][2]
    elif (instruct == "or"):
        if dtaFor[0] == -1 and dtaFor[1] == -1:
            temp = int(Register[reqRegisters[1]], 16) | \
                int(Register[reqRegisters[2]], 16)
        elif dtaFor[0] != -1 and dtaFor[1] != -1:
            if dtaFor[0] == reqRegisters[1]:
                temp = previous_registers[0][2] | previous_registers[1][2]
            else:
                temp = previous_registers[1][2] | previous_registers[0][2]
        else:
            if dtaFor[0] != -1:
                if dtaFor[0] == reqRegisters[1]:
                    temp = previous_registers[0][2] | int(Register[reqRegisters[2]],
                                                          16)
                else:
                    temp = int(Register[reqRegisters[1]],
                               16) | previous_registers[0][2]
            else:
                if dtaFor[1] == reqRegisters[1]:
                    temp = previous_registers[1][2] | int(Register[reqRegisters[2]],
                                                          16)
                else:
                    temp = int(Register[reqRegisters[1]],
                               16) | previous_registers[1][2]

    elif (instruct == "not"):
        if reqRegisters[1] in dtaFor:
            if reqRegisters[1] == dtaFor[0]:
                temp = ~ previous_registers[0][2]
            else:
                temp = ~ previous_registers[1][2]
        else:
            temp = ~ int(Register[reqRegisters[1]], 16)

    elif (instruct == "bne"):
        if Register[reqRegisters[0]] != Register[reqRegisters[1]]:
            PC = Addres[reqRegisters[2]]
            return mem(instruct, reqRegisters, True)
        else:
            return mem(instruct, reqRegisters, False)
    elif (instruct == "beq"):
        if Register[reqRegisters[0]] == Register[reqRegisters[1]]:
            PC = Addres[reqRegisters[2]]

            return mem(instruct, reqRegisters, True)
        else:
            return mem(instruct, reqRegisters, False)
    elif (instruct == "j"):
        PC = Addres[reqRegisters[0]]
        return mem(instruct, reqRegisters, True)
    elif (instruct == "jr"):
        return "BREAK"
    elif (instruct == "li"):
        temp = int(reqRegisters[1])
    elif (instruct == "la"):
        temp = MemAddres[reqRegisters[1]]
    elif (instruct == "move"):
        temp = int(Register[reqRegisters[1]], 16)
    elif (instruct == "srl"):
        if reqRegisters[1] in dtaFor:
            if reqRegisters[1] == dtaFor[0]:
                temp = previous_registers[0][2] >> int(reqRegisters[2])
            else:
                temp = previous_registers[1][2] >> int(reqRegisters[2])
        else:
            temp = int(Register[reqRegisters[1]], 16) >> int(reqRegisters[2])

    elif (instruct == "sll"):
        if reqRegisters[1] in dtaFor:
            if reqRegisters[1] == dtaFor[0]:
                temp = previous_registers[0][2] << int(reqRegisters[2])
            else:
                temp = previous_registers[1][2] << int(reqRegisters[2])
        else:
            temp = int(Register[reqRegisters[1]], 16) << int(reqRegisters[2])

    elif (instruct == "andi"):
        if reqRegisters[1] in dtaFor:
            if reqRegisters[1] == dtaFor[0]:
                temp = previous_registers[0][2] & int(reqRegisters[2])
            else:
                temp = previous_registers[1][2] & int(reqRegisters[2])
        else:
            temp = int(Register[reqRegisters[1]], 16) & int(reqRegisters[2])

    elif instruct == "slt":

        temp = int(Register[reqRegisters[2]], 16) > int(
            Register[reqRegisters[1]], 16)
        #return mem(instruct, reqRegisters, temp)
    elif (instruct == "syscall"):
        return mem(instruct, reqRegisters, 0)

    tp = previous_registers[1].copy()
    tp[2] = previous_registers[0][2]

    previous_registers[1] = tp
    previous_registers[0][2] = temp

    # print(instructions_till_now)

    return mem(instruct, reqRegisters, temp)


def mem(instructType, reqRegisters, temp):

    global PC
    if(len(reqRegisters) == 4):
        if(reqRegisters[3] == "lw"):
            if(type(dataSegment[temp//4]) == int):
                Register[reqRegisters[0]] = hex(dataSegment[temp//4])
            else:
                if dataSegment[temp//4].find('x') != -1:
                    Register[reqRegisters[0]] = hex(
                        int(dataSegment[temp//4], 16))
                else:
                    Register[reqRegisters[0]] = hex(int(dataSegment[temp//4]))
        else:
            dataSegment[temp//4] = Register[reqRegisters[0]]

        tp = previous_registers[1].copy()
        tp[3] = previous_registers[0][3]

        previous_registers[1] = tp
        previous_registers[0][3] = int(Register[reqRegisters[0]], 16)

        print(previous_registers)
        print(stalls_list)
        print(data_forwarding_list)
        print(my_clock)
    else:
        tp = previous_registers[1].copy()
        tp[3] = previous_registers[0][3]

        previous_registers[1] = tp
        previous_registers[0][3] = temp

        print(previous_registers)
        print(stalls_list)
        print(data_forwarding_list)
        print(my_clock)
        return writeBack(instructType, reqRegisters, temp)


def writeBack(instructType, reqRegisters, temp):
    global PC
    if instructType == "add" or instructType == "sub" or instructType == "subi" or instructType == "mul" or instructType == "div" or instructType == "addi" or instructType == "and" or instructType == "or" or instructType == "not" or instructType == "li" or instructType == "la" or instructType == "move" or instructType == "srl" or instructType == "sll" or instructType == "andi" or instructType == "slt":
        Register[reqRegisters[0]] = hex(int(temp))
    if instructType == "syscall":
        lastInstruct = Instructions[PC-2]
        lastInstruct = list(lastInstruct.split())

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

                    label = Label(console, text=toPrint).pack()
                    print()
            elif (int(Register['$v0'], 16) == 4):
                toPrint = ""
                values = list(MemAddres.values())
                position = values.index(int(Register['$a0'], 16))
                if position + 1 < len(values):
                    for i in range(0, values[position+1]-values[position]):
                        print(dataSegment[int(Register['$a0'], 16)+i], end="")
                        toPrint = toPrint + \
                            dataSegment[int(Register['$a0'], 16)+i]

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


class Table:

    def __init__(self, root):
        # for i in range(1):
        i = 0
        l1 = Label(ctr_mid, text=" ", width=50, anchor='w',
                   bg="light green")  # added one Label
        l1.grid(row=2, column=0)
        self.e = Entry(root, width=45, fg='black',
                       font=('Arial', 10, 'bold'))
        self.e.grid(row=i+2, column=0)
        printPC = "PC = "+str(PC)
        self.e.insert(END, printPC)

        l1 = Label(ctr_mid, text=" ", width=50, anchor='w',
                   bg="light green")  # added one Label
        l1.grid(row=i+3, column=0)
        self.e = Entry(root, width=50, fg='black',
                       font=('Arial', 10, 'bold'))
        self.e.grid(row=i + 4, column=0)
        l1 = Label(ctr_mid, text=" ", width=50, anchor='w',
                   bg="light green")  # added one Label
        l1.grid(row=i + 5, column=0)
        printPC = "Executed Instruction = " + str(lastinstruction)
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
                        self.e.grid(row=6, column=0)
                        self.e.insert(END, "REGISTERS")
                    if j == 1:
                        self.e.grid(row=6, column=1)
                        self.e.insert(END, "VALUES")

                self.e = Entry(root, width=51, fg='black',
                               font=('Arial', 10, 'bold'))
                if values1[i] == 1:
                    if j == 0:
                        self.e.grid(row=i+7, column=0)
                        self.e.configure(background="yellow")
                        self.e.insert(END, keys[i])
                    if j == 1:
                        self.e.grid(row=i + 7, column=1)
                        self.e.configure(background="yellow")
                        self.e.insert(END, values[i][2:])
                else:
                    if j == 0:
                        self.e.grid(row=i+7, column=0)
                        self.e.insert(END, keys[i])
                    if j == 1:
                        self.e.grid(row=i + 7, column=1)
                        self.e.insert(END, values[i][2:])
        restoreRegisters()


class Table1:
    def __init__(self, root):

        i = 0
        ctr_right2 = Frame(ctr_right, bg='white', width=0)
        ctr_right2.grid(row=1, column=0, sticky="ns")
        l1 = Label(ctr_right1, text="", width=35,
                   anchor='w', bg='gray')  # added one Label
        l1.grid(row=0, column=0)
        self.e = Entry(ctr_right1, width=35, fg='black',
                       font=('Arial', 10, 'bold'))
        self.e.grid(row=1, column=0)
        self.e.insert(END, "DATA SEGMENT ")
        l1 = Label(ctr_right1, text="", width=35,
                   anchor='w', bg='gray')  # added one Label
        l1.grid(row=2, column=0)
        h = Scrollbar(ctr_right2, orient='horizontal')
        h.pack(side=BOTTOM, fill=X)
        v = Scrollbar(ctr_right2)
        v.pack(side=RIGHT, fill=Y)
        text1 = Text(ctr_right2, width=35, height=40, wrap=NONE,
                     xscrollcommand=h.set,
                     yscrollcommand=v.set)
        while(dataSegment[i] != 0):
            inst = dataSegment[i] + "\n"
            text1.insert(END, inst)
            i += 1
        # tag_delete(tagname)
        text1.pack(side=TOP)
        h.config(command=text1.xview)
        v.config(command=text1.yview)


class Table2:
    def __init__(self, root):
        global info
        if my_clock==0:
           cycle = "The number of cycles taken are: " + str(my_clock )
        else:
           cycle = "The number of cycles taken are: " + str(my_clock + 4)
        stall = "The number of stalls are: " + str(totalStalls)
        cycles1 = Label(root, text=cycle, width=30, fg='black', bg='pink', padx='10', pady='10', font=boldFont)
        cycles1.grid(row=0, column=0)
        stalls1 = Label(root, text=stall, width=30, fg='black', bg='light blue', padx='10', pady='10', font=boldFont)
        stalls1.grid(row=1, column=0)
        middle = Frame(root, bg='light green', width=16)
        middle.grid(row=2, column=0, sticky="ns")

        h1 = Scrollbar(middle, orient='horizontal')
        h1.pack(side=BOTTOM, fill=X)
        v1 = Scrollbar(middle)
        v1.pack(side=RIGHT, fill=Y)
        text1 = Text(middle, width=180, height=35, wrap=NONE,
                     xscrollcommand=h1.set,
                     yscrollcommand=v1.set)
        inst="     "
        if my_clock==0:
            text1.pack(side=TOP)
            h1.config(command=text1.xview)
            v1.config(command=text1.yview)
            return
        for j in range(1,my_clock+5):
          if (j>=0 and j<=9):
            inst=inst+"C"+str(j)+"     "
          if (j>=10 and j<=99):
            inst=inst+"C"+str(j)+"    "
          if (j>=100 and j<=999):
            inst=inst+"C"+str(j)+"   "
        inst = inst + "\n"
        text1.insert(END, inst)
        for j in range(0,len(info)):
          l=0
          inst=""
          if(j>=0 and j<=9):
            inst="I"+str(j)+"   "
            l=l+4
            for k in range(0,info[j][0]):
                inst=inst+"       "
                l=l+7
          elif (j >= 10 and j <= 99):
              inst = "I" + str(j) + "  "
              l=l+3
              for k in range(0, info[j][0]):
                  inst = inst + "       "
                  l=l+7
          elif (j >= 100 and j <= 999):
              inst = "I" + str(j) + " "
              l=l+2
              for k in range(0, info[j][0]):
                  inst = inst + "       "
                  l=l+7
          if info[j][2]==0:
             for k in range(1, 2):
                  if k == 1:
                      inst = inst + "IF     "
                      l=l+7
             m= str(str(j + 2) + "." + str(l))
             for k in range(0,info[j][1]):
                  inst = inst + "Stall  "
                  l=l+7
             for k in range(2,6):
                  if k == 2:
                      inst = inst + "ID/RF  "
                  if k == 3:
                      inst = inst + "EXE    "
                  if k == 4:
                      inst = inst + "MEM    "
                  if k == 5:
                      inst = inst + "WB     "
          else:
              m = str(str(j + 2) + "." + str(l))
              for k in range(0, info[j][1]):
                  inst = inst + "Stall  "
                  l = l + 7
              for k in range(1, 6):
                  if k == 1:
                      inst = inst + "IF     "
                  if k == 2:
                      inst = inst + "ID/RF  "
                  if k == 3:
                      inst = inst + "EXE    "
                  if k == 4:
                      inst = inst + "MEM    "
                  if k == 5:
                      inst = inst + "WB     "
          inst=inst+"\n"
          text1.insert(END, inst)
          n=str(str(j + 2) + "." + str(l))
          text1.tag_add("start", m, n)
          text1.tag_config("start", background="red")
        text1.pack(side=TOP)
        h1.config(command=text1.xview)
        v1.config(command=text1.yview)

class Table3:
    def __init__(self, root):
      if is_data_forwarding_allowed==False:
          cycle = "The availability of data forwarding is: FALSE"
          cycles1 = Label(root, text=cycle, fg='black', bg='pink', padx='10', pady='10', font=boldFont)
          cycles1.grid(row=0, column=0)
      else:
        cycle = "The availability of data forwarding is: TRUE"
        heading = "THE DATA FORWARDING INFORMATION IS AS FOLLOWS"
        cycles1 = Label(root, text=cycle, width=50, fg='black', bg='pink', padx='10', pady='10', font=boldFont)
        cycles1.grid(row=0, column=0)
        heading1 = Label(root, text=heading, width=50, fg='black', bg='light blue', padx='10', pady='10', font=boldFont)
        heading1.grid(row=1, column=0)
        middle = Frame(root, bg='light green', width=16)
        middle.grid(row=2, column=0, sticky="ns")

        h2 = Scrollbar(middle, orient='horizontal')
        h2.pack(side=BOTTOM, fill=X)
        v2 = Scrollbar(middle)
        v2.pack(side=RIGHT, fill=Y)
        text2 = Text(middle, width=180, height=35, wrap=NONE,
                     xscrollcommand=h2.set,
                     yscrollcommand=v2.set)
        for j in range(0, len(data_forwarding_list)):
            inst = str(j+1)+"     "
            inst=inst+data_forwarding_list[j]
            inst = inst + "\n"
            text2.insert(END, inst)
        text2.pack(side=TOP)
        h2.config(command=text2.xview)
        v2.config(command=text2.yview)


def press(num):
    global PC
    global my_clock
    j = num
    if num == '1' and PC < len(Instructions):
        while 1:
            if PC == len(Instructions):
                break
            inst = Instructions[PC]
            ans = InstructionFetch(inst)

            if ans == (-2, -2):
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
                # adding 4 extra for the end
                my_clock += 4
                break
        t = Table(ctr_mid)
        t1 = Table1(ctr_right2)
        t2 = Table2(stalls)
        t3 = Table3(data_forwarding)
        gui.mainloop()
    elif num == '2':
        if PC < len(Instructions):
            inst = Instructions[PC]
            for j in range(0, len(Instructions)):
                text.delete("1.0", "end")
            for j in range(0, len(Instructions)):
                inst1 = str(j) + ": " + Instructions[j] + "\n"
                text.insert(END, inst1)
            text.pack(side=TOP)
            ans = InstructionFetch(inst)
            if ans == (-2, -2):
                root = Tk()
                root.geometry("500x300")
                root.title("ERROR")
                toPrint = ("TOO LESS ARGUMENTS ERROR OCCURRED IN LINE : " +
                           str(PC) + " INSTRUCTION : \"" + inst + "\"")
                label = Label(root, text=toPrint).pack()
            elif ans == (-1, -1):
                root = Tk()
                root.geometry("500x300")
                root.title("ERROR")
                toPrint = ("SYNTAX ERROR OCCURRED IN LINE : " +
                           str(PC) + " INSTRUCTION : \"" + inst + "\"")
                label = Label(root, text=toPrint).pack()
            elif ans == "BREAK":
                PC = len(Instructions)

            t = Table(ctr_mid)
            t1 = Table1(ctr_right2)
            t2 = Table2(stalls)
            t3 = Table3(data_forwarding)
            gui.mainloop()
            if PC == len(Instructions):
                return



information=Tk()
information.title("Information about pipelining")
information.geometry("400x200")
def var_states():
   global information
   global is_data_forwarding_allowed
   var_1=var1.get()
   var_2=var2.get()
   if(var_1==1):
       is_data_forwarding_allowed=True
   if(var_2==1):
       is_data_forwarding_allowed=False
   information.destroy()
Label(information, text="Is data forwarding allowed?").grid(row=1, sticky=W)
var1 = IntVar()
Checkbutton(information, text="Yes", variable=var1).grid(row=2, sticky=W)
var2 = IntVar()
Checkbutton(information, text="No", variable=var2).grid(row=3, sticky=W)
Button(information, text='Submit', command=var_states).grid(row=4, sticky=W, pady=4)

windowWidth = information.winfo_reqwidth()
windowHeight = information.winfo_reqheight()
positionRight = int(information.winfo_screenwidth() / 2 - windowWidth / 2)
positionDown = int(information.winfo_screenheight() / 2 - windowHeight / 2)
information.geometry("+{}+{}".format(positionRight, positionDown))
information.mainloop()



gui = Tk()
gui.configure(background="light green")
gui.title("BYTIFY")
console = Tk()
windowWidth = console.winfo_reqwidth()
windowHeight = console.winfo_reqheight()
positionRight = int(console.winfo_screenwidth() / 2 - windowWidth / 2)
positionDown = int(console.winfo_screenheight() / 2 - windowHeight / 2)
console.geometry("+{}+{}".format(positionRight, positionDown))

equation = StringVar()
boldFont = tkFont.Font(size=10, weight="bold")

tabControl = ttk.Notebook(gui)
tab1 = ttk.Frame(tabControl)
center = Frame(tab1, bg='black', padx=3, pady=3)
gui.grid_rowconfigure(1, weight=1)
gui.grid_columnconfigure(0, weight=1)
stalls=Frame(tabControl)
data_forwarding=Frame(tabControl)

tabControl.add(tab1, text='        EXECUTION OF THE INSTRUCTIONS           ')
tabControl.add(stalls, text='        INFORMATION ABOUT STALLS AND NUMBER OF CYCLES     ')
tabControl.add(data_forwarding, text='        INFORMATION ABOUT DATA FORWARDING     ')
tabControl.pack(expand=1, fill="both")
t2=Table2(stalls)
t3=Table3(data_forwarding)

center.grid(row=1, sticky="nsew")
center.grid_rowconfigure(0, weight=1)
center.grid_columnconfigure(1, weight=1)

ctr_left = Frame(center, bg='light blue', width=50)
ctr_left1 = Frame(ctr_left, bg='light blue', width=50)

ctr_left.grid(row=0, column=0, sticky="ns")
ctr_left1.grid(row=1, column=0, sticky="wens")

l1 = Label(ctr_left, text='TEXT', width=30, bg='light pink',
           fg='black', font=boldFont)  # added one Label
l1.grid(row=0, column=0)


h = Scrollbar(ctr_left1, orient='horizontal')
h.pack(side=BOTTOM, fill=X)
v = Scrollbar(ctr_left1)
v.pack(side=RIGHT, fill=Y)
text = Text(ctr_left1, width=45, height=25, wrap=NONE,
            xscrollcommand=h.set,
            yscrollcommand=v.set)
for j in range(0, len(Instructions)):
    inst = str(j) + ": " + Instructions[j] + "\n"
    text.insert(END, inst)
text.pack(side=TOP)
h.config(command=text.xview)
v.config(command=text.yview)

ctr_mid = Frame(center, bg='light green', width=10)
ctr_right = Frame(center, bg='gray', width=50)
ctr_right1 = Frame(ctr_right, bg='gray', width=50)
ctr_right2 = Frame(ctr_right, bg='gray', width=50)
ctr_mid.grid(row=0, column=1, sticky="ns")
ctr_right.grid(row=0, column=2, sticky="ns")
ctr_right1.grid(row=0, column=0, sticky="ns")
ctr_right2.grid(row=1, column=0, sticky="ns")
t = Table(ctr_mid)
t1 = Table1(ctr_right2)

ctr_left2 = Frame(ctr_left, bg='light blue', width=50)
ctr_left2.grid(row=3, column=0, sticky="wens")


l1 = Label(ctr_left, text='CHOOSE THE OPTIONS FOR THE INSTRUCTION', width=40, bg='light pink',
           fg='black', font=boldFont)  # added one Label
l1.grid(row=2, column=0)

ttk.Label(ctr_left2, text = "Change type:",
          font = ("Times New Roman", 10)).grid(column = 0,
          row = 0, padx = 10, pady = 25)

name_var=StringVar()
value=StringVar()
pc_var=StringVar()
def submit():
    global info
    global Instructions
    global PC
    global Registers1
    global Register
    global dataSegment
    global dataSegment1
    global Addres
    global space
    global my_clock
    global data_forwarding_list
    global totalStalls

    name = name_var.get()
    value1=value.get()
    pcvalue=pc_var.get()
    e1.delete(0,'end')
    e2.delete(0, 'end')
    info=[]
    data_forwarding_list=[]
    space=0
    my_clock=0
    totalStalls=0
    t2=Table2(stalls)
    instructions.delete(0,'end')
    if(value1=="Delete instruction"):
       for j in range(0, len(Instructions)):
        text.delete("0.0","end")
       Instructions.pop(int(pcvalue))
       improveInstructions(Instructions)
       for j in range(0, len(Instructions)):
          inst = str(j) + ": " + Instructions[j] + "\n"
          text.insert(END, inst)
       keys = list(Addres.keys())
       for j in range(0,len(Addres)):
           if(Addres[keys[j]]>int(pcvalue)):
               Addres[keys[j]]=Addres[keys[j]]-1
       text.pack(side=TOP)
    elif (value1 == "Add instruction"):
        for j in range(0, len(Instructions)):
            text.delete("1.0", "end")
        Instructions.insert(int(pcvalue),name)
        for j in range(0, len(Instructions)):
            inst = str(j) + ": " + Instructions[j] + "\n"
            text.insert(END, inst)
        keys = list(Addres.keys())
        for j in range(0, len(Addres)):
            if (Addres[keys[j]] > int(pcvalue)):
                Addres[keys[j]] = Addres[keys[j]] + 1
        text.pack(side=TOP)
    elif (value1 == "Replace instruction"):
        for j in range(0, len(Instructions)):
            text.delete("1.0", "end")
        Instructions[int(pcvalue)]=name
        for j in range(0, len(Instructions)):
            inst = str(j) + ": " + Instructions[j] + "\n"
            text.insert(END, inst)
        text.pack(side=TOP)
    PC=0
    Register=Registers1
    dataSegment=dataSegment1
    t = Table(ctr_mid)
    t1 = Table1(ctr_right2)
    t2 = Table2(stalls)
    t3 = Table3(data_forwarding)
    gui.mainloop()

instructions = ttk.Combobox(ctr_left2, width=25, textvariable=value)
instructions['values'] = ["Replace instruction","Delete instruction","Add instruction"]
instructions.grid(column=1, row=0)
instructions.current()

ttk.Label(ctr_left2, text = "Enter the PC value:",
          font = ("Times New Roman", 10)).grid(column = 0,
          row = 2, padx = 10, pady = 10)
e2 = Entry(ctr_left2,textvariable = pc_var)
e2.grid(row=2, column=1)


ttk.Label(ctr_left2, text = "Enter the instruction:",
          font = ("Times New Roman", 10)).grid(column = 0,
          row = 3, padx = 10, pady = 10)
e1 = Entry(ctr_left2,textvariable = name_var)
e1.grid(row=3, column=1)
submitbutton=Button(ctr_left2,text = 'Submit', command = submit)

submitbutton.grid(row=4,column=1)

onestep = Button(ctr_mid, text='ONE STEP EXECUTION', fg='white', bg='black', font=boldFont,
                 command=lambda: press('1'), height=1, width=36)
onestep.grid(row=0, column=0)
stepbystep = Button(ctr_mid, text='STEP BY STEP EXECUTION', fg='white', bg='black', font=boldFont,
                    command=lambda: press('2'), height=1, width=36)
stepbystep.grid(row=0, column=1)

console.title("Console")

gui.mainloop()