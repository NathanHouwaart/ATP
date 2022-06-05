test_function_if:
	push      {lr, r4 - r7}
	add       test_variable_reg , r1 , r0 
	mov       literal_value_100_97_100_reg , #100 
	mov       literal_value_100_97_100_test_variable_res_reg , #1 
	cmp       test_variable_reg , literal_value_100_97_100_reg 
	bgt       literal_value_100_97_100_gt_test_variable_res_greater_than 
	mov       literal_value_100_97_100_test_variable_res_reg , #0 
literal_value_100_97_100_gt_test_variable_res_greater_than:
	cmp       literal_value_100_97_100_test_variable_res_reg , #0 
	beq       test_function_if_if_false_0_79_305 
	mov       literal_value_120_131_134_reg , #120 
	mov       literal_value_120_131_134_test_variable_res_reg , #1 
	cmp       test_variable_reg , literal_value_120_131_134_reg 
	bgt       literal_value_120_131_134_gt_test_variable_res_greater_than 
	mov       literal_value_120_131_134_test_variable_res_reg , #0 
literal_value_120_131_134_gt_test_variable_res_greater_than:
	cmp       literal_value_120_131_134_test_variable_res_reg , #0 
	beq       test_function_if_if_false_1_113_224 
	mov       test_variable_reg , #142 
	b         test_function_if_if_end_1_113_224 
test_function_if_if_false_1_113_224:
	mov       test_variable_reg , #101 
test_function_if_if_end_1_113_224:
	b         test_function_if_if_end_0_79_305 
test_function_if_if_false_0_79_305:
	mov       literal_value_15_261_263_reg , #15 
	mov       literal_value_15_261_263_test_variable_res_reg , #1 
	cmp       test_variable_reg , literal_value_15_261_263_reg 
	bgt       literal_value_15_261_263_gt_test_variable_res_greater_than 
	mov       literal_value_15_261_263_test_variable_res_reg , #0 
literal_value_15_261_263_gt_test_variable_res_greater_than:
	cmp       literal_value_15_261_263_test_variable_res_reg , #0 
	beq       test_function_if_if_end_1_243_303 
	mov       test_variable_reg , #15 
test_function_if_if_end_1_243_303:
test_function_if_if_end_0_79_305:
	mov       r0 , test_variable_reg 
test_function_if_end:
	pop       {pc, r4 - r7}


test_variable_reg                                            [8, None]
r1                                                           [1, None]
r0                                                           [2, None]
literal_value_100_97_100_reg                                 [2, None]
literal_value_100_97_100_test_variable_res_reg               [3, None]
literal_value_120_131_134_reg                                [2, None]
literal_value_120_131_134_test_variable_res_reg              [3, None]
literal_value_15_261_263_reg                                 [2, None]
literal_value_15_261_263_test_variable_res_reg               [3, None]

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
program finished in 0.00207 s
