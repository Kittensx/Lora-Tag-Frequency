import os
import time
import logging
import json
from tqdm import tqdm
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import yaml
from safetensors import safe_open
from threading import Timer
import csv
from datetime import datetime

class MetaDataScanner:
    def __init__(self, config):
        self.directories_to_scan = config.get("directories_to_scan", [])
        self.log_file = config.get("log_file", "scan_log.txt")
        self.error_log = config.get("error_log", "errors_log.txt")
        self.tag_frequency_levels = config.get("tag_frequency_levels", {"high": 75, "medium": 40, "low": 0})
        self.batch_time = config.get("batch_time", 10)
        self.pending_files = set()
        self.progress_bar = None
        self.file_count = 0
        self.files_processed = 0
        self.error_count = 0
        
        # Ensure log file directories exist
        self.ensure_directory_exists(self.log_file)
        self.ensure_directory_exists(self.error_log)

    def ensure_directory_exists(file_path):
        folder = os.path.dirname(file_path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created missing folder: {folder}")
            
    def scan_directory(self, directory):
        self.file_count = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".safetensors"):
                    self.file_count += 1
        return self.file_count

    def process_file(self, file_path):
        try:
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            output_file_pattern = os.path.join(os.path.dirname(file_path), f"{file_name}_*_tagfrequency.txt")

            existing_files = [f for f in os.listdir(os.path.dirname(file_path)) if f.startswith(file_name) and f.endswith("_tagfrequency.txt")]
            if existing_files:
                logging.info(f"Tag frequency file already exists for {file_path}. Skipping creation.")
                return

            if not file_path.endswith(".safetensors"):
                logging.info(f"Skipped non-SafeTensor file: {file_path}")
                return

            with safe_open(file_path, framework="numpy") as st:
                metadata = st.metadata()

            if "ss_tag_frequency" not in metadata:
                logging.info(f"'ss_tag_frequency' field not found in the metadata for file: {file_path}")
                return

            tag_frequencies = metadata["ss_tag_frequency"]
            if isinstance(tag_frequencies, str):
                tag_frequencies = json.loads(tag_frequencies)

            if not tag_frequencies:
                logging.info(f"'ss_tag_frequency' field is empty for file: {file_path}")
                return

            for activation_text, tags in tag_frequencies.items():
                if not tags:
                    logging.info(f"No tags found in 'ss_tag_frequency' for activation text: {activation_text}")
                    continue

                sorted_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)
                top_frequency = sorted_tags[0][1]
                thresholds = {k: v * top_frequency / 100 for k, v in self.tag_frequency_levels.items()}

                categories = {level: [] for level in self.tag_frequency_levels.keys()}
                for tag, freq in sorted_tags:
                    for level, threshold in thresholds.items():
                        if freq >= threshold:
                            categories[level].append(tag)
                            break

                output_file_name = os.path.join(os.path.dirname(file_path), f"{file_name}_{activation_text}_tagfrequency.txt")
                with open(output_file_name, 'w', encoding="utf-8") as output_file:
                    output_file.write("Tag Frequency Analysis\n\n")
                    output_file.write(f"Possible Activation Text/Name of Dataset: {activation_text}\n\n")
                    for level, tags in categories.items():
                        output_file.write(f"{level.capitalize()} Frequency Tags (>= {self.tag_frequency_levels[level]}%):\n")
                        output_file.write(", ".join(tags) + "\n\n")
                logging.info(f"Output written to {output_file_name}")
                
                # Update MetadataTracker with this file
                tracker.update_metadata(file_name, {k: ", ".join(v) for k, v in categories.items()}, file_path)
            
            self.files_processed += 1

        except Exception as e:
            logging.error(f"An error occurred processing file {file_path}: {e}")
            self.error_count += 1

    def process_pending_files(self):
        logging.info("Processing batch of pending files...")
        for file_path in list(self.pending_files):
            self.process_file(file_path)
            self.pending_files.remove(file_path)

    def scan_and_process(self):
        logging.basicConfig(filename=self.log_file, level=logging.INFO, format='%(asctime)s - %(message)s')
        logging.basicConfig(filename=self.error_log, level=logging.ERROR, format='%(asctime)s - %(message)s')
        logging.info(f"Starting directory scan. Logs are saved to {self.log_file}")

        total_files = 0
        
        # Check for missing files in the metadata
        missing_files = tracker.get_missing_files(self.directories_to_scan)
        if missing_files:
            logging.info(f"Found {len(missing_files)} missing files in the metadata. Adding them to the scan queue.")
            for file_path in missing_files:
                self.process_file(file_path)
        for directory in self.directories_to_scan:
            logging.info(f"Scanning directory: {directory}")
            total_files += self.scan_directory(directory)

        print(f"Found {total_files} files.")

        self.progress_bar = tqdm(total=total_files, desc="Processing files", unit="file")
        for directory in self.directories_to_scan:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.process_file(file_path)
                    self.progress_bar.update(1)

        self.progress_bar.close()
        logging.info(f"Scan completed: {total_files} files scanned.")
        logging.info(f"Files processed: {self.files_processed}")

class DirectoryMonitor(FileSystemEventHandler):
    def __init__(self, scanner):
        self.scanner = scanner
        self.timer = None

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".safetensors"):
            self.scanner.pending_files.add(event.src_path)
            if not self.timer:
                self.timer = Timer(self.scanner.batch_time, self.scanner.process_pending_files)
                self.timer.start()
            else:
                self.timer.cancel()
                self.timer = Timer(self.scanner.batch_time, self.scanner.process_pending_files)
                self.timer.start()
                
