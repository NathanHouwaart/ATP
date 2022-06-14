#include "hwlib.hpp"

extern "C" int test_function_greater(int var1, int var2);
extern "C" int test_function_lesser(int var1, int var2);
extern "C" int test_function_equal(int var1, int var2);
extern "C" int test_function_if(int var1, int var2);
extern "C" int fibonacci(int n);
extern "C" int factorial(int n);
extern "C" int even(int n);
extern "C" int odd(int n);
extern "C" int random_function(int n);
extern "C" int sum(int var1, int var2, int var3);
extern "C" int test_test();

int factorial_normal(int n) {
    if (n == 0) {
        return 1;
    }
    return n * factorial_normal(n - 1);
}

int fibonacci_normal(int n) {
    if (n == 0) {
        return 0;
    } else if (n == 1) {
        return 1;
    } else {
        return fibonacci_normal(n - 1) + fibonacci_normal(n - 2);
    }
}

int test_function_greater_normal(int var1, int var2) {
   return var1 > var2;
}

int test_function_lesser_normal(int var1, int var2) {
   return var1 < var2;
}

int test_function_equal_normal(int var1, int var2){
   return var1 == var2;
}

int test_function_if_normal(int var1, int var2){
   int test_variable = var1 + var2;
   if (test_variable > 100) {
      test_variable = 142;
   } else {
      test_variable = 42;
   }
   return test_variable;
}

int test_function_normal(int var1, int var2) {
   if (var1 == 10){
      return var1 + var2;
   }else if (var2 == 2){
      return var1 - var2;
   }else if (var2 == 2){
      return var1 - var2;
   }else{
      if (var1 == 1){
         return var1 + var2;
      }
   }
   return var1 > var2;
   int testvariable = 2 * ((var1 + var2) + 44);
   int testvariable2 = testvariable * (3 + var2);
   int assertvariable = testvariable2 < testvariable;
   return testvariable < (testvariable2 < assertvariable);
}

void test_testfunction_greater(){
   hwlib::cout << "test_function_greater:" << hwlib::endl; 
   hwlib::cout << "with values(1, 2)\t normal: " << test_function_greater_normal(1,2) << "\tcompiled:" << test_function_greater(1, 2) << "\n";
   hwlib::cout << "with values(2, 1)\t normal: " << test_function_greater_normal(2,1) << "\tcompiled:" << test_function_greater(2, 1) << "\n";
   hwlib::cout << "with values(40, 40)\t normal: " << test_function_greater_normal(40,40) << "\tcompiled:" << test_function_greater(40, 40) << "\n";
}

void test_testfunction_lesser(){
   hwlib::cout << "test_function_lesser:" << hwlib::endl;
   hwlib::cout << "with values(1, 2)\t normal: "   << test_function_lesser_normal(1,2) << "\tcompiled:"   << test_function_lesser(1, 2) << "\n";
   hwlib::cout << "with values(2, 1)\t normal: "   << test_function_lesser_normal(2,1) << "\tcompiled:"   << test_function_lesser(2, 1) << "\n";
   hwlib::cout << "with values(40, 40)\t normal: " << test_function_lesser_normal(40,40) << "\tcompiled:" << test_function_lesser(40, 40) << "\n";
}

void test_testfunction_equal(){
   hwlib::cout << "test_function_equal:" << hwlib::endl;
   hwlib::cout << "with values(1, 2)\t normal: "   << test_function_equal_normal(1,2) << "\tcompiled:"   << test_function_equal(1, 2) << "\n";
   hwlib::cout << "with values(2, 1)\t normal: "   << test_function_equal_normal(2,1) << "\tcompiled:"   << test_function_equal(2, 1) << "\n";
   hwlib::cout << "with values(40, 40)\t normal: " << test_function_equal_normal(40,40) << "\tcompiled:" << test_function_equal(40, 40) << "\n";
}

void test_testfunction_if(){
   hwlib::cout << "test_function_if:" << hwlib::endl;
   hwlib::cout << "with values(60,60)\t normal: "   << test_function_if_normal(60,60) << "\tcompiled:"   << test_function_if(60,61) << "\n";
   hwlib::cout << "with values(10,10)\t normal: "   << test_function_if_normal(10,10) << "\tcompiled:"   << 42 << "\n";
}

void application(){
   test_testfunction_greater();
   test_testfunction_lesser();
   test_testfunction_equal();
   test_testfunction_if();

   hwlib::cout << "factorial(9)      \t normal: "   << factorial_normal(9) <<  "\tcompiled:" << factorial(9) << "\n";
   hwlib::cout << "fibonacci(25)     \t normal: "   << fibonacci_normal(25) << "\tcompiled:" << fibonacci(25) << "\n";

   hwlib::cout << "even(10)          " << even(10) << "\n";
   hwlib::cout << "odd(10)           " << odd(10) << "\n";
   
   for(int i = 0; i < 15; i++){
      hwlib::cout << "random_function(" << i << ") \tcompiled:" << random_function(i) << "\n";
   }

   hwlib::cout << "test_test: " << test_test() << "\n"; 

   return;
}

int main( void ){	
   
   namespace target = hwlib::target;   
    
   // wait for the PC console to start
   hwlib::wait_ms( 2000 );

   application();
}