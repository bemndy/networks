CC=gcc
CFLAGS=-Wall -g -std=gnu99 
LIBS = -lcrypto
DEPS = cgrab.h
OBJ = cgrab.o

# I want to test locally on my macbook, but I need openssl depen, for crypto used in cgrab.c
# So I am adding this to conditonally use the one installed on my macbook/brew

ifeq ($(shell uname),Darwin)
  OPENSSL := $(shell brew --prefix openssl@3)
  CFLAGS += -I$(OPENSSL)/include
  LIBS   += -L$(OPENSSL)/lib
  endif

%.o: %.c $(DEPS)
	$(CC) $(CFLAGS) -c -o $@ $< 

cgrab: $(OBJ)
	$(CC) $(CFLAGS) -o $@ $^ $(LIBS)

clean:
	rm -f *.o cgrab