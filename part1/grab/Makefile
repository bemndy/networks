CC=gcc
CFLAGS=-Wall -g -std=c99 
LIBS = -lcrypto
DEPS = cgrab.h
OBJ = cgrab.o

%.o: %.c $(DEPS)
	$(CC) $(CFLAGS) -c -o $@ $< 

cgrab: $(OBJ)
	$(CC) $(CFLAGS) -o $@ $^ $(LIBS)

clean:
	rm -f *.o cgrab