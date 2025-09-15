import os

# Define the string to replace and its replacement
old_string = "qwen3-8b"
new_string = "gemma3-4b"

# Loop through files in the current directory
for filename in os.listdir("."):
    if not os.path.isfile(filename):
        continue  # Skip directories

    # Check if the filename contains the old string
    if old_string in filename:
        new_filename = filename.replace(old_string, new_string)
        os.rename(filename, new_filename)
        print(f"Renamed: {filename} -> {new_filename}")
