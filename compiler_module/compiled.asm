.global  odd
odd:
	push      { lr , r4 - r7 }
	mov       literal_value_0_27_28_reg , #0 
	mov       literal_value_0_27_28_n_res_reg , #1 
	cmp       literal_value_0_27_28_reg , r0 
	beq       literal_value_0_27_28_eq_n_res_equal 
	mov       literal_value_0_27_28_n_res_reg , #0 
literal_value_0_27_28_eq_n_res_equal:
	cmp       literal_value_0_27_28_n_res_reg , #0 
	beq       odd_if_end_0_20_48 
	mov       literal_value_0_43_44_reg , #0 
	mov       r0 , literal_value_0_43_44_reg 
	b         odd_end 
odd_if_end_0_20_48:
	mov       literal_value_1_64_65_reg , #1 
	sub       literal_value_1_64_65_n_res_reg , r0 , literal_value_1_64_65_reg 
	notpush   { literal_value_1_64_65_n_res_reg }
	mov       r0 , literal_value_1_64_65_n_res_reg 
	bl        even
	mov       literal_value_1_64_65_n_res_reg , r0 
	notpop    { literal_value_1_64_65_n_res_reg }
	mov       r0 , literal_value_1_64_65_n_res_reg 
odd_end:
	pop       { pc , r4 - r7 }


.global  even
even:
	push      { lr , r4 - r7 }
	mov       literal_value_0_102_103_reg , #0 
	mov       literal_value_0_102_103_n_res_reg , #1 
	cmp       literal_value_0_102_103_reg , r0 
	beq       literal_value_0_102_103_eq_n_res_equal 
	mov       literal_value_0_102_103_n_res_reg , #0 
literal_value_0_102_103_eq_n_res_equal:
	cmp       literal_value_0_102_103_n_res_reg , #0 
	beq       even_if_end_0_95_123 
	mov       literal_value_1_118_119_reg , #1 
	mov       r0 , literal_value_1_118_119_reg 
	b         even_end 
even_if_end_0_95_123:
	mov       literal_value_1_138_139_reg , #1 
	sub       literal_value_1_138_139_n_res_reg , r0 , literal_value_1_138_139_reg 
	notpush   { literal_value_1_138_139_n_res_reg }
	mov       r0 , literal_value_1_138_139_n_res_reg 
	bl        odd
	mov       literal_value_1_138_139_n_res_reg , r0 
	notpop    { literal_value_1_138_139_n_res_reg }
	mov       r0 , literal_value_1_138_139_n_res_reg 
even_end:
	pop       { pc , r4 - r7 }


.global  random_function
random_function:
	push      { lr , r4 - r7 }
	notpush   { r0 }
	mov       r0 , r0 
	bl        fibonacci
	mov       r0 , r0 
	notpop    { r0 }
	mov       test_variable_reg , r0 
	mov       literal_value_100_245_248_reg , #100 
	mov       literal_value_100_245_248_test_variable_res_reg , #1 
	cmp       test_variable_reg , literal_value_100_245_248_reg 
	bgt       literal_value_100_245_248_gt_test_variable_res_greater_than 
	mov       literal_value_100_245_248_test_variable_res_reg , #0 
literal_value_100_245_248_gt_test_variable_res_greater_than:
	notpush   { test_variable_reg }
	mov       r0 , test_variable_reg 
	bl        even
	mov       test_variable_reg , r0 
	notpop    { test_variable_reg }
	orr       test_variable_literal_value_100_245_248_test_variable_res_reg_res_reg , test_variable_reg , literal_value_100_245_248_test_variable_res_reg 
	cmp       None , #0 
	beq       random_function_if_false_0_225_342 
	mov       solution_reg , #42 
	b         random_function_if_end_0_225_342 
random_function_if_false_0_225_342:
	mov       solution_reg , #2 
random_function_if_end_0_225_342:
	mov       r0 , solution_reg 
random_function_end:
	pop       { pc , r4 - r7 }


.global  fibonacci
fibonacci:
	push      { lr , r4 - r7 }
	mov       literal_value_2_398_399_reg , #2 
	mov       literal_value_2_398_399_n_res_reg , #1 
	cmp       r0 , literal_value_2_398_399_reg 
	blt       literal_value_2_398_399_lt_n_res_less_than 
	mov       literal_value_2_398_399_n_res_reg , #0 
literal_value_2_398_399_lt_n_res_less_than:
	cmp       literal_value_2_398_399_n_res_reg , #0 
	beq       fibonacci_if_end_0_392_419 
	mov       r0 , r0 
	b         fibonacci_end 
