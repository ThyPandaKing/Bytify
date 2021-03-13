.data

.word 100,1,-20,1000,5,9,1001,-10,-1,-500

.text
li  $s0 , 0
li   $t0 , 10  # size of array
li   $s1 , 0   # first index

MainLoop:
    li     $s0, 0
    li      $s1, 0             # j
    addi	$t0, $t0, -1	   # i
    beq     $t0, $zero, Finish
LoopFirst:
    lw		$t1, 0($s0)		   # filled 0+s1 in  , a[i]
    beq		$t0, $s1, MainLoop # if $t0 == $s1, i==j then target
    lw		$t2, 4($s0)		   # a[i+1] 
    addi	$s1, $s1, 1 	   #  j++
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
