

def FillMemory(data, dataSegment, MemAddres):
    indx = 0
    for dta in data:
        if dta.find(':') != -1:
            l = dta.find(':')
            temp = dta[:l]
            temp = temp.strip()
            MemAddres[temp] = indx
        if(dta.find('.word') != -1):
            l = dta.find('.word')

            final = dta[l+5:]
            final = final.replace(',', ' ')
            get = final.split()
            for i in range(0, len(get)):
                # print(get[i])
                m = int(get[i])
                hexi = hex(m)
                # print(hexi, m)
                # hexa = ''
                # # for j in range(0, 10-len(hexi)):
                # #     hexa += '0'
                # hexa = hexa+hexi[2:]
                # hexa = "0x"+hexa
                dataSegment[indx] = hexi
                indx += 1
        if(dta.find('.asciiz') != -1):
            first = dta.find('"')

            a = dta[first+1:]
            last = a.find('"')
            final = dta[first+1:first+last+1]
            get = [final[i:i + 4] for i in range(0, len(final), 4)]
            for i in range(0, len(get)):
                dataSegment[indx] = get[i]
                indx += 1
    return indx
