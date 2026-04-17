cmake_minimum_required(VERSION 3.10)
project(libqalculate VERSION 5.10.0 LANGUAGES C CXX)

# Options
option(BUILD_TEXTPORT "Build the text port (qalc)" ON)
option(BUILD_TESTS "Build test programs" OFF)
option(BUILD_UNITTESTS "Build unittest runner" ON)
option(ENABLE_COMPILED_DEFINITIONS "Compile definitions into the library" OFF)
option(ENABLE_INSECURE "Enable insecure functions and variables" ON)
option(WITH_LIBCURL "Use libcurl for exchange rates" ON)
option(WITH_ICU "Use ICU for unicode support" ON)
option(WITH_READLINE "Use readline for text port" ON)

# Configure header
include(CheckIncludeFile)
include(CheckIncludeFileCXX)
include(CheckFunctionExists)
include(CheckLibraryExists)

check_include_file(gmp.h HAVE_GMP_H)
check_include_file(mpfr.h HAVE_MPFR_H)
check_include_file_cxx(unordered_map HAVE_UNORDERED_MAP)
check_function_exists(pipe2 HAVE_PIPE2)
check_include_file(iconv.h HAVE_ICONV)
check_include_file(inttypes.h HAVE_INTTYPES_H)
check_include_file(memory.h HAVE_MEMORY_H)
check_include_file(stdint.h HAVE_STDINT_H)
check_include_file(stdlib.h HAVE_STDLIB_H)
check_include_file(strings.h HAVE_STRINGS_H)
check_include_file(string.h HAVE_STRING_H)
check_include_file(sys/stat.h HAVE_SYS_STAT_H)
check_include_file(sys/types.h HAVE_SYS_TYPES_H)
check_include_file(unistd.h HAVE_UNISTD_H)

