# Metadata Exporter and Scanner

This Python script is designed to scan specified directories for metadata in various file types and export it in both JSON/YAML and CSV formats. It also supports monitoring directories for new files and keeping a structured database of scanned files.

## Features
- Scans `.pt`, `.pth`, `.safetensors`, and user-defined file types.
- Exports metadata to JSON/YAML and CSV formats.
- Monitors directories for new files and processes them in real-time.
- Keeps a detailed structured database of scanned files.

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/metadata-exporter.git
   cd metadata-exporter
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure the script by editing the config.yaml file.


## Usage
To run the script:

   ```
   python tagfreq_class.py
   ```

## Configuration
The config.yaml file allows you to:

### Specify directories to scan.
### Enable or disable metadata export.
### Define file extensions to scan.
### Choose export formats and file locations.

## License
This project is licensed under the MIT License.

## Author
Kittensx
Email: your.email@example.com
GitHub: Kittensx

## Contributing
Contributions are welcome! Feel free to submit a pull request or open an issue.

4. ** LICENSE**
Copyright (c) 2024 Kittensx

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
