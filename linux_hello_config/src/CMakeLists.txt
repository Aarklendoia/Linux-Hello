cmake_minimum_required(VERSION 3.20)
project(linux-hello-config-launcher)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_CXX_STANDARD 17)

find_package(Qt6 COMPONENTS Core Gui Qml Quick REQUIRED)

add_executable(linux-hello-config-launcher qml_launcher.cpp)

target_link_libraries(linux-hello-config-launcher
    Qt6::Core
    Qt6::Gui
    Qt6::Qml
    Qt6::Quick
)

# Installation
install(TARGETS linux-hello-config-launcher DESTINATION bin RENAME linux-hello-config)
