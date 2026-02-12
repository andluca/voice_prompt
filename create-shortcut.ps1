$WshShell = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')

# Background shortcut (no console window)
$bg = $WshShell.CreateShortcut("$desktop\Voice Prompt.lnk")
$bg.TargetPath = "$PSScriptRoot\venv\Scripts\pythonw.exe"
$bg.Arguments = "-m voice_prompt start"
$bg.WorkingDirectory = $PSScriptRoot
$bg.Description = "Voice Prompt background service"
$bg.Save()
Write-Host "Created: Voice Prompt.lnk (background)"

# Terminal shortcut (shows logs)
$fg = $WshShell.CreateShortcut("$desktop\Voice Prompt Terminal.lnk")
$fg.TargetPath = "$PSScriptRoot\venv\Scripts\python.exe"
$fg.Arguments = "-m voice_prompt start"
$fg.WorkingDirectory = $PSScriptRoot
$fg.Description = "Voice Prompt with terminal logs"
$fg.Save()
Write-Host "Created: Voice Prompt Terminal.lnk (with logs)"
