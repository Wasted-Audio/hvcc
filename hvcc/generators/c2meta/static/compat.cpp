#include <cstdlib>
#include <cstddef>

struct _reent;
extern void *memalign(size_t align, size_t size);

extern "C" {

void* _memalign_r(struct _reent* r, size_t alignment, size_t bytes) {
    (void)r;
    return memalign(alignment, bytes);
}

}
