import InputFile as InputFile
import math
import memorySegment as FillMemory
from tkinter import *
from tkinter import font as tkFont
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askopenfile
import copy

Addres = {}
MemAddres = {}
PC = 0

# variables for pipelining (GUI)
lastinstruction = 0
space = -1
no_stalls = 0
totalStalls = 0
totalStalls1 = 0
info = []
info1 = []
infostall = []
infostall1=[]
infostall2=[]
infostall3=[]
Instructions = []
Data = []

# variables for cache
cache_size_1 = 32  # bytes
cache_size_2 = 32  # bytes
block_size_1 = 8  # bytes
block_size_2 = 8  # bytes
associativity_1 = 2
associativity_2 = 2
set_number_1 = 2
set_number_2 = 2
main_memory_access_time = 1
second_cache_access_time = 1
number_of_hits_in_l1 = 0
number_of_hits_in_l2 = 0
total_access = 0

# stalls=10000*[10000*[0]]


# variables used for pipelining
instructions_till_now = 0
is_data_forwarding_allowed = True
my_clock = 0
previous_registers = 2*[4*[0]]
stalls_list = []
data_forwarding_list = []
last_pc_value = 0
lastpc = 0

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
    "$sp": '0x1000',         # Stack Pointer
    "$fp": '0x0',         # Frame Pointer
    "$ra": '0x0'          # Return Address
}
Registers1 = Register.copy()

changedRegisters = {
    "$zero": 0, "$at": 0, "$v0": 0, "$v1": 0, "$a0": 0, "$a1": 0, "$a2": 0, "$a3": 0, "$t0": 0, "$t1": 0, "$t2": 0, "$t3": 0, "$t4": 0,
    "$t5": 0, "$t6": 0, "$t7": 0, "$s0": 0, "$s1": 0, "$s2": 0, "$s3": 0, "$s4": 0, "$s5": 0, "$s6": 0, "$s7": 0, "$t8": 0, "$t9": 0, "$k0": 0, "$k1": 0,
    "$gp": 0, "$sp": 4096, "$fp": 0, "$ra": 0
}


class cache_block:

    def __init__(self, block_siz):
        self.clock = -1
        self.tag = -1
        self.blocks = []
        for i in range(block_siz):
            self.blocks.append(0)


class cache_set:
    def __init__(self, associativity_for_this, block_siz):
        self.block_size = block_siz
        self.set_arr = []
        for i in range(associativity_for_this):
            self.set_arr.append(cache_block(block_siz))


class real_cache:
    def __init__(self, set_number, associativity, block_size):
        self.set_number = set_number
        self.offset_bits = math.log2(block_size)
        self.index_bits = math.log2(set_number)
        self.tag_bits = 32 - self.index_bits - self.offset_bits
        self.associativity = associativity
        self.block_size = block_size
        self.cache = []
        for i in range(set_number):
            self.cache.append(cache_set(associativity, block_size))


# given address , and proper bit size of 3 parameters returns all the 3 parameters


def address_to_values(address, offset_bits, index_bits):
    index = 0
    offset = 0
    tag = 0
    temp = []
    ind = 0
    while ind < offset_bits:
        ind += 1
        temp.append(address % 2)
        address //= 2

    ind = 1
    for i in temp:
        offset += i*ind
        ind *= 2

    temp = []
    ind = 0
    while ind < index_bits:
        ind += 1
        temp.append(address % 2)
        address //= 2

    ind = 1
    for i in temp:
        index += i*ind
        ind *= 2

    tag = address

    return tag, index, offset


def set_finder(index, level):
    global cache_main_level_1
    global cache_main_level_2
    if level == 1:
        return cache_main_level_1.cache[index]
    else:
        return cache_main_level_2.cache[index]


def search_tag(tag, set_to_search: cache_set):

    for st in set_to_search.set_arr:
        if st.tag == tag:
            return st

    return -1


def find_offset(offset, block: cache_block):

    return block[offset]


def find_from_next(address, set_to_be_replaced: cache_set, from_main_mem: bool):
    global block_size_1
    global block_size_2
    global my_clock
    global no_stalls
    global stalls_list
    global main_memory_access_time
    global cache_main_level_1
    global cache_main_level_2
    global second_cache_access_time
    global totalStalls
    global space
    global infostall
    global lastpc
    global info
    global number_of_hits_in_l2

    if from_main_mem == True:
        # print(type(cache_block))
        new_block = cache_block(set_to_be_replaced.block_size)
        idx = 0

        while idx < block_size_1:
            new_block.blocks[idx] = dataSegment[address+idx]
            # print('data segment -> ', dataSegment[address + idx], address)
            idx += 1

        # as value is to be added in l2 (because we are checking in main mem) we will send it's parameters

        nw_tag, nw_index, nw_offset = address_to_values(
            address, cache_main_level_2.offset_bits, cache_main_level_2.index_bits)

        new_block.tag = nw_tag

        my_clock += main_memory_access_time-1
        new_block.clock = my_clock
        totalStalls += main_memory_access_time-1
        no_stalls += main_memory_access_time-1
        if len(infostall) == 0:
            b = []
            b.append(PC - 1)
            b.append(0)
            b.append(lastpc)
            b.append(main_memory_access_time - 1)
            infostall.append(b)
        else:
            if lastpc == infostall[len(infostall)-1][2]:
                infostall[len(infostall)-1][1] += main_memory_access_time-1
            else:
                b = []
                b.append(PC - 1)
                b.append(main_memory_access_time-1)
                b.append(lastpc)
                infostall.append(b)
        info[len(info)-1][4] += main_memory_access_time - 1
        stalls_list.append(
            f'{main_memory_access_time - 1} , Due to Cache Miss in Level 2 for PC = {PC - 1} , clock = {my_clock - main_memory_access_time}')
        # print('to be initiallized ', new_block.tag, nw_tag)
        LRU(set_to_be_replaced, new_block)
    else:
        is_value_in, nw_set, nw_block = search_address(
            address, cache_main_level_2, 2)

        my_clock += second_cache_access_time  - 1
        totalStalls = totalStalls + second_cache_access_time  - 1
        no_stalls += second_cache_access_time  - 1
        if len(infostall) == 0:
            b = []
            b.append(PC - 1)
            b.append(second_cache_access_time  - 1)
            b.append(lastpc)
            b.append(0)
            infostall.append(b)
        else:
            if lastpc == infostall[len(infostall)-1][2]:
                infostall[len(infostall)-1][1] += second_cache_access_time  - 1
            else:
                b = []
                b.append(PC - 1)
                b.append(second_cache_access_time  - 1)
                b.append(lastpc)
                b.append(0)
                infostall.append(b)
        info[len(info) - 1][4] += second_cache_access_time  - 1
        stalls_list.append(
            f'{ second_cache_access_time - 1} , Due to Cache Miss in Level 1 for PC = {PC - 1} , clock = {my_clock - main_memory_access_time}')

        if is_value_in:
            # hit in l2
            number_of_hits_in_l2 += 1

            nw_block.tag, nw_st, nw_offset = address_to_values(
                address, cache_main_level_1.offset_bits, cache_main_level_1.index_bits)
            nw_block.clock = my_clock
            # print('to be initiallized ', nw_block.tag)
            LRU(set_to_be_replaced, nw_block)
        else:
            find_from_next(address, nw_set, True)
            is_value_in, nw_set, nw_block = search_address(
                address, cache_main_level_2, 2)
            nw_block.tag, nw_st, nw_offset = address_to_values(
                address, cache_main_level_1.offset_bits, cache_main_level_1.index_bits)
            # print('to be initiallized ', nw_block.tag)
            nw_block.clock = my_clock
            LRU(set_to_be_replaced, nw_block)


