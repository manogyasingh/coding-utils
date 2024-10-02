import os
import argparse
import sys
import logging
from pathlib import Path
import mimetypes

try:
    import pathspec
except ImportError:
    print("The 'pathspec' library is required to run this script.")
    print("Install it using: pip install pathspec")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    print("The 'tqdm' library is required to run this script.")
    print("Install it using: pip install tqdm")
    sys.exit(1)


def setup_logging(log_file: str):
    """
    Configures logging to log messages to both console and a log file.

    Args:
        log_file (str): Path to the log file.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File Handler
    fh = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console Handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def load_gitignore_patterns(input_dir: str, extra_patterns: list = None) -> pathspec.PathSpec:
    """
    Loads and compiles all .gitignore patterns from the input directory and its subdirectories,
    including additional patterns to always ignore specific files.

    Args:
        input_dir (str): Path to the input directory.
        extra_patterns (list, optional): Additional patterns to ignore. Defaults to None.

    Returns:
        pathspec.PathSpec: Compiled pathspec object containing all ignore patterns.
    """
    gitignore_files = list(Path(input_dir).rglob('.gitignore'))
    all_patterns = []
    for gitignore in gitignore_files:
        try:
            with open(gitignore, 'r', encoding='utf-8') as f:
                patterns = f.read().splitlines()
                all_patterns.extend(patterns)
            logging.debug(f"Loaded .gitignore: {gitignore}")
        except Exception as e:
            logging.warning(f"Failed to read {gitignore}: {e}")

    if extra_patterns:
        all_patterns.extend(extra_patterns)
        logging.debug(f"Added extra ignore patterns: {extra_patterns}")

    if not all_patterns:
        logging.info("No .gitignore patterns found.")
        return None

    spec = pathspec.PathSpec.from_lines('gitwildmatch', all_patterns)
    return spec


def is_binary_file(file_path: str) -> bool:
    """
    Determines if a file is binary.

    Args:
        file_path (str): Path to the file.

    Returns:
        bool: True if binary, False otherwise.
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        # Unknown type, perform a heuristic check
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\0' in chunk:
                    return True
        except Exception as e:
            logging.warning(f"Could not read file for binary check {file_path}: {e}")
            return True  # Assume binary if cannot read
    else:
        if mime_type.startswith('text/'):
            return False
        else:
            return True
    return False


def should_ignore(file_path: str, spec: pathspec.PathSpec, input_dir: str) -> bool:
    """
    Determines if a file should be ignored based on the .gitignore patterns.

    Args:
        file_path (str): Absolute path to the file.
        spec (pathspec.PathSpec): Compiled pathspec object.
        input_dir (str): Path to the input directory.

    Returns:
        bool: True if the file should be ignored, False otherwise.
    """
    if spec is None:
        return False

    # Compute the relative path from the input directory
    rel_path = os.path.relpath(file_path, input_dir)
    return spec.match_file(rel_path)


