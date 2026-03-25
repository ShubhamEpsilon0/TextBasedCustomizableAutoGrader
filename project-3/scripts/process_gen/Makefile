CXX = gcc
CXXFLAGS = -Wall -Wextra -g
TARGET = process_generator
SRC = process_generator.c

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) -o $(TARGET)

clean:
	rm -f $(TARGET)

.PHONY: all clean verbose
