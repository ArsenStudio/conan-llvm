project(PackageTest CXX)
cmake_minimum_required(VERSION 2.8.12)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

include ("share/llvm/cmake/LLVMConfig")
include ("share/clang/cmake/ClangConfig")

IF(NOT LLVM_INSTALL_PREFIX)
    MESSAGE(FATAL_ERROR "ERROR! LLVM NOT FOUND!")
ENDIF()

add_executable(example example.cpp)
target_link_libraries(example ${CONAN_LIBS})