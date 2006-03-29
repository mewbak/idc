# Makefile


ARCH=$(shell uname -m)

CC = gcc
CFLAGS = -O

ifneq ($(ARCH),i686)
 ifeq ($(ARCH),x86_64)
# force generation of 32bit in 64bit systems
CFLAGS += -m32
 else
$(error An Intel x86 or AMD 64 machine is required.)
 endif
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