def append_file_content(file_path: str, outfile, input_dir: str):
    """
    Appends the content of a single file to the output file with a header.

    Args:
        file_path (str): Path to the file to be appended.
        outfile (file object): The output file object opened in write mode.
        input_dir (str): Path to the input directory.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as infile:
            relative_path = os.path.relpath(file_path, input_dir)
            outfile.write(f"\n\n# ----- Start of {relative_path} -----\n\n")
            content = infile.read()
            outfile.write(content)
            outfile.write(f"\n\n# ----- End of {relative_path} -----\n")
        logging.debug(f"Appended file: {file_path}")
    except UnicodeDecodeError:
        logging.warning(f"Skipped binary file: {file_path}")
    except Exception as e:
        logging.error(f"Failed to read {file_path}: {e}")


def consolidate_files(input_dir: str, output_file: str, include_subdirs: bool, spec: pathspec.PathSpec, extensions: list):
    """
    Consolidates all non-ignored, non-binary files from the input directory into a single output file.

    Args:
        input_dir (str): Path to the input directory containing files to consolidate.
        output_file (str): Path to the output file where contents will be written.
        include_subdirs (bool): Whether to include files from subdirectories.
        spec (pathspec.PathSpec): Compiled pathspec object for ignoring files.
        extensions (list): List of file extensions to include.
    """
    files_to_process = []

    if include_subdirs:
        for root, dirs, files in os.walk(input_dir):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for filename in files:
                file_path = os.path.join(root, filename)
                if should_ignore(file_path, spec, input_dir):
                    logging.debug(f"Ignored by .gitignore: {file_path}")
                    continue
                if not os.path.isfile(file_path):
                    continue
                if extensions and not any(filename.lower().endswith(ext) for ext in extensions):
                    logging.debug(f"Ignored by extension filter: {file_path}")
                    continue
                if is_binary_file(file_path):
                    logging.debug(f"Skipped binary file: {file_path}")
                    continue
                files_to_process.append(file_path)
    else:
        for filename in os.listdir(input_dir):
            file_path = os.path.join(input_dir, filename)
            if not os.path.isfile(file_path):
                continue
            if should_ignore(file_path, spec, input_dir):
                logging.debug(f"Ignored by .gitignore: {file_path}")
                continue
            if extensions and not any(filename.lower().endswith(ext) for ext in extensions):
                logging.debug(f"Ignored by extension filter: {file_path}")
                continue
            if is_binary_file(file_path):
                logging.debug(f"Skipped binary file: {file_path}")
                continue
            files_to_process.append(file_path)

    logging.info(f"Total files to consolidate: {len(files_to_process)}")

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for file_path in tqdm(files_to_process, desc="Consolidating files", unit="file"):
            append_file_content(file_path, outfile, input_dir)

    logging.info(f"All specified files have been consolidated into '{output_file}'.")


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate multiple files into a single file, respecting .gitignore and skipping binary files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'input_dir',
        nargs='?',
        default='.',
        type=str,
        help='Path to the input directory containing files to consolidate.'
    )
    parser.add_argument(
        'output_file',
        nargs='?',
        default='summarised.txt',
        type=str,
        help='Path to the output file where contents will be written.'
    )
    parser.add_argument(
        '--no-include-subdirs',
        dest='include_subdirs',
        action='store_false',
        help='Do not include files from subdirectories.'
    )
    parser.add_argument(
        '--extensions',
        nargs='+',
        help='List of file extensions to include (e.g., --extensions .py .js)'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        default='consolidate_files.log',
        help='Path to the log file.'
    )

    args = parser.parse_args()

    input_dir = args.input_dir
    output_file = args.output_file
    include_subdirs = args.include_subdirs
    extensions = args.extensions
    log_file = args.log_file

    setup_logging(log_file)

    if not os.path.isdir(input_dir):
        logging.error(f"The directory '{input_dir}' does not exist or is not a directory.")
        sys.exit(1)

    logging.info(f"Starting consolidation:")
    logging.info(f"Input Directory: {os.path.abspath(input_dir)}")
    logging.info(f"Output File: {os.path.abspath(output_file)}")
    logging.info(f"Include Subdirectories: {include_subdirs}")
    if extensions:
        logging.info(f"File Extensions Filter: {extensions}")
    else:
        logging.info("File Extensions Filter: None (all file types included)")

    # Determine extra patterns to ignore: the script itself, log files, and the output file
    script_file = os.path.basename(__file__)
    log_file_name = os.path.basename(log_file)
    output_file_name = os.path.basename(output_file)

    extra_ignore_patterns = [
        script_file,
        log_file_name,
        output_file_name
    ]

    # Load .gitignore patterns along with extra ignore patterns
    spec = load_gitignore_patterns(input_dir, extra_ignore_patterns)
    if spec:
        logging.info("Loaded .gitignore patterns. Files matching the patterns will be ignored.")
    else:
        logging.info("No .gitignore patterns found. All files will be considered for consolidation.")

    consolidate_files(input_dir, output_file, include_subdirs, spec, extensions)


if __name__ == "__main__":
    main()
