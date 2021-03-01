dataSegmentNormal=[]
dataSegmentHexa=[]
##  for normal conversion
"""
while 1:
    s=input()
    if s.strip()==".text" :
        break
    else :
        if(s.find('.word')!=-1):
            l=s.find('.word')
            final = s[l+5:]
            final=final.replace(',','')
            get = final.split()
            for i in range(0,len(get)):
              dataSegmentNormal.append(get[i])
        if(s.find('.asciiz')!=-1):
            first=s.find('"')
            a=s[first+1:]
            last=a.find('"')
            final=s[first+1:first+last+1]
            get = [final[i:i + 4] for i in range(0, len(final), 4)]
            for i in range(0,len(get)):
              dataSegmentNormal.append(get[i])
print("DATA SEGMENT NORMAL:",dataSegmentNormal)
"""
## converting everything into hexadecimal form

while 1:
    s=input()
    if s.strip()==".text" :
        break
    else :
        if(s.find('.word')!=-1):
            l=s.find('.word')
            final = s[l+5:]
            final=final.replace(',',' ')
            get = final.split()
            for i in range(0,len(get)):
              m=int(get[i])
              hexi = hex(m)
              hexa=''
              for j in range (0,10-len(hexi)):
                  hexa+='0'
              hexa=hexa+hexi[2:]
              dataSegmentHexa.append(hexa)
        if(s.find('.asciiz')!=-1):
            first=s.find('"')
            a=s[first+1:]
            last=a.find('"')
            final=s[first+1:first+last+1]
            l=0
            get = [final[i:i + 4] for i in range(0, len(final), 4)]
            for i in range(0,len(get)):
               hexa=''
               for j in range (0,len(get[i])):
                   b=hex(ord(get[i][len(get[i])-1-j]))
                   hexa+=b[2:]
               hexi = ''
               for j in range(0, 8 - len(hexa)):
                   hexi += '0'
                   l=1
               hexi = hexi + hexa
               dataSegmentHexa.append(hexi)
            if l==1:
                dataSegmentHexa.append('00000000')
print("DATA SEGMENT HEXADECIMAL:",dataSegmentHexa)

"""
Ascii values
ord('h')

Converts x from decimal to hexadecimal
hex(x)
"""