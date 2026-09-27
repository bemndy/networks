CC=gcc
CFLAGS=-Wall -g -std=c99 
DEPS = cgrab.h
OBJ = cgrab.o

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

cgrab: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS)

clean:
	rm -f *.o cgrab