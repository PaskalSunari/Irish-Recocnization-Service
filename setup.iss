#define MyAppName "Irish Middleware"
#define MyAppVersion "1.0"
#define MyAppPublisher "Search Technology"
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
SetupIconFile=eye-recognition.ico
UninstallDisplayIcon={app}\eye-recognition.ico

[Files]
; Main application executable
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
; NSSM service manager
Source: "nssm.exe"; DestDir: "{app}"; Flags: ignoreversion
; Add any other required files here
Source: "eye-recognition.ico"; DestDir: "{app}"; Flags: ignoreversion

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
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; IconFilename: "{app}\eye-recognition.ico"

[Messages]
FinishedLabel=Setup has finished installing [name] on your computer. The service is now running and will start automatically when Windows starts.
PrivilegesRequired=Administrator privileges are required to install Irish Middleware.

[Code]
var
  DeviceIPPage: TInputQueryWizardPage;

function InitializeSetup(): Boolean;
begin
  Result := True; // Continue setup
end;

procedure InitializeWizard;
begin
  DeviceIPPage := CreateInputQueryPage(
    wpWelcome,
    'Device IP Address',
    'Please enter the IP address of your device.',
    'The application needs to know the device IP address to function properly.'
  );
  DeviceIPPage.Add('Device IP:', False);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    RegWriteStringValue(
      HKLM, 'Software\IrishMiddleware', 'DeviceIP', DeviceIPPage.Values[0]
    );
  end;
end;