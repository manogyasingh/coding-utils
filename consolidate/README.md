# Consolidate Files Script

## Overview

The **Consolidate Files** script is a Python tool designed to aggregate multiple files from a directory (and its subdirectories) into a single summary file. This is particularly useful for providing context to AI models like ChatGPT or for simplifying project documentation.

## Features

- **Recursive Traversal**: By default, the script scans the current directory and all its subdirectories.
- **.gitignore Support**: Respects patterns defined in all `.gitignore` files within the input directory tree.
- **Automatic Exclusion**: Always ignores itself (`consolidate_files.py`), its log files (e.g., `consolidate_files.log`), and the output file (`summarised.txt`).
- **Binary File Handling**: Detects and skips binary files to prevent read errors.
- **Progress Indicators**: Displays a progress bar using `tqdm` to indicate consolidation status.
- **Comprehensive Logging**: Logs detailed information, warnings, and errors to both the console and a log file.
- **Unit Testing**: Includes a basic test suite to ensure core functionalities work as expected.

## Prerequisites

- **Python 3.6 or Later**: Ensure Python is installed on your system.
- **Required Python Libraries**:
  - `pathspec`: For parsing `.gitignore` files.
  - `tqdm`: For displaying progress bars.

### Installation

1. **Clone the Repository** (if applicable) or **Download the Script**:
   ```bash
   git clone https://github.com/yourusername/consolidate-files.git
   cd consolidate-files
   ```

2. **Install Required Libraries**:
   ```bash
   pip install pathspec tqdm
   ```

## Usage

### Basic Usage

To consolidate all eligible files in the current directory and its subdirectories into `summarised.txt`:

```bash
python consolidate_files.py
```

### Custom Input Directory and Output File

Specify a different input directory and output file:

```bash
python consolidate_files.py /path/to/input_directory /path/to/output_file.txt
```

### Exclude Subdirectories

To consolidate files only in the specified directory without traversing subdirectories:

```bash
python consolidate_files.py --no-include-subdirs
```

### Filter by Specific File Extensions

To include only certain file types (e.g., `.py` and `.js` files):

```bash
python consolidate_files.py --extensions .py .js
```

### Specify a Custom Log File

Change the default log file name and location:

```bash
python consolidate_files.py --log-file my_custom_log.log
```

### Combine Multiple Options

For example, to consolidate only `.py` files in a specific directory without including subdirectories and using a custom log file:

```bash
python consolidate_files.py /path/to/input_directory /path/to/output_file.txt --extensions .py --no-include-subdirs --log-file my_log.log
```

### Help and Documentation

To view all available options and usage instructions:

```bash
python consolidate_files.py -h
```

## Example

Suppose you have a project directory `my_project` containing multiple Python and JavaScript files, along with a `.gitignore` specifying files to exclude. To consolidate these files into `all_code.txt`, run:

```bash
python consolidate_files.py my_project all_code.txt --extensions .py .js
```

## Logging

The script generates a log file (`consolidate_files.log` by default) detailing the consolidation process, including any warnings or errors encountered. To specify a different log file:

```bash
python consolidate_files.py --log-file my_custom_log.log
```

## Running Unit Tests

A basic unit test suite is provided to verify the script's core functionalities.

### To Run the Tests:

1. **Ensure Both Scripts Are in the Same Directory**:
   - `consolidate_files.py`
   - `test_consolidate_files.py`

2. **Execute the Tests**:
   ```bash
   python test_consolidate_files.py
   ```

   **Expected Output**:
   ```
   ....
   ----------------------------------------------------------------------
   Ran 4 tests in 0.XXXs

   OK
   ```

## Additional Considerations

- **Multiple `.gitignore` Files**: The script scans the entire directory tree for `.gitignore` files, ensuring that nested ignore rules are respected.
- **Binary Files**: Non-text files (e.g., images, executables) are automatically detected and skipped to prevent read errors.
- **Progress Feedback**: With `tqdm`, a real-time progress bar provides feedback on the consolidation status, enhancing user experience for large projects.
- **Extensibility**: The script is modular and can be extended or integrated with other tools as needed.
- **Error Handling**: Robust error handling ensures that the script continues processing other files even if some files encounter issues.

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

---
