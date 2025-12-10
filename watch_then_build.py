import sys
import time
import json
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileWatchHandler(FileSystemEventHandler):
    def __init__(self, group_name, batch_file, tracked_files, debounce_seconds):
        self.group_name = group_name
        self.batch_file = batch_file
        self.tracked_files = [Path(f).resolve() for f in tracked_files]
        self.debounce_seconds = debounce_seconds
        self.last_run = 0
        # Track actual modification times to filter out access-only events
        self.file_mtimes = {}
        for f in self.tracked_files:
            try:
                self.file_mtimes[f] = f.stat().st_mtime
            except OSError:
                self.file_mtimes[f] = 0
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Check if the modified file is one of our tracked files
        modified_path = Path(event.src_path).resolve()
        if modified_path in self.tracked_files:
            # Check if the actual modification time changed (not just access time)
            try:
                current_mtime = modified_path.stat().st_mtime
            except OSError:
                return
            
            last_mtime = self.file_mtimes.get(modified_path, 0)
            if current_mtime == last_mtime:
                # File was accessed but not actually modified - ignore
                return
            
            self.file_mtimes[modified_path] = current_mtime
            current_time = time.time()
            
            if current_time - self.last_run > self.debounce_seconds:
                print(f"\n[{time.strftime('%H:%M:%S')}] [{self.group_name}]")
                print(f"  Changed: {event.src_path}")
                print(f"  Running: {self.batch_file}")
                
                try:
                    result = subprocess.run(
                        self.batch_file,
                        shell=True,
                        capture_output=True,
                        text=True,
                        cwd=Path(self.batch_file).parent if Path(self.batch_file).parent.exists() else None
                    )
                    
                    if result.stdout:
                        print(f"  Output:\n{self._indent(result.stdout)}")
                    if result.stderr:
                        print(f"  Errors:\n{self._indent(result.stderr)}")
                    
                    if result.returncode == 0:
                        print(f"  ✓ [{self.group_name}] completed successfully")
                    else:
                        print(f"  ✗ [{self.group_name}] exited with code {result.returncode}")
                        
                except Exception as e:
                    print(f"  ✗ Failed to run batch file: {e}")
                
                self.last_run = current_time
    
    def _indent(self, text):
        return '\n'.join(f"    {line}" for line in text.splitlines())

def load_config(config_file):
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        if 'groups' not in config:
            print("Error: Config file must contain 'groups' array")
            return None
        
        return config
    except FileNotFoundError:
        print(f"Error: Config file not found: {config_file}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python watch_then_build.py <config_file.json>")
        print("\nConfig file format:")
        print("""{
  "groups": [
    {
      "name": "Project Name",
      "batch_file": "path/to/build.bat",
      "files": ["path/to/file1.txt", "path/to/file2.cmake"]
    }
  ],
  "debounce_seconds": 2
}""")
        sys.exit(1)
    
    config_file = sys.argv[1]
    config = load_config(config_file)
    
    if not config:
        sys.exit(1)
    
    debounce_seconds = config.get('debounce_seconds', 2)
    observer = Observer()
    groups_configured = 0
    
    print("=" * 60)
    print("File Watcher - Multi-Group Monitor")
    print("=" * 60)
    
    for group in config['groups']:
        group_name = group.get('name', 'Unnamed Group')
        batch_file = group.get('batch_file')
        files = group.get('files', [])
        
        if not batch_file:
            print(f"\n⚠ Warning: Group '{group_name}' has no batch_file, skipping")
            continue
        
        if not Path(batch_file).exists():
            print(f"\n⚠ Warning: Batch file not found for '{group_name}': {batch_file}")
            continue
        
        if not files:
            print(f"\n⚠ Warning: Group '{group_name}' has no files to watch, skipping")
            continue
        
        print(f"\n[{group_name}]")
        print(f"  Batch file: {batch_file}")
        
        # Validate files and collect their parent directories
        valid_files = []
        directories_to_watch = set()
        
        for file_path in files:
            path = Path(file_path)
            if path.exists():
                valid_files.append(str(path))
                directories_to_watch.add(str(path.parent))
                print(f"  ✓ Tracking: {file_path}")
            else:
                print(f"  ✗ File not found: {file_path}")
        
        if not valid_files:
            print(f"  ⚠ No valid files found for '{group_name}', skipping")
            continue
        
        # Create handler with the list of valid files
        event_handler = FileWatchHandler(group_name, batch_file, valid_files, debounce_seconds)
        
        # Watch the parent directories (non-recursively)
        for directory in directories_to_watch:
            observer.schedule(event_handler, directory, recursive=False)
        
        groups_configured += 1
    
    if groups_configured == 0:
        print("\nError: No valid groups configured")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print(f"Watching {groups_configured} group(s) for file changes...")
    print("Press Ctrl+C to stop")
    print("=" * 60 + "\n")
    
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping watcher...")
        observer.stop()
    
    observer.join()
    print("Watcher stopped.")

if __name__ == "__main__":
    main()
