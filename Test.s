.data

.word  1431655765 , 0 , 0
MSG1:  .asciiz "Count of Zero is : "
MSG2:  .asciiz "\nCount of One  is : "

.text

.globl main
main:
    li  $s1 , 0
    lw  $s0 , 0($s1)       # number to compute
    li  $s2 , 1            # act as counter to 32 bit number
    li  $t0 , 0            # act as loop index
    li  $t3 , 33           # end index/temination condition
    li  $t1 , 0            # count 0
    li  $t2 , 0            # count 1
Loop: 
    and     $s3 , $s0 , $s2       # to check the bit
    addi	  $t0 , $t0 , 1	        # $t0 = $t1 + 1
    sll     $s2 , $s2 , 1         # shift the number bit, x2
    beq     $s3 , $zero , incZero # found 0 -> and is zero
    bne     $s3 , $zero , incOne  # found 1
check:
    bne     $t0 , $t3 , Loop      # iteration 
    sw		  $t1 , 0($s1)		      # save count zero 
    sw      $t2 , 4($s1)          # save count zero
    j		    SomePrinting					# jump to SomePrinting
    
incZero:
    addi	$t1, $t1, 1			# $t1 = $t1 + 1
    j		check				      # jump to check
    
incOne:
    addi	$t2, $t2, 1			# $t1 = $t1 + 1
    j		check				      # jump to check

# printing msg
SomePrinting:
    li  $v0 , 4
    la  $a0 , MSG1
    syscall
    li  $v0 , 1
    move$a0 , $t1
    syscall
    li  $v0 , 4
    la  $a0 , MSG2
    syscall
    li  $v0 , 1
    move$a0 , $t2
    syscall
    jr		$ra					# jump to $ra
    