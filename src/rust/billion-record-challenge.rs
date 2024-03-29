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
    city: String,
    min_temperature: f64,
    max_temperature: f64,
    sum: f64,
    count: usize,
}

impl Stats {
    fn new(city: String) -> Self {
        Self {
            city,
            ..Default::default()
        }
    }

    fn average(&self) -> f64 {
        match self.count {
            0 => 0.0,
            count => self.sum / count as f64,
        }
    }
}

impl Default for Stats {
    fn default() -> Self {
        Self {
            city: String::default(),
            min_temperature: f64::INFINITY,
            max_temperature: f64::NEG_INFINITY,
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

fn main() {
    let args = Arguments::parse();
    let path = Path::new(&args.source);
    if !path.exists() {
        println!("File does not exist: {}", args.source);
        process::exit(1);
    }

    let file = File::open(path).unwrap();
    let reader = BufReader::new(file);

    let start_point = Instant::now();
    let mut record_processed = 0;
    let mut stats: HashMap<String, Stats> = HashMap::new();
    for line in reader.lines() {
        let line_content = line.unwrap();
        let (city, temperature_string) = line_content.split_once(";").unwrap();

        let city = city.to_string();
        let temperature = temperature_string.parse::<f64>().unwrap();
        let record = stats
            .entry(city.clone())
            .or_insert(Stats::new(city.clone()));

        record.min_temperature = temperature.min(record.min_temperature);
        record.max_temperature = temperature.max(record.max_temperature);
        record.sum += temperature;
        record.count += 1;

        record_processed += 1;
        if record_processed > 0 && record_processed % 50_000_000 == 0 {
            println!(
                "Process {} measurements in {}",
                record_processed,
                format_duration(start_point.elapsed())
            );
        }
    }

    let mut records: Vec<&Stats> = stats.values().collect();
    records.sort_by(|a, b| a.city.cmp(&b.city));
    for record in records {
        println!(
            "{}/{}/{}/{:.1}",
            record.city,
            record.min_temperature,
            record.max_temperature,
            record.average()
        );
    }

    println!(
        "The file was processed in {}",
        format_duration(start_point.elapsed())
    );
}
