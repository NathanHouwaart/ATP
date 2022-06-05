test_function:
	push      {lr, r4 - r7}
	mov        r2  , #10 
	mov        r3  , #1 
	cmp        r2  ,  r0  
	beq       literal_value_10_53_55_eq_var1_res_equal 
	mov        r3  , #0 
literal_value_10_53_55_eq_var1_res_equal:
	cmp        r3  , #0 
	beq       test_function_if_false_0_43_291 
	add        r2  ,  r1  ,  r0  
	mov        r0  ,  r2  
	b         test_function_end 
test_function_if_false_0_43_291:
	mov        r3  , #2 
	mov        r4  , #1 
	cmp        r3  ,  r1  
	beq       literal_value_2_100_101_eq_var2_res_equal 
	mov        r4  , #0 
literal_value_2_100_101_eq_var2_res_equal:
	cmp        r4  , #0 
	beq       test_function_if_false_1_90_291 
	sub        r2  ,  r1  ,  r0  
	mov        r0  ,  r2  
	b         test_function_end 
test_function_if_false_1_90_291:
	mov        r3  , #2 
	mov        r4  , #1 
	cmp        r3  ,  r1  
	beq       literal_value_2_146_147_eq_var2_res_equal 
	mov        r4  , #0 
literal_value_2_146_147_eq_var2_res_equal:
	cmp        r4  , #0 
	beq       test_function_if_false_2_136_291 
	sub        r2  ,  r1  ,  r0  
	mov        r0  ,  r2  
	b         test_function_end 
test_function_if_false_2_136_291:
	mov        r3  , #2 
	mov        r4  , #1 
	cmp        r3  ,  r1  
	beq       literal_value_2_192_193_eq_var2_res_equal 
	mov        r4  , #0 
literal_value_2_192_193_eq_var2_res_equal:
	cmp        r4  , #0 
	beq       test_function_if_false_3_182_291 
	sub        r2  ,  r1  ,  r0  
	mov        r0  ,  r2  
	b         test_function_end 
test_function_if_false_3_182_291:
	mov        r3  , #1 
	mov        r4  , #1 
	cmp        r3  ,  r0  
	beq       literal_value_1_253_254_eq_var1_res_equal 
	mov        r4  , #0 
literal_value_1_253_254_eq_var1_res_equal:
	cmp        r4  , #0 
	beq       test_function_if_false_4_243_289 
	add        r2  ,  r1  ,  r0  
	mov        r0  ,  r2  
	b         test_function_end 
test_function_if_false_4_243_289:
	add        r3  ,  r1  ,  r0  
	mov        r4  , #44 
	add        r3  ,  r4  ,  r3  
	mov        r4  , #2 
	mul        r3  ,  r3  ,  r4  
	mov        r3  , #3 
	add        r1  ,  r1  ,  r3  
	mul        r1  ,  r1  ,  r3  
	mov        r1  , #1 
	cmp        r3  ,  r4  
	blt       test_variable_lt_test_variable2_res_less_than 
	mov        r1  , #0 
test_variable_lt_test_variable2_res_less_than:
	mov        r1  , #1 
	cmp        r4  ,  r4  
	bgt       assert_variable_gt_test_variable2_res_greater_than 
	mov        r1  , #0 
assert_variable_gt_test_variable2_res_greater_than:
	mov        r2  , #1 
	cmp        r1  ,  r3  
	beq       assert_variable_test_variable2_res_reg_eq_test_variable_res_equal 
	mov        r2  , #0 
assert_variable_test_variable2_res_reg_eq_test_variable_res_equal:
	mov        r0  ,  r2  
test_function_end:
	pop       {pc, r4 - r7}