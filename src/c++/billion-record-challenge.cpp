#include <algorithm>
#include <filesystem>
#include <format>
#include <fstream>
#include <iostream>
#include <string>
#include <string_view>
#include <thread>
#include <unordered_map>

#include <cxxopts.hpp>

struct Stats {
    std::int64_t min   = std::numeric_limits<std::int64_t>::max();
    std::int64_t max   = std::numeric_limits<std::int64_t>::min();
    std::int64_t sum   = 0.0;
    std::size_t  count = 0;

    Stats() = default;
    Stats(std::int64_t temperature)
        : min(temperature)
        , max(temperature)
        , sum(temperature)
        , count(1) {}

    [[nodiscard]] double minimum() const {
        return min * 0.1;
    }

    [[nodiscard]] double maximum() const {
        return max * 0.1;
    }

    [[nodiscard]] double mean() const {
        if (count == 0) {
            return 0.0;
        }

        return sum / static_cast<double>(count) * 0.1;
    }
};

class StringHasher {
public:
    using hash_type      = std::size_t;
    using is_transparent = void;

    static constexpr hash_type FNV_offset_basis = 14695981039346656037ULL;
    static constexpr hash_type FNV_prime        = 1099511628211ULL;

    hash_type operator()(const char* str) const {
        return fnv1a_hash(str);
    }

    hash_type operator()(std::string_view str) const {
        return fnv1a_hash(str);
    }

    hash_type operator()(const std::string& str) const {
        return fnv1a_hash(str);
    }

private:
    static hash_type fnv1a_hash(std::string_view str) {
        hash_type hash = FNV_offset_basis;
        for (const unsigned char c : str) {
            hash ^= c;
            hash *= FNV_prime;
        }
        return hash;
    }
};

using Registry = std::unordered_map<std::string, Stats, StringHasher, std::equal_to<>>;


[[nodiscard]] std::int64_t parse_temperature(std::string_view bytes) {
    switch (bytes.size()) {
        case 5: {
            // "-99.9"
            return -100 * (bytes[1] - '0') - 10 * (bytes[2] - '0') - (bytes[4] - '0');
        }

        case 4: {
            if (bytes[0] == '-') {
                // "-9.9"
                return -10 * (bytes[1] - '0') - (bytes[3] - '0');
            } else {
                // "99.9"
                return 100 * (bytes[0] - '0') + 10 * (bytes[1] - '0');
            }
        }

        default: {
            // "9.9"
            return 10 * (bytes[0] - '0') + (bytes[2] - '0');
        }
    }
}

[[nodiscard]] std::string time_past_since(const std::chrono::system_clock::time_point& start_point) {
    const auto current_time = std::chrono::system_clock::now();
    auto       delta        = duration_cast<std::chrono::milliseconds>(current_time - start_point);

    const auto minutes      = duration_cast<std::chrono::minutes>(delta);
    const auto seconds      = duration_cast<std::chrono::seconds>(delta - minutes);
    const auto milliseconds = duration_cast<std::chrono::milliseconds>(delta - minutes - seconds);

    return std::format("{:02d}:{:02d}:{:03d}", minutes.count(), seconds.count(), milliseconds.count());
}

[[nodiscard]] Registry gather(std::vector<Registry> results) {
    Registry registry;
    for (const auto& result : results) {
        for (auto&& [station, data] : result) {
            if (auto it = registry.find(station); it != registry.end()) {
                auto& record = it->second;

                record.min = std::min(record.min, data.min);
                record.max = std::max(record.max, data.max);
                record.sum += data.sum;
                record.count += data.count;
            } else {
                registry.emplace(std::move(station), std::move(data));
            }
        }
    }
    return registry;
}

[[nodiscard]] Registry process_chunk(const std::filesystem::path& source_path, std::size_t offset, std::size_t size = -1) {
    Registry registry;

    std::ifstream source(source_path, std::ios::binary);
    source.seekg(offset);

    std::string line;
    std::size_t bytes_remains = size;
    while ((bytes_remains != 0) && std::getline(source, line)) {
        const std::size_t delimiter_pos = line.find(';');

        const auto station     = std::string_view{line.data(), delimiter_pos};
        const auto temperature = parse_temperature({line.data() + delimiter_pos + 1});
        if (auto it = registry.find(station); it != registry.end()) {
            auto& record = it->second;

            record.min = std::min(record.min, temperature);
            record.max = std::max(record.max, temperature);
            record.sum += temperature;
            record.count++;
        } else {
            registry.emplace(station, temperature);
        }

        bytes_remains -= line.size();
        bytes_remains -= 1;  // new line character
    }

    return registry;
}

[[nodiscard]] std::size_t get_file_size(std::ifstream& file) {
    const auto original_pos = file.tellg();

    file.seekg(0, std::ios::end);
    const auto file_size = file.tellg();
    file.seekg(original_pos);

    return file_size;
}

[[nodiscard]] std::size_t seek_to(std::ifstream& file, std::size_t offset, char target) {
    file.seekg(offset);
    char symbol = 0;
    while (file.get(symbol)) {
        if (symbol == target) {
            return ++offset;
        }
        offset++;
    }
    return file.tellg();
}

[[nodiscard]] Registry process_measurements(const std::filesystem::path& source_path, std::size_t cpu_count) {
    std::vector<Registry> results(cpu_count);

    std::ifstream source(source_path, std::ios::binary);
    const auto    file_size       = get_file_size(source);
    const auto    base_chunk_size = (file_size + cpu_count - 1) / cpu_count;

    std::vector<std::thread> pool;

    std::size_t start = 0;
    for (auto i = 0u; i != cpu_count; i++) {
        const auto hint = std::min(file_size, start + base_chunk_size);
        const auto end  = seek_to(source, hint, '\n');

        pool.emplace_back([&result = results[i], &source_path, offset = start, size = end - start] {
            result = process_chunk(source_path, offset, size);
        });

        start = end;
    }

    for (auto& thread : pool) {
        thread.join();
    }

    return gather(std::move(results));
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
        const auto& station = it->first;
        const auto& record  = it->second;
        result.append(std::format("{}={:.1f}/{:.1f}/{:.1f}, ", station, record.minimum(), record.mean(), record.maximum()));
    }
    result.resize(result.size() - 2);

    std::cout << std::format("{{{}}}\n", result);
}

[[nodiscard]] std::size_t get_cpu_count() {
    return std::thread::hardware_concurrency();
}

int main(int argc, const char* argv[]) {
    std::ios::sync_with_stdio(false);
    std::setlocale(LC_ALL, "en_US.UTF-8");

    cxxopts::Options options("billion-record-challenge", "Read measurements from a CSV file and print statistics.");
    options.add_options()
        ("source", "Source file path", cxxopts::value<std::filesystem::path>())
        ("pool-size", "Number of CPUs to use", cxxopts::value<std::size_t>()->default_value(std::to_string(get_cpu_count())))
        ("help", "Print usage")
    ;
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

    const auto cpu_count = args["pool-size"].as<std::size_t>();
    const auto registry  = process_measurements(source_path, cpu_count);
    print_statistic(registry);

    std::cout << std::format("The file was processed in {}\n", time_past_since(start_point));
    return 0;
}
