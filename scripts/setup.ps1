# Windows setup script for Voice-to-Claude
$ErrorActionPreference = "Stop"

$RepoDir = Split-Path -Parent $PSScriptRoot
# If run from scripts/ directly, go up one level
if (Test-Path "$RepoDir\scripts\setup.ps1") {
    # already correct
} else {
    $RepoDir = $PSScriptRoot
}

$VenvDir = Join-Path $RepoDir "venv"

Write-Host "=== Voice-to-Claude Setup ===" -ForegroundColor Cyan

# 1. Create venv
if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment..."
    python -m venv $VenvDir
}

& "$VenvDir\Scripts\Activate.ps1"

# 2. Install dependencies
Write-Host "Installing dependencies..."
pip install --upgrade pip
pip install -r (Join-Path $RepoDir "requirements.txt")

# 3. Create config directory
$ConfigDir = Join-Path $env:USERPROFILE ".voice-to-claude"
if (-not (Test-Path $ConfigDir)) {
    New-Item -ItemType Directory -Path $ConfigDir | Out-Null
}
$ConfigFile = Join-Path $ConfigDir "config.yaml"
if (-not (Test-Path $ConfigFile)) {
    Copy-Item (Join-Path $RepoDir "config.yaml.example") $ConfigFile
    Write-Host "Config copied to $ConfigFile"
}

# 4. Optionally download model
Write-Host ""
$dl = Read-Host "Download Whisper large-v3 model now? (~3 GB) [y/N]"
if ($dl -match "^[Yy]$") {
    python (Join-Path $RepoDir "scripts\download-model.py")
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "  Activate venv:  $VenvDir\Scripts\Activate.ps1"
Write-Host "  Run:            python -m voice_prompt"
Write-Host "  Quick test:     python -m voice_prompt test"
