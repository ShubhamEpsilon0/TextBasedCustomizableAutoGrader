obj-m += kmod.o
kmod-y += kmod-main.o kmod-ioctl.o
ccflags-y += -Wno-error=implicit-function-declaration -Wno-error=unused-variable -Wno-error=missing-prototypes -Wno-error=unused-result

all:
	make -C /usr/src/linux M=$(PWD) modules

clean:
	make -C /usr/src/linux M=$(PWD) clean

install:
	insmod kmod.ko
remove: 
	rmmod kmod
