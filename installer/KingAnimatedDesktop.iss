; King Animated Desktop - Inno Setup 6 script
; Build:  iscc /DAppVersion=1.0.1 installer\KingAnimatedDesktop.iss
; Prerequisite: dist\KingAnimatedDesktop\ must exist (PyInstaller one-folder build) - see build_windows_installer.bat
#ifndef AppVersion
  #define AppVersion "1.0.1"
#endif
#define AppName "King Animated Desktop"
#define AppExe  "KingAnimatedDesktop.exe"

[Setup]
AppId={{7D3C1E52-4B6A-4F0E-9B1D-6B1D4E0C5A11}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher=TeamExyKings
AppCopyright=Copyright (c) 2026 TeamExyKings (MIT License)
AppPublisherURL=https://teamexykings.in
AppSupportURL=https://github.com/yashwanthramsomireddy/king-animated-desktop/issues
AppUpdatesURL=https://github.com/yashwanthramsomireddy/king-animated-desktop/releases
VersionInfoVersion={#AppVersion}.0
VersionInfoCompany=TeamExyKings
VersionInfoDescription=King Animated Desktop Setup
VersionInfoCopyright=Copyright (c) 2026 TeamExyKings

; ---- install location: C:\Program Files\King Animated Desktop ----
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=admin
#if Ver >= 0x06030000
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
#else
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
#endif
MinVersion=10.0

; ---- legal: licence must be accepted, privacy notice shown (EU / GDPR transparency) ----
LicenseFile=..\EULA.txt
InfoBeforeFile=..\PRIVACY.txt

; ---- look & behaviour ----
WizardStyle=modern
SetupIconFile=..\assets\king_animated_desktop.ico
UninstallDisplayIcon={app}\{#AppExe}
UninstallDisplayName={#AppName}
OutputDir=..\dist
OutputBaseFilename=KingAnimatedDesktop_Setup_{#AppVersion}
Compression=lzma2
SolidCompression=yes
CloseApplications=yes
RestartApplications=no
SetupLogging=no
ShowLanguageDialog=auto
UsePreviousLanguage=no

; ---- Languages: English + the main EU/EEA languages shipped with Inno Setup ----
; NOTE: the licence and privacy texts are provided in English (authoritative version).
[Languages]
Name: "english";    MessagesFile: "compiler:Default.isl"
#if FileExists(CompilerPath + "Languages\French.isl")
#define HAS_french
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
#endif
#if FileExists(CompilerPath + "Languages\German.isl")
#define HAS_german
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
#endif
#if FileExists(CompilerPath + "Languages\Spanish.isl")
#define HAS_spanish
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
#endif
#if FileExists(CompilerPath + "Languages\Italian.isl")
#define HAS_italian
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"
#endif
#if FileExists(CompilerPath + "Languages\Dutch.isl")
#define HAS_dutch
Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"
#endif
#if FileExists(CompilerPath + "Languages\Portuguese.isl")
#define HAS_portuguese
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"
#endif
#if FileExists(CompilerPath + "Languages\Polish.isl")
#define HAS_polish
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"
#endif
#if FileExists(CompilerPath + "Languages\Czech.isl")
#define HAS_czech
Name: "czech"; MessagesFile: "compiler:Languages\Czech.isl"
#endif
#if FileExists(CompilerPath + "Languages\Danish.isl")
#define HAS_danish
Name: "danish"; MessagesFile: "compiler:Languages\Danish.isl"
#endif
#if FileExists(CompilerPath + "Languages\Finnish.isl")
#define HAS_finnish
Name: "finnish"; MessagesFile: "compiler:Languages\Finnish.isl"
#endif
#if FileExists(CompilerPath + "Languages\Hungarian.isl")
#define HAS_hungarian
Name: "hungarian"; MessagesFile: "compiler:Languages\Hungarian.isl"
#endif
#if FileExists(CompilerPath + "Languages\Slovenian.isl")
#define HAS_slovenian
Name: "slovenian"; MessagesFile: "compiler:Languages\Slovenian.isl"
#endif
[CustomMessages]
english.TaskDesktop=Create a &desktop shortcut
english.TaskStartup=Start King Animated Desktop automatically when I sign in to &Windows (you can turn this off later in Settings)
english.GrpShortcuts=Shortcuts:
english.GrpStartup=Startup:
english.LaunchNow=Launch King Animated Desktop now
english.AskDeleteData=Also delete my King Animated Desktop settings?%n%nThis removes the folder %1 (your chosen objects and customisations). King Animated Desktop stores no other personal data.
english.ShortcutSettings=King Animated Desktop Settings
english.ShortcutPrivacy=Privacy Notice
english.ShortcutLicenses=Licenses and Notices
english.ShortcutUninstall=Uninstall King Animated Desktop
#ifdef HAS_french
french.TaskDesktop=Créer un raccourci sur le &bureau
french.TaskStartup=Lancer King Animated Desktop automatiquement à l'ouverture de session &Windows (modifiable ensuite dans les paramètres)
french.GrpShortcuts=Raccourcis :
french.GrpStartup=Démarrage :
french.LaunchNow=Lancer King Animated Desktop maintenant
french.AskDeleteData=Supprimer aussi mes paramètres King Animated Desktop ?%n%nCela supprime le dossier %1 (vos objets et personnalisations). King Animated Desktop ne stocke aucune autre donnée personnelle.
french.ShortcutSettings=Paramètres de King Animated Desktop
french.ShortcutPrivacy=Avis de confidentialité
french.ShortcutLicenses=Licences et mentions
french.ShortcutUninstall=Désinstaller King Animated Desktop
#endif
#ifdef HAS_german
german.TaskDesktop=&Desktop-Verknüpfung erstellen
german.TaskStartup=King Animated Desktop beim Anmelden an &Windows automatisch starten (später in den Einstellungen änderbar)
german.GrpShortcuts=Verknüpfungen:
german.GrpStartup=Autostart:
german.LaunchNow=King Animated Desktop jetzt starten
german.AskDeleteData=Auch meine King-Animated-Desktop-Einstellungen löschen?%n%nDadurch wird der Ordner %1 entfernt (Ihre gewählten Objekte und Anpassungen). King Animated Desktop speichert keine anderen personenbezogenen Daten.
german.ShortcutSettings=King Animated Desktop Einstellungen
german.ShortcutPrivacy=Datenschutzhinweis
german.ShortcutLicenses=Lizenzen und Hinweise
german.ShortcutUninstall=King Animated Desktop deinstallieren
#endif
#ifdef HAS_spanish
spanish.TaskDesktop=Crear un acceso directo en el &escritorio
spanish.TaskStartup=Iniciar King Animated Desktop automáticamente al iniciar sesión en &Windows (se puede desactivar luego en Ajustes)
spanish.GrpShortcuts=Accesos directos:
spanish.GrpStartup=Inicio:
spanish.LaunchNow=Iniciar King Animated Desktop ahora
spanish.AskDeleteData=¿Eliminar también mis ajustes de King Animated Desktop?%n%nSe eliminará la carpeta %1 (tus objetos y personalizaciones). King Animated Desktop no almacena otros datos personales.
spanish.ShortcutSettings=Ajustes de King Animated Desktop
spanish.ShortcutPrivacy=Aviso de privacidad
spanish.ShortcutLicenses=Licencias y avisos
spanish.ShortcutUninstall=Desinstalar King Animated Desktop
#endif
#ifdef HAS_italian
italian.TaskDesktop=Crea un collegamento sul &desktop
italian.TaskStartup=Avvia King Animated Desktop automaticamente all'accesso a &Windows (modificabile poi nelle Impostazioni)
italian.GrpShortcuts=Collegamenti:
italian.GrpStartup=Avvio:
italian.LaunchNow=Avvia King Animated Desktop ora
italian.AskDeleteData=Eliminare anche le mie impostazioni di King Animated Desktop?%n%nVerrà rimossa la cartella %1 (oggetti e personalizzazioni scelti). King Animated Desktop non memorizza altri dati personali.
italian.ShortcutSettings=Impostazioni di King Animated Desktop
italian.ShortcutPrivacy=Informativa sulla privacy
italian.ShortcutLicenses=Licenze e note
italian.ShortcutUninstall=Disinstalla King Animated Desktop
#endif
#ifdef HAS_dutch
dutch.TaskDesktop=Snelkoppeling op het &bureaublad maken
dutch.TaskStartup=King Animated Desktop automatisch starten bij aanmelden bij &Windows (later uit te schakelen in Instellingen)
dutch.GrpShortcuts=Snelkoppelingen:
dutch.GrpStartup=Opstarten:
dutch.LaunchNow=King Animated Desktop nu starten
dutch.AskDeleteData=Ook mijn King Animated Desktop-instellingen verwijderen?%n%nDit verwijdert de map %1 (uw gekozen objecten en aanpassingen). King Animated Desktop slaat geen andere persoonsgegevens op.
dutch.ShortcutSettings=King Animated Desktop-instellingen
dutch.ShortcutPrivacy=Privacyverklaring
dutch.ShortcutLicenses=Licenties en vermeldingen
dutch.ShortcutUninstall=King Animated Desktop verwijderen
#endif
#ifdef HAS_portuguese
portuguese.TaskDesktop=Criar um atalho no &ambiente de trabalho
portuguese.TaskStartup=Iniciar o King Animated Desktop automaticamente ao iniciar sessão no &Windows (pode desativar depois nas Definições)
portuguese.GrpShortcuts=Atalhos:
portuguese.GrpStartup=Arranque:
portuguese.LaunchNow=Iniciar o King Animated Desktop agora
portuguese.AskDeleteData=Eliminar também as minhas definições do King Animated Desktop?%n%nIsto remove a pasta %1 (os seus objetos e personalizações). O King Animated Desktop não guarda outros dados pessoais.
portuguese.ShortcutSettings=Definições do King Animated Desktop
portuguese.ShortcutPrivacy=Aviso de privacidade
portuguese.ShortcutLicenses=Licenças e avisos
portuguese.ShortcutUninstall=Desinstalar o King Animated Desktop
#endif
#ifdef HAS_polish
polish.TaskDesktop=Utwórz skrót na &pulpicie
polish.TaskStartup=Uruchamiaj King Animated Desktop automatycznie po zalogowaniu do &Windows (można wyłączyć później w Ustawieniach)
polish.GrpShortcuts=Skróty:
polish.GrpStartup=Autostart:
polish.LaunchNow=Uruchom King Animated Desktop teraz
polish.AskDeleteData=Usunąć także moje ustawienia King Animated Desktop?%n%nZostanie usunięty folder %1 (wybrane obiekty i personalizacje). King Animated Desktop nie przechowuje innych danych osobowych.
polish.ShortcutSettings=Ustawienia King Animated Desktop
polish.ShortcutPrivacy=Informacja o prywatności
polish.ShortcutLicenses=Licencje i informacje
polish.ShortcutUninstall=Odinstaluj King Animated Desktop
#endif
#ifdef HAS_czech
czech.TaskDesktop=Vytvořit zástupce na &ploše
czech.TaskStartup=Spouštět King Animated Desktop automaticky po přihlášení do &Windows (později lze vypnout v Nastavení)
czech.GrpShortcuts=Zástupci:
czech.GrpStartup=Spuštění:
czech.LaunchNow=Spustit King Animated Desktop nyní
czech.AskDeleteData=Smazat také moje nastavení King Animated Desktop?%n%nTím se odstraní složka %1 (vaše vybrané objekty a úpravy). King Animated Desktop neukládá žádné jiné osobní údaje.
czech.ShortcutSettings=Nastavení King Animated Desktop
czech.ShortcutPrivacy=Zásady ochrany soukromí
czech.ShortcutLicenses=Licence a oznámení
czech.ShortcutUninstall=Odinstalovat King Animated Desktop
#endif
#ifdef HAS_danish
danish.TaskDesktop=Opret en genvej på &skrivebordet
danish.TaskStartup=Start King Animated Desktop automatisk, når jeg logger på &Windows (kan slås fra senere i Indstillinger)
danish.GrpShortcuts=Genveje:
danish.GrpStartup=Opstart:
danish.LaunchNow=Start King Animated Desktop nu
danish.AskDeleteData=Slet også mine King Animated Desktop-indstillinger?%n%nDet fjerner mappen %1 (dine valgte objekter og tilpasninger). King Animated Desktop gemmer ingen andre personoplysninger.
danish.ShortcutSettings=King Animated Desktop-indstillinger
danish.ShortcutPrivacy=Privatlivspolitik
danish.ShortcutLicenses=Licenser og meddelelser
danish.ShortcutUninstall=Afinstaller King Animated Desktop
#endif
#ifdef HAS_finnish
finnish.TaskDesktop=Luo &työpöydän pikakuvake
finnish.TaskStartup=Käynnistä King Animated Desktop automaattisesti &Windowsiin kirjautuessa (voi poistaa myöhemmin Asetuksista)
finnish.GrpShortcuts=Pikakuvakkeet:
finnish.GrpStartup=Käynnistys:
finnish.LaunchNow=Käynnistä King Animated Desktop nyt
finnish.AskDeleteData=Poistetaanko myös King Animated Desktop -asetukseni?%n%nTämä poistaa kansion %1 (valitsemasi kohteet ja mukautukset). King Animated Desktop ei tallenna muita henkilötietoja.
finnish.ShortcutSettings=King Animated Desktop -asetukset
finnish.ShortcutPrivacy=Tietosuojaseloste
finnish.ShortcutLicenses=Lisenssit ja huomautukset
finnish.ShortcutUninstall=Poista King Animated Desktop
#endif
#ifdef HAS_hungarian
hungarian.TaskDesktop=&Asztali parancsikon létrehozása
hungarian.TaskStartup=A King Animated Desktop automatikus indítása &Windows-bejelentkezéskor (később kikapcsolható a Beállításokban)
hungarian.GrpShortcuts=Parancsikonok:
hungarian.GrpStartup=Indítás:
hungarian.LaunchNow=King Animated Desktop indítása most
hungarian.AskDeleteData=Törli a King Animated Desktop beállításaimat is?%n%nEz eltávolítja a(z) %1 mappát (a kiválasztott objektumok és testreszabások). A King Animated Desktop más személyes adatot nem tárol.
hungarian.ShortcutSettings=King Animated Desktop beállítások
hungarian.ShortcutPrivacy=Adatvédelmi tájékoztató
hungarian.ShortcutLicenses=Licencek és közlemények
hungarian.ShortcutUninstall=King Animated Desktop eltávolítása
#endif
#ifdef HAS_slovenian
slovenian.TaskDesktop=Ustvari bližnjico na &namizju
slovenian.TaskStartup=Samodejno zaženi King Animated Desktop ob prijavi v &Windows (kasneje ga lahko izklopite v Nastavitvah)
slovenian.GrpShortcuts=Bližnjice:
slovenian.GrpStartup=Zagon:
slovenian.LaunchNow=Zaženi King Animated Desktop zdaj
slovenian.AskDeleteData=Želite izbrisati tudi moje nastavitve King Animated Desktop?%n%nTo odstrani mapo %1 (izbrani predmeti in prilagoditve). King Animated Desktop ne shranjuje drugih osebnih podatkov.
slovenian.ShortcutSettings=Nastavitve King Animated Desktop
slovenian.ShortcutPrivacy=Obvestilo o zasebnosti
slovenian.ShortcutLicenses=Licence in obvestila
slovenian.ShortcutUninstall=Odstrani King Animated Desktop
#endif

[Tasks]
; Both are ticked by default and clearly worded; the user can untick either one.
Name: "desktopicon"; Description: "{cm:TaskDesktop}"; GroupDescription: "{cm:GrpShortcuts}"
Name: "startupicon"; Description: "{cm:TaskStartup}"; GroupDescription: "{cm:GrpStartup}"

[Files]
Source: "..\dist\KingAnimatedDesktop\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "..\LICENSE";                DestDir: "{app}"; Flags: ignoreversion
Source: "..\EULA.txt";               DestDir: "{app}"; Flags: ignoreversion
Source: "..\PRIVACY.txt";            DestDir: "{app}"; Flags: ignoreversion
Source: "..\THIRD_PARTY_NOTICES.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md";              DestDir: "{app}"; Flags: ignoreversion
Source: "..\licenses\*";             DestDir: "{app}\licenses"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\web\king-animated-desktop\*"; DestDir: "{app}\web\king-animated-desktop"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}";                          Filename: "{app}\{#AppExe}"; WorkingDir: "{app}"
Name: "{autoprograms}\{cm:ShortcutSettings}";               Filename: "{app}\{#AppExe}"; Parameters: "--settings"; WorkingDir: "{app}"
Name: "{autoprograms}\{cm:ShortcutPrivacy}";                Filename: "{app}\web\king-animated-desktop\privacy-policy.html"
Name: "{autoprograms}\{cm:ShortcutLicenses}";               Filename: "{app}\THIRD_PARTY_NOTICES.txt"
Name: "{autoprograms}\{cm:ShortcutUninstall}";              Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}";                           Filename: "{app}\{#AppExe}"; WorkingDir: "{app}"; Tasks: desktopicon

[Registry]
; Start with Windows - per-user entry (HKCU) written only if the box was ticked.
; The app keeps it in sync with Settings > General > "Start with Windows".
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "KingAnimatedDesktop"; ValueData: """{app}\{#AppExe}"" --background"; Flags: uninsdeletevalue; Tasks: startupicon

[Run]
Filename: "{app}\{#AppExe}"; Parameters: "--settings"; Description: "{cm:LaunchNow}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{sys}\taskkill.exe"; Parameters: "/F /IM {#AppExe}"; Flags: runhidden; RunOnceId: "KillKingAnimatedDesktop"

[Code]
// Close a running copy before files are replaced.
function PrepareToInstall(var NeedsRestart: Boolean): String;
var rc: Integer;
begin
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM {#AppExe}', '', SW_HIDE, ewWaitUntilTerminated, rc);
  Result := '';
end;

// If "start with Windows" was un-ticked, record that so the app does not turn it back on at first run.
procedure CurStepChanged(CurStep: TSetupStep);
var cfgDir, cfgFile: String;
begin
  if (CurStep = ssPostInstall) and (not WizardIsTaskSelected('startupicon')) then
  begin
    cfgDir := ExpandConstant('{userappdata}\KingAnimatedDesktop');
    cfgFile := cfgDir + '\config.json';
    if not FileExists(cfgFile) then
    begin
      ForceDirectories(cfgDir);
      SaveStringToFile(cfgFile, '{"start_with_windows": false}', False);
    end;
  end;
end;

// Right to erasure: offer to delete the user's settings when uninstalling.
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var dataDir: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    RegDeleteValue(HKEY_CURRENT_USER, 'Software\Microsoft\Windows\CurrentVersion\Run', 'KingAnimatedDesktop');
    dataDir := ExpandConstant('{userappdata}\KingAnimatedDesktop');
    if DirExists(dataDir) then
      if (not UninstallSilent) and
         (MsgBox(FmtMessage(CustomMessage('AskDeleteData'), [dataDir]), mbConfirmation, MB_YESNO or MB_DEFBUTTON1) = IDYES) then
        DelTree(dataDir, True, True, True)
      else if UninstallSilent then
        DelTree(dataDir, True, True, True);
  end;
end;