# return true if address is in cache_level_2 also return the entire block , false otherwise

def search_address(address, cache_to_search, level):
    nw_tag, nw_index, nw_offset = address_to_values(
        address, cache_to_search.offset_bits, cache_to_search.index_bits)
    # print(nw_tag, nw_index,  nw_offset)
    nw_set = set_finder(nw_index, level)

    # for k in nw_set.set_arr:
    #     print('set -> ', k.blocks, k.tag)
    nw_blk = search_tag(nw_tag, nw_set)

    # if type(nw_blk) == cache_block:
    #     print(nw_blk.blocks, nw_blk.tag)

    if nw_blk == -1:
        return False, nw_set, -1
    else:
        return True, nw_set, nw_blk


# will first of all check whole set then find minimum in it, replace it
def LRU(set_to_check: cache_set, new_block: cache_block):
    global cache_main_level_1
    global cache_main_level_2
    temp_clock = 100000
    j = 0
    k = 0
    for st in set_to_check.set_arr:

        if st.clock < temp_clock:
            temp_clock = st.clock
            j = k
        k += 1

    set_to_check.set_arr[j] = new_block
    # print("val ", new_block.blocks, new_block.tag)
    # print("in new set index ",
    #       set_to_check.set_arr[j].blocks, set_to_check.set_arr[j].tag)

    # set_to_check.set_arr[j].tag = nw_tg
    # set_to_check.set_arr[j].clock = my_clock


# will update the main memory (check for input parameters to take)


def update_block_in_main_mem(address, value):
    global cache_main_level_1
    global cache_main_level_2
    search, set1, block1 = search_address(address, cache_main_level_1, 1)
    if(search == True):
        block1 = value
    search, set1, block1 = search_address(address, cache_main_level_2, 2)
    if (search == True):
        block1 = value


class stall:
    def __init__(self, ck, pc):
        self.clock = ck
        self.at_instruction = pc


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


def checkForStalls(instType, arr):
    global previous_registers
    global my_clock
    global PC
    global last_pc_value
    global space
    global no_stalls
    global info
    global totalStalls
    global lastinstruction
    no_stalls = 0
    # in arithemetic or bitwise instructions
    if instType == "":
        a = []
        a.append(space)
        a.append(no_stalls)
        a.append(0)
        a.append(lastpc)
        a.append(0)
        info.append(a)
        return[-1, -1]
    st = 1
    if checkBranch(instType):
        st = 0
    if checkBranch(previous_registers[1][0]):
        if last_pc_value+1 != PC - 1:
            if is_data_forwarding_allowed == False:
                my_clock += 3
                no_stalls = 3
                totalStalls += 3
                a = []
                a.append(space)
                a.append(no_stalls)
                a.append(0)
                a.append(lastpc)
                a.append(0)
                info.append(a)
                space = space + 3
                b = []
                b.append(PC-1)
                b.append(3)
                b.append(lastpc)
                b.append(0)
                infostall.append(b)
                stalls_list.append(
                    f'{3} , Due to Branch Statement for PC = {PC - 1} , clock = {my_clock - 4}')
                return [-1, -1]
            my_clock += 1
            totalStalls += 1
            no_stalls = 1
            a = []
            a.append(space)
            a.append(no_stalls)
            a.append(1)
            a.append(lastpc)
            a.append(0)
            info.append(a)
            space = space+1
            b = []
            b.append(PC - 1)
            b.append(1)
            b.append(lastpc)
            b.append(0)
            infostall.append(b)
            stalls_list.append(
                f'{1} , Due to Wrong Branch Prediction for PC = {PC - 1} , clock = {my_clock - 1}')
            data_forwarding_list.append(
                f'ID-EXE → IF-ID for PC = {PC - 1}, clock = {my_clock - 1}')
            return [-1, -1]
        a = []
        a.append(space)
        a.append(no_stalls)
        a.append(0)
        a.append(lastpc)
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
            a.append(lastpc)
            a.append(0)
            info.append(a)
            space = space + 3
            b = []
            b.append(PC - 1)
            b.append(3)
            b.append(lastpc)
            b.append(0)
            infostall.append(b)
            stalls_list.append(
                f'{3} , Due to Data Dependency for PC = {PC - 1} , clock = {my_clock - 4}')
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
                        a.append(lastpc)
                        a.append(0)
                        info.append(a)
                        space = space + 1
                        b = []
                        b.append(PC - 1)
                        b.append(1)
                        b.append(lastpc)
                        b.append(0)
                        infostall.append(b)
                        stalls_list.append(
                            f'{1} , Due to Data Dependency on LW/SW for PC = {PC - 1}, clock = {my_clock - 1}')
                        data_forwarding_list[-1] = f'MEM-WB → ID-EXE for PC = {PC - 1}, clock = {my_clock}'
                        return [previous_registers[0][1], -1]
                    a = []
                    a.append(space)
                    a.append(no_stalls)
                    a.append(0)
                    a.append(lastpc)
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
                    a.append(lastpc)
                    a.append(0)
                    info.append(a)
                    space = space + 1
                    b = []
                    b.append(PC - 1)
                    b.append(1)
                    b.append(lastpc)
                    b.append(0)
                    infostall.append(b)
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
                a.append(lastpc)
                a.append(0)
                info.append(a)
                return [previous_registers[0][1], -1]
            else:
                a = []
                a.append(space)
                a.append(no_stalls)
                a.append(0)
                a.append(lastpc)
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
        a.append(lastpc)
        a.append(0)
        info.append(a)
        return [-1, -1]
    a = []
    a.append(space)
    a.append(no_stalls)
    a.append(0)
    a.append(lastpc)
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
    global lastpc

    lastpc = PC
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
    space += 1
    instructions_till_now += 1
    previous_registers[1][0] = previous_registers[0][0]
    previous_registers[0][0] = inst

    return InstructionDecode(inst)


