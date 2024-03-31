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

fn process_measurements(path: &Path) -> HashMap<String, Stats> {
    let file = File::open(path).unwrap();
    let buffer_size = 4096 * 4096;
    let reader = BufReader::with_capacity(buffer_size, file);

    let mut stats: HashMap<String, Stats> = HashMap::new();
    for line in reader.lines() {
        let line_content = line.unwrap();
        let (city, temperature_string) = line_content.split_once(";").unwrap();

        let city = city.to_string();
        let temperature = temperature_string.parse::<f64>().unwrap();
        if !stats.contains_key(&city) {
            stats.insert(city.clone(), Stats::default());
        }
        let record = stats.get_mut(&city).unwrap();

        if temperature < record.min {
            record.min = temperature;
        }

        if temperature > record.max {
            record.max = temperature;
        }

        record.sum += temperature;
        record.count += 1;
    }

    return stats;
}

fn print_statistic(stats: &HashMap<String, Stats>) {
    let mut keys: Vec<&String> = stats.keys().collect();
    keys.sort_by(|a, b| a.cmp(&b));

    let mut result = String::new();
    result.push_str("{");
    for key in keys {
        let record = stats.get(key).unwrap();
        let info = format!(
            "{}={}/{:.1}/{}, ",
            key,
            record.min,
            record.mean(),
            record.max
        );
        result.push_str(&info);
    }
    result.push_str("}");

    println!("{result}");
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
