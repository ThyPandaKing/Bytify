.data

.word 10,11,3

.text

.globl main
main:

    li $t0 , 2
    li $s0 , 1
BOI:
    # li      $v1, 0
    beq     $t1, $s0 , finish

    addi	$t0, $t0, -1		# $t0 = $t1 + 0
    bne		$t0, $zero, BOI	    # if $t0 == $t1 then target

addi	$t0, $t0, 1			# $t0 = $t1 + 0
move    $t1 , $t0 
addi	$t1, $t1, 1			# $t1 = $t1 1 0

slt     $t2 , $t0 , $t1
li      $t1, 1
beq		$t2, $t1, BOI	# if $t2 == $t1 then target

finish:
    li  $v0 , 1
    move $a0 , $t1
    syscall


    
    