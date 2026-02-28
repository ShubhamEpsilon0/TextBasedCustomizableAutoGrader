obj-m = producer_consumer.o
ccflags-y := -Wno-error=missing-prototypes -Wno-error=restrict

all:
	make -C /usr/src/linux M=$(PWD) modules

clean:
	make -C /usr/src/linux M=$(PWD) clean
