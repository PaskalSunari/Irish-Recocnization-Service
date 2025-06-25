#define MyAppName "Irish Middleware"
#define MyAppVersion "1.0"
#define MyAppPublisher "Your Company"
#define MyAppExeName "main.exe"

[Setup]
AppId={{YOUR-UNIQUE-GUID-HERE}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={commonpf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=installer
OutputBaseFilename=IrishMiddleware_Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Files]
; Main application executable
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
; NSSM service manager
Source: "nssm.exe"; DestDir: "{app}"; Flags: ignoreversion
; Add any other required files here

[Run]
; Install and start the service
Filename: "{app}\nssm.exe"; Parameters: "install IrishMiddleware ""{app}\main.exe"""; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "set IrishMiddleware DisplayName ""Irish Middleware Service"""; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "set IrishMiddleware Description ""Irish Middleware Service for User Management"""; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "set IrishMiddleware Start SERVICE_AUTO_START"; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "start IrishMiddleware"; Flags: runhidden

[UninstallRun]
; Stop and remove service on uninstall
Filename: "{app}\nssm.exe"; Parameters: "stop IrishMiddleware"; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "remove IrishMiddleware confirm"; Flags: runhidden

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "http://localhost:5000/"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

[Messages]
FinishedLabel=Setup has finished installing [name] on your computer. The service is now running and will start automatically when Windows starts.