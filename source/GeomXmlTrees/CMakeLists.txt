cmake_minimum_required(VERSION 2.6)
set(PROJECT geomxml)
project(${PROJECT})


# all source files
file(GLOB SOURCES
	tinyxml/*.h
	tinyxml/*.cpp
	*.h
	*.cpp)

# Specify C++11 flag for g++
if(CMAKE_COMPILER_IS_GNUCXX OR "${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17")
endif()
if(CMAKE_COMPILER_IS_GNUCXX)
	message(STATUS "GCC detected, adding compile flags")
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")
endif()


# Include path for additional CMake library finding scripts
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/")

# Add directory containing FindSFML.cmake to module path
set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake/Modules/;${CMAKE_MODULE_PATH};${CMAKE_SOURCE_DIR}")


# Find SFML
#find_package( SFML 2 COMPONENTS graphics window system )


if(WIN32)
	add_executable(${PROJECT} WIN32 ${SOURCES})
else()
	add_executable(${PROJECT} ${SOURCES})
endif()


#  C++17
#set(CMAKE_CXX_STANDARD 17)
#set(CMAKE_CXX_STANDARD_REQUIRED ON)
#set(CMAKE_CXX_EXTENSIONS OFF)
#set_target_properties(${PROJECT} PROPERTIES CXX_STANDARD 17 CXX_EXTENSIONS OFF)
target_compile_features(${PROJECT} PRIVATE cxx_std_17)

target_link_libraries(${PROJECT_NAME} stdc++fs)


#target_link_libraries(${PROJECT} ${SFML_LIBRARIES})
#if(WIN32)
#	target_link_libraries(${PROJECT} "-lopengl32 -lglu32 -lgdi32")
#else()
#	target_link_libraries(${PROJECT} "-lGL")
#endif()
