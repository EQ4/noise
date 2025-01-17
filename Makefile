# Files to include
#C_SRC  = $(wildcard *.c)
#OBJECTS := $(patsubst %.c,%.o,$(C_SRC))
OBJECTS = \
		  core/block.o \
		  core/error.o \
		  core/note.o \
		  core/ntype.o \
		  blocks/audio/compressor.o \
		  blocks/audio/function_gen.o \
		  blocks/audio/impulse.o \
		  blocks/audio/lpf.o \
		  blocks/audio/mixer.o \
		  blocks/audio/recorder.o \
		  blocks/audio/sample.o \
		  blocks/audio/wave.o \
		  blocks/io/midi_integrator.o \
		  blocks/io/midi_reader.o \
		  blocks/io/midi_smf.o \
		  blocks/io/midi_writer.o \
		  blocks/io/portaudio.o \
		  blocks/accumulator.o \
		  blocks/constant.o \
		  blocks/debug.o \
		  blocks/fittings.o \
		  blocks/instruments/instrument.o \
		  blocks/instruments/saw.o \
		  blocks/instruments/sine.o \
		  blocks/instruments/snare.o \
		  blocks/maths.o \
		  blocks/sequencer.o \
		  samples/drum.o \

APP_OBJECTS = \
				app/test.o \
				app/test_midi.o \
				app/test_synth.o \
				app/test_sample.o \

APP_TARGETS = $(APP_OBJECTS:app/%.o=noise_%)

TARGET = libnoise.so

CC = gcc

INC = -I.
LIB = -L/usr/local/lib

DEPS = $(OBJECTS:.o=.d) $(APP_OBJECTS:.o=.d)
-include $(DEPS)

# compile and generate dependency info;
%.o: %.c
	gcc -c $(CFLAGS) $*.c -o $*.o
	gcc -MM $(CFLAGS) $*.c > $*.d

# Assembler, compiler, and linker flags
override CFLAGS += $(INC) -O0 -g -Wall -Wextra -Werror -Wno-unused-parameter -Wno-unused -Wwrite-strings -std=c99 -fPIC
#override CFLAGS += $(INC) -O3 -g -Wall -Wextra -Werror -Wno-unused-parameter -Wno-unused -Wwrite-strings -std=c99 
override LFLAGS += $(LIB) $(CFLAGS)
LIBS = -lm -lportaudio -lsndfile

# Targets
.PHONY: clean all python
.DEFAULT_GOAL = all
all: $(TARGET) $(APP_TARGETS) python
clean:
	-rm -f $(OBJECTS) $(APP_OBJECTS:.o=.d) $(OUTPUT) $(DEPS) $(PYTHONLIB) python/build

$(TARGET): $(OBJECTS)
	$(CC) -shared -Wl,-soname,$@ -o $@ $^ $(LIBS)

noise_%: app/%.o $(OBJECTS)
	$(CC) $(LFLAGS) -o $@ $^ $(LIBS) -lnoise -L.

PYTHONLIB = python/_noise.so

$(PYTHONLIB): $(TARGET)
	cd python; python setup.py build_ext --inplace

python: $(PYTHONLIB)
