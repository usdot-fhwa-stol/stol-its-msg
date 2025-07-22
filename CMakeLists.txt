cmake_minimum_required(VERSION 3.14)
project(stol_its_msg C CXX) 

set(CMAKE_C_STANDARD 99)
set(CMAKE_CXX_STANDARD 17)

message(STATUS "C Compiler: ${CMAKE_C_COMPILER}")
message(STATUS "C++ Compiler: ${CMAKE_CXX_COMPILER}")

file(GLOB SPEC_FILES "${CMAKE_SOURCE_DIR}/asn1/raw/carma_j2735/*.asn1")
foreach(spec_file ${SPEC_FILES})
    get_filename_component(fname ${spec_file} NAME)
    string(REPLACE ".asn1" "" fname ${fname})
    message(STATUS "Processing ASN.1 specification file: ${fname}")

    # just use the filename without extension for the directory

    set(SRC_DIR "${CMAKE_SOURCE_DIR}/stol_its_coding/${fname}/src")
    set(INC_DIR "${CMAKE_SOURCE_DIR}/stol_its_coding/${fname}/include")
    set(OBJ_DIR "${CMAKE_BINARY_DIR}/${fname}/obj")

    file(GLOB HEADER_FILES "${INC_DIR}/*.h")
    foreach(header ${HEADER_FILES})
        get_filename_component(h_fname ${header} NAME)
        configure_file(${header} ${CMAKE_BINARY_DIR}/asn1c/${fname}/${h_fname} COPYONLY)
    endforeach()

    file(GLOB C_SOURCE_FILES "${SRC_DIR}/*.c")
    foreach(source ${C_SOURCE_FILES})
        get_filename_component(c_fname ${source} NAME)
        configure_file(${source} ${CMAKE_BINARY_DIR}/asn1c/${fname}/${c_fname} COPYONLY)
    endforeach()


    file(GLOB ASN1_FILES "${CMAKE_SOURCE_DIR}/build/asn1c/${fname}/*")
    add_library(c_objlib_${fname} OBJECT ${ASN1_FILES})


    set(CODEGEN_DIR "${CMAKE_SOURCE_DIR}/stol_its_conversion/${fname}/*")

    file(GLOB CODEGEN_FILES "${CODEGEN_DIR}")
    foreach(file ${CODEGEN_FILES})
        get_filename_component(cg_fname ${file} NAME)
        configure_file(${file} ${CMAKE_BINARY_DIR}/codegen/${fname}/${cg_fname} COPYONLY)
    endforeach()


    file(GLOB HEADER_FILES "${INC_DIR}/*.h")
    foreach(header ${HEADER_FILES})
        get_filename_component(cg_h_fname ${header} NAME)
        configure_file(${header} ${CMAKE_BINARY_DIR}/codegen/${fname}/${cg_h_fname} COPYONLY)
    endforeach()

    # add main.cpp and json.hpp to the codegen files
    configure_file(${CMAKE_SOURCE_DIR}/assets/TestMessage00.json ${CMAKE_BINARY_DIR}/TestMessage00.json COPYONLY)
    configure_file(${CMAKE_SOURCE_DIR}/assets/TestMessage00_main.cpp ${CMAKE_BINARY_DIR}/codegen/${fname}/TestMessage00_main.cpp COPYONLY)
    configure_file(${CMAKE_SOURCE_DIR}/assets/json.hpp ${CMAKE_BINARY_DIR}/codegen/${fname}/json.hpp COPYONLY)

    file(GLOB CODEGEN_ALL_FILES "${CMAKE_BINARY_DIR}/codegen/${fname}/*")
    add_library(cpp_objlib_${fname} OBJECT ${CODEGEN_ALL_FILES})

    # Final executable using both
    add_executable(decode_${fname}
        $<TARGET_OBJECTS:c_objlib_${fname}>
        $<TARGET_OBJECTS:cpp_objlib_${fname}>
    )
endforeach()




