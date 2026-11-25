#define MyAppName "ALPHA PC MONITOR"
#define MyAppVersion "0.1.0"
[Setup]
AppId={{6C2E8B4D-4F1B-4B2D-9E4D-31A1C0A12001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=ALPHA TECHNOLOGY
DefaultDirName={autopf}\ALPHA PC MONITOR
DefaultGroupName=ALPHA PC MONITOR
OutputDir=output
OutputBaseFilename=ALPHA-PC-MONITOR-Setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
[Files]
Source: "..\dist\ALPHA-PC-MONITOR\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
[Icons]
Name: "{group}\ALPHA PC MONITOR"; Filename: "{app}\ALPHA-PC-MONITOR.exe"
Name: "{autodesktop}\ALPHA PC MONITOR"; Filename: "{app}\ALPHA-PC-MONITOR.exe"
