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

static int setup_memory_region(unsigned long start, unsigned long end);

/*
 * Description:
 * This test allocates 199 pages with R+W permissions and 1 page with read-only
 * permission. It checks that the read-only page is correctly set.
 */

static int setup_memory_region(unsigned long start, unsigned long end)
{
    unsigned long size;
    unsigned long hole_start;
    unsigned long hole_size;
    unsigned long addr;
    char *base;

    if (start >= end) {
        fprintf(stderr, "setup_memory_region: invalid range\n");
        return -1;
    }

    if ((start % 0x1000) != 0 || (end % 0x1000) != 0) {
        fprintf(stderr, "setup_memory_region: range must be page aligned\n");
        return -1;
    }

    size = end - start;
    if (size < 3 * 0x1000) {
        fprintf(stderr, "setup_memory_region: need at least 3 pages\n");
        return -1;
    }

    base = mmap((void *)start,size, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED_NOREPLACE,-1, 0);
    if (base == MAP_FAILED) {
        printf("mmap failed\n");
        return -1;
    }

    for (addr = start; addr < end; addr += 0x1000) {
        *(volatile char *)addr = 'a';
    }

    hole_start = start + 0x1000;
    hole_size  = size - (2 * 0x1000);

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
    unsigned long setup_end   = 0x10000000 + (200UL * 0x1000) + 0x1000;
    unsigned long page;
    int *vaddr_ptr;
    unsigned long ro_addr = 0x10000000 + (199UL * 0x1000);

    if (setup_memory_region(setup_start, setup_end) < 0) {
        return false;
    }

    allocCall = malloc(sizeof(struct alloc_info));
    if (!allocCall) {
        perror("malloc");
        return false;
    }

    allocCall->vaddr     = 0x10000000;
    allocCall->num_pages = 199;
    allocCall->write     = true;

    if (ioctl(devfd, ALLOCATE, allocCall) < 0) {
        free(allocCall);
        return false;
    }

    for (page = 0; page < 199; page++) {
        vaddr_ptr = (int *)(0x10000000 + (0x1000 * page));
        printf("READing RW page (%lx)\n", (unsigned long)vaddr_ptr);
        assert(*vaddr_ptr == 0);
    }
    printf("Passed: READ (RW pages)\n");

    for (page = 0; page < 199; page++) {
        vaddr_ptr = (int *)(0x10000000 + (0x1000 * page));
        printf("WRITEing RW page (%lx)\n", (unsigned long)vaddr_ptr);
        *vaddr_ptr = (int)page;
        assert(*vaddr_ptr == (int)page);
    }
    printf("Passed: WRITE (RW pages)\n");

    allocCall->vaddr     = ro_addr;
    allocCall->num_pages = 1;
    allocCall->write     = false;

    if (ioctl(devfd, ALLOCATE, allocCall) < 0) {
        free(allocCall);
        return false;
    }

    vaddr_ptr = (int *)ro_addr;
    printf("READing RO page (%lx)\n", (unsigned long)vaddr_ptr);
    assert(*vaddr_ptr == 0);
    printf("Passed: READ (RO page)\n");

    printf("WRITEing RO page (%lx)\n", (unsigned long)vaddr_ptr);
    *vaddr_ptr = 1234;
    printf("Failed: WRITE is still allowed on RO page.\n");

    free(allocCall);
    return false;
}

int main(void)
{
    printf("Executing: TEST5\n");

    if (!open_device_driver())
        return -1;

    register_segfault_handler();

    if (!test_allocate()) {
        printf("Allocate Failed!\n");
        return -1;
    }

    printf("Passed: TEST5\n");
    close(devfd);
    return 0;
}
