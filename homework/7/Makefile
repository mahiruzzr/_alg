CXX      ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra
BUILD    := build

DIFF_SRC := src/diff_main.cpp src/diff_dp.cpp src/diff_myers.cpp src/diff_types.cpp
CNK_SRC  := src/cnk.cpp
HEADERS  := src/diff_types.h src/diff_dp.h src/diff_myers.h src/bigint.h

all: $(BUILD)/diff_main.exe $(BUILD)/cnk.exe

$(BUILD):
	mkdir $(BUILD)

$(BUILD)/diff_main.exe: $(DIFF_SRC) $(HEADERS) | $(BUILD)
	$(CXX) $(CXXFLAGS) -o $@ $(DIFF_SRC)

$(BUILD)/cnk.exe: $(CNK_SRC) src/bigint.h | $(BUILD)
	$(CXX) $(CXXFLAGS) -o $@ $(CNK_SRC)

test: all
	$(BUILD)/diff_main.exe selftest

clean:
	-del /q $(BUILD)\*.exe 2>nul || rm -f $(BUILD)/*.exe

.PHONY: all test clean
