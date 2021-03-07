.data
array:
    .word 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1   	#initial array
PrintArray: .asciiz "Final Sorted Array is\n"

PrintSpace: .asciiz " "

.text
.globl main

main:
    	lui   $s0 , 0 			#save first address of array
    	li    $s1 , 1      			#just one to check for equality  
    	li    $t0 , 0      			#act like my first loop incrementing register 
    	li    $t1 , 0      			#act like my second loop incrementing register
    	li    $t2 , 10     			#total times first loop works
    	li    $t3 , 10     			#total times second loop works = 11 - $t2 for every iteration 
FirstLoop:  
        li    $t1 , 0           		#initialize the inner loop counter (j) 
        
SecondLoop:
        
        lw    $t4 , 0($s0)            		# contains a[j]
        lw    $t5 , 4($s0)            		# contains a[j+1] where j>=0
        slt   $s3 , $t5 , $t4         		# $s3 is one if a[j]>a[j+1] 
        beq   $s3 , $s1 , SWAP        		# Go to swap
After:  addi  $s0 , $s0 , 4                 		# assigned After to jump back from swap to here
        addi  $t1 , $t1 , 1           		# incrementing the counter
        bne   $t1 , $t3 , SecondLoop  		# second loop condition check
        addi  $t3 , $t3 , -1          		# decrementing $t3 count so that in next iteration counter 
                                      		# does not goes till end
        lui   $s0 , 0            		# reinitillize the starting address 
        addi  $t0 , $t0 , 1           		# incrementing first loops counter
        bne   $t0 , $t2 , FirstLoop   		# condition check for First loop

PrintResult:                          		# code to print the sorted array and finish execution
        li      $v0 , 4
        la      $a0 , PrintArray
        syscall
        li      $v0 , 1
        li      $t0 , 0
        lui     $s0 , 0
        lw      $s1 , 0($s0)
        move    $a0 , $s1
Loop:   syscall
        li      $v0 , 4
        la      $a0 , PrintSpace
        syscall                                 # printing space
        li      $v0 , 1
        addi    $s0 , 4
        addi    $t0 , 1
        lw      $s1 , 0($s0)
        move    $a0 , $s1
        bne     $t0 , $t2 , Loop
        jr $ra        


SWAP:                                          # swap code
      sw   $t4  , 4($s0)
      sw   $t5  , 0($s0)
      j    After                               # jump back to initial position