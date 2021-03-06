#!/bin/bash

cd fear-engine
	./../premake/bin/premake5 gmake2
	sed -i -E "s/-Iinclude/-isystem include/g" Engine.make
	sed -i -E "s/ALL_CXXFLAGS \+=/ALL_CXXFLAGS += -Wunused -Wall -Wextra -Werror -Wno-missing-field-initialized -Wold-style-cast -Wduplicated-branches -Wduplicated-cond -Wshadow/g" Engine.make
	CC=x86_64-w64-mingw32-gcc CXX=x86_64-w64-mingw32-g++ make
cd ..
