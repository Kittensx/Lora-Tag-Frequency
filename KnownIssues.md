# Known issues
## 1. Does not recognize all loras. It functions right now by looking for loras that have specific fields, in particular, "ss_tag_frequency" in the metadata. If that specific word does not exist, and it is formatted a different way, this won't pick up the tags.
## 2. Trigger words - the first entry after ss_tag_frequency may be the name of the image set or it may be the trigger word. I'm not 100%, hence the language, "Possible Triggerword". 
## 3. Does not count correctly. It currently shows the number of files in the folder (other file types, text files, etc), not just the loras. It might say something like, 201 files updated, 1100 files scanned. This has been corrected in version 2, but not for version 1. 
# If you find anything else in this version of the file which should be added here please let me know in the comments.
