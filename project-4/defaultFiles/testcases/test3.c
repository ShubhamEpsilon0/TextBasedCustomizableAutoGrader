#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdbool.h>
#include <sys/mman.h>
#include <linux/ioctl.h>
#include <sys/ioctl.h>
#include <assert.h>
#include <errno.h>
#include <string.h>

#include "../common.h"
#include "helper.h"

bool test_allocate(void);
bool test_free(void);
static int setup_memory_region(unsigned long start, unsigned long end);

/*
 * Description:
 * This test allocates 4096 pages with R+W permissions and checks that
 * the pages can be allocated, accessed, and freed correctly.
 *
 * Method:
 *   1. Reserve a region with one mapped page before and one mapped page after.
 *   2. Unmap the middle 4096-page hole.
 *   3. Ask the kernel module to fill that hole.
 */

static int setup_memory_region(unsigned long start, unsigned long end)
{
    unsigned long page_size = 0x1000;
    unsigned long size;
    unsigned long hole_start;
    unsigned long hole_size;
    unsigned long addr;
    char *base;

    if (start >= end) {
        fprintf(stderr, "setup_memory_region: invalid range\n");
        return -1;
    }

    if ((start % page_size) != 0 || (end % page_size) != 0) {
        fprintf(stderr, "setup_memory_region: range must be page aligned\n");
        return -1;
    }

    size = end - start;
    if (size < 3 * page_size) {
        fprintf(stderr, "setup_memory_region: need at least 3 pages\n");
        return -1;
    }

    base = mmap((void *)start,
                size,
                PROT_READ | PROT_WRITE,
                MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED_NOREPLACE,
                -1,
                0);
    if (base == MAP_FAILED) {
        fprintf(stderr, "mmap failed: %s\n", strerror(errno));
        return -1;
    }

    for (addr = start; addr < end; addr += page_size) {
        *(volatile char *)addr = 'a';
    }

    hole_start = start + page_size;
    hole_size  = size - (2 * page_size);

    if (munmap((void *)hole_start, hole_size) < 0) {
        fprintf(stderr, "munmap failed: %s\n", strerror(errno));
        munmap((void *)start, size);
        return -1;
    }

    return 0;
}

bool test_allocate(void)
{
    struct alloc_info *allocCall;
    unsigned long setup_start = 0x10000000 - 0x1000;
    unsigned long setup_end   = 0x10000000 + (4096UL * 0x1000) + 0x1000;
    unsigned long pages;
    int *vaddr_ptr;

    if (setup_memory_region(setup_start, setup_end) < 0) {
        return false;
    }

    allocCall = malloc(sizeof(struct alloc_info));
    if (!allocCall) {
        perror("malloc");
        return false;
    }

    allocCall->vaddr     = 0x10000000;
    allocCall->num_pages = 4096;
    allocCall->write     = true;

    if (ioctl(devfd, ALLOCATE, allocCall) < 0) {
        free(allocCall);
        return false;
    }

    for (pages = 0; pages < allocCall->num_pages; pages++) {
        vaddr_ptr = (int *)(allocCall->vaddr + (0x1000 * pages));
        printf("READing (%lx)\n", (unsigned long)vaddr_ptr);
        assert(*vaddr_ptr == 0);
    }
    printf("Passed: READ\n");

    for (pages = 0; pages < allocCall->num_pages; pages++) {
        vaddr_ptr = (int *)(allocCall->vaddr + (0x1000 * pages));
        printf("WRITEing (%lx)\n", (unsigned long)vaddr_ptr);
        *vaddr_ptr = (int)pages;
        assert(*vaddr_ptr == (int)pages);
    }
    printf("Passed: WRITE\n");

    free(allocCall);
    return true;
}

int main(void)
{
    printf("Executing: TEST3\n");

    if (!open_device_driver())
        return -1;

    if (!test_allocate()) {
        printf("Allocate Failed!\n");
        return -1;
    }

    printf("Passed: TEST3\n");
    close(devfd);
    return 0;
}
