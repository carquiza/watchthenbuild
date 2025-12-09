# Watch Then Build

A Python-based file watcher that automatically runs batch files when specific tracked files are modified.
Supports multiple project groups with independent build configurations.

I use this as a light way to automatically rebuild my projects when my makefiles get changed.
Yes, it's like npm watch but with specific files only, and in Python. Because.

## Features

- **Multi-Group Monitoring**: Watch multiple files across projects, each group triggering its own batch file
- **Specific File Tracking**: Monitor only the files you care about (e.g., CMakeLists.txt, config files, specific source files)
- **Debouncing**: Prevents multiple rapid executions when files are saved multiple times
- **Real-time Feedback**: Shows output from batch files as they run
- **JSON Configuration**: Easy-to-edit configuration file for all your projects
- **Cross-Project Support**: One watcher can monitor files from all your projects simultaneously

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Steps

1. **Install Python** (if not already installed):
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, make sure to check "Add Python to PATH"

2. **Install the watchdog library**:
   ```bash
   pip install watchdog
   ```

3. **Download the script**:
   - Clone this repository or download `watch_then_build.py`

## Configuration

### Creating a Configuration File

Create a JSON file (e.g., `watch_config.json`) with the following structure:

```json
{
  "groups": [
    {
      "name": "Main Project",
      "batch_file": "C:/projects/main/build.bat",
      "files": [
        "C:/projects/main/CMakeLists.txt",
        "C:/projects/main/config.json",
        "C:/projects/main/src/important_file.cpp"
      ]
    },
    {
      "name": "Plugin System",
      "batch_file": "C:/projects/plugins/build_plugins.bat",
      "files": [
        "C:/projects/plugins/core/CMakeLists.txt",
        "C:/projects/plugins/extensions/plugin.config"
      ]
    }
  ],
  "debounce_seconds": 2
}
```

### Configuration Parameters

- **groups**: Array of project groups to monitor
  - **name**: Display name for the group (used in console output)
  - **batch_file**: Full path to the batch file to execute when any tracked file changes
  - **files**: Array of specific file paths to monitor
- **debounce_seconds**: Time (in seconds) to wait before allowing another execution (prevents rapid repeated builds)

### Path Format

Paths can use either forward slashes (`/`) or backslashes (`\\`):
- `C:/projects/main/CMakeLists.txt`
- `C:\\projects\\main\\CMakeLists.txt`
- `C:\projects\main\CMakeLists.txt`

## Usage

### Basic Usage

```bash
python watch_then_build.py watch_config.json
```

### Example Output

```
============================================================
File Watcher - Multi-Group Monitor
============================================================

[Main Project]
  Batch file: C:/projects/main/build.bat
  ✓ Tracking: C:/projects/main/CMakeLists.txt
  ✓ Tracking: C:/projects/main/config.json
  ✓ Tracking: C:/projects/main/src/important_file.cpp

[Plugin System]
  Batch file: C:/projects/plugins/build_plugins.bat
  ✓ Tracking: C:/projects/plugins/core/CMakeLists.txt
  ✓ Tracking: C:/projects/plugins/extensions/plugin.config

============================================================
Watching 2 group(s) for file changes...
Press Ctrl+C to stop
============================================================

[14:23:45] [Main Project]
  Changed: C:/projects/main/CMakeLists.txt
  Running: C:/projects/main/build.bat
  Output:
    Building project...
    CMake completed successfully
  ✓ [Main Project] completed successfully
```

### Stopping the Watcher

Press `Ctrl+C` to stop monitoring.

## Use Cases

### Monitor CMake Files
Track CMakeLists.txt files across your project to automatically rebuild when build configuration changes.

### Watch Configuration Files
Monitor config.json, settings.ini, or other configuration files to trigger reload scripts.

### Track Critical Source Files
Watch specific header or implementation files that require special build steps when modified.

### Multiple File Types
Mix and match any file types - CMake files, config files, source files, whatever you need to monitor.

## Tips and Best Practices

1. **Use Absolute Paths**: Always use full paths in your config file to avoid ambiguity

2. **Test Batch Files First**: Run your batch files manually before setting up the watcher to ensure they work correctly

3. **Adjust Debounce Time**: If your text editor saves files multiple times, increase `debounce_seconds` to 3-5 seconds

4. **Organize by Purpose**: Group files that should trigger the same build action together

5. **Keep It Running**: Consider creating a shortcut or startup script to launch the watcher automatically

6. **Check Paths**: The script will warn you about missing files or batch files on startup

## Troubleshooting

### "Module 'watchdog' not found"
Run: `pip install watchdog`

### "Config file not found"
Make sure you're running the command from the correct directory, or use an absolute path to the config file

### "File not found" warnings
Check that all paths in your config file are correct and the files exist

### Batch file runs but nothing happens
- Verify the batch file works when run manually
- Check that the batch file has proper error handling
- Make sure the batch file paths are correct in the config

### Changes not being detected
- Ensure the file path in your config matches the actual file location exactly
- Check that the watcher is still running (check the console)
- Verify the file exists before starting the watcher

## License

Chris Arquiza has licensed this project under the GNU General Public License v3.0 - see the LICENSE file for details.

