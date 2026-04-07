obj-m += memalloc.o
memalloc-y += memalloc-main.o memalloc-helper.o
ccflags-y := -Wno-error=missing-prototypes -Wno-error=restrict -Wno-error=unused-variable

all:
	make -C /usr/src/linux M=$(PWD) modules

clean:
	make -C /usr/src/linux M=$(PWD) clean

