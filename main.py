import argparse
import logging
import os
import stat
import sys
from pathlib import Path

try:
    import pathspec
    from rich.console import Console
    from rich.table import Column, Table
except ImportError as e:
    print(f"Error: Missing dependencies. Please install them: pip install pathspec rich")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PermissionComplexityAnalyzer:
    """
    Analyzes the complexity of file system permission configurations.
    """

    def __init__(self, path, ignore_patterns=None, verbose=False):
        """
        Initializes the PermissionComplexityAnalyzer.

        Args:
            path (str): The path to analyze.
            ignore_patterns (list, optional): A list of glob patterns to ignore. Defaults to None.
            verbose (bool, optional): Enable verbose output. Defaults to False.
        """
        self.path = Path(path).resolve()
        self.ignore_patterns = ignore_patterns or []
        self.verbose = verbose
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
            logging.debug("Verbose output enabled.")
        self.console = Console()  # Use rich for better output
        self.spec = None  # Initialize pathspec for efficient ignoring

        if not self.path.exists():
            raise FileNotFoundError(f"Path not found: {self.path}")

        if self.ignore_patterns:
            try:
                self.spec = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, self.ignore_patterns)
            except Exception as e:
                raise ValueError(f"Invalid ignore patterns: {e}")

    def is_ignored(self, path_str):
        """
        Checks if a file or directory should be ignored based on the ignore patterns.

        Args:
            path_str (str): The path to check.

        Returns:
            bool: True if the path should be ignored, False otherwise.
        """
        if self.spec:
            return self.spec.match_file(path_str)
        return False

    def calculate_complexity(self, path):
        """
        Calculates a complexity score for a given path. This is a simplified
        example and can be extended with more sophisticated metrics.

        Args:
            path (Path): The path to analyze.

        Returns:
            int: A complexity score.
        """
        try:
            stat_info = os.stat(path)
            mode_bits = stat.S_IMODE(stat_info.st_mode)
        except OSError as e:
             logging.error(f"Error getting file stats for {path}: {e}")
             return 0

        # Score formula: the number of permission bits set (the nine
        # read, write, and execute bits plus the setuid, setgid, and
        # sticky bits) plus the path depth below the analyzed root.
        bits_set = bin(mode_bits & 0o7777).count("1")
        try:
            rel = Path(path).resolve().relative_to(self.path) if hasattr(self, "path") else Path(path)
            depth = 0 if str(rel) == "." else len(rel.parts)
            # For a single file analyzed directly, depth below that file is 0.
            if self.path.is_file():
                depth = 0
        except Exception:
            depth = 0

        complexity = bits_set + depth

        return complexity

    def analyze_permissions(self):
        """
        Analyzes the permissions of files and directories within the specified path.
        """
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Path", style="dim", width=50)
        table.add_column("Complexity", justify="right")

        total_complexity = 0

        if self.path.is_file():
            complexity = self.calculate_complexity(self.path)
            total_complexity += complexity
            table.add_row(str(self.path), str(complexity))
            self.console.print(table)
            self.console.print(f"\nTotal Complexity: {total_complexity}", style="bold green")
            return

        try:
            for root, dirs, files in os.walk(self.path):
                root_path = Path(root)

                # Prune ignored directories in place so the walk does not descend into them.
                dirs[:] = [
                    d for d in dirs
                    if not self.is_ignored(str((root_path / d).relative_to(self.path)))
                ]

                if self.is_ignored(str(root_path.relative_to(self.path))):
                    logging.debug(f"Ignoring directory: {root_path}")
                    continue

                complexity = self.calculate_complexity(root_path)
                total_complexity += complexity
                table.add_row(str(root_path.relative_to(self.path)), str(complexity))

                for file in files:
                    file_path = root_path / file
                    if self.is_ignored(str(file_path.relative_to(self.path))):
                        logging.debug(f"Ignoring file: {file_path}")
                        continue

                    complexity = self.calculate_complexity(file_path)
                    total_complexity += complexity
                    table.add_row(str(file_path.relative_to(self.path)), str(complexity))

        except OSError as e:
            logging.error(f"Error walking the directory: {e}")
            print(f"Error: {e}")
            return

        self.console.print(table)
        self.console.print(f"\nTotal Complexity: {total_complexity}", style="bold green")

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.

    Returns:
        argparse.ArgumentParser: The argument parser object.
    """
    parser = argparse.ArgumentParser(
        description="Analyzes the complexity of file system permission configurations."
    )
    parser.add_argument("path", help="The path to analyze.")
    parser.add_argument(
        "-i",
        "--ignore",
        nargs="+",
        help="A list of glob patterns to ignore (e.g., *.log, /tmp/*).",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output."
    )
    return parser

def main():
    """
    Main function to execute the permission complexity analyzer.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    try:
        analyzer = PermissionComplexityAnalyzer(args.path, args.ignore, args.verbose)
        analyzer.analyze_permissions()

    except FileNotFoundError as e:
        logging.error(str(e))
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        logging.error(str(e))
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.exception("An unexpected error occurred:")
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Example Usage:
    # python pa_permission_complexity_analyzer.py /path/to/analyze
    # python pa_permission_complexity_analyzer.py /path/to/analyze -i "*.txt" "*.log"
    # python pa_permission_complexity_analyzer.py /path/to/analyze -v
    main()