strcpy:
    addi $sp, $sp, -4
    sw $s0, 0($sp)
    add $s0, $zero, $zero
L1: add $t1, $s0, $a1
    lb $t2, 0($t1)
    add $t3, $s0, $a0
    sb $t2, 0($t3)
    beq $t2, $zero, L2
    addi $s0, $s0, 1
    j L1
