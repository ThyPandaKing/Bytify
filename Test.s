.data

my:  .asciiz "Hello Goergy"
my2: .word 1

.text
.globl main

main:
HUE:    li $a0 , 10
    move 	$t0, $a0		# $t0 = $t1
    jr		$ra	
    addi    $t0 , $t0 , -1

    li      $s0 , 1
    				# jump to $ra
    