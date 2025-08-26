; -- setup.iss --
; Inno Setup script for Optical POS

[Setup]
AppName=Optical POS
AppVersion=1.0
DefaultDirName={autopf}\Optical POS
DefaultGroupName=Optical POS
UninstallDisplayIcon={app}\OpticalPOS.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
OutputBaseFilename=OpticalPOS-1.0-setup

[Files]
Source: "..\dist\OpticalPOS\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\Optical POS"; Filename: "{app}\OpticalPOS.exe"
Name: "{commondesktop}\Optical POS"; Filename: "{app}\OpticalPOS.exe"

[Run]
Filename: "{app}\OpticalPOS.exe"; Description: "Launch Optical POS"; Flags: nowait postinstall skipifsilent
