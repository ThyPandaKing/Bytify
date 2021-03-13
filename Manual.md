# Arithmetic

## Add

```
add $register1 , $register2 , $register3
```

adds value of $register2 and $register3 and save in $register1.

## SUB

```
sub $register1 , $register2 , $register3
```

substracts value of $register2 and $register3 and save in $register1.

## MUL

```
mul $register1 , $register2 , $register3
```

multiplies value of $register2 and $register3 and save in $register1.

## DIV

```
div $register1 , $register2 , $register3
```

divides value of $register2 and $register3 and save in $register1.

## ADDI

```
addi $register1 , $register2 , <constant>
```

adds value of $register2 and constant and save in $register1.

## SUBI

```
subi $register1 , $register2 , <constant>
```

adds value of $register2 and constant and save in $register1.

# Bitwise

## AND

```
and $register1 , $register2 , $register3
```

bitwise AND the values of $register2 and $register3 and save in $register1.

## OR

```
or $register1 , $register2 , $register3
```

bitwise OR the values of $register2 and $register3 and save in $register1.

## NOT

```
not $register1 , $register2
```

negates value of $register2 and save in $register1.

## SLL

```
sll $register1 , $register2 , <constant>
```

shift left the $register2 value by constant units and save in $register1

## SRL

```
srl $register1 , $register2 , <constant>
```

shift right the $register2 value by constant units and save in $register1

## ANDI

```
andi $register1 , $register2 , <constant>
```

AND values of $register2 and constant and save in $register1.

# Initializing

## LI

```
li $register , <constant>
```

set the value of $register as that constant.

## LA

```
la $register , <MemoryAddress>
```

set the address of that memory segment location in $register.

used to print memory segment values , with the help of $v0 , $ a0 , and syscall function.

## MOVE

```
move $register1 , $register2
```

copies the value of $register2 to $register1.

# Branch

## SLT

```
slt     $register1, $register2, $register3
```

if $register3 > $register2 then $register1 will be set to one , otherwise 0.

## BNE

```
bne $register1  , $register2 , <AddressLocation>
```

if $register1 != $register2 jump to AddressLocation

## BEQ

```
beq $register1  , $register2 , <AddressLocation>
```

if $register1 == $register2 jump to AddressLocation

## Jump

```
j <AddressLocation>
```

Unconditional jump to AddressLocation

## Jump Break (Exit)

```
jr  $ra
```

used to end the code , exit condition

# Memory

## LW

```
lw $register1 , <constant>($register2)
```

set the value of $register1 with the value at (constant+$register2) in memory.

## SW

```
sw $register1 , <constant>($register2)
```

copy the value of $register1 at the address of (constant+$register2) in memory.

# Printing

## SYSCALL

```
syscall
```

Alone this command has no use , but combining with some values it can be used to print values in console.
