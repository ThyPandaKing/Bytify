.data

.word 10,11,3

.text

.globl main
main:
    li $t0 , 3
    li $t1 , 1
    add $t0 , $t0 , $t1
    lw  $t2 , 0($t0)
    move $t3 , $t1
    div  $t0 , $t3 , $t0
    