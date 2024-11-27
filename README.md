# Lora-Tag-Frequency
Creates a txt file which shows the 3 top ranked ranges for tags while also searching for activation text for the Lora. If the activation text is "img" or blank then it was not able to find it.

This repository is meant to run in the background and monitors files. You can also just run it once for your target folders, and run it each time you add new Lora to your folders. For example outputs, see "output examples" folder.

This is a placeholder readme while I work out functionality, and is meant to work like a coming soon.

Without  the loratagfreq.py file this repository will not work.

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
   git clone https://github.com/kittensx/metadata-exporter.git
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
   python loratagfreq.py
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
Email: kittensx.github@gmail.com
GitHub: [Kittensx](https://github.com/Kittensx/Lora-Tag-Frequency)
Find me on CivitAi:https://civitai.com/user/KittensX
Buy me a coffee :)  https://ko-fi.com/kittensx

## Contributing
Contributions are welcome! Feel free to submit a pull request or open an issue.

** LICENSE**
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

