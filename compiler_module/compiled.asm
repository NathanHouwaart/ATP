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
	mov       solution_reg , #0 
	notpush   { r0 }
	mov       r0 , r0 
	bl        fibonacci
	mov       r0 , r0 
	notpop    { r0 }
	mov       test_variable_reg , r0 
	mov       literal_value_100_264_267_reg , #100 
	mov       literal_value_100_264_267_test_variable_res_reg , #1 
	cmp       test_variable_reg , literal_value_100_264_267_reg 
	bgt       literal_value_100_264_267_gt_test_variable_res_greater_than 
	mov       literal_value_100_264_267_test_variable_res_reg , #0 
literal_value_100_264_267_gt_test_variable_res_greater_than:
	cmp       literal_value_100_264_267_test_variable_res_reg , #0 
	beq       random_function_if_false_0_244_332 
	mov       solution_reg , #42 
	b         random_function_if_end_0_244_332 
random_function_if_false_0_244_332:
	mov       solution_reg , #2 
random_function_if_end_0_244_332:
	mov       r0 , solution_reg 
random_function_end:
	pop       { pc , r4 - r7 }


.global  fibonacci
fibonacci:
	push      { lr , r4 - r7 }
	mov       literal_value_2_388_389_reg , #2 
	mov       literal_value_2_388_389_n_res_reg , #1 
	cmp       r0 , literal_value_2_388_389_reg 
	blt       literal_value_2_388_389_lt_n_res_less_than 
	mov       literal_value_2_388_389_n_res_reg , #0 
literal_value_2_388_389_lt_n_res_less_than:
	cmp       literal_value_2_388_389_n_res_reg , #0 
	beq       fibonacci_if_end_0_382_409 
	mov       r0 , r0 
	b         fibonacci_end 
fibonacci_if_end_0_382_409:
	mov       literal_value_2_451_452_reg , #2 
	sub       literal_value_2_451_452_n_res_reg , r0 , literal_value_2_451_452_reg 
	notpush   { literal_value_2_451_452_n_res_reg }
	mov       r0 , literal_value_2_451_452_n_res_reg 
	bl        fibonacci
	mov       literal_value_2_451_452_n_res_reg , r0 
	notpop    { literal_value_2_451_452_n_res_reg }
	mov       literal_value_1_431_432_reg , #1 
	sub       literal_value_1_431_432_n_res_reg , r0 , literal_value_1_431_432_reg 
	notpush   { literal_value_1_431_432_n_res_reg }
	mov       r0 , literal_value_1_431_432_n_res_reg 
	bl        fibonacci
	mov       literal_value_1_431_432_n_res_reg , r0 
	notpop    { literal_value_1_431_432_n_res_reg }
	add       function_return_reg , literal_value_2_451_452_n_res_reg , literal_value_1_431_432_n_res_reg 
	mov       r0 , function_return_reg 
fibonacci_end:
	pop       { pc , r4 - r7 }




literal_value_0_27_28_reg                                    [2, None]
literal_value_0_27_28_n_res_reg                              [3, None]
r0                                                           [30, None]
literal_value_0_43_44_reg                                    [2, None]
literal_value_1_64_65_reg                                    [2, None]
literal_value_1_64_65_n_res_reg                              [6, None]
{                                                            [10, None]
}                                                            [10, None]
literal_value_0_102_103_reg                                  [2, None]
literal_value_0_102_103_n_res_reg                            [3, None]
literal_value_1_118_119_reg                                  [2, None]
literal_value_1_138_139_reg                                  [2, None]
literal_value_1_138_139_n_res_reg                            [6, None]
solution_reg                                                 [4, None]
test_variable_reg                                            [2, None]
literal_value_100_264_267_reg                                [2, None]
literal_value_100_264_267_test_variable_res_reg              [3, None]
literal_value_2_388_389_reg                                  [2, None]
literal_value_2_388_389_n_res_reg                            [3, None]
literal_value_2_451_452_reg                                  [2, None]
literal_value_2_451_452_n_res_reg                            [6, None]
literal_value_1_431_432_reg                                  [2, None]
literal_value_1_431_432_n_res_reg                            [6, None]
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
	mov        r1  , #0 
	push       { r1 , r2 , r3 , }
	mov         r0   ,   r0   
	bl        fibonacci
	mov         r0   ,   r0   
	pop        { r1 , r2 , r3 , }
	mov        r2  ,  r0  
	mov        r3  , #100 
	mov        r4  , #1 
	cmp        r2  ,  r3  
	bgt       literal_value_100_264_267_gt_test_variable_res_greater_than 
	mov        r4  , #0 
literal_value_100_264_267_gt_test_variable_res_greater_than:
	cmp        r4  , #0 
	beq       random_function_if_false_0_244_332 
	mov        r1  , #42 
	b         random_function_if_end_0_244_332 
random_function_if_false_0_244_332:
	mov        r1  , #2 
random_function_if_end_0_244_332:
	mov        r0  ,  r1  
random_function_end:
	pop       { pc , r4 - r7 }


.global  fibonacci
fibonacci:
	push      { lr , r4 - r7 }
	mov        r1  , #2 
	mov        r2  , #1 
	cmp        r0  ,  r1  
	blt       literal_value_2_388_389_lt_n_res_less_than 
	mov        r2  , #0 
literal_value_2_388_389_lt_n_res_less_than:
	cmp        r2  , #0 
	beq       fibonacci_if_end_0_382_409 
	mov         r0   ,   r0   
	b         fibonacci_end 
fibonacci_if_end_0_382_409:
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



program finished in 0.00733 s
