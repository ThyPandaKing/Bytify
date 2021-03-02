

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
                m = int(get[i])
                hexi = hex(m)
                hexa = ''
                for j in range(0, 10-len(hexi)):
                    hexa += '0'
                hexa = hexa+hexi[2:]
                dataSegment[indx] = hexa
                indx += 1
        if(dta.find('.asciiz') != -1):
            first = dta.find('"')

            a = dta[first+1:]
            last = a.find('"')
            final = dta[first+1:first+last+1]
            get = [final[i:i + 4] for i in range(0, len(final), 4)]

            if len(get[-1]) < 4:
                if len(get[-1]) == 1:
                    get[-1] += "000000"

                elif len(get[-1]) == 2:
                    get[-1] += "0000"

                elif len(get[-1]) == 3:
                    get[-1] += "00"

            for i in range(0, len(get)):
                dataSegment[indx] = get[i]
                indx += 1
    return indx
