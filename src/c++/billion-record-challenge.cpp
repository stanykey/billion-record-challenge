#include <algorithm>
#include <filesystem>
#include <format>
#include <fstream>
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>

#include <cxxopts.hpp>

struct Stats {
    double      min   = std::numeric_limits<double>::max();
    double      max   = std::numeric_limits<double>::min();
    double      sum   = 0.0;
    std::size_t count = 0;

    [[nodiscard]] double mean() const {
        if (count == 0) {
            return 0.0;
        }

        return sum / static_cast<double>(count);
    }
};

[[nodiscard]] double parse_temperature(std::string_view str) {
    double value = 0.0;
    std::ignore  = std::from_chars(str.data(), str.data() + str.size(), value);
    return value;
}

[[nodiscard]] std::string time_past_since(const std::chrono::system_clock::time_point& start_point) {
    const auto current_time = std::chrono::system_clock::now();
    auto       delta        = duration_cast<std::chrono::milliseconds>(current_time - start_point);

    const auto minutes      = duration_cast<std::chrono::minutes>(delta);
    const auto seconds      = duration_cast<std::chrono::seconds>(delta - minutes);
    const auto milliseconds = duration_cast<std::chrono::milliseconds>(delta - minutes - seconds);

    return std::format("{:02d}:{:02d}:{:03d}", minutes.count(), seconds.count(), milliseconds.count());
}

[[nodiscard]] std::unordered_map<std::string, Stats> process_measurements(const std::filesystem::path& source_path) {
    std::unordered_map<std::string, Stats> stats(1'000);

    std::string   line;
    std::ifstream source(source_path);
    while (std::getline(source, line)) {
        const std::size_t delimiter_pos = line.find(';');

        const std::string      name(line.data(), delimiter_pos);
        const std::string_view temperature_string(line.data() + delimiter_pos + 1);

        if (!stats.contains(name)) {
            stats.emplace(name, Stats{});
        }
        auto& record = stats[name];

        const auto temperature = parse_temperature(temperature_string);
        if (temperature < record.min) {
            record.min = temperature;
        }
        if (temperature > record.max) {
            record.max = temperature;
        }

        record.sum += temperature;
        record.count++;
    }

    return stats;
}

void print_statistic(const std::unordered_map<std::string, Stats>& stats) {
    using Item = std::unordered_map<std::string, Stats>::const_iterator;

    std::vector<Item> items;
    items.reserve(stats.size());
    for (auto it = stats.cbegin(); it != stats.cend(); ++it) {
        items.emplace_back(it);
    }
    std::sort(items.begin(), items.end(), [](const Item& lhs, const Item& rhs) { return lhs->first < rhs->first; });

    std::cout << "{";
    for (const auto& item : items) {
        const auto& key  = item->first;
        const auto& data = item->second;
        std::cout << std::format("{}/{}/{:.1f}/{}, ", key, data.min, data.mean(), data.max);
    }
    std::cout << "}\n";
}

int main(int argc, const char* argv[]) {
    std::ios::sync_with_stdio(false);

    cxxopts::Options options("billion-record-challenge", "Read measurements from a CSV file and print statistics.");
    options.add_options()("source", "Source file path", cxxopts::value<std::filesystem::path>())("help", "Print usage");
    options.parse_positional("source");

    const auto args = options.parse(argc, argv);
    if (args.count("help")) {
        std::cout << options.help() << std::endl;
        return 0;
    }

    const auto& source_path = args["source"].as<std::filesystem::path>();
    if (!std::filesystem::is_regular_file(source_path)) {
        std::cout << std::format("File does not exist: {}\n", source_path.string());
        return 1;
    }

    const auto start_point = std::chrono::system_clock::now();

    const auto stats = process_measurements(source_path);
    print_statistic(stats);

    std::cout << std::format("The file was processed in {}\n", time_past_since(start_point));
    return 0;
}
