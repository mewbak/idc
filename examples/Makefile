# Makefile for the COM examples.

# It requires the 8086 development environment available from
# http://www.cix.co.uk/~mayday/ and http://elks.sourceforge.net/

CC = gcc
CFLAGS = -m32

AS = as
ASFLAGS = 

LD = ld
LDFLAGS = 


#all: $(basename $(wildcard *.s *.c))
all: $(patsubst %.c,%.s,$(wildcard *.c))


%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

%.s: %.c
	$(CC) $(CFLAGS) -S $<

%.o: %.s
	$(AS) $(ASFLAGS) -o $@ $<

%: %.o
	$(LD) $(LDFLAGS) -o $@ $<


clean:
	rm -f *.o


.PHONY: all clean
