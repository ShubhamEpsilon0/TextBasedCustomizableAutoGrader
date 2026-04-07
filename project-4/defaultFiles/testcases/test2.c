#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdbool.h>
#include <sys/mman.h>
#include <unistd.h>
#include <linux/ioctl.h>
#include <sys/ioctl.h>
#include <assert.h>

#include "../common.h"
#include "helper.h"

bool test_allocate(void);
bool test_free(void);
static int setup_memory_region(unsigned long start, unsigned long end);

/* 
 * Description:
 * This test allocates a page with R+W permissions and checks that
 * the page can be allocated, accessed, and freed correctly.
 */

bool test_allocate(void){
    setup_memory_region((0x10000000 - 0x1000), (0x10000000 + 0x2000));
    struct alloc_info* allocCall;    
    allocCall = malloc(sizeof(struct alloc_info));
    allocCall->vaddr                = 0x10000000;
    allocCall->num_pages            = 1;
    allocCall->write                = true;
    if (ioctl(devfd, ALLOCATE, allocCall) < 0) {
        return false;
    }

    /* Testing read permissions on allocated page */
    int* vaddr_ptr = (int*) allocCall->vaddr;
    assert(*vaddr_ptr == 0);
    printf("Passed: READ\n");

    /* Testing write permissions on allocated page */
    *vaddr_ptr = 1;
    assert(*vaddr_ptr == 1);
    printf("Passed: WRITE\n");

    return true;
}

static int setup_memory_region(unsigned long start, unsigned long end)
{
    unsigned long page_size = 0x1000;
    unsigned long size;
    unsigned long hole_start;
    unsigned long hole_size;
    unsigned long addr;
    char *base;

    if (start >= end) {
        printf(stderr, "setup_memory_region: invalid range\n");
        return -1;
    }

    size = end - start;
    if (size < 3 * page_size) {
        printf("setup_memory_region: need at least 3 pages to create a middle hole\n");
        return -1;
    }

    base = mmap((void *)start,size, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED_NOREPLACE,-1, 0);
    if (base == MAP_FAILED) {
        printf("mmap failed\n");
        return -1;
    }

    /*
     * Touch each page so the mapping is definitely populated.
     */
    for (addr = start; addr < end; addr += page_size) {
        *(char *)addr = 'a';
    }

    hole_start = start + page_size;
    hole_size  = size - 2 * page_size;

    if (munmap((void *)hole_start, hole_size) < 0) {
        printf("munmap failed\n");
        return -1;
    }

    return 0;
}

int main(void)
{
    printf("Executing: TEST2\n");

    if (!open_device_driver()) return -1;
    
    if(!test_allocate()) {
    	printf("Allocate Failed!\n");
        return -1;
    }

    printf("Passed: TEST2\n");
    close(devfd);
    return 0;
}


