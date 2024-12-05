I am working on two versions of this file: 
# Version 1
Barebones without using Watchdog to monitor files. It says it is monitoring files, but it does not in fact work.
This file only updates when you run the program. If you add new files to it, you need to shut down the program (if running) and run it again.

# Version 2
A more advanced version of this file which actively monitors folders and creates the proper files. 

## Excel Database for tracking all scanned Loras
Options to export the database to CSV (note: CSV files are limited therefore you will get multiple CSV files if needed to ensure compatibilitiy with Excel), .xlsx, sqlite. 
## The metadata can be exported to either a yaml or json file per your preferred format. 
## Extensive logging enabled.
## Set your file_extensions per config (example: ".pt", ".pth", ".safetensors")
## All file names can be renamed per config file
## Customized tag_frequency_levels per config file.
## Set a Scan Interval, set excluded directories, set directories to scan, set batch limit, set timestamp format, and other settings via a config file. 
## In addition, it creates an excel database file with pertinent information about each LORA for references,
## I've also been working on adding a language option which allows you to set the language for the output files, with a note that tags should be used in the original file. 
This should help you to use the correct tags, especially if a language other than english was used for the Lora.
## Lastly, I want to review each file and ensure each file is optimized for multithreading - since that is a feature I added in about half way and it is not fully integrated. 

