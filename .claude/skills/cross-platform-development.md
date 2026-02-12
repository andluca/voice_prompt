# Cross-Platform Development (Linux + Windows)

## Path Handling

### Always Use pathlib.Path
```python
from pathlib import Path

# ✅ Cross-platform paths
config_dir = Path.home() / ".voice_prompt"
config_file = config_dir / "config.yaml"
log_file = config_dir / "logs" / "app.log"

# ✅ Works on both Windows and Linux
cache_dir = Path("~/.cache/whisper").expanduser()

# ❌ Don't use os.path or string concatenation
config_dir = os.path.expanduser("~") + "/.voice_prompt"  # Breaks on Windows
config_file = config_dir + "/config.yaml"  # Wrong separator on Windows
```

### Handle Path Separators
```python
# ✅ pathlib handles this automatically
from pathlib import Path
path = Path("/tmp/audio.wav")  # Works on Linux
path = Path("C:/Users/user/audio.wav")  # Works on Windows

# ❌ Don't hardcode separators
path = "/tmp/audio.wav"  # Fails on Windows
path = "C:\\Users\\user\\audio.wav"  # Only works on Windows
```

## Platform Detection

### Use platform.system()
```python
import platform

def get_config_dir() -> Path:
    """Get platform-appropriate config directory."""
    system = platform.system()
    
    if system == "Linux":
        # XDG standard: ~/.config/voice_prompt
        return Path.home() / ".config" / "voice_prompt"
    elif system == "Windows":
        # Windows: %APPDATA%/voice_prompt
        return Path(os.getenv("APPDATA")) / "voice_prompt"
    elif system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "voice_prompt"
    else:
        # Fallback
        return Path.home() / ".voice_prompt"
```

### Platform-Specific Code Blocks
```python
import platform

if platform.system() == "Windows":
    # Windows-specific implementation
    import winsound
    winsound.Beep(1000, 200)
else:
    # Unix-like systems
    os.system('aplay beep.wav')
```

## Audio Recording

### sounddevice Works Cross-Platform
```python
import sounddevice as sd
import numpy as np

# ✅ Same code on Linux and Windows
def record_audio(duration: float, samplerate: int = 16000) -> np.ndarray:
    """Record audio - works on both platforms."""
    audio = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype='int16'
    )
    sd.wait()  # Wait for recording to complete
    return audio
```

### Query Available Devices
```python
import sounddevice as sd

def list_audio_devices():
    """List available audio devices."""
    devices = sd.query_devices()
    print(devices)
    
    # Get default input device
    default_input = sd.default.device[0]
    print(f"Default input: {devices[default_input]['name']}")
```

## Keyboard Handling

### pynput for Cross-Platform Hotkeys
```python
from pynput import keyboard

# ✅ Works identically on Linux and Windows
def setup_hotkey():
    """Register global hotkey."""
    def on_activate():
        print("Hotkey activated!")
    
    # Parse hotkey string
    hotkey = keyboard.HotKey(
        keyboard.HotKey.parse('<ctrl>+<shift>+v'),
        on_activate
    )
    
    def for_canonical(f):
        return lambda k: f(listener.canonical(k))
    
    with keyboard.Listener(
        on_press=for_canonical(hotkey.press),
        on_release=for_canonical(hotkey.release)
    ) as listener:
        listener.join()
```

### Platform-Specific Key Codes
```python
from pynput import keyboard
import platform

def get_meta_key():
    """Get platform-appropriate meta key."""
    if platform.system() == "Darwin":  # macOS
        return keyboard.Key.cmd
    else:  # Linux, Windows
        return keyboard.Key.ctrl
```

## File System

### Create Directories Cross-Platform
```python
from pathlib import Path

# ✅ Create directory with parents
config_dir = Path.home() / ".voice_prompt"
config_dir.mkdir(parents=True, exist_ok=True)

# ✅ Check if file exists
if config_file.exists():
    print("Config found")

# ✅ Read/write files (same on all platforms)
with open(config_file, 'w') as f:
    f.write(content)
```