def InstructionDecode(inst):
    global PC
    global last_pc_value
    if inst == "syscall":
        checkForStalls("syscall", [])
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
        # return mem(instruct, reqRegisters, temp)
    elif (instruct == "syscall"):
        return mem(instruct, reqRegisters, 0)

    tp = previous_registers[1].copy()
    tp[2] = previous_registers[0][2]

    previous_registers[1] = tp
    previous_registers[0][2] = temp

    # print(instructions_till_now)

    return mem(instruct, reqRegisters, temp)


def print_caches():
    global cache_main_level_1
    global cache_main_level_2

    print('level 1 cache -> ')
    for k in cache_main_level_1.cache:
        for e in k.set_arr:
            for b in e.blocks:
                print(b, end=" ")
            print()
    print('level 2 cache -> ')
    for k in cache_main_level_2.cache:
        for e in k.set_arr:
            for b in e.blocks:
                print(b, end=" ")
            print()


def mem(instructType, reqRegisters, temp):
    # print(set_number_1, set_number_2)
    global PC
    global total_access
    global number_of_hits_in_l1

    if(len(reqRegisters) == 4):

        if(reqRegisters[3] == "lw"):
            # total access increased
            total_access += 1

            is_value_in, nw_set, nw_block = search_address(
                temp//4, cache_main_level_1, 1)
            if is_value_in == True:
                # hit in l1

                number_of_hits_in_l1 += 1

                # print('from first as value is in cache')
                # print(is_value_in, nw_set.set_arr, nw_block.blocks)
                nw_tag, nw_index, nw_offset = address_to_values(
                    temp//4, cache_main_level_1.offset_bits, cache_main_level_1.index_bits)
                Register[reqRegisters[0]] = nw_block.blocks[nw_offset]
                # print(nw_tag, nw_index, nw_offset)
            else:
                # print('in second')
                find_from_next(temp//4, nw_set, False)
                nw_tag, nw_index, nw_offset = address_to_values(
                    temp//4, cache_main_level_1.offset_bits, cache_main_level_1.index_bits)

                # print(nw_tag, nw_index, nw_offset)

                is_value_in, nw_set, nw_block = search_address(
                    temp//4, cache_main_level_1, 1)
                if nw_block != -1:
                    Register[reqRegisters[0]] = nw_block.blocks[nw_offset]
            if (type(dataSegment[temp // 4]) == int):
                Register[reqRegisters[0]] = hex(dataSegment[temp // 4])
            else:
                if dataSegment[temp // 4].find('x') != -1:
                    Register[reqRegisters[0]] = hex(
                        int(dataSegment[temp // 4], 16))
                else:
                    Register[reqRegisters[0]] = hex(
                        int(dataSegment[temp // 4]))

        else:
            dataSegment[temp//4] = Register[reqRegisters[0]]
            update_block_in_main_mem(temp//4, Register[reqRegisters[0]])

        tp = previous_registers[1].copy()
        tp[3] = previous_registers[0][3]
        previous_registers[1] = tp
        previous_registers[0][3] = int(Register[reqRegisters[0]], 16)

    else:
        tp = previous_registers[1].copy()
        tp[3] = previous_registers[0][3]

        previous_registers[1] = tp
        previous_registers[0][3] = temp

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
        text1.config(state=DISABLED)
        h.config(command=text1.xview)
        v.config(command=text1.yview)


class Table2:
    def __init__(self, root):
        global totalStalls
        global infostall
        global infostall1
        global totalStalls1
        global infostall2
        global infostall3
        info1=[]
        totalStalls1=totalStalls
        infostall2=copy.deepcopy(infostall1)
        infostall3 = copy.deepcopy(infostall)
        info1=copy.deepcopy(info)
        if my_clock == 0:
            cycle = "The number of cycles taken are: " + str(my_clock)
            ipc = "Instructions per cycle(IPC): 0"
        else:
            cycle = "The number of cycles taken are: " + str(my_clock + 4)
            ip = len(info)/(my_clock+4)
            ipc = "Instructions per cycle(IPC): "+str(ip)
        stall = "The number of stalls are: " + str(totalStalls)
        cycles1 = Label(root, text=cycle, width=80, fg='black',
                        bg='pink', padx='10', pady='10', font=boldFont)
        cycles1.grid(row=0, column=0)
        ipc1 = Label(root, text=ipc, width=80, fg='black',
                     bg='light blue', padx='10', pady='10', font=boldFont)
        ipc1.grid(row=1, column=0)
        stalls1 = Label(root, text=stall, width=80, fg='black',
                        bg='pink', padx='10', pady='10', font=boldFont)
        stalls1.grid(row=2, column=0)
        middle = Frame(root, bg='light green', width=16)
        middle.grid(row=3, column=0, sticky="ns")

        h1 = Scrollbar(middle, orient='horizontal')
        h1.pack(side=BOTTOM, fill=X)
        v1 = Scrollbar(middle)
        v1.pack(side=RIGHT, fill=Y)
        text1 = Text(middle, width=180, height=35, wrap=NONE,
                     xscrollcommand=h1.set,
                     yscrollcommand=v1.set)
        inst = "     "
        if my_clock == 0:
            text1.pack(side=TOP)
            h1.config(command=text1.xview)
            v1.config(command=text1.yview)
            return
        o = 0
        for j in range(1, my_clock+5):
            if (j >= 0 and j <= 9):
                inst = inst+"C"+str(j)+"     "
                o = o+7
            if (j >= 10 and j <= 99):
                inst = inst+"C"+str(j)+"    "
                o = o+7
            if (j >= 100 and j <= 999):
                inst = inst+"C"+str(j)+"   "
                o = o+7
        inst = inst + "\n"
        text1.insert(END, inst)

        def show_info(text):
            label.configure(text=text)

        label = Label(middle)
        label.pack(side="top", fill="x")
        for j in range(0, len(info)):
            l = 0
            m1 = str(str(j + 2) + "." + str(l))
            l1 = str(str(j + 2) + "." + str(l))
            m2 = str(str(j + 2) + "." + str(l))
            l2 = str(str(j + 2) + "." + str(l))
            m3 = str(str(j + 2) + "." + str(l))
            l3 = str(str(j + 2) + "." + str(l))
            m4 = str(str(j + 2) + "." + str(l))
            l4 = str(str(j + 2) + "." + str(l))
            m5 = str(str(j + 2) + "." + str(l))
            l5 = str(str(j + 2) + "." + str(l))
            m6 = str(str(j + 2) + "." + str(l))
            l6 = str(str(j + 2) + "." + str(l))
            m7 = str(str(j + 2) + "." + str(l))
            l7 = str(str(j + 2) + "." + str(l))
            m8 = str(str(j + 2) + "." + str(l))
            l8 = str(str(j + 2) + "." + str(l))
            m9 = str(str(j + 2) + "." + str(l))
            l9 = str(str(j + 2) + "." + str(l))
            m10 = str(str(j + 2) + "." + str(l))
            l10 = str(str(j + 2) + "." + str(l))
            m11 = str(str(j + 2) + "." + str(l))
            l11 = str(str(j + 2) + "." + str(l))
            m12 = str(str(j + 2) + "." + str(l))
            l12 = str(str(j + 2) + "." + str(l))
            m13 = str(str(j + 2) + "." + str(l))
            l13 = str(str(j + 2) + "." + str(l))
            num = 0
            om = 0
            inst = ""
            if(j >= 0 and j <= 9):
                inst = "I"+str(j)+"   "
                l = l+4
            elif (j >= 10 and j <= 99):
                inst = "I" + str(j) + "  "
                l = l+4
            elif (j >= 100 and j <= 999):
                inst = "I" + str(j) + " "
                l = l+4
            if j>=3:
                if info1[j-3][4]!=0:
                  for k in range(0, info1[j][0]-info1[j-3][4]):
                      inst = inst + "       "
                      l = l + 7
                      num = num + 1
                  m1 = str(str(j + 2) + "." + str(l))
                  for k in range(0, info1[j - 3][4]):
                      inst = inst + "Stall  "
                      l = l + 7
                      totalStalls+=1
                      om=om+1
                  l1= str(str(j + 2) + "." + str(l))
                else:
                    for k in range(0, info1[j][0]):
                        inst = inst + "       "
                        l = l + 7
                        num = num + 1
            else:
                for k in range(0,info1[j][0]):
                        inst = inst + "       "
                        l = l+7
                        num = num + 1
            if info1[j][2] == 0:
                if j>=1:
                    if info1[j-1][1]!=0:
                        if j >= 2:
                            if info1[j - 2][4] != 0:
                                m2 = str(str(j + 2) + "." + str(l))
                                for mm in range(0, info1[j - 2][4]):
                                    inst = inst + "Stall  "
                                    totalStalls += 1
                                    om = om+1
                                    l = l + 7
                                l2 = str(str(j + 2) + "." + str(l))
                                for oo in range(j + 1, len(info1)):
                                    info1[oo][0] += info1[j - 2][4]
                                for k in range(1, 2):
                                    if k == 1:
                                        inst = inst + "IF     "
                                        l = l+7
                                        num = num + 1
                                m3 = str(str(j + 2) + "." + str(l))
                                for k in range(0, info1[j][1]):
                                    inst = inst + "Stall  "
                                    l = l + 7
                                l3 = str(str(j + 2) + "." + str(l))
                            else:
                                for k in range(1, 2):
                                    if k == 1:
                                        inst = inst + "IF     "
                                        l = l + 7
                                        num = num + 1
                                m4 = str(str(j + 2) + "." + str(l))
                                if j >= 2:
                                    if info1[j - 2][4] != 0:
                                        for mm in range(0, info1[j - 2][4]):
                                            inst = inst + "Stall  "
                                            totalStalls += 1
                                            om=om+1
                                            l=l+7
                                        for oo in range(j + 1, len(info1)):
                                            info1[oo][0] += info1[j - 2][4]
                                for k in range(0, info1[j][1]):
                                    inst = inst + "Stall  "
                                    l = l + 7
                                l4 = str(str(j + 2) + "." + str(l))
                    else:
                        for k in range(1, 2):
                            if k == 1:
                                inst = inst + "IF     "
                                l = l + 7
                                num = num + 1
                        m5 = str(str(j + 2) + "." + str(l))
                        if j >= 2:
                            if info1[j - 2][4] != 0:
                                for mm in range(0, info1[j - 2][4]):
                                    inst = inst + "Stall  "
                                    l = l+7
                                    totalStalls += 1
                                    om=om+1
                                for oo in range(j + 1, len(info1)):
                                    info1[oo][0] += info[j - 2][4]
                        for k in range(0, info1[j][1]):
                            inst = inst + "Stall  "
                            l = l + 7
                        l5 = str(str(j + 2) + "." + str(l))
                # """
                else:
                    for k in range(1, 2):
                        if k == 1:
                            inst = inst + "IF     "
                            l = l+7
                            num = num + 1
                    m6 = str(str(j + 2) + "." + str(l))
                    if j>=2:
                        if info1[j - 2][4] != 0 :
                            for mm in range(0, info1[j - 2][4]):
                                inst = inst + "Stall  "
                                totalStalls += 1
                                l=l+7
                                om=om+1
                            for oo in range(j+1,len(info1)):
                                info1[oo][0]+=info1[j - 2][4]
                    for k in range(0, info1[j][1]):
                        inst = inst + "Stall  "
                        l = l+7
                    l6 = str(str(j + 2) + "." + str(l))
                # """
                n = str(str(j + 2) + "." + str(l))
                for k in range(2, 6):
                    if info1[j][1]!=0 and k==2 and j>=1:
                        m7 = str(str(j + 2) + "." + str(l))
                        for mm in range(0, info1[j-1][4]):
                            inst = inst +"Stall  "
                            totalStalls += 1
                            om = om+1
                            l = l+7
                        l7 = str(str(j + 2) + "." + str(l))
                    if k == 2:
                        inst = inst + "ID/RF  "
                        l = l+7
                    if k == 3:
                        inst = inst + "EXE    "
                        l = l+7
                    if k == 4:
                        inst = inst + "MEM    "
                        l = l+7
                    if k == 5:
                        inst = inst + "WB     "
                        l = l+7
                    if k == 3:
                        m8 = str(str(j + 2) + "." + str(l))
                        for mm in range(0, info1[j][4]):
                            inst = inst +"Stall  "
                            l=l+7
                        l8 = str(str(j + 2) + "." + str(l))
                    if j>=1:
                        if info1[j-1][4]!=0 and k==2 and info1[j][1]==0:
                            m9 = str(str(j + 2) + "." + str(l))
                            for mm in range(0, info1[j-1][4]):
                                inst = inst +"Stall  "
                                totalStalls += 1
                                om = om+1
                                l = l+7
                            l9 = str(str(j + 2) + "." + str(l))

            else:
                num = num + 1
                m10 = str(str(j + 2) + "." + str(l))
                for k in range(0, info1[j][1]):
                    inst = inst + "Stall  "
                    l = l + 7
                l10 = str(str(j + 2) + "." + str(l))
                n = str(str(j + 2) + "." + str(l))
                for k in range(1, 6):
                    if k == 1:
                        inst = inst + "IF     "
                        l = l+7
                    if k == 2:
                        inst = inst + "ID/RF  "
                        l = l+7
                    if k == 3:
                        inst = inst + "EXE    "
                        l = l+7
                    if k == 4:
                        inst = inst + "MEM    "
                        l = l+7
                    if k == 5:
                        inst = inst + "WB     "
                        l = l+7
                    if k == 3:
                        m11 = str(str(j + 2) + "." + str(l))
                        for mm in range(0, info1[j][4]):
                            inst = inst + "Stall  "
                            l = l+7
                        l11 = str(str(j + 2) + "." + str(l))
                    if j >= 1:
                        m12 = str(str(j + 2) + "." + str(l))
                        if info1[j-1][4]!=0 and k==2:
                            for mm in range(0, info1[j-1][4]):
                                inst = inst +"Stall  "
                                totalStalls += 1
                                om = om+1
                                l = l+7
                        l12 = str(str(j + 2) + "." + str(l))
                    if j>=2:
                        if info1[j-2][4]!=0 and k==1:
                            m13 = str(str(j + 2) + "." + str(l))
                            for mm in range(0, info1[j-2][4]):
                                inst = inst +"Stall  "
                                totalStalls += 1
                                om = om+1
                                l = l+7
                            l13 = str(str(j + 2) + "." + str(l))
            inst = inst+"\n"
            tag = inst
            text = inst
            flag = 0
            for k in range(0, len(infostall)):
                if infostall[k][0] == j:
                    infostall[k][1] += om
                    flag = 1
                    break
            if flag == 0 and om != 0:
                b = []
                b.append(info1[j][3])
                b.append(om)
                infostall1.append(b)
            text1.insert("end", text, (tag,))
            temp = "INSTRUCTION NUMBER: "+str(j)+"       INSTRUCTION: "+str(
                Instructions[info1[j][3]])+"          STARTING CLOCK CYCLE:  "+str(num)
            text1.tag_bind(tag, "<Enter>", lambda event1,
                           temp=temp: show_info(temp))
            text1.tag_bind(tag, "<Leave>", lambda event1,
                           temp=temp: show_info(""))
            text1.tag_add("start", m1, l1)
            text1.tag_add("start", m2, l2)
            text1.tag_add("start", m3, l3)
            text1.tag_add("start", m4, l4)
            text1.tag_add("start", m5, l5)
            text1.tag_add("start", m6, l6)
            text1.tag_add("start", m7, l7)
            text1.tag_add("start", m8, l8)
            text1.tag_add("start", m9, l9)
            text1.tag_add("start", m10, l10)
            text1.tag_add("start", m11, l11)
            text1.tag_add("start", m12, l12)
            text1.tag_add("start", m13, l13)
            text1.tag_config("start", background="red")
            r = str(j+2)+".0"
            s = str(j+2)+".4"
            text1.tag_add("inst", r, s)
            text1.tag_config("inst", background="light green")
        p = "1.0"
        q = "1." + str(o+2)
        text1.tag_add("cycle", p, q)
        text1.tag_config("cycle", background="light green")
        text1.pack(side=TOP)
        h1.config(command=text1.xview)
        v1.config(command=text1.yview)
        text1.config(state=DISABLED)
        stall = "The number of stalls are: " + str(totalStalls)
        stalls1 = Label(root, text=stall, width=80, fg='black',
                        bg='pink', padx='10', pady='10', font=boldFont)
        stalls1.grid(row=2, column=0)


class Table3:
    def __init__(self, root):
        cycle = "The number of stalls are: "+str(totalStalls)
        heading = "THE STALLS OCCURED AT THE FOLLOWING INSTRUCTIONS"
        cycles1 = Label(root, text=cycle, width=50, fg='black',
                        bg='pink', padx='10', pady='10', font=boldFont)
        cycles1.grid(row=0, column=0)
        heading1 = Label(root, text=heading, width=50, fg='black', bg='light blue', padx='10', pady='10',
                         font=boldFont)
        heading1.grid(row=1, column=0)
        middle1 = Frame(root, bg='light green', width=16)
        middle1.grid(row=2, column=0, sticky="ns")

        h3 = Scrollbar(middle1, orient='horizontal')
        h3.pack(side=BOTTOM, fill=X)
        v3 = Scrollbar(middle1)
        v3.pack(side=RIGHT, fill=Y)
        text3 = Text(middle1, width=90, height=35, wrap=NONE,
                     xscrollcommand=h3.set,
                     yscrollcommand=v3.set)
        for j in range(0, len(infostall)):
            inst = str(j + 1) + "     "
            inst = inst + str(infostall[j][1])+" stall(s) - " + \
                str(Instructions[infostall[j][0]])
            inst = inst + "\n"
            text3.insert(END, inst)
        for j in range(0, len(infostall1)):
            inst = str(j + 1) + "     "
            inst = inst + str(infostall1[j][1])+" stall(s) - " + \
                str(Instructions[infostall1[j][0]])
            inst = inst + "\n"
            text3.insert(END, inst)
        text3.pack(side=TOP)
        h3.config(command=text3.xview)
        v3.config(command=text3.yview)
        if is_data_forwarding_allowed == False:
            cycle = "The availability of data forwarding is: FALSE"
            cycles1 = Label(root, text=cycle, fg='black',
                            bg='pink', padx='10', pady='10', font=boldFont)
            cycles1.grid(row=0, column=1)
        else:
            cycle = "The availability of data forwarding is: TRUE"
            heading = "THE DATA FORWARDING INFORMATION IS AS FOLLOWS"
            cycles1 = Label(root, text=cycle, width=50, fg='black',
                            bg='pink', padx='10', pady='10', font=boldFont)
            cycles1.grid(row=0, column=1)
            heading1 = Label(root, text=heading, width=50, fg='black', bg='light blue', padx='10', pady='10',
                             font=boldFont)
            heading1.grid(row=1, column=1)
        middle = Frame(root, bg='light green', width=16)
        middle.grid(row=2, column=1, sticky="ns")

        h2 = Scrollbar(middle, orient='horizontal')
        h2.pack(side=BOTTOM, fill=X)
        v2 = Scrollbar(middle)
        v2.pack(side=RIGHT, fill=Y)
        text2 = Text(middle, width=90, height=35, wrap=NONE,
                     xscrollcommand=h2.set,
                     yscrollcommand=v2.set)
        for j in range(0, len(data_forwarding_list)):
            inst = str(j + 1) + "     "
            inst = inst + data_forwarding_list[j]
            inst = inst + "\n"
            text2.insert(END, inst)
        text2.pack(side=TOP)
        text2.config(state=DISABLED)
        text3.config(state=DISABLED)
        h2.config(command=text2.xview)
        v2.config(command=text2.yview)

class Table4:
    def __init__(self, root):
        if total_access==0:
            cycle = "The hit rate of level 1 is: " + str(0)
        else:
            cycle = "The hit rate of level 1 is: "+str(number_of_hits_in_l1/total_access)
        if total_access==0:
              heading = "The hit rate of level 2 is: " + str(0)
        else:
            heading = "The hit rate of level 2 is: "+str(number_of_hits_in_l2/total_access)
        cycles1 = Label(root, text=cycle, width=50, fg='black',
                        bg='pink', padx='10', pady='10', font=boldFont)
        cycles1.grid(row=0, column=0)
        heading1 = Label(root, text=heading, width=50, fg='black', bg='light blue', padx='10', pady='10',
                         font=boldFont)
        heading1.grid(row=1, column=0)
        cycle = "Cache size of level 1 is: " + str(cache_size_1)+"       Block size of level 1 is: "\
                + str(block_size_1)+"     Associativity of level 1 is:"+str(associativity_1)\
                +"     Access Latency of level 1 is:"+str(second_cache_access_time)
        heading ="Cache size of level 2 is: " + str(cache_size_2)+"       Block size of level 2 is: "\
                + str(block_size_2)+"     Associativity of level 2 is:"+str(associativity_2)\
                +"     Access Latency of level 2 is:"+str(main_memory_access_time)
        cycles1 = Label(root, text=cycle, width=100, fg='black',
                        bg='pink', padx='10', pady='10', font=boldFont)
        cycles1.grid(row=2, column=0)
        heading1 = Label(root, text=heading, width=100, fg='black', bg='light blue', padx='10', pady='10',
                         font=boldFont)
        heading1.grid(row=3, column=0)
        middle1 = Frame(root, bg='light green', width=16)
        middle1.grid(row=4, column=0, sticky="ns")

        h3 = Scrollbar(middle1, orient='horizontal')
        h3.pack(side=BOTTOM, fill=X)
        v3 = Scrollbar(middle1)
        v3.pack(side=RIGHT, fill=Y)
        text3 = Text(middle1, width=180, height=30, wrap=NONE,
                     xscrollcommand=h3.set,
                     yscrollcommand=v3.set)
        inst = ""
        inst = inst + "                                                  CACHE 1  "
        inst = inst + "\n\n\n"
        text3.insert(END, inst)
        l=associativity_1
        l=l*10
        inst = ""
        for j in range (0,set_number_1):
            if j>=0 and j<=9:
                m=6
            elif j>=10 and j<=99:
                m=7
            else:
                m=8
            n=l-m
            if n%2==0:
                for k in range(0,n//2):
                    inst=inst+" "
                inst=inst+"SET- "+str(j)
                for k in range(0,n//2):
                    inst=inst+" "
            else:
                for k in range(0,n//2-1):
                    inst=inst+" "
                inst=inst+"SET- "+str(j)
                for k in range(0,n//2+1):
                    inst=inst+" "
        text3.insert(END, inst)
        text3.insert(END, "\n\n")
        inst=""
        for j in range(0,set_number_1):
            for k in range(0,associativity_1):
                inst=inst+"BLOCK- "+str(k)
                inst1="BLOCK- "+str(k)
                for o in range(0,10-len(inst1)):
                    inst=inst+" "
        text3.insert(END, inst)
        text3.insert(END, "\n\n")
        inst=""
        for j in range(0,set_number_1):
          for n in range(0,associativity_1):
            inst= inst+str(cache_main_level_1.cache[j].set_arr[n].tag)
            inst1=str(cache_main_level_1.cache[j].set_arr[n].tag)
            for k in range(0,10-len(inst1)):
                inst=inst+" "
        text3.insert(END, inst)
        text3.insert(END, "\n\n")
        for l in range(0, block_size_1):
            inst=""
            for j in range(0,set_number_1):
              for n in range(0,associativity_1):
                    inst= inst+str(cache_main_level_1.cache[j].set_arr[n].blocks[l])
                    inst1=str(cache_main_level_1.cache[j].set_arr[n].blocks[l])
                    for k in range(0,10-len(inst1)):
                        inst=inst+" "
            inst=inst+"\n"
            text3.insert(END, inst)
        text3.insert(END,"\n\n\n")
        inst = ""
        inst = inst + "                                                  CACHE 2  "
        inst = inst + "\n\n\n"
        text3.insert(END, inst)
        l = associativity_2
        l = l * 10
        inst = ""
        for j in range(0, set_number_2):
            if j >= 0 and j <= 9:
                m = 6
            elif j >= 10 and j <= 99:
                m = 7
            else:
                m = 8
            n = l - m
            if n % 2 == 0:
                for k in range(0, n // 2):
                    inst = inst + " "
                inst = inst + "SET- " + str(j)
                for k in range(0, n // 2):
                    inst = inst + " "
            else:
                for k in range(0, n // 2 - 1):
                    inst = inst + " "
                inst = inst + "SET- " + str(j)
                for k in range(0, n // 2 + 1):
                    inst = inst + " "
        text3.insert(END, inst)
        text3.insert(END, "\n\n")
        inst = ""
        for j in range(0, set_number_2):
            for k in range(0, associativity_2):
                inst = inst + "BLOCK- " + str(k)
                inst1 = "BLOCK- " + str(k)
                for o in range(0, 10 - len(inst1)):
                    inst = inst + " "
        text3.insert(END, inst)
        text3.insert(END, "\n\n")
        inst = ""
        for j in range(0, set_number_2):
            for n in range(0, associativity_2):
                inst = inst + str(cache_main_level_2.cache[j].set_arr[n].tag)
                inst1 = str(cache_main_level_2.cache[j].set_arr[n].tag)
                for k in range(0, 10 - len(inst1)):
                    inst = inst + " "
        text3.insert(END, inst)
        text3.insert(END, "\n\n")
        for l in range(0, block_size_2):
            inst = ""
            for j in range(0, set_number_2):
                for n in range(0, associativity_2):
                    inst = inst + str(cache_main_level_2.cache[j].set_arr[n].blocks[l])
                    inst1 = str(cache_main_level_2.cache[j].set_arr[n].blocks[l])
                    for k in range(0, 10 - len(inst1)):
                        inst = inst + " "
            inst = inst + "\n"
            text3.insert(END, inst)
        text3.pack(side=TOP)
        h3.config(command=text3.xview)
        v3.config(command=text3.yview)
        text3.config(state=DISABLED)

def press(num):
    global PC
    global my_clock
    global info
    global Instructions
    global Registers1
    global Register
    global dataSegment
    global dataSegment1
    global Addres
    global space
    global data_forwarding_list
    global totalStalls
    global stalls_list
    global infostall
    global previous_registers
    global cache_main_level_1
    global cache_main_level_2
    global infostall1
    global totalStalls1
    global infostalls2
    global infostalls3
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
                print(number_of_hits_in_l1, number_of_hits_in_l2)
                # adding 4 extra for the end
                my_clock += 4
                break
        t = Table(ctr_mid)
        t1 = Table1(ctr_right2)
        t2 = Table2(stalls)
        t3 = Table3(data_forwarding)
        t4=Table4(cache)
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
            t4 = Table4(cache)
            totalStalls = totalStalls1
            infostall1 = copy.deepcopy(infostall2)
            infostall = copy.deepcopy(infostall3)
            gui.mainloop()
            if PC == len(Instructions):
                return

    elif num == '3':
        info = []
        data_forwarding_list = []
        stalls_list = []
        infostall = []
        infostall1 = []
        previous_registers = 2 * [4 * [0]]
        space = -1
        my_clock = 0
        totalStalls = 0
        t2 = Table2(stalls)
        PC = 0
        Register = Registers1.copy()
        dataSegment = dataSegment1.copy()
        for j in range(0, len(Instructions)):
            text.delete("0.0", "end")
        for j in range(0, len(Instructions)):
            inst = str(j) + ": " + Instructions[j] + "\n"
            text.insert(END, inst)
        t = Table(ctr_mid)
        t1 = Table1(ctr_right2)
        t2 = Table2(stalls)
        t3 = Table3(data_forwarding)
        cache_main_level_1 = real_cache(
            set_number_1, associativity_1, block_size_1)
        cache_main_level_2 = real_cache(
            set_number_2, associativity_2, block_size_2)
        t4 = Table4(cache)
        gui.mainloop()


information = Tk()
information.title("Information about pipelining")
# information.geometry("400x200")


def var_states():
    global information
    global is_data_forwarding_allowed
    global cache_size_1
    global block_size_1
    global associativity_1
    global second_cache_access_time
    global cache_size_2
    global block_size_2
    global associativity_2
    global main_memory_access_time
    global set_number_1
    global set_number_2
    var_1 = var1.get()
    var_2 = var2.get()
    if(var_1 == 1):
        is_data_forwarding_allowed = True
    if(var_2 == 1):
        is_data_forwarding_allowed = False
    l10=l1.get()
    if l10!=0:
        cache_size_1 = l10
        cache_size_1 = cache_size_1 // 4
        block_size_1 = l2.get()
        block_size_1 = block_size_1 // 4
        associativity_1 = l3.get()
        second_cache_access_time = l4.get()
        cache_size_2 = l5.get()
        cache_size_2 = cache_size_2 // 4
        block_size_2 = l6.get()
        block_size_2 = block_size_2 // 4
        associativity_2 = l7.get()
        main_memory_access_time = l8.get()
        l = block_size_1 * associativity_1
        set_number_1 = cache_size_1 // l
        l = block_size_2 * associativity_2
        set_number_2 = cache_size_2 // l
    information.destroy()


def open_file():
    global cache_size_1
    global block_size_1
    global associativity_1
    global second_cache_access_time
    global cache_size_2
    global block_size_2
    global associativity_2
    global main_memory_access_time
    global set_number_1
    global set_number_2
    file = askopenfile(mode='r')
    m = 0
    if file is not None:
        content = file.readlines()
        for list in content:
            list = list.strip()
            if m == 0:
                cache_size_1 = int(list)
                cache_size_1 = cache_size_1//4
            elif m == 1:
                block_size_1 = int(list)
                block_size_1 = block_size_1//4
            elif m == 2:
                associativity_1 = int(list)
            elif m == 3:
                second_cache_access_time = int(list)
            elif m == 4:
                cache_size_2 = int(list)
                cache_size_2 = cache_size_2 // 4
            elif m == 5:
                block_size_2 = int(list)
                block_size_2 = block_size_2 // 4
            elif m == 6:
                associativity_2 = int(list)
            elif m == 7:
                main_memory_access_time = int(list)
            m = m+1
        l = block_size_1*associativity_1
        set_number_1 = cache_size_1//l
        l = block_size_2 * associativity_2
        set_number_2 = cache_size_2 // l


Label(information, text="Is data forwarding allowed?").grid(row=1, sticky=W)
var1 = IntVar()
Checkbutton(information, text="Yes", variable=var1).grid(row=2, sticky=W)
var2 = IntVar()
Checkbutton(information, text="No", variable=var2).grid(row=3, sticky=W)
l1 = IntVar()
l2 = IntVar()
l3 = IntVar()
l4 = IntVar()
l5 = IntVar()
l6 = IntVar()
l7 = IntVar()
l8 = IntVar()
Label(information, text="Upload a file that has 8 lines where the lines contain the following info:-").grid(row=4, sticky=W)
Label(information, text="1st line should contain cache size of level 1").grid(
    row=5, sticky=W)
Label(information, text="2nd line should contain block size of level 1").grid(
    row=6, sticky=W)
Label(information, text="3rd line should contain associativity of level 1").grid(
    row=7, sticky=W)
Label(information, text="4th line should contain access latency of level 1").grid(
    row=8, sticky=W)
Label(information, text="5th line should contain cache size of level 2").grid(
    row=9, sticky=W)
Label(information, text="6th line should contain block size of level 2").grid(
    row=10, sticky=W)
Label(information, text="7th line should contain associativity of level 2").grid(
    row=11, sticky=W)
Label(information, text="8th line should contain access latency of level 2").grid(
    row=12, sticky=W)
Button(information, text='Upload File', command=lambda: open_file()).grid(
    row=13, sticky=W, pady=4, padx=4)
Button(information, text='Submit', command=var_states).grid(
    row=23, sticky=W, pady=4, padx=4)


Label(information, text="                       or   Enter the values below          ").grid(row=14, sticky=W)
ttk.Label(information, text="  Cache size of level 1",font=("Times New Roman", 10)).grid(column=0,
                                             row=15,sticky=W)
e2 = Entry(information, textvariable=l1)
e2.grid(row=15, column=0)
ttk.Label(information, text="  Block size of level 1",font=("Times New Roman", 10)).grid(column=0,
                                             row=16,sticky=W)
e2 = Entry(information, textvariable=l2)
e2.grid(row=16, column=0)
ttk.Label(information, text="Associativity of level 1",font=("Times New Roman", 10)).grid(column=0,
                                             row=17,sticky=W)
e2 = Entry(information, textvariable=l3)
e2.grid(row=17, column=0)
ttk.Label(information, text="Access latency-level 1",font=("Times New Roman", 10)).grid(column=0,
                                             row=18,sticky=W)
e2 = Entry(information, textvariable=l4)
e2.grid(row=18, column=0)
ttk.Label(information, text="     Cache size of level 2",font=("Times New Roman", 10)).grid(column=0,
                                             row=19,sticky=W)
e2 = Entry(information, textvariable=l5)
e2.grid(row=19, column=0)
ttk.Label(information, text="  Block size of level 2  ",font=("Times New Roman", 10)).grid(column=0,
                                             row=20,sticky=W)
e2 = Entry(information, textvariable=l6)
e2.grid(row=20, column=0)
ttk.Label(information, text="Associativity of level 2",font=("Times New Roman", 10)).grid(column=0,
                                             row=21,sticky=W)
e2 = Entry(information, textvariable=l7)
e2.grid(row=21, column=0)
ttk.Label(information, text="Access latency-level 2   ",font=("Times New Roman", 10)).grid(column=0,
                                             row=22,sticky=W)
e2 = Entry(information, textvariable=l8)
e2.grid(row=22, column=0)
windowWidth = information.winfo_reqwidth()
windowHeight = information.winfo_reqheight()
positionRight = int(information.winfo_screenwidth() / 2 - windowWidth / 2)
positionDown = int(information.winfo_screenheight() / 2 - windowHeight / 2)
information.geometry("+{}+{}".format(positionRight, positionDown))
information.mainloop()

cache_main_level_1 = real_cache(set_number_1, associativity_1, block_size_1)
cache_main_level_2 = real_cache(set_number_2, associativity_2, block_size_2)


gui = Tk()
gui.configure(background="light green")
gui.title("BYTIFY")
console = Tk()
windowWidth = console.winfo_reqwidth()
windowHeight = console.winfo_reqheight()
positionRight = int(console.winfo_screenwidth() / 2 - windowWidth / 2)
positionDown = int(console.winfo_screenheight() / 2 - windowHeight / 2)
console.geometry("+{}+{}".format(positionRight, positionDown))


def OpenFile():
    global Instructions
    global Data
    global indx
    global dataSegment1
    global dataSegment
    global MemAddres
    name = askopenfilename()
    Instructions, Data = InputFile.InputFile(name)
    improveInstructions(Instructions)
    indx = FillMemory.FillMemory(Data, dataSegment, MemAddres)
    dataSegment1 = dataSegment.copy()
    press('3')


def NewFile():
    global Instructions
    global Data
    global indx
    global dataSegment1
    global dataSegment
    global MemAddres
    global cache_main_level_1
    global cache_main_level_2
    cache_main_level_1 = real_cache(
        set_number_1, associativity_1, block_size_1)
    cache_main_level_2 = real_cache(
        set_number_2, associativity_2, block_size_2)
    dataSegment = 1024 * [0]
    name = askopenfilename()
    Instructions, Data = InputFile.InputFile(name)
    improveInstructions(Instructions)
    indx = FillMemory.FillMemory(Data, dataSegment, MemAddres)
    dataSegment1 = dataSegment.copy()
    press('3')


menu = Menu(gui)
gui.config(menu=menu)
filemenu = Menu(menu)
menu.add_cascade(label='File', menu=filemenu)
filemenu.add_command(label='Open...', command=OpenFile)
filemenu.add_command(label='New', command=NewFile)
filemenu.add_separator()
filemenu.add_command(label='Exit', command=gui.quit)
helpmenu = Menu(menu)
menu.add_cascade(label='Help', menu=helpmenu)
helpmenu.add_command(label='About')

equation = StringVar()
boldFont = tkFont.Font(size=10, weight="bold")

tabControl = ttk.Notebook(gui)
tab1 = ttk.Frame(tabControl)
center = Frame(tab1, bg='black', padx=3, pady=3)
gui.grid_rowconfigure(1, weight=1)
gui.grid_columnconfigure(0, weight=1)
stalls = Frame(tabControl, bg='black')
data_forwarding = Frame(tabControl, bg='light green')
cache = Frame(tabControl, bg='light green')

tabControl.add(tab1, text='        EXECUTION OF THE INSTRUCTIONS           ')
tabControl.add(
    stalls, text='        INFORMATION ABOUT STALLS AND NUMBER OF CYCLES     ')
tabControl.add(data_forwarding,
               text='        INFORMATION ABOUT DATA FORWARDING     ')
tabControl.add(cache,
               text='        CACHE     ')
tabControl.pack(expand=1, fill="both")
t2 = Table2(stalls)
t3 = Table3(data_forwarding)

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

ttk.Label(ctr_left2, text="Change type:",
          font=("Times New Roman", 10)).grid(column=0,
                                             row=0, padx=10, pady=25)

name_var = StringVar()
value = StringVar()
pc_var = StringVar()


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
    global stalls_list
    global infostall
    global previous_registers
    global cache_main_level_1
    global cache_main_level_2
    name = name_var.get()
    value1 = value.get()
    pcvalue = pc_var.get()
    e1.delete(0, 'end')
    e2.delete(0, 'end')
    info = []
    data_forwarding_list = []
    stalls_list = []
    infostall = []
    previous_registers = 2*[4*[0]]
    space = -1
    my_clock = 0
    totalStalls = 0
    t2 = Table2(stalls)
    instructions.delete(0, 'end')
    if(value1 == "Delete instruction"):
        for j in range(0, len(Instructions)):
            text.delete("0.0", "end")
        Instructions.pop(int(pcvalue))
        improveInstructions(Instructions)
        for j in range(0, len(Instructions)):
            inst = str(j) + ": " + Instructions[j] + "\n"
            text.insert(END, inst)
        keys = list(Addres.keys())
        for j in range(0, len(Addres)):
            if(Addres[keys[j]] > int(pcvalue)):
                Addres[keys[j]] = Addres[keys[j]]-1
        text.pack(side=TOP)
    elif (value1 == "Add instruction"):
        for j in range(0, len(Instructions)):
            text.delete("1.0", "end")
        Instructions.insert(int(pcvalue), name)
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
        Instructions[int(pcvalue)] = name
        for j in range(0, len(Instructions)):
            inst = str(j) + ": " + Instructions[j] + "\n"
            text.insert(END, inst)
        text.pack(side=TOP)
    PC = 0
    Register = Registers1.copy()
    dataSegment = dataSegment1.copy()
    t = Table(ctr_mid)
    t1 = Table1(ctr_right2)
    t2 = Table2(stalls)
    t3 = Table3(data_forwarding)
    cache_main_level_1 = real_cache(
        set_number_1, associativity_1, block_size_1)
    cache_main_level_2 = real_cache(
        set_number_2, associativity_2, block_size_2)
    t4 = Table4(cache)
    gui.mainloop()


instructions = ttk.Combobox(ctr_left2, width=25, textvariable=value)
instructions['values'] = ["Replace instruction",
                          "Delete instruction", "Add instruction"]
instructions.grid(column=1, row=0)
instructions.current()

ttk.Label(ctr_left2, text="Enter the PC value:",
          font=("Times New Roman", 10)).grid(column=0,
                                             row=2, padx=10, pady=10)
e2 = Entry(ctr_left2, textvariable=pc_var)
e2.grid(row=2, column=1)


ttk.Label(ctr_left2, text="Enter the instruction:",
          font=("Times New Roman", 10)).grid(column=0,
                                             row=3, padx=10, pady=10)
e1 = Entry(ctr_left2, textvariable=name_var)
e1.grid(row=3, column=1)
submitbutton = Button(ctr_left2, text='Submit', command=submit)

submitbutton.grid(row=4, column=1)

onestep = Button(ctr_mid, text='ONE STEP EXECUTION', fg='white', bg='black', font=boldFont,
                 command=lambda: press('1'), height=1, width=36)
onestep.grid(row=0, column=0)
stepbystep = Button(ctr_mid, text='STEP BY STEP EXECUTION', fg='white', bg='black', font=boldFont,
                    command=lambda: press('2'), height=1, width=36)
stepbystep.grid(row=0, column=1)

reload = Button(ctr_mid, text='RESTART', fg='white', bg='black', font=boldFont,
                command=lambda: press('3'), height=1, width=20)
reload.grid(row=3, column=1)

console.title("Console")


gui.mainloop()
