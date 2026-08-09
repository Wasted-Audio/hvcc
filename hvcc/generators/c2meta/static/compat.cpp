#include <cstdlib>

extern "C" {

void* _memalign_r(struct _reent* r, size_t alignment, size_t bytes) {
    (void)r;
    (void)alignment;
    return std::malloc(bytes);
}

}
