# pa-permission-complexity-analyzer

Analyzes the complexity of permission configurations and assigns a complexity score to highlight potentially problematic areas. Focused on tools for analyzing and assessing file system permissions.

Score formula: for each path, the score is the number of permission bits set (the nine read, write, and execute bits plus the setuid, setgid, and sticky bits, counted from the file mode) plus the path depth below the analyzed root (the root itself is depth 0, a direct child is depth 1, and so on). A single file path given as the argument is scored as that one file at depth 0. Ignore patterns prune ignored directories from the walk, so their contents are not analyzed. The -v flag sets the logging level to DEBUG.

## Install

```
git clone https://github.com/ShadowGuard-AI/pa-permission-complexity-analyzer.git
cd pa-permission-complexity-analyzer
pip install -r requirements.txt
```

## Usage

```
python3 main.py PATH [options]
```

## Parameters

- `PATH`: Required positional. The path to analyze.
- `-i, --ignore`: One or more glob patterns to ignore (for example, `*.log`, `/tmp/*`).
- `-v, --verbose`: Enable verbose output (sets logging to DEBUG).

## Verified in this wave

`python3 main.py --help` could not run in this sandbox: it exits 1 with "Error: Missing dependencies. Please install them: pip install pathspec rich" because those packages are not installed and installs are not made in this wave. Parameters above are taken from the argument parser in `main.py`, and `main.py` passes `py_compile`. No live analysis run is claimed.

## License

See LICENSE.
