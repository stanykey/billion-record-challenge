#include <filesystem>
#include <format>
#include <iostream>


int main(int argc, const char* argv[]) {
    if (argc != 2) {
        std::cout << "Usage: billion-record-challenge <SOURCE>\n";
        return 1;
    }

    const auto source_path = std::filesystem::path(argv[1]);
    if (!std::filesystem::is_regular_file(source_path)) {
        std::cout << std::format("File does not exist: {}\n", source_path.string());
        return 1;
    }

    return 0;
}
