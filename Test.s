.data

.word 10,11,3

.text

.globl main
main:
    li $t0 , 5
BOI:
    addi	$t0, $t0, -1		# $t0 = $t1 + 0
    bne		$t0, $zero, BOI	    # if $t0 == $t1 then target


    
    