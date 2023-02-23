CFLAGS=-W -Wall -g

all: wrapper test

clean:
	rm -f *.o wrapper test

wrapper: util.o filesystem.o wrapper.o
	$(CC) $(CFLAGS) $^ -o $@

test: util.o filesystem.o test.o
	$(CC) $(CFLAGS) $^ -o $@

