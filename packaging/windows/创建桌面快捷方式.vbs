Set WshShell = CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")
Set oShortcut = WshShell.CreateShortcut(strDesktop & "\GNU Radio 伴侣 (中文版).lnk")
strCurDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

oShortcut.TargetPath = strCurDir & "\一键启动-GNU Radio中文版.bat"
oShortcut.WorkingDirectory = strCurDir
oShortcut.WindowStyle = 1
oShortcut.Description = "GNU Radio 伴侣 (GRC) 简体中文增强版"

' 如果存在官方图标则绑定图标
strIcon = strCurDir & "\runtime\Menu\gnuradio.ico"
If CreateObject("Scripting.FileSystemObject").FileExists(strIcon) Then
    oShortcut.IconLocation = strIcon & ", 0"
End If

oShortcut.Save
MsgBox "桌面快捷方式已成功创建！" & vbCrLf & vbCrLf & "位置：" & strDesktop & "\GNU Radio 伴侣 (中文版).lnk", 64, "GNU Radio 中文版"
