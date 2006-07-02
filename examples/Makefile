# Makefile


PYTHON = python
export PYTHONPATH = ..

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

CFLAGS += -fomit-frame-pointer -fno-builtin -fno-hosted -foptimize-register-move -mregparm=3

AS = as
ASFLAGS = 

LD = ld
LDFLAGS = 


all: \
	$(patsubst %.c,%.s,$(wildcard *.c)) \
	$(patsubst %.s,%.aterm,$(wildcard *.s))


%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

%.s: %.c
	$(CC) $(CFLAGS) -S $<

%.o: %.s
	$(AS) $(ASFLAGS) -o $@ $<

%: %.o
	$(LD) $(LDFLAGS) -o $@ $<

.PRECIOUS: %s

%.aterm: %.s
	$(PYTHON) ../util/translate.py $<


clean:
	rm -f $(patsubst %.s,%.aterm,$(wildcard *.s))
	rm -f $(patsubst %.c,%.s,$(wildcard *.c))


.PHONY: all clean
