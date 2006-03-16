# Makefile


CC = gcc
CFLAGS = -O
ifeq ($(whell uname -m),x86_64)
# force generation of 32bit in 64bit systems
CFLAGS += -m32
endif

AS = as
ASFLAGS = 

LD = ld
LDFLAGS = 

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
	rm -f $(patsubst %.c,%.s,$(wildcard *.c))


.PHONY: all clean
