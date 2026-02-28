objects = process_generator
CC=gcc

all: $(objects)

$(objects): %: %.c
	$(CC) $(CFLAGS) -o $@ $<

clean: $(objects)
	rm $(objects)
