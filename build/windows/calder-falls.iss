; Inno Setup script for the Calder Falls installer.
; build/build-exe.py --installer runs this with the values below filled in:
;   AppVersion  from calder_falls/__init__.py
;   SourceDir   the PyInstaller folder (dist/Calder-Falls)
;   IconFile    the .ico it made from assets/icon
;   OutDir      dist/
;
; Installs for the current user only, so it never asks for admin rights.

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
; Never change AppId: Windows uses it to match upgrades and the uninstaller
AppId={{6B1F3C2E-1610-4C1D-9A86-CA1DE4FA1186}
AppName=Calder Falls
AppVersion={#AppVersion}
AppPublisher=NullAngst
AppPublisherURL=https://github.com/NullAngst/Calder-Falls
DefaultDirName={autopf}\Calder Falls
DefaultGroupName=Calder Falls
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir={#OutDir}
OutputBaseFilename=Calder-Falls-Setup-x64
SetupIconFile={#IconFile}
UninstallDisplayIcon={app}\Calder Falls.exe
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Tasks]
Name: "desktopicon"; Description: "Put an icon on the desktop"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Calder Falls"; Filename: "{app}\Calder Falls.exe"
Name: "{autodesktop}\Calder Falls"; Filename: "{app}\Calder Falls.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Calder Falls.exe"; Description: "Play Calder Falls"; Flags: nowait postinstall skipifsilent