### Temporary Files
```python
import tempfile
from pathlib import Path

# ✅ Platform-appropriate temp directory
with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as tmp:
    temp_path = Path(tmp.name)
    # Use temp_path
    # File automatically deleted after block

# ✅ Get temp directory
temp_dir = Path(tempfile.gettempdir())
```

## Environment Variables

### Cross-Platform Environment Access
```python
import os
from pathlib import Path

# ✅ Get environment variable with fallback
cache_dir = os.getenv("VOICE_PROMPT_CACHE", str(Path.home() / ".cache"))

# ✅ Platform-specific environment variables
if platform.system() == "Windows":
    appdata = Path(os.getenv("APPDATA"))
    config_dir = appdata / "voice_prompt"
else:
    config_dir = Path.home() / ".config" / "voice_prompt"
```

## Subprocess and Commands

### Cross-Platform Command Execution
```python
import subprocess
import platform

def open_file_browser(path: Path):
    """Open file browser at path."""
    system = platform.system()
    
    if system == "Windows":
        subprocess.run(["explorer", str(path)])
    elif system == "Darwin":  # macOS
        subprocess.run(["open", str(path)])
    else:  # Linux
        subprocess.run(["xdg-open", str(path)])
```

### Shell vs No Shell
```python
# ✅ Avoid shell=True (security risk and platform-dependent)
subprocess.run(["python", "script.py"])

# ❌ shell=True behaves differently on Windows vs Linux
subprocess.run("python script.py", shell=True)
```

## Line Endings

### Handle Different Line Endings
```python
# ✅ Python handles line endings automatically
with open(file_path, 'w') as f:
    f.write("line 1\nline 2\n")  # Converts to platform-appropriate ending

# ✅ Universal newline mode (default in Python 3)
with open(file_path, 'r') as f:
    content = f.read()  # Handles \n, \r\n, \r automatically
```

## Notifications

### Cross-Platform Desktop Notifications
```python
from plyer import notification

def show_notification(title: str, message: str, timeout: int = 3):
    """Show desktop notification - works on Linux and Windows."""
    try:
        notification.notify(
            title=title,
            message=message,
            timeout=timeout,
            app_name="Voice Prompt"
        )
    except Exception as e:
        # Fallback to console if notifications fail
        print(f"{title}: {message}")
        logger.error(f"Notification failed: {e}")
```

## Testing Cross-Platform

### Use pytest Markers
```python
import pytest
import platform

@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="Linux-only test"
)
def test_systemd_service():
    """Test systemd service installation."""
    ...

@pytest.mark.skipif(
    platform.system() == "Linux",
    reason="Windows-only test"
)
def test_windows_service():
    """Test Windows service installation."""
    ...
```

### Mock Platform-Specific Code
```python
from unittest.mock import patch

@patch('platform.system')
def test_cross_platform_config(mock_system):
    """Test config directory on different platforms."""
    # Test Windows
    mock_system.return_value = "Windows"
    config_dir = get_config_dir()
    assert "AppData" in str(config_dir)
    
    # Test Linux
    mock_system.return_value = "Linux"
    config_dir = get_config_dir()
    assert ".config" in str(config_dir)
```

## Installation Scripts

### Linux (bash)
```bash
#!/bin/bash
set -e  # Exit on error

# Detect Python
if command -v python3 &> /dev/null; then
    PYTHON=python3
else
    echo "Python 3 not found!"
    exit 1
fi

# Create venv
$PYTHON -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create config directory (XDG standard)
mkdir -p ~/.config/voice_prompt
cp config.yaml.example ~/.config/voice_prompt/config.yaml

echo "Installation complete!"
```

### Windows (PowerShell)
```powershell
# setup.ps1
$ErrorActionPreference = "Stop"

# Detect Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error "Python not found! Install from python.org"
    exit 1
}

# Create venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create config directory
$configDir = "$env:APPDATA\voice_prompt"
New-Item -ItemType Directory -Force -Path $configDir
Copy-Item config.yaml.example "$configDir\config.yaml"

Write-Host "Installation complete!"
```

## Service/Daemon Management

### Linux (systemd)
```ini
# voice_prompt.service
[Unit]
Description=Voice Prompt Service
After=network.target

[Service]
Type=simple
ExecStart=/path/to/venv/bin/python -m voice_prompt
Restart=on-failure
User=%i

[Install]
WantedBy=default.target
```

