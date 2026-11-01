# pa-permission-complexity-analyzer
Analyzes the complexity of permission configurations and assigns a complexity score to highlight potentially problematic areas. - Focused on Tools for analyzing and assessing file system permissions

Score formula: for each path, the score is the number of permission bits set (the nine read, write, and execute bits plus the setuid, setgid, and sticky bits, counted from the file mode) plus the path depth below the analyzed root (the root itself is depth 0, a direct child is depth 1, and so on). A single file path given as the argument is scored as that one file at depth 0. Ignore patterns prune ignored directories from the walk, so their contents are not analyzed. The -v flag sets the logging level to DEBUG.

## Install
`git clone https://github.com/ShadowStrikeHQ/pa-permission-complexity-analyzer`

## Usage
`./pa-permission-complexity-analyzer [params]`

## Parameters
- `-h`: Show help message and exit
- `-i`: No description provided
- `-v`: Enable verbose output.

## License
Copyright (c) ShadowStrikeHQ
