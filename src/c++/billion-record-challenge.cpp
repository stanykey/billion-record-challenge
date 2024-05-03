#include <algorithm>
#include <filesystem>
#include <format>
#include <fstream>
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>

#include <cxxopts.hpp>

struct Stats {
    double      min   = std::numeric_limits<double>::max();
    double      max   = std::numeric_limits<double>::min();
    double      sum   = 0.0;
    std::size_t count = 0;

    Stats() = default;
    Stats(double temperature)
        : min(temperature)
        , max(temperature)
        , sum(temperature)
        , count(1) {}

    [[nodiscard]] double minimum() const {
        return min;
    }

    [[nodiscard]] double maximum() const {
        return max;
    }

    [[nodiscard]] double mean() const {
        if (count == 0) {
            return 0.0;
        }

        return sum / static_cast<double>(count);
    }
};

struct StringHasher {
    using hash_type      = std::hash<std::string_view>;
    using is_transparent = void;

    std::size_t operator()(const char* str) const {
        return hash_type{}(str);
    }

    std::size_t operator()(std::string_view str) const {
        return hash_type{}(str);
    }

    std::size_t operator()(std::string const& str) const {
        return hash_type{}(str);
    }
};

using Registry = std::unordered_map<std::string, Stats, StringHasher, std::equal_to<>>;


[[nodiscard]] double parse_temperature(std::string_view str) {
    double value = 0.0;
    std::from_chars(str.data(), str.data() + str.size(), value);
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

[[nodiscard]] Registry process_measurements(const std::filesystem::path& source_path) {
    Registry registry;

    std::string   line;
    std::ifstream source(source_path, std::ios::binary);
    while (std::getline(source, line)) {
        const std::size_t delimiter_pos = line.find(';');

        const auto name        = std::string_view{line.data(), delimiter_pos};
        const auto temperature = parse_temperature({line.data() + delimiter_pos + 1});
        if (auto it = registry.find(name); it != registry.end()) {
            auto& record = it->second;

            record.min = std::min(record.min, temperature);
            record.max = std::max(record.max, temperature);
            record.sum += temperature;
            record.count++;
        } else {
            registry.emplace(name, temperature);
        }
    }

    return registry;
}

void print_statistic(const Registry& registry) {
    using Item = Registry::const_iterator;

    std::vector<Item> items;
    items.reserve(registry.size());
    for (auto it = registry.cbegin(); it != registry.cend(); ++it) {
        items.emplace_back(it);
    }
    std::sort(items.begin(), items.end(), [](const Item& lhs, const Item& rhs) { return lhs->first < rhs->first; });

    std::string result;
    for (const auto& it : items) {
        const auto& key  = it->first;
        const auto& data = it->second;
        result.append(std::format("{}={:.1f}/{:.1f}/{:.1f}, ", key, data.minimum(), data.mean(), data.maximum()));
    }
    result.resize(result.size() - 2);

    std::cout << std::format("{{{}}}\n", result);
}

int main(int argc, const char* argv[]) {
    std::ios::sync_with_stdio(false);
    std::setlocale(LC_ALL, "en_US.UTF-8");

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

    const auto registry = process_measurements(source_path);
    print_statistic(registry);

    std::cout << std::format("The file was processed in {}\n", time_past_since(start_point));
    return 0;
}
