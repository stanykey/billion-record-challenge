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
    std::string city;

    float       min_temperature = std::numeric_limits<float>::max();
    float       max_temperature = std::numeric_limits<float>::min();
    float       sum             = 0.0f;
    std::size_t count           = 0;

    [[nodiscard]] float average() const {
        if (count == 0) {
            return 0.0f;
        }

        return sum / static_cast<float>(count);
    }
};


[[nodiscard]] float parse_float(std::string_view str) {
    float value = 0.0f;
    std::ignore = std::from_chars(str.data(), str.data() + str.size(), value);
    return value;
}


[[nodiscard]] std::string time_past_since(const std::chrono::system_clock::time_point& start_point) {
    const auto current_time = std::chrono::system_clock::now();
    auto       delta        = duration_cast<std::chrono::milliseconds>(current_time - start_point);

    const auto minutes = duration_cast<std::chrono::minutes>(delta);
    delta -= minutes;

    const auto seconds = duration_cast<std::chrono::seconds>(delta);
    delta -= seconds;

    const auto milliseconds = duration_cast<std::chrono::milliseconds>(delta);

    return std::format("{:02d}:{:02d}.{:03d}", minutes.count(), seconds.count(), milliseconds.count());
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

    std::ifstream                          source(source_path);
    std::unordered_map<std::string, Stats> stats(1'000);

    std::string line;
    std::size_t record_processed = 0;
    const auto  start_point      = std::chrono::system_clock::now();
    while (std::getline(source, line)) {
        const std::size_t delimiter_pos = line.find(';');

        const std::string      name(line.data(), delimiter_pos);
        const std::string_view temperature_string(line.data() + delimiter_pos + 1);

        auto [it, inserted] = stats.try_emplace(name, Stats{});
        auto& record        = it->second;
        if (inserted) {
            record.city = name;
        }

        const auto temperature = parse_float(temperature_string);
        record.min_temperature = std::min(temperature, record.min_temperature);
        record.max_temperature = std::max(temperature, record.max_temperature);
        record.sum += temperature;
        record.count++;

        record_processed++;
        if (record_processed > 0 && record_processed % 50'000'000 == 0) {
            std::cout << format("Process {} measurements in {}\n", record_processed, time_past_since(start_point));
        }
    }

    std::vector<Stats> records;
    records.reserve(stats.size());
    for (auto& [key, record] : stats) {
        records.emplace_back(std::move(record));
    }
    stats.clear();

    std::sort(records.begin(), records.end(), [](const Stats& lhs, const Stats& rhs) { return lhs.city < rhs.city; });

    for (const auto& record : records) {
        std::cout << format("{}/{}/{}/{}\n", record.city, record.min_temperature, record.max_temperature, record.average());
    }

    std::cout << format("The file was processed in {}\n", time_past_since(start_point));
    return 0;
}
