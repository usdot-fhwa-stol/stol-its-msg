cmake_minimum_required(VERSION 3.14)
project(stol_its_msg C CXX) 

set(CMAKE_C_STANDARD 99)
set(CMAKE_CXX_STANDARD 17)

message(STATUS "C Compiler: ${CMAKE_C_COMPILER}")
message(STATUS "C++ Compiler: ${CMAKE_CXX_COMPILER}")

set(SRC_DIR "${CMAKE_SOURCE_DIR}/stol_its_coding/src")
set(INC_DIR "${CMAKE_SOURCE_DIR}/stol_its_coding/include")
set(OBJ_DIR "${CMAKE_BINARY_DIR}/obj")

file(GLOB HEADER_FILES "${INC_DIR}/*.h")
foreach(header ${HEADER_FILES})
    get_filename_component(fname ${header} NAME)
    configure_file(${header} ${CMAKE_BINARY_DIR}/asn1c/${fname} COPYONLY)
endforeach()

file(GLOB C_SOURCE_FILES "${SRC_DIR}/*.c")
foreach(source ${C_SOURCE_FILES})
    get_filename_component(fname ${source} NAME)
    configure_file(${source} ${CMAKE_BINARY_DIR}/asn1c/${fname} COPYONLY)
endforeach()


file(GLOB ASN1_FILES "${CMAKE_SOURCE_DIR}/build/asn1c/*")
add_library(c_objlib OBJECT ${ASN1_FILES})


set(CODEGEN_DIR "${CMAKE_SOURCE_DIR}/stol_its_conversion/*")

file(GLOB CODEGEN_FILES "${CODEGEN_DIR}")
foreach(file ${CODEGEN_FILES})
    get_filename_component(fname ${file} NAME)
    configure_file(${file} ${CMAKE_BINARY_DIR}/codegen/${fname} COPYONLY)
endforeach()


file(GLOB HEADER_FILES "${INC_DIR}/*.h")
foreach(header ${HEADER_FILES})
    get_filename_component(fname ${header} NAME)
    configure_file(${header} ${CMAKE_BINARY_DIR}/codegen/${fname} COPYONLY)
endforeach()

# add main.cpp and json.hpp to the codegen files
configure_file(${CMAKE_SOURCE_DIR}/assets/CommonSafetyRequest.json ${CMAKE_BINARY_DIR}/CommonSafetyRequest.json COPYONLY)
configure_file(${CMAKE_SOURCE_DIR}/assets/main1.cpp ${CMAKE_BINARY_DIR}/codegen/main1.cpp COPYONLY)
configure_file(${CMAKE_SOURCE_DIR}/assets/json.hpp ${CMAKE_BINARY_DIR}/codegen/json.hpp COPYONLY)

file(GLOB CODEGEN_ALL_FILES "${CMAKE_BINARY_DIR}/codegen/*")
add_library(cpp_objlib OBJECT ${CODEGEN_ALL_FILES})

# Final executable using both
add_executable(decode
    $<TARGET_OBJECTS:c_objlib>
    $<TARGET_OBJECTS:cpp_objlib>
)




