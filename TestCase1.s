.data

.word  1,2,3,4,5       # defineing variables
MSG1:  .asciiz "Count of Zero's Groups is : "
MSG2:  .asciiz "\nCount of One's Groups  is : "

.text

.globl main
main:
    lui $s1 , 0
    lw  $s0 , 0($s1)       # number to compute
    li  $s2 , 5            # act as counter to 32 bit number
    li  $s3 , 5
FLoop:
Loop:
    lw		$s0, 0($s1)		# 
    addi	$s0 , $s0 , 1	         # $t0 = $t1 + 1
    sw		$s0, 0($s1)		# 
    addi	$s2, $s2, -1			# s = $t1 + 0
    
    addi	$s1, $s1, 4		# s1= $s1 + 0
    bne     $s2 , $zero , Loop   # found 1
    addi	$s3, $s3, -1
    addi	$s2, $s2, 5
    li		$s1, 	0	# $s1 = 0
    bne     $s3 , $zero , FLoop   # found 1
    jr		$ra					# jump to $ra
    

    