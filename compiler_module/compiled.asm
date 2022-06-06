
literal_value_2_32_33_reg                                    [2, None]
literal_value_2_32_33_n_res_reg                              [3, None]
r0                                                           [10, None]
literal_value_2_95_96_reg                                    [2, None]
literal_value_2_95_96_n_res_reg                              [6, None]
{                                                            [4, None]
}                                                            [4, None]
literal_value_1_75_76_reg                                    [2, None]
literal_value_1_75_76_n_res_reg                              [6, None]
function_return_reg                                          [2, None]

.global fibonacci 
fibonacci: 
	push     { lr , r4 - r7 } 
	mov       r1  , #2 
	mov       r2  , #1 
	cmp       r0  ,  r1  
	blt      literal_value_2_32_33_lt_n_res_less_than 
	mov       r2  , #0 
literal_value_2_32_33_lt_n_res_less_than: 
	cmp       r2  , #0 
	beq      fibonacci_if_end_0_26_53 
	mov        r0   ,   r0   
	b        fibonacci_end 
fibonacci_if_end_0_26_53: 
	mov       r1  , #2 
	sub       r1  ,  r0  ,  r1  
	push       { r0 , r2 , r3 , }
	mov       r0  ,  r1  
	bl       fibonacci 
	mov       r1  ,  r0  
	pop        { r0 , r2 , r3 , }
	mov       r2  , #1 
	sub       r2  ,  r0  ,  r2  
	push       { r0 , r1 , r3 , }
	mov       r0  ,  r2  
	bl       fibonacci 
	mov       r2  ,  r0  
	pop        { r0 , r1 , r3 , }
	add       r1  ,  r1  ,  r2  
	mov       r0  ,  r1  
fibonacci_end: 
	pop      { pc , r4 - r7 } 


None
program finished in 0.00155 s
