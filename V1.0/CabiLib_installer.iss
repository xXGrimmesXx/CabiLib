[Setup]
AppName=CabiLib
AppVersion=1.0
DefaultDirName={autopf}\CabiLib
OutputBaseFilename=CabiLib_installateur
; Logo de l'installateur (icône .ico)
SetupIconFile=cabilib_logo.ico

[Files]
; L'exécutable principal de votre application
Source: "CabiLib.exe"; DestDir: "{app}"; Flags: ignoreversion
; Autres DLL ou fichiers nécessaires (si vous en avez)
; Source: "*.dll"; DestDir: "{app}"; Flags: ignoreversion

; Fichiers à copier dans AppData lors de l'installation
[Files]
Source: "CabiLib.db"; DestDir: "{userappdata}\CabiLib"; Flags: onlyifdoesntexist uninsneveruninstall
Source: "C:\Users\mloui\Desktop\CabiLib\src\Constantes.json"; DestDir: "{userappdata}\CabiLib"; Flags: onlyifdoesntexist uninsneveruninstall

[Icons]
; Créer un raccourci dans le menu Démarrer
Name: "{autoprograms}\CabiLib"; Filename: "{app}\CabiLib.exe"
; Créer un raccourci sur le Bureau (optionnel)
Name: "{autodesktop}\CabiLib"; Filename: "{app}\CabiLib.exe"; Tasks: desktopicon

[Tasks]
; Permettre à l'utilisateur de choisir s'il veut un raccourci Bureau
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Icônes supplémentaires:"

[Code]
var
  LogoPage: TInputFileWizardPage;
  LogoFilePath: String;

procedure InitializeWizard;
begin
  // Créer une page personnalisée pour sélectionner le logo
  LogoPage := CreateInputFilePage(
    wpSelectDir,
    'Sélection du logo',
    'Choisissez un fichier image pour le logo de l''application',
    'Veuillez sélectionner un fichier image (PNG, JPG, BMP) qui servira de logo.'
  );
  
  // Ajouter un champ de sélection de fichier
  LogoPage.Add(
    'Fichier logo:',
    'Image Files|*.png;*.jpg;*.jpeg;*.bmp|All Files|*.*',
    '.png'
  );
  
  // Optionnel : définir une valeur par défaut
  LogoPage.Values[0] := '';
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  // Vérifier si l'utilisateur a sélectionné un fichier sur la page du logo
  if CurPageID = LogoPage.ID then
  begin
    LogoFilePath := LogoPage.Values[0];
    
    // Vérifier qu'un fichier a été sélectionné
    if LogoFilePath = '' then
    begin
      MsgBox('Veuillez sélectionner un fichier logo.', mbError, MB_OK);
      Result := False;
      Exit;
    end;
    
    // Vérifier que le fichier existe
    if not FileExists(LogoFilePath) then
    begin
      MsgBox('Le fichier sélectionné n''existe pas.', mbError, MB_OK);
      Result := False;
      Exit;
    end;
  end;
end;

function InitializeSetup(): Boolean;
var
  DbPath, JsonPath: String;
begin
  Result := True;
  DbPath := ExpandConstant('{userappdata}\CabiLib\CabiLib.db');
  JsonPath := ExpandConstant('{userappdata}\CabiLib\Constantes.json');
  
  if FileExists(DbPath) then
    MsgBox('AVANT INSTALLATION:' + #13#10 + 'CabiLib.db EXISTE', mbInformation, MB_OK)
  else
    MsgBox('AVANT INSTALLATION:' + #13#10 + 'CabiLib.db N''EXISTE PAS', mbInformation, MB_OK);
    
  if FileExists(JsonPath) then
    MsgBox('AVANT INSTALLATION:' + #13#10 + 'Constantes.json EXISTE', mbInformation, MB_OK)
  else
    MsgBox('AVANT INSTALLATION:' + #13#10 + 'Constantes.json N''EXISTE PAS', mbInformation, MB_OK);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  DbPath, JsonPath: String;
  DbExists, JsonExists: String;
begin
  if CurStep = ssPostInstall then
  begin
    DbPath := ExpandConstant('{userappdata}\CabiLib\CabiLib.db');
    JsonPath := ExpandConstant('{userappdata}\CabiLib\Constantes.json');
    
    if FileExists(DbPath) then
      DbExists := 'OUI'
    else
      DbExists := 'NON';
      
    if FileExists(JsonPath) then
      JsonExists := 'OUI'
    else
      JsonExists := 'NON';
    
    MsgBox('APRES INSTALLATION:' + #13#10 + 
           'CabiLib.db existe: ' + DbExists + #13#10 +
           'Constantes.json existe: ' + JsonExists, 
           mbInformation, MB_OK);
  end;
end;