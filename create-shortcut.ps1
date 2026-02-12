$WshShell = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')
$Shortcut = $WshShell.CreateShortcut("$desktop\Voice Prompt.lnk")
$Shortcut.TargetPath = "$PSScriptRoot\venv\Scripts\pythonw.exe"
$Shortcut.Arguments = "-m voice_prompt start"
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "Voice-to-Claude background service"
$Shortcut.Save()
Write-Host "Shortcut created on Desktop!"
