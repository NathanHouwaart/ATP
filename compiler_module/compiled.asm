.cpu cortex-m0
.text
.align 4

.global  sum
sum:
	push      { lr , r4 - r7 }
	add        r3  ,  r1  ,  r0  
	add        r3  ,  r2  ,  r3  
	mov        r0  ,  r3  
sum_end:
	pop       { pc , r4 - r7 }


.global  test_test
test_test:
	push      { lr , r4 - r7 }
	mov        r4  , #10 
	mov        r5  , #20 
	mov        r6  , #30 
	push       { r0 , r1 , r2 , r3}
	mov        r0  ,  r4  
	mov        r1  ,  r5  
	mov        r2  ,  r6  
	bl        sum
	mov        r4  ,  r0  
	mov        r5  ,  r1  
	mov        r6  ,  r2  
	pop        { r0 , r1 , r2 , r3}
	mov        r0  ,  r4  
test_test_end:
	pop       { pc , r4 - r7 }



.global  odd
odd:
	push      { lr , r4 - r7}
	mov        r1  , #0 
	mov        r2  , #1 
	cmp        r1  ,  r0  
	beq       literal_value_0_27_28_eq_n_res_equal 
	mov        r2  , #0 
literal_value_0_27_28_eq_n_res_equal:
	cmp        r2  , #0 
	beq       odd_if_end_0_20_48 
	mov        r1  , #0 
	mov        r0  ,  r1  
	b         odd_end 
odd_if_end_0_20_48:
	mov        r1  , #1 
	sub        r1  ,  r0  ,  r1  
	push       { r0 , r2 , r3 }
	mov        r0  ,  r1  
	bl        even
	mov        r1  ,  r0  
	pop        { r0 , r2 , r3 }
	mov        r0  ,  r1  
odd_end:
	pop       { pc , r4 - r7}


.global  even
even:
	push      { lr , r4 - r7}
	mov        r1  , #0 
	mov        r2  , #1 
	cmp        r1  ,  r0  
	beq       literal_value_0_102_103_eq_n_res_equal 
	mov        r2  , #0 
literal_value_0_102_103_eq_n_res_equal:
	cmp        r2  , #0 
	beq       even_if_end_0_95_123 
	mov        r1  , #1 
	mov        r0  ,  r1  
	b         even_end 
even_if_end_0_95_123:
	mov        r1  , #1 
	sub        r1  ,  r0  ,  r1  
	push       { r0 , r2 , r3 }
	mov        r0  ,  r1  
	bl        odd
	mov        r1  ,  r0  
	pop        { r0 , r2 , r3 }
	mov        r0  ,  r1  
even_end:
	pop       { pc , r4 - r7}



.global  random_function
random_function:
	push      { lr , r4 - r7 }
	push       { r1 , r2 , r3 }
	mov         r0   ,   r0   
	bl        fibonacci
	mov         r0   ,   r0   
	pop        { r1 , r2 , r3 }
	mov        r1  ,  r0  
	mov        r2  , #100 
	mov        r3  , #1 
	cmp        r1  ,  r2  
	bgt       literal_value_100_245_248_gt_test_variable_res_greater_than 
	mov        r3  , #0 
literal_value_100_245_248_gt_test_variable_res_greater_than:
	push       { r0 , r2 , r3 }
	mov        r0  ,  r1  
	bl        even
	mov        r1  ,  r0  
	pop        { r0 , r2 , r3 }
	orr        r1  ,  r1  ,  r3  
	cmp        r1  , #0 
	beq       random_function_if_false_0_225_342 
	mov        r1  , #42 
	b         random_function_if_end_0_225_342 
random_function_if_false_0_225_342:
	mov        r1  , #2 
random_function_if_end_0_225_342:
	mov        r0  ,  r1  
random_function_end:
	pop       { pc , r4 - r7 }

.global fibonacci 
fibonacci: 
        push     { lr , r4 - r7 } 
        mov       r1  , #2 
        mov       r2  , #1 
        cmp       r0  ,  r1  
        blt      literal_value_2_516_517_lt_n_res_less_than 
        mov       r2  , #0 
literal_value_2_516_517_lt_n_res_less_than: 
        cmp       r2  , #0 
        beq      fibonacci_if_end_0_510_537 
        mov        r0   ,   r0   
        b        fibonacci_end 
