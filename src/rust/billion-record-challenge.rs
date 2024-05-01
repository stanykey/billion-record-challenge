use clap::Parser;
use std::collections::HashMap;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::Path;
use std::process;
use std::string::String;
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
    min: f64,
    max: f64,
    sum: f64,
    count: usize,
}

impl Stats {
    fn mean(&self) -> f64 {
        match self.count {
            0 => 0.0,
            count => self.sum / count as f64,
        }
    }
}

impl Default for Stats {
    fn default() -> Self {
        Self {
            min: f64::INFINITY,
            max: f64::NEG_INFINITY,
            sum: 0.0,
            count: 0,
        }
    }
}

fn format_duration(duration: Duration) -> String {
    // Calculate minutes, seconds, and milliseconds
    let total_seconds = duration.as_secs();
    let minutes = total_seconds / 60;
    let seconds = total_seconds % 60;
    let milliseconds = duration.subsec_millis();

    // Format the duration as MM:SS:MM string
    format!("{:02}:{:02}:{:03}", minutes, seconds, milliseconds)
}

fn parse_temperature(temperature: &str) -> f64 {
    temperature.parse::<f64>().unwrap()
}

fn process_line(line: &str, registry: &mut HashMap<String, Stats>) {
    let (city, temperature) = line.split_once(";").unwrap();

    let temperature = parse_temperature(&temperature);
    if !registry.contains_key(city) {
        registry.insert(
            city.to_string(),
            Stats {
                min: temperature,
                max: temperature,
                sum: temperature,
                count: 1,
            },
        );
    } else {
        let record = registry.get_mut(city).unwrap();
        record.min = temperature.min(record.min);
        record.max = temperature.max(record.max);
        record.sum += temperature;
        record.count += 1;
    }
}

fn process_measurements(path: &Path) -> HashMap<String, Stats> {
    let file = File::open(path).unwrap();
    let buffer_size = 4096 * 4096;
    let reader = BufReader::with_capacity(buffer_size, file);

    let mut registry: HashMap<String, Stats> = HashMap::new();
    for line in reader.lines() {
        process_line(line.unwrap().as_str(), &mut registry);
    }
    return registry;
}

fn print_statistic(registry: &HashMap<String, Stats>) {
    let mut keys: Vec<&String> = registry.keys().collect();
    keys.sort_by(|a, b| a.cmp(&b));

    let mut result = keys.iter().fold(String::new(), |mut report, key| {
        let record = registry.get(*key).unwrap();
        let info = format!(
            "{}={}/{:.1}/{}, ",
            key,
            record.min,
            record.mean(),
            record.max
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
