.data

.word 10,2,3,6,11,5,4,3,2,1

.text
lui  $s0 , 0
li   $t0 , 10  # size of array
li   $s1 , 0  # first index

MainLoop:
    lui     $s0, 0
    li      $s1, 0
    addi	$t0, $t0, -1	   # $t0 = $t1 + 0
    beq     $t0, $zero, Finish
LoopFirst:
    lw		$t1, 0($s0)		   # filled 0+s1 in t1
    beq		$t0, $s1, MainLoop # if $t0 == $t1 then target
    lw		$t2, 4($s0)		   # 
    addi	$s1, $s1, 1 	   # $t1 = 
    slt     $t3, $t2, $t1      # if(a[i]>a[i+1])t3=1
    bne		$t3, $zero, SWAP   # if $t0 == $t1 then target
Back:
    addi	$s0, $s0, 4		   # $t0 = $t1 + 0
    j       LoopFirst


SWAP:
    sw		$t2, 0($s0)		# 
    sw		$t1, 4($s0)		# 
    j       Back

Finish:
jr		$ra					# jump to $ra
