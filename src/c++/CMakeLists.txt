find_package(cxxopts CONFIG REQUIRED)

add_executable(create-measurements create-measurements.cpp)
target_link_libraries(create-measurements PRIVATE cxxopts::cxxopts)

add_executable(billion-record-challenge billion-record-challenge.cpp)
target_link_libraries(billion-record-challenge PRIVATE cxxopts::cxxopts)
