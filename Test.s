.data

.word 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20

.text

.globl main
main:
    lw $t0 , 4($s0)
    lw $s1 , 4($s0)
    lw $s2 , 0($s0)
    lw $t0 , 4($s0)
    lw $s1 , 8($s0)
    lw $s2 , 8($s0)
    lw $s1 , 4($s0)
    lw $s2 , 20($s0)
    

    
    