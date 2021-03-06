.data

.word  7 , 0 , 0       # defineing variables
MSG1:  .asciiz "Count of Zero's Groups is : "
MSG2:  .asciiz "\nCount of One's Groups  is : "

.text

.globl main
main:
    lui $s1 , 0
    lw  $s0 , 0($s1)       # number to compute
    li  $s2 , 1            # act as counter to 32 bit number
    li  $t0 , 0            # act as loop index
    li  $t3 , 32           # end index/temination condition
    li  $t1 , 0            # count 0
    li  $t2 , 0            # count 1
Loop: 
    and     $s3 , $s0 , $s2        # to check first bit
    addi	  $t0 , $t0 , 1	         # $t0 = $t1 + 1
    sll     $s2 , $s2 , 1
    beq     $s3 , $zero , zeroGrp  # found 0 -> 'and' is zero
    bne     $s3 , $zero , oneGrp   # found 1
check:                            # end of execution
    sw		  $t1 , 4($s1)		      # save count zero 
    sw      $t2 , 8($s1)          # save count one
    jr		    $ra					# jump to SomePrinting
    
zeroGrp:                          # bit came is zero 
    addi	  $t1, $t1, 1			      # $t1 = $t1 + 1
innerZero:
    and     $s3 , $s0 , $s2       # to check the bit
    addi	  $t0 , $t0 , 1	        # $t0 = $t0 + 1
    sll     $s2 , $s2 , 1
    beq     $t0 , $t3 , check     # to check for overflow
    beq     $s3 , $zero , innerZero
                                    # loop varient
    j		    oneGrp				          # jump to zero grp
    
oneGrp:                           # bit came is one 
    addi	  $t2, $t2, 1			      # $t2 = $t2 + 1
innerOne:
    and     $s3 , $s0 , $s2       # to check the bit
    addi	  $t0 , $t0 , 1	        # $t0 = $t0 + 1
    sll     $s2 , $s2 , 1
    beq     $t0 , $t3 , check     # to check for overflow
    bne     $s3 , $zero , innerOne
                                    # loop varient
    j		    zeroGrp				          # jump to one grp


# someting to print
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
    