if(ENABLE_COMPILED_DEFINITIONS)
    set(GEN_DEFINITIONS_FILE "${CMAKE_CURRENT_BINARY_DIR}/definitions.cc")
    file(WRITE "${GEN_DEFINITIONS_FILE}" "#include <libqalculate/definitions.h>\n\n")
     file(APPEND "${GEN_DEFINITIONS_FILE}" "const char * const definitions_gresource_xml = nullptr;\n\n")
    
    set(DATA_FILES_COMPILED
        "currencies.xml" "currencies_xml"
        "datasets.xml" "datasets_xml"
        "elements.xml" "elements_xml"
        "eurofxref-daily.xml" "eurofxref_daily_xml"
        "functions.xml" "functions_xml"
        "planets.xml" "planets_xml"
        "prefixes.xml" "prefixes_xml"
        "units.xml" "units_xml"
        "variables.xml" "variables_xml"
        "rates.json" "rates_json"
    )
    
    list(LENGTH DATA_FILES_COMPILED LEN)
    math(EXPR STOP "${LEN} - 1")
    foreach(I RANGE 0 ${STOP} 2)
        list(GET DATA_FILES_COMPILED ${I} FILE)
        math(EXPR J "${I} + 1")
        list(GET DATA_FILES_COMPILED ${J} VAR)
        
        set(FILE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/data/${FILE}")
        if(NOT EXISTS "${FILE_PATH}")
            set(FILE_PATH "${FILE_PATH}.in")
        endif()
        
        if(EXISTS "${FILE_PATH}")
            file(READ "${FILE_PATH}" CONTENT)
            string(REPLACE "\\" "\\\\" CONTENT "${CONTENT}")
            string(REPLACE "\"" "\\\"" CONTENT "${CONTENT}")
            string(REPLACE "\n" "\\n" CONTENT "${CONTENT}")
            string(REPLACE "\r" "" CONTENT "${CONTENT}")
            file(APPEND "${GEN_DEFINITIONS_FILE}" "const char * const ${VAR} = \"${CONTENT}\";\n")
         else()
             file(APPEND "${GEN_DEFINITIONS_FILE}" "const char * const ${VAR} = nullptr;\n")
         endif()
    endforeach()
    
    list(APPEND LIBQALCULATE_SOURCES "${GEN_DEFINITIONS_FILE}")
endif()

if(NOT ENABLE_INSECURE)
    set(DISABLE_INSECURE 1)
endif()

# Dependencies
find_package(LibXml2)
if(NOT LIBXML2_FOUND AND NOT LibXml2_FOUND)
    find_library(LIBXML2_LIBRARY NAMES libxml2)
    find_path(LIBXML2_INCLUDE_DIR NAMES libxml/xmlmemory.h PATH_SUFFIXES libxml2)
    if(LIBXML2_LIBRARY)
        set(LIBXML2_FOUND TRUE)
        set(LIBXML2_LIBRARIES ${LIBXML2_LIBRARY})
    endif()
endif()
if(LIBXML2_FOUND OR LibXml2_FOUND)
    set(HAVE_LIBXML2 1)
endif()
if(WITH_LIBCURL)
    find_package(CURL REQUIRED)
    set(HAVE_LIBCURL 1)
endif()

if(WITH_ICU)
    find_package(ICU 78 REQUIRED COMPONENTS uc dt i18n)
    if(NOT ICU_FOUND)

    else()
        set(HAVE_ICU 1)
    endif()
endif()

# Find GMP and MPFR
# These are often not provided by find_package on Windows
# We'll try to find them or assume they are available if the user provides paths
find_library(GMP_LIBRARY NAMES gmp libgmp)
find_path(GMP_INCLUDE_DIR NAMES gmp.h)
if(GMP_LIBRARY AND GMP_INCLUDE_DIR)
    set(HAVE_GMP_H 1)
else()
    message(FATAL_ERROR "GMP not found. Please provide GMP_LIBRARY and GMP_INCLUDE_DIR")
endif()

find_library(MPFR_LIBRARY NAMES mpfr libmpfr)
find_path(MPFR_INCLUDE_DIR NAMES mpfr.h)
if(MPFR_LIBRARY AND MPFR_INCLUDE_DIR)
    set(HAVE_MPFR_H 1)
else()
    message(FATAL_ERROR "MPFR not found. Please provide MPFR_LIBRARY and MPFR_INCLUDE_DIR")
endif()

# if(WITH_READLINE)
find_library(READLINE_LIBRARY NAMES readline)
find_path(READLINE_INCLUDE_DIR NAMES readline/readline.h)
if(READLINE_LIBRARY)
    set(HAVE_LIBREADLINE 1)
    set(HAVE_HISTORY 1)
endif()
# endif()

# Threading
find_package(Threads REQUIRED)
if(Threads_FOUND)
    set(HAVE_PTHREADS 1)
endif()

# Iconv
find_package(Iconv)
if(Iconv_FOUND)
    set(HAVE_ICONV 1)
endif()

# Package data directory
if(NOT PACKAGE_DATA_DIR)
    set(PACKAGE_DATA_DIR "${CMAKE_INSTALL_PREFIX}/share/qalculate")
endif()

configure_file(config.h.cmake config.h)

# Include directories
include_directories(
    ${CMAKE_CURRENT_BINARY_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/libqalculate
    ${LIBXML2_INCLUDE_DIR}
    ${GMP_INCLUDE_DIR}
    ${MPFR_INCLUDE_DIR}
)

if(HAVE_LIBCURL)
    include_directories(${CURL_INCLUDE_DIRS})
endif()
if(HAVE_ICU)
    include_directories(${ICU_INCLUDE_DIRS})
endif()
if(Iconv_FOUND)
    include_directories(${Iconv_INCLUDE_DIRS})
endif()

# Add definitions for MSVC
add_definitions(-DHAVE_CONFIG_H)
if(MSVC)
    set(CMAKE_CXX_STANDARD 20)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)
    add_definitions(-D_CRT_SECURE_NO_WARNINGS -D_CRT_NONSTDC_NO_DEPRECATE)
    add_definitions(-DNOMINMAX)
endif()

# libqalculate library
set(LIBQALCULATE_SOURCES
    libqalculate/Function.cc
    libqalculate/Calculator.cc
    libqalculate/Calculator-plot.cc
    libqalculate/Calculator-parse.cc
    libqalculate/Calculator-definitions.cc
    libqalculate/Calculator-calculate.cc
    libqalculate/Calculator-convert.cc
    libqalculate/DataSet.cc
    libqalculate/Variable.cc
    libqalculate/ExpressionItem.cc
    libqalculate/Number.cc
    libqalculate/MathStructure.cc
    libqalculate/Prefix.cc
    libqalculate/util.cc
    libqalculate/Unit.cc
    libqalculate/QalculateDateTime.cc
    libqalculate/BuiltinFunctions-util.cc
    libqalculate/BuiltinFunctions-trigonometry.cc
    libqalculate/BuiltinFunctions-matrixvector.cc
    libqalculate/BuiltinFunctions-datetime.cc
    libqalculate/BuiltinFunctions-statistics.cc
    libqalculate/BuiltinFunctions-explog.cc
    libqalculate/BuiltinFunctions-special.cc
    libqalculate/BuiltinFunctions-algebra.cc
    libqalculate/BuiltinFunctions-calculus.cc
    libqalculate/BuiltinFunctions-number.cc
    libqalculate/BuiltinFunctions-combinatorics.cc
    libqalculate/BuiltinFunctions-logical.cc
    libqalculate/MathStructure-factor.cc
    libqalculate/MathStructure-gcd.cc
    libqalculate/MathStructure-integrate.cc
    libqalculate/MathStructure-isolatex.cc
    libqalculate/MathStructure-polynomial.cc
    libqalculate/MathStructure-matrixvector.cc
    libqalculate/MathStructure-print.cc
    libqalculate/MathStructure-differentiate.cc
    libqalculate/MathStructure-calculate.cc
    libqalculate/MathStructure-eval.cc
    libqalculate/MathStructure-convert.cc
    libqalculate/MathStructure-decompose.cc
    libqalculate/MathStructure-limit.cc
)

if(ENABLE_COMPILED_DEFINITIONS)
    set(GEN_DEFINITIONS_FILE "${CMAKE_CURRENT_BINARY_DIR}/definitions.cc")
    file(WRITE "${GEN_DEFINITIONS_FILE}" "#include <libqalculate/definitions.h>\n\n")
     file(APPEND "${GEN_DEFINITIONS_FILE}" "const char * const definitions_gresource_xml = nullptr;\n\n")
    
    set(DATA_FILES_COMPILED
        "currencies.xml" "currencies_xml"
        "datasets.xml" "datasets_xml"
        "elements.xml" "elements_xml"
        "eurofxref-daily.xml" "eurofxref_daily_xml"
        "functions.xml" "functions_xml"
        "planets.xml" "planets_xml"
        "prefixes.xml" "prefixes_xml"
        "units.xml" "units_xml"
        "variables.xml" "variables_xml"
        "rates.json" "rates_json"
    )
    
    list(LENGTH DATA_FILES_COMPILED LEN)
    math(EXPR STOP "${LEN} - 1")
    foreach(I RANGE 0 ${STOP} 2)
        list(GET DATA_FILES_COMPILED ${I} FILE)
        math(EXPR J "${I} + 1")
        list(GET DATA_FILES_COMPILED ${J} VAR)
        
        set(FILE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/data/${FILE}")
        if(NOT EXISTS "${FILE_PATH}")
            set(FILE_PATH "${FILE_PATH}.in")
        endif()
        
        if(EXISTS "${FILE_PATH}")
            file(READ "${FILE_PATH}" CONTENT)
            string(REPLACE "\\" "\\\\" CONTENT "${CONTENT}")
            string(REPLACE "\"" "\\\"" CONTENT "${CONTENT}")
            string(REPLACE "\n" "\\n" CONTENT "${CONTENT}")
            string(REPLACE "\r" "" CONTENT "${CONTENT}")
            file(APPEND "${GEN_DEFINITIONS_FILE}" "const char * const ${VAR} = \"${CONTENT}\";\n")
         else()
             file(APPEND "${GEN_DEFINITIONS_FILE}" "const char * const ${VAR} = nullptr;\n")
         endif()
    endforeach()
    
    list(APPEND LIBQALCULATE_SOURCES "${GEN_DEFINITIONS_FILE}")
endif()

add_library(qalculate SHARED ${LIBQALCULATE_SOURCES})
target_compile_definitions(qalculate PRIVATE LIBQALCULATE_EXPORTS)
set_target_properties(qalculate PROPERTIES
    CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON
    WINDOWS_EXPORT_ALL_SYMBOLS ON
)
target_link_libraries(qalculate
    ${LIBXML2_LIBRARY}
    # Fallback for common Windows names
    ${GMP_LIBRARY}
    ${MPFR_LIBRARY}
    Threads::Threads
)

if(HAVE_LIBCURL)
    target_link_libraries(qalculate ${CURL_LIBRARIES})
endif()
if(HAVE_ICU)
    target_link_libraries(qalculate ${ICU_LIBRARIES} ${ICU_I18N_LIBRARIES} ${ICU_UC_LIBRARIES} ${ICU_DATA_LIBRARIES})
endif()
if(Iconv_FOUND)
    target_link_libraries(qalculate ${Iconv_LIBRARIES})
endif()
if(WIN32)
    target_link_libraries(qalculate bcrypt)
endif()

# qalc executable
if(BUILD_TEXTPORT)
    add_executable(qalc src/qalc.cc)
    target_link_libraries(qalc qalculate)
    # if(HAVE_READLINE)
    target_link_libraries(qalc ${READLINE_LIBRARY} ${READLINE_LIBRARIES})
    target_include_directories(qalc PRIVATE ${READLINE_INCLUDE_DIR})
    # endif()
    if(MSVC)
        set_target_properties(qalc PROPERTIES LINK_FLAGS "/NODEFAULTLIB:LIBCMT")
    endif()
endif()

# Installation
install(TARGETS qalculate qalc
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

install(DIRECTORY libqalculate/ DESTINATION include/libqalculate
    FILES_MATCHING PATTERN "*.h"
)

# Data files
set(DATA_FILES
    currencies.xml
    datasets.xml
    elements.xml
    functions.xml
    planets.xml
    prefixes.xml
    units.xml
    variables.xml
    rates.json
)

foreach(FILE ${DATA_FILES})
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/data/${FILE}.in")
        configure_file("${CMAKE_CURRENT_SOURCE_DIR}/data/${FILE}.in" "${CMAKE_CURRENT_BINARY_DIR}/data/${FILE}" COPYONLY)
    elseif(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/data/${FILE}")
        configure_file("${CMAKE_CURRENT_SOURCE_DIR}/data/${FILE}" "${CMAKE_CURRENT_BINARY_DIR}/data/${FILE}" COPYONLY)
    endif()
endforeach()

install(DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/data/" DESTINATION share/qalculate
    FILES_MATCHING PATTERN "*.xml" PATTERN "*.json"
)
