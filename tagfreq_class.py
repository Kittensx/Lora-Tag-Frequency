import os
from tqdm import tqdm
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from datetime import datetime
import json
from safetensors import safe_open

class MetaDataScanner:
    def __init__(self, config):
        self.directories_to_scan = config.get("directories_to_scan", [])
        self.log_file = config.get("log_file", "scan_log.txt")
        self.error_log = config.get("error_log", "errors_log.txt")
        self.progress_bar = None
        self.file_count = 0       
        self.files_processed = 0
        self.error_count = 0

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

            # Check if any tag frequency file already exists
            existing_files = [f for f in os.listdir(os.path.dirname(file_path)) if f.startswith(file_name) and f.endswith("_tagfrequency.txt")]
            if existing_files:
                logging.info(f"Tag frequency file already exists for {file_path}. Skipping creation.")
                return
            if not file_path.endswith(".safetensors"):
                logging.info(f"Skipped non-SafeTensor file: {file_path}")
                return

            # Open the SafeTensor file and read metadata
            with safe_open(file_path, framework="numpy") as st:
                metadata = st.metadata()

            # Ensure the "ss_tag_frequency" field exists
            if "ss_tag_frequency" not in metadata:
                logging.info(f"'ss_tag_frequency' field not found in the metadata for file: {file_path}")
                return

            # Parse the tag frequencies
            tag_frequencies = metadata["ss_tag_frequency"]
            if isinstance(tag_frequencies, str):
                tag_frequencies = json.loads(tag_frequencies)

            # Check if tag_frequencies is empty
            if not tag_frequencies:
                logging.info(f"'ss_tag_frequency' field is empty for file: {file_path}")
                return

            for activation_text, tags in tag_frequencies.items():
                # Check if tags are empty
                if not tags:
                    logging.info(f"No tags found in 'ss_tag_frequency' for activation text: {activation_text}")
                    continue

                # Sort tags by frequency in descending order
                sorted_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)

                # Ensure sorted_tags is not empty
                if not sorted_tags:
                    logging.info(f"No valid tags to process for activation text: {activation_text}")
                    continue

                # Get the highest frequency
                top_frequency = sorted_tags[0][1]
                threshold_high = top_frequency * 0.75
                threshold_medium = top_frequency * 0.4

                # Initialize category lists
                high_frequency = []
                medium_frequency = []
                low_frequency = []

                for tag, freq in sorted_tags:
                    if freq >= threshold_high:
                        high_frequency.append(tag)
                    elif threshold_medium <= freq < threshold_high:
                        medium_frequency.append(tag)
                    else:
                        low_frequency.append(tag)

                file_name = os.path.splitext(os.path.basename(file_path))[0]
                # Construct the output file name
                output_file_name = os.path.join(os.path.dirname(file_path), f"{file_name}_{activation_text}_tagfrequency.txt")

                # Write to the file
                with open(output_file_name, 'w', encoding="utf-8") as output_file:
                    output_file.write(f"Tag Frequency v1.0\n\n")
                    output_file.write(f"Possible Activation Text/Name of Dataset: {activation_text}\n\n")
                    output_file.write("High Frequency Tags (>= 75%):\n")
                    output_file.write(", ".join(high_frequency) + "\n\n")
                    output_file.write("Medium Frequency Tags (40-75%):\n")
                    output_file.write(", ".join(medium_frequency) + "\n\n")
                    output_file.write("Low Frequency Tags (< 40%):\n")
                    output_file.write(", ".join(low_frequency) + "\n")
                logging.info(f"Output written to {output_file_name}")

            self.files_processed += 1

        except Exception as e:
            logging.error(f"An error occurred processing file {file_path}: {e}")
            #print(f"An error occurred: {e}")
            self.error_count +=1


    def scan_and_process(self):
        logging.basicConfig(filename=self.log_file, level=logging.INFO,
                            format='%(asctime)s - %(message)s')
        logging.basicConfig(filename=self.error_log, level=logging.ERROR,
                            format='%(asctime)s - %(message)s')
                            
        logging.info(f"Starting directory scan. Logs are saved to {self.log_file}")
        logging.info(f"Error Logs will be saved to {self.error_log}")

        total_files = 0
        
        
        for directory in self.directories_to_scan:
            logging.info(f"Scanning directory: {directory}")
            file_count = self.scan_directory(directory)        
            total_files += file_count


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

    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            self.scanner.process_file(event.src_path)

if __name__ == "__main__":
    config = {
        "directories_to_scan": [r"d:\stable-diffusion-webui\models\Lora"],  # Replace with actual paths
        "log_file": "metadata_scan_log.txt"
    }

    scanner = MetaDataScanner(config)
    scanner.scan_and_process()

    # Set up watchdog to monitor directories
    observer = Observer()
    event_handler = DirectoryMonitor(scanner)

    for directory in config["directories_to_scan"]:
        observer.schedule(event_handler, directory, recursive=True)

    print("Monitoring for new files. Press Ctrl+C to exit.")
    try:
        observer.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
    if self.error_count >0:
        print(f"Errors were detected during program execution. Please refer to the {error_log} for details.")