fibonacci_if_end_0_510_537: 
        mov       r1  , #2 
        sub       r1  ,  r0  ,  r1  
        push     { r0 , r2 , r3 }
        mov       r0  ,  r1  
        bl       fibonacci 
        mov       r1  ,  r0  
        pop      { r0 , r2 , r3 }
        mov       r2  , #1 
        sub       r2  ,  r0  ,  r2  
        push     { r0 , r1 , r3 }
        mov       r0  ,  r2  
        bl       fibonacci 
        mov       r2  ,  r0  
        pop      { r0 , r1 , r3 }
        add       r3  ,  r1  ,  r2  
        mov       r0  ,  r3  
fibonacci_end: 
        pop      { pc , r4 - r7 }


################################################################################
.global test_function_greater
test_function_greater:
	push      {lr, r4 - r7}
	mov        r2  , #1 
	cmp        r0  ,  r1  
	bgt       var2_gt_var1_res_greater_than 
	mov        r2  , #0 
var2_gt_var1_res_greater_than:
	mov        r0  ,  r2  
test_function_greater_end:
	pop       {pc, r4 - r7}


################################################################################
.global test_function_lesser
test_function_lesser:
	push      {lr, r4 - r7}
	mov        r2  , #1 
	cmp        r0  ,  r1  
	blt       var2_lt_var1_res_less_than 
	mov        r2  , #0 
var2_lt_var1_res_less_than:
	mov        r0  ,  r2  
test_function_lesser_end:
	pop       {pc, r4 - r7}


################################################################################
.global test_function_equal
test_function_equal:
	push      {lr, r4 - r7}
	mov        r2  , #1 
	cmp        r1  ,  r0  
	beq       var2_eq_var1_res_equal 
	mov        r2  , #0 
var2_eq_var1_res_equal:
	mov        r0  ,  r2  
test_function_equal_end:
	pop       {pc, r4 - r7}


################################################################################
.global test_function_if
test_function_if:
	push      {lr, r4 - r7}
	add        r1  ,  r1  ,  r0  
	mov        r2  , #100 
	mov        r3  , #1 
	cmp        r1  ,  r2  
	bgt       literal_value_100_97_100_gt_test_variable_res_greater_than 
	mov        r3  , #0 
literal_value_100_97_100_gt_test_variable_res_greater_than:
	cmp        r3  , #0 
	beq       test_function_if_if_false_0_79_305 
	mov        r2  , #120 
	mov        r3  , #1 
	cmp        r1  ,  r2  
	bgt       literal_value_120_131_134_gt_test_variable_res_greater_than 
	mov        r3  , #0 
literal_value_120_131_134_gt_test_variable_res_greater_than:
	cmp        r3  , #0 
	beq       test_function_if_if_false_1_113_224 
	mov        r1  , #142 
	b         test_function_if_if_end_1_113_224 
test_function_if_if_false_1_113_224:
	mov        r1  , #101 
test_function_if_if_end_1_113_224:
	b         test_function_if_if_end_0_79_305 
test_function_if_if_false_0_79_305:
	mov        r2  , #15 
	mov        r3  , #1 
	cmp        r1  ,  r2  
	bgt       literal_value_15_261_263_gt_test_variable_res_greater_than 
	mov        r3  , #0 
literal_value_15_261_263_gt_test_variable_res_greater_than:
	cmp        r3  , #0 
	beq       test_function_if_if_end_1_243_303 
	mov        r1  , #15 
test_function_if_if_end_1_243_303:
test_function_if_if_end_0_79_305:
	mov        r0  ,  r1  
test_function_if_end:
	pop       {pc, r4 - r7}


################################################################################
.global factorial 
factorial: 
        push     { lr , r4 - r7 } 
        mov       r1  , #0 
        mov       r2  , #1 
        cmp       r1  ,  r0  
        beq      literal_value_0_33_34_eq_n_res_equal 
        mov       r2  , #0 
literal_value_0_33_34_eq_n_res_equal: 
        cmp       r2  , #0 
        beq      factorial_if_end_0_26_54 
        mov       r1  , #1 
        mov       r0  ,  r1  
        b        factorial_end 
factorial_if_end_0_26_54: 
        mov       r1  , #1 
        sub       r1  ,  r0  ,  r1  
        push     { r0 , r2 , r3 }
        mov       r0  ,  r1  
        bl       factorial 
        mov       r1  ,  r0  
        pop      { r0 , r2 , r3 }
        mul       r1  ,  r1  ,  r0  
        mov       r0  ,  r1  
factorial_end: 
        pop      { pc , r4 - r7 } 
