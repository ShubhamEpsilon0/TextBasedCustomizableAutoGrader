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

/*
 * Description:
 * This test allocates 4097 pages and checks that allocation fails
 * because the maximum allowed number of pages is 4096.
 */

bool test_allocate(void)
{
    struct alloc_info *allocCall;
    long ret;

    allocCall = malloc(sizeof(struct alloc_info));
    if (!allocCall) {
        perror("malloc");
        return false;
    }

    allocCall->vaddr     = 0x10000000;
    allocCall->num_pages = 4097;
    allocCall->write     = true;

    errno = 0;
    ret = ioctl(devfd, ALLOCATE, allocCall);

    if (ret != -1) {
        printf("Expected allocation failure, but ioctl succeeded.\n");
        free(allocCall);
        return false;
    }

    if (errno != 2) {
        printf("Unexpected errno: %d (%s)\n", errno, strerror(errno));
        free(allocCall);
        return false;
    }

    printf("Allocation failed correctly\n");
    free(allocCall);
    return true;
}

int main(void)
{
    printf("Executing: TEST6\n");

    if (!open_device_driver())
        return -1;

    if (!test_allocate()) {
        printf("Failed: TEST6\n");
        return -1;
    }

    printf("Passed: TEST6\n");
    close(devfd);
    return 0;
}
