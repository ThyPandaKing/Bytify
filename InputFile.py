def InputFile():

    # file input as it is
    file = open('BubbleSort.s', 'r')

    # all lines in a list
    l = file.readlines()

    # extacting them in better way
    instructions = []

    # data simplification
    for list in l:
        # removing starting and ending spaces
        list = list.strip()

        # enter when we have something in line
        if len(list) > 0:
            temp = ''
            for k in list:
                # removing comments
                if k[0] == '#':
                    break
                temp += k
            # add better line
            if len(temp) > 0:
                instructions.append(temp)

    dataSegment = []

    i = 0
    # seprating data and instrution segment
    for inst in instructions:
        i += 1
        if inst == '.text':
            break
        dataSegment.append(inst)

    instructions = instructions[i-1:]
    # for dta in dataSegment:
    #     print(dta)

    # print()
    # for inst in instructions:
    #     print(inst)

    return instructions, dataSegment
