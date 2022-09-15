#include <stdio.h>


class Foo {
    public:
        int bar;
        static int evaluate(int a, int b) {
            return a + b;
        }
};

float sum(float* nums, int size) {
    float total = 0;
    for(int i=0; i<size; i++) {
        total += nums[i];
    }
    return total;
}


int main() {

    float nums[5] = {1,2,3,4};

    float t = sum(nums, 5);

    typedef int(*fptr)(int, int);
    fptr test = &Foo::evaluate;

    printf("this is a result: %d\n", test(3,4));

    return 0;
}