class MetadataTracker:
    def __init__(self, structured_data_file="metadata.json"):
        self.structured_data_file = structured_data_file
        self.metadata = self.load_metadata()

    def load_metadata(self):
        """Load existing metadata from a file, or initialize an empty structure."""
        if os.path.exists(self.structured_data_file):
            with open(self.structured_data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_metadata(self):        
        """Save the current metadata to the structured data file."""
        os.makedirs(os.path.dirname(self.structured_data_file), exist_ok=True)
        with open(self.structured_data_file, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=4)

    def update_metadata(self, lora_name, categories, file_path):
        """Update metadata for a LoRA file."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.metadata[lora_name] = {
            "categories": categories,
            "file_path": file_path,
            "last_scanned": current_time,
        }
        self.save_metadata()
        
    def get_missing_files(self, directories_to_scan):
        """Find files in the directories that are not in the metadata."""
        missing_files = []
        for directory in directories_to_scan:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(".safetensors"):
                        file_name = os.path.splitext(file)[0]
                        if file_name not in self.metadata:
                            missing_files.append(os.path.join(root, file))
        return missing_files
        
    def export_to_csv(self, csv_file="metadata_overview.csv"):
        """Export metadata to a CSV file."""
        if not self.metadata:
            print("No metadata available to export.")
            return
        
        headers = ["LoRA Name", "File Path", "Last Scanned"] + list(self.get_all_categories())
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for lora_name, data in self.metadata.items():
                row = [
                    lora_name,
                    data["file_path"],
                    data["last_scanned"],
                ]
                for category in headers[3:]:
                    row.append(data["categories"].get(category, ""))
                writer.writerow(row)

        print(f"Metadata exported to {csv_file}")

    def get_all_categories(self):
        """Get all unique categories from the metadata."""
        categories = set()
        for data in self.metadata.values():
            categories.update(data["categories"].keys())
        return categories


class MetadataExporter:
    def __init__(self, config):
        self.export_enabled = config.get("export_metadata", False)
        self.output_format = config.get("output_format", "json")  # Default to JSON
        self.output_file = config.get("output_file", "metadata_export.json")
        self.csv_file = config.get("csv_output_file", "metadata_export.csv")  # CSV file for export
        self.file_extensions = config.get("file_extensions", [".pt", ".pth", ".safetensors"])  # Default extensions
        self.directories_to_scan = config.get("directories_to_scan", [])
        self.metadata = {}

    def scan_files(self):
        """Scan files for specified extensions and extract metadata."""
        for directory in self.directories_to_scan:
            for root, _, files in os.walk(directory):
                for file in files:
                    if any(file.endswith(ext) for ext in self.file_extensions):
                        file_path = os.path.join(root, file)
                        self.extract_metadata(file_path)

    def extract_metadata(self, file_path):
        """Extract metadata from a file. Custom logic for each file type can be added here."""
        try:
            # Example for demonstration purposes
            if file_path.endswith(".safetensors"):
                from safetensors import safe_open
                with safe_open(file_path, framework="numpy") as st:
                    metadata = st.metadata()
            elif file_path.endswith((".pt", ".pth")):
                import torch
                metadata = torch.load(file_path, map_location="cpu").get("metadata", {})
            else:
                metadata = {"error": "Unknown file type or no metadata parser available."}

            self.metadata[file_path] = metadata
        except Exception as e:
            self.metadata[file_path] = {"error": str(e)}

    def export_metadata(self):
        """Export metadata to a YAML or JSON file."""
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        if self.output_format.lower() == "yaml":
            with open(self.output_file, "w", encoding="utf-8") as f:
                yaml.dump(self.metadata, f, default_flow_style=False, allow_unicode=True)
        else:  # Default to JSON
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, indent=4)
        print(f"Metadata exported to {self.output_file}")
    
    def export_to_csv(self):
        """Export metadata to a CSV file."""
        os.makedirs(os.path.dirname(self.csv_file), exist_ok=True)
        all_keys = set()
        for metadata in self.metadata.values():
            if isinstance(metadata, dict):
                all_keys.update(metadata.keys())

        headers = ["File Path"] + sorted(all_keys)

        with open(self.csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for file_path, metadata in self.metadata.items():
                row = [file_path]
                if isinstance(metadata, dict):
                    row.extend(metadata.get(key, "") for key in headers[1:])
                else:
                    row.extend(["" for _ in headers[1:]])
                writer.writerow(row)

        print(f"Metadata exported to {self.csv_file}")
        
    def run(self):
        """Run the metadata export process if enabled."""
        if self.export_enabled:
            print("Metadata export is enabled. Starting export process...")
            self.scan_files()
            self.export_metadata()
            self.export_to_csv()
        else:
            print("Metadata export is disabled in the configuration.")

if __name__ == "__main__":
    
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Metadata export process
    metadata_exporter = MetadataExporter(config)
    metadata_exporter.run()
    
    tracker = MetadataTracker(config)
    scanner = MetaDataScanner(config)
    
    # Process files, including any missing ones
    scanner.scan_and_process()

    # Set up directory monitoring
    observer = Observer()
    event_handler = DirectoryMonitor(scanner)
    for directory in config.get("directories_to_scan", []):
        observer.schedule(event_handler, directory, recursive=True)

    print("Monitoring for new files. Press Ctrl+C to exit.")
    try:
        observer.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    
    # Export metadata to CSV after scanning
    tracker.export_to_csv()
