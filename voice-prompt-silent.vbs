Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "powershell -WindowStyle Hidden -Command ""& 'd:\Usu' & Chr(225) & 'rios\traba\Documents\GitHub\voice-to-claude\venv\Scripts\python.exe' -m voice_prompt start""", 0, False
