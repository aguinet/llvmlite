
cmake_minimum_required(VERSION 2.8.8)

# This will define the name of the solution file in the build directory
project(llvmlite_ffi)

include(ExternalProject)
include(CheckIncludeFiles)

find_package(LLVM REQUIRED CONFIG)

message(STATUS "Found LLVM ${LLVM_PACKAGE_VERSION}")
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")

# Set your project compile flags.
# E.g. if using the C++ header files
# you will need to enable C++11 support
# for your compiler.

include_directories(${LLVM_INCLUDE_DIRS})
add_definitions(${LLVM_DEFINITIONS})

# Look for SVML
set(CMAKE_REQUIRED_INCLUDES ${LLVM_INCLUDE_DIRS})

CHECK_INCLUDE_FILES("llvm/IR/SVML.inc" HAVE_SVML)
if(HAVE_SVML)
    message(STATUS "SVML found")
    add_definitions(-DHAVE_SVML)
else()
    message(STATUS "SVML not found")
endif()


# Define our shared library
add_library(llvmlite SHARED assembly.cpp bitcode.cpp core.cpp initfini.cpp
            module.cpp value.cpp executionengine.cpp transforms.cpp
            passmanagers.cpp targets.cpp dylib.cpp linker.cpp object_file.cpp)

if (MSVC)
  message(STATUS "Compiling with MSVC: compiler-rt/builtins will be statically linked to llvmlite/ffi")
  # Add compiler-rt/builtins
  set(COMPILER_RT_PREFIX ${CMAKE_CURRENT_BINARY_DIR}/compiler_rt_builtins)
  set(COMPILER_RT_BUILTINS_CMAKE_FLAGS
    -DLLVM_CONFIG_PATH=${LLVM_INSTALL_PREFIX}/bin/llvm-config.exe
    # Bug fix: somehow compiler-rt/buitlins does not honor the CMAKE_INSTALL_PREFIX passed throught the cmake_install.cmake script
    -DCMAKE_INSTALL_PREFIX=${COMPILER_RT_PREFIX}
  )
  ExternalProject_add(compiler_rt_builtins
    PREFIX ${COMPILER_RT_PREFIX}
    DOWNLOAD_COMMAND URL http://releases.llvm.org/${LLVM_PACKAGE_VERSION}/compiler-rt-${LLVM_PACKAGE_VERSION}.src.tar.xz URL_HASH SHA256=782edfc119ee172f169c91dd79f2c964fb6b248bd9b73523149030ed505bbe18
    GIT_TAG release_70
    SOURCE_SUBDIR lib/builtins/
    CMAKE_ARGS ${COMPILER_RT_BUILTINS_CMAKE_FLAGS}
    )
  # Get architecture from the triple
  string(FIND ${TARGET_TRIPLE} "-" ARCH_END)
  string(SUBSTRING ${TARGET_TRIPLE} 0 ${ARCH_END} ARCH)

  add_library(compiler_rt_builtins_lib IMPORTED STATIC GLOBAL)
  add_dependencies(compiler_rt_builtins_lib compiler_rt_builtins)
  set_target_properties(compiler_rt_builtins_lib PROPERTIES
      IMPORTED_LOCATION "${COMPILER_RT_PREFIX}/lib/windows/clang_rt.builtins-${ARCH}.lib")
endif()

add_dependencies(llvmlite compiler_rt_builtins)
# Find the libraries that correspond to the LLVM components
# that we wish to use
# llvm_map_components_to_libnames(llvm_libs support core irreader)
set(LLVM_LINK_COMPONENTS
  ${LLVM_TARGETS_TO_BUILD}
  Analysis
  AsmParser
  AsmPrinter
  BinaryFormat
  BitReader
  BitWriter
  CodeGen
  Core
  Coroutines
  Coverage
  DebugInfoCodeView
  DebugInfoMSF
  ExecutionEngine
  GlobalISel
  IRReader
  InstCombine
  Instrumentation
  LTO
  Linker
  MC
  MCDisassembler
  MCJIT
  MCParser
  ObjCARCOpts
  ObjCARCOpts
  Object
  Option
  Passes
  ProfileData
  RuntimeDyld
  ScalarOpts
  SelectionDAG
  Support
  Target
  TransformUtils
  Vectorize
  ipo
)
llvm_map_components_to_libnames(llvm_libs ${LLVM_LINK_COMPONENTS})

# Link against LLVM libraries
target_link_libraries(llvmlite ${llvm_libs} ${compiler_rt_builtins_lib}) 
