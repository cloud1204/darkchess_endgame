CXX = g++
CXXFLAGS = -std=c++17 -O2 -Wall -Wextra

SOURCES = main.cpp piece.cpp state.cpp endgame_table.cpp utils.cpp
OBJECTS = $(SOURCES:.cpp=.o)
HEADERS = piece.h state.h endgame_table.h utils.h
TARGET = endgame

# Default target
all: $(TARGET)

# Link object files to create executable
$(TARGET): $(OBJECTS)
	$(CXX) $(OBJECTS) -o $(TARGET)

# Compile source files to object files
%.o: %.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Create cached endgame boards directory if it doesn't exist
setup:
	mkdir -p cached_endgame_boards

# Clean build artifacts
clean:
	rm -f $(OBJECTS) $(TARGET)

# Clean everything including cache
distclean: clean
	rm -rf cached_endgame_boards

# Rebuild everything
rebuild: clean all

# Install (copy to system path, optional)
install: $(TARGET)
	cp $(TARGET) /usr/local/bin/

# Uninstall
uninstall:
	rm -f /usr/local/bin/$(TARGET)

# Show help
help:
	@echo "Available targets:"
	@echo "  all       - Build the executable (default)"
	@echo "  clean     - Remove object files and executable"
	@echo "  distclean - Remove everything including cache"
	@echo "  rebuild   - Clean and rebuild"
	@echo "  setup     - Create cache directory"
	@echo "  install   - Install to system path"
	@echo "  uninstall - Remove from system path"
	@echo "  help      - Show this help"

# Declare phony targets
.PHONY: all clean distclean rebuild setup install uninstall help

# Debug info (optional)
debug: CXXFLAGS += -g -DDEBUG
debug: $(TARGET)

# Release with optimization
release: CXXFLAGS += -O3 -DNDEBUG
release: clean $(TARGET)