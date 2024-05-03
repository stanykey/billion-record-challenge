use clap::Parser;
use std::collections::HashMap;
use std::fs::File;
use std::hash::{BuildHasherDefault, Hasher};
use std::io::{BufRead, BufReader, Read, Seek, SeekFrom};
use std::path::Path;
use std::process;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

#[derive(Parser)]
#[command(
    name = "billion-record-challenge",
    version = "0.0.1",
    author = "Sergii Lovygin",
    about = "Read measurements from a CSV file and print statistics."
)]
struct Arguments {
    #[clap()]
    source: String,

    #[clap(long, default_value_t = get_cpu_count())]
    pool_size: usize,
}

#[derive(Debug)]
struct Stats {
    min: i32,
    max: i32,
    sum: i32,
    count: usize,
}

impl Stats {
    fn new(temperature: i32) -> Self {
        Self {
            min: temperature,
            max: temperature,
            sum: temperature,
            count: 1,
        }
    }

    fn minimum(&self) -> f64 {
        (self.min as f64) * 0.1
    }

    fn maximum(&self) -> f64 {
        (self.max as f64) * 0.1
    }

    fn mean(&self) -> f64 {
        match self.count {
            0 => 0.0,
            count => self.sum as f64 / count as f64 * 0.1,
        }
    }
}

impl Clone for Stats {
    fn clone(&self) -> Self {
        Stats {
            min: self.min,
            max: self.max,
            sum: self.sum,
            count: self.count,
        }
    }
}

struct FnvHasher(u64);

impl Default for FnvHasher {
    fn default() -> FnvHasher {
        FnvHasher(0xcbf29ce484222325)
    }
}

impl Hasher for FnvHasher {
    fn finish(&self) -> u64 {
        self.0
    }

    fn write(&mut self, bytes: &[u8]) {
        let FnvHasher(mut hash) = *self;
        for byte in bytes {
            hash = hash ^ (*byte as u64);
            hash = hash.wrapping_mul(0x100000001b3);
        }
        *self = FnvHasher(hash);
    }
}

type Registry = HashMap<String, Stats, BuildHasherDefault<FnvHasher>>;

fn format_duration(duration: Duration) -> String {
    // Calculate minutes, seconds, and milliseconds
    let total_seconds = duration.as_secs();
    let minutes = total_seconds / 60;
    let seconds = total_seconds % 60;
    let milliseconds = duration.subsec_millis();

    // Format the duration as MM:SS:MM string
    format!("{:02}:{:02}:{:03}", minutes, seconds, milliseconds)
}

fn parse_temperature(bytes: &[u8]) -> i32 {
    match bytes.len() {
        5 => {
            // b"-99.9"
            -100 * ((bytes[1] - b'0') as i32)
                - 10 * ((bytes[2] - b'0') as i32)
                - ((bytes[4] - b'0') as i32)
        }
        4 => {
            if bytes[0] == b'-' {
                // b"-9.9"
                -10 * ((bytes[1] - b'0') as i32) - ((bytes[3] - b'0') as i32)
            } else {
                // b"99.9"
                100 * ((bytes[0] - b'0') as i32) + 10 * ((bytes[1] - b'0') as i32)
            }
        }
        _ => {
            // b"9.9"
            10 * ((bytes[0] - b'0') as i32) + ((bytes[2] - b'0') as i32)
        }
    }
}

fn process_line(line: &[u8], registry: &mut Registry) {
    let delimiter = line.iter().position(|&b| b == b';').unwrap();

    let city = unsafe { std::str::from_utf8_unchecked(&line[..delimiter]) };
    let temperature = parse_temperature(&line[delimiter + 1..line.len()]);

    if !registry.contains_key(city) {
        registry.insert(city.to_string(), Stats::new(temperature));
    } else {
        let record = registry.get_mut(city).unwrap();
        record.min = temperature.min(record.min);
        record.max = temperature.max(record.max);
        record.sum += temperature;
        record.count += 1;
    }
}

fn print_statistic(registry: &Registry) {
    let mut keys: Vec<&String> = registry.keys().collect();
    keys.sort_by(|a, b| a.cmp(&b));

    let mut result = keys.iter().fold(String::new(), |mut report, key| {
        let record = registry.get(*key).unwrap();
        let info = format!(
            "{}={:.1}/{:.1}/{:.1}, ",
            key,
            record.minimum(),
            record.mean(),
            record.maximum()
        );
        report.push_str(&info);
        report
    });
    result.truncate(result.len() - 2);

    println!("{{{}}}", result);
}

fn get_cpu_count() -> usize {
    thread::available_parallelism().unwrap().get()
}

fn process_chunk(path: &Path, start: u64, chunk_size: u64) -> Registry {
    let buffer_size = 4096 * 4096;
    let file = File::open(path).unwrap();
    let mut reader = BufReader::with_capacity(buffer_size, file);
    reader.seek(SeekFrom::Start(start)).unwrap();

    let mut registry = Registry::default();
    let mut line = Vec::new();
    let mut bytes_remains = chunk_size;
    while bytes_remains != 0 && reader.read_until(b'\n', &mut line).unwrap() != 0 {
        process_line(&line[..line.len() - 1], &mut registry);
        bytes_remains -= line.len() as u64;
        line.clear();
    }
    registry
}

fn merge(results: Vec<Registry>) -> Registry {
    let mut registry = Registry::default();
    for result in results {
        for (city, data) in result {
            if !registry.contains_key(&city) {
                registry.insert(city, data);
            } else {
                let record = registry.get_mut(&city).unwrap();
                record.min = data.min.min(record.min);
                record.max = data.max.max(record.max);
                record.sum += data.sum;
                record.count += data.count;
            }
        }
    }
    registry
}

fn process_measurements(path: &Path, pool_size: usize) -> Registry {
    let file = File::open(path).unwrap();
    let file_size = file.metadata().unwrap().len();
    let base_chunk_size = (file_size + (pool_size - 1) as u64) / pool_size as u64;

    let results = Arc::new(Mutex::new(Vec::<Registry>::with_capacity(pool_size)));
    thread::scope(|s| {
        let mut start: u64 = 0;

        let mut file_reader = BufReader::new(&file);

        for _ in 0..pool_size {
            let mut end = file_size.min(start + base_chunk_size);

            file_reader.seek(SeekFrom::Start(end)).unwrap();

            let mut buffer = [0; 1];
            while let Ok(()) = file_reader.read_exact(&mut buffer) {
                if buffer[0] == b'\n' {
                    end += 1; // Include the newline character
                    break;
                }
                end += 1;
            }

            let results = Arc::clone(&results);
            s.spawn(move || {
                let chunk_size = end - start;
                let result = process_chunk(path, start, chunk_size);

                let mut results = results.lock().unwrap();
                results.push(result);
            });

            start = end;
        }
    });

    let results = results.lock().unwrap().clone();
    merge(results)
}

fn main() {
    let args = Arguments::parse();
    let path = Path::new(&args.source);
    if !path.exists() {
        println!("File does not exist: {}", args.source);
        process::exit(1);
    }

    let start_point = Instant::now();

    let stats = process_measurements(path, args.pool_size);
    print_statistic(&stats);

    println!(
        "The file was processed in {}",
        format_duration(start_point.elapsed())
    );
}