fibonacci_if_end_0_392_419:
	mov       literal_value_2_461_462_reg , #2 
	sub       literal_value_2_461_462_n_res_reg , r0 , literal_value_2_461_462_reg 
	notpush   { literal_value_2_461_462_n_res_reg }
	mov       r0 , literal_value_2_461_462_n_res_reg 
	bl        fibonacci
	mov       literal_value_2_461_462_n_res_reg , r0 
	notpop    { literal_value_2_461_462_n_res_reg }
	mov       literal_value_1_441_442_reg , #1 
	sub       literal_value_1_441_442_n_res_reg , r0 , literal_value_1_441_442_reg 
	notpush   { literal_value_1_441_442_n_res_reg }
	mov       r0 , literal_value_1_441_442_n_res_reg 
	bl        fibonacci
	mov       literal_value_1_441_442_n_res_reg , r0 
	notpop    { literal_value_1_441_442_n_res_reg }
	add       function_return_reg , literal_value_2_461_462_n_res_reg , literal_value_1_441_442_n_res_reg 
	mov       r0 , function_return_reg 
fibonacci_end:
	pop       { pc , r4 - r7 }




literal_value_0_27_28_reg                                    [2, None]
literal_value_0_27_28_n_res_reg                              [3, None]
r0                                                           [32, None]
literal_value_0_43_44_reg                                    [2, None]
literal_value_1_64_65_reg                                    [2, None]
literal_value_1_64_65_n_res_reg                              [6, None]
{                                                            [12, None]
}                                                            [12, None]
literal_value_0_102_103_reg                                  [2, None]
literal_value_0_102_103_n_res_reg                            [3, None]
literal_value_1_118_119_reg                                  [2, None]
literal_value_1_138_139_reg                                  [2, None]
literal_value_1_138_139_n_res_reg                            [6, None]
test_variable_reg                                            [7, None]
literal_value_100_245_248_reg                                [2, None]
literal_value_100_245_248_test_variable_res_reg              [3, None]
test_variable_literal_value_100_245_248_test_variable_res_reg_res_reg [1, None]
None                                                         [1, None]
solution_reg                                                 [3, None]
literal_value_2_398_399_reg                                  [2, None]
literal_value_2_398_399_n_res_reg                            [3, None]
literal_value_2_461_462_reg                                  [2, None]
literal_value_2_461_462_n_res_reg                            [6, None]
literal_value_1_441_442_reg                                  [2, None]
literal_value_1_441_442_n_res_reg                            [6, None]
function_return_reg                                          [2, None]

.global  odd
odd:
	push      { lr , r4 - r7 }
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
	push       { r0 , r2 , r3 , }
	mov        r0  ,  r1  
	bl        even
	mov        r1  ,  r0  
	pop        { r0 , r2 , r3 , }
	mov        r0  ,  r1  
odd_end:
	pop       { pc , r4 - r7 }


.global  even
even:
	push      { lr , r4 - r7 }
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
	push       { r0 , r2 , r3 , }
	mov        r0  ,  r1  
	bl        odd
	mov        r1  ,  r0  
	pop        { r0 , r2 , r3 , }
	mov        r0  ,  r1  
even_end:
	pop       { pc , r4 - r7 }


.global  random_function
random_function:
	push      { lr , r4 - r7 }
	push       { r1 , r2 , r3 , }
	mov         r0   ,   r0   
	bl        fibonacci
	mov         r0   ,   r0   
	pop        { r1 , r2 , r3 , }
	mov        r1  ,  r0  
	mov        r2  , #100 
	mov        r3  , #1 
	cmp        r1  ,  r2  
	bgt       literal_value_100_245_248_gt_test_variable_res_greater_than 
	mov        r3  , #0 
literal_value_100_245_248_gt_test_variable_res_greater_than:
	push       { r0 , r2 , r3 , }
	mov        r0  ,  r1  
	bl        even
	mov        r1  ,  r0  
	pop        { r0 , r2 , r3 , }
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


.global  fibonacci
fibonacci:
	push      { lr , r4 - r7 }
	mov        r1  , #2 
	mov        r2  , #1 
	cmp        r0  ,  r1  
	blt       literal_value_2_398_399_lt_n_res_less_than 
	mov        r2  , #0 
literal_value_2_398_399_lt_n_res_less_than:
	cmp        r2  , #0 
	beq       fibonacci_if_end_0_392_419 
	mov         r0   ,   r0   
	b         fibonacci_end 
fibonacci_if_end_0_392_419:
	mov        r1  , #2 
	sub        r1  ,  r0  ,  r1  
	push       { r0 , r2 , r3 , }
	mov        r0  ,  r1  
	bl        fibonacci
	mov        r1  ,  r0  
	pop        { r0 , r2 , r3 , }
	mov        r2  , #1 
	sub        r2  ,  r0  ,  r2  
	push       { r0 , r1 , r3 , }
	mov        r0  ,  r2  
	bl        fibonacci
	mov        r2  ,  r0  
	pop        { r0 , r1 , r3 , }
	add        r1  ,  r1  ,  r2  
	mov        r0  ,  r1  
fibonacci_end:
	pop       { pc , r4 - r7 }



program finished in 0.00926 s
