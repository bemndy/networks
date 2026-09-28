CC=gcc
CFLAGS=-Wall -g -std=c99 
DEPS = cgrab.h
OBJ = cgrab.o

%.o: %.c $(DEPS)
	$(CC) $(CFLAGS) -c -o $@ $< 

cgrab: $(OBJ)
	$(CC) $(CFLAGS) -o $@ $^ 

clean:
	rm -f *.o cgrab