```bash
# Install service
mkdir -p ~/.config/systemd/user
cp voice_prompt.service ~/.config/systemd/user/
systemctl --user enable voice_prompt
systemctl --user start voice_prompt
```

### Windows (Startup)
```powershell
# Add to Windows startup
$startupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$shortcut = "$startupPath\voice_prompt.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcut)
$Shortcut.TargetPath = "pythonw.exe"  # No console window
$Shortcut.Arguments = "-m voice_prompt"
$Shortcut.WorkingDirectory = "$PWD"
$Shortcut.Save()
```

## Logging

### Platform-Appropriate Log Locations
```python
import platform
from pathlib import Path

def get_log_dir() -> Path:
    """Get platform-appropriate log directory."""
    system = platform.system()
    
    if system == "Linux":
        # XDG standard: ~/.local/state/voice_prompt
        return Path.home() / ".local" / "state" / "voice_prompt"
    elif system == "Windows":
        # Windows: %LOCALAPPDATA%/voice_prompt/logs
        return Path(os.getenv("LOCALAPPDATA")) / "voice_prompt" / "logs"
    elif system == "Darwin":  # macOS
        return Path.home() / "Library" / "Logs" / "voice_prompt"
    else:
        return Path.home() / ".voice_prompt" / "logs"

# Create log directory
log_dir = get_log_dir()
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "voice-prompt.log"
```

## Performance Considerations

### GPU Detection
```python
def get_device() -> str:
    """Detect best available device for Whisper."""
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
    except ImportError:
        pass
    
    # Check for Apple Silicon (macOS)
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        try:
            import torch
            if torch.backends.mps.is_available():
                return "mps"  # Metal Performance Shaders
        except (ImportError, AttributeError):
            pass
    
    return "cpu"
```

## Common Pitfalls

### 1. Hardcoded Paths
```python
# ❌ Only works on Linux
LOG_FILE = "/var/log/voice-prompt.log"
CONFIG_FILE = "~/.voice_prompt/config.yaml"

# ✅ Cross-platform
LOG_FILE = get_log_dir() / "voice-prompt.log"
CONFIG_FILE = get_config_dir() / "config.yaml"
```

### 2. Shell-Specific Commands
```python
# ❌ Linux-only
os.system("killall -9 voice-prompt")

# ✅ Cross-platform
import psutil
for proc in psutil.process_iter(['name']):
    if proc.info['name'] == 'voice-prompt':
        proc.kill()
```

### 3. Permission Assumptions
```python
# ❌ Assumes Unix permissions
os.chmod(file_path, 0o755)

# ✅ Check platform first
if platform.system() != "Windows":
    os.chmod(file_path, 0o755)
```

### 4. Case-Sensitive File Systems
```python
# ❌ Assumes case-insensitive (Windows behavior)
if Path("Config.yaml").exists():
    ...

# ✅ Use exact case
if Path("config.yaml").exists():
    ...
```

## Testing Strategy

### Test on Both Platforms Regularly
1. **Primary development**: Linux (Omarchy)
2. **Test on Windows**: At least once per major feature
3. **Continuous Integration**: GitHub Actions with both platforms

### GitHub Actions Example
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ["3.9", "3.10", "3.11"]
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r requirements.txt
      - run: pytest
```

## Documentation

### Document Platform Differences
```python
def setup_service():
    """Install as system service.
    
    Platform-specific behavior:
    - Linux: Installs systemd user service
    - Windows: Creates startup shortcut
    - macOS: Creates LaunchAgent
    
    Requires:
    - Linux: systemd
    - Windows: No additional requirements
    - macOS: launchctl
    """
    ...
```

## Summary Checklist

When writing cross-platform code:
- [ ] Use pathlib.Path for all paths
- [ ] Test on both Linux and Windows
- [ ] Use platform.system() for platform-specific code
- [ ] Avoid shell=True in subprocess
- [ ] Use platform-appropriate config/log directories
- [ ] Handle environment variables carefully
- [ ] Use plyer for notifications
- [ ] Document platform differences
- [ ] Create installation scripts for both platforms
- [ ] Test with CI on multiple platforms
