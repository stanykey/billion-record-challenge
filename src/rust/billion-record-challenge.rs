use clap::Parser;
use std::collections::HashMap;
use std::fs::File;
use std::hash::{BuildHasherDefault, Hasher};
use std::io::{BufRead, BufReader};
use std::path::Path;
use std::process;
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

    fn min(&self) -> f64 {
        (self.min as f64) * 0.1
    }

    fn max(&self) -> f64 {
        (self.max as f64) * 0.1
    }

    fn mean(&self) -> f64 {
        match self.count {
            0 => 0.0,
            count => self.sum as f64 / count as f64 * 0.1,
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
            hash = hash * 0x100000001b3;
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

fn parse_temperature(temperature: &str) -> i32 {
    let bytes = temperature.as_bytes();
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

fn process_line(line: &str, registry: &mut Registry) {
    let (city, temperature) = line.split_once(";").unwrap();

    let temperature = parse_temperature(&temperature);
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

fn process_measurements(path: &Path) -> Registry {
    let file = File::open(path).unwrap();
    let buffer_size = 4096 * 4096;
    let mut reader = BufReader::with_capacity(buffer_size, file);

    let mut registry = Registry::default();
    let mut line = String::new();
    while reader.read_line(&mut line).unwrap() != 0 {
        process_line(&line[..line.len() - 1], &mut registry);
        line.clear();
    }
    return registry;
}

fn print_statistic(registry: &Registry) {
    let mut keys: Vec<&String> = registry.keys().collect();
    keys.sort_by(|a, b| a.cmp(&b));

    let mut result = keys.iter().fold(String::new(), |mut report, key| {
        let record = registry.get(*key).unwrap();
        let info = format!(
            "{}={:.1}/{:.1}/{:.1}, ",
            key,
            record.min(),
            record.mean(),
            record.max()
        );
        report.push_str(&info);
        report
    });
    result.truncate(result.len() - 2);

    println!("{{{}}}", result);
}

fn main() {
    let args = Arguments::parse();
    let path = Path::new(&args.source);
    if !path.exists() {
        println!("File does not exist: {}", args.source);
        process::exit(1);
    }

    let start_point = Instant::now();

    let stats = process_measurements(path);
    print_statistic(&stats);

    println!(
        "The file was processed in {}",
        format_duration(start_point.elapsed())
    );
}
