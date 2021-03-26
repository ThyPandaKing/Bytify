.data


.text

.globl main
main:
    li $t0 , 4
    li $t1 , 3
    sub $t0 , $t0 , $t1
    li $v0 , 1
    sll $v1 , $v0 , 1
    srl $t2 , $v0 , 1
    