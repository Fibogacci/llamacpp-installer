"""
Automatyczny instalator llama.cpp
Copyright (c) 2025 Fibogacci
Licencja: MIT

Website: https://fibogacci.pl
GitHub: https://github.com/fibogacci
Projekt: https://fibogacci.pl/ai/llamacpp
LinkedIn: https://linkedin.com/in/Fibogacci

System tłumaczeń dla interfejsu w języku polskim i angielskim
"""
import os
from typing import Dict, Any


class TranslationManager:
    """Menedżer tłumaczeń obsługujący polski i angielski"""
    
    def __init__(self, language: str = "pl"):
        self.language = language.lower()
        self._translations = {
            "pl": self._get_polish_translations(),
            "en": self._get_english_translations()
        }
    
    def set_language(self, language: str) -> None:
        """Ustaw język interfejsu"""
        if language.lower() in self._translations:
            self.language = language.lower()
        else:
            raise ValueError(f"Nieobsługiwany język: {language}")
    
    def get(self, key: str, **kwargs) -> str:
        """Pobierz przetłumaczony tekst"""
        translations = self._translations.get(self.language, self._translations["pl"])
        text = translations.get(key, key)
        
        # Formatuj tekst z parametrami jeśli są podane
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, ValueError):
                return text
        
        return text
    
    def _get_polish_translations(self) -> Dict[str, str]:
        """Polskie tłumaczenia"""
        return {
            # Główny interfejs
            "app_title": "Instalator llama.cpp",
            "app_subtitle": "Automatyczny instalator z optymalizacjami sprzętowymi | by Fibogacci",
            "author": "by Fibogacci | fibogacci.pl",
            
            # Przyciski i akcje
            "exit": "Wyjście",
            "cancel": "Anuluj",
            "select": "Wybierz",
            "browse": "Przeglądaj",
            "back": "Powrót",
            "create": "Utwórz",
            "refresh": "Odśwież",
            "home": "Dom",
            "up_folder": "↑ Folder wyżej",
            "home_folder": "🏠 Katalog domowy",
            "new_folder": "📁+ Nowy katalog",
            
            # Wybór sprzętu
            "select_hardware": "Wybierz typ sprzętu:",
            "auto_detected": "Automatycznie wykryty: {hardware_type}",
            "hardware_info": "Informacje o sprzęcie",
            "start_installation": "Rozpocznij instalację",
            
            # Katalogi i pliki
            "installation_directory": "Katalog instalacji:",
            "dir_placeholder": "Ścieżka do katalogu instalacji...",
            "config_placeholder": "Ścieżka do pliku .txt z flagami CMAKE...",
            "select_directory": "Wybierz katalog",
            "select_install_dir": "Wybierz katalog instalacji",
            "select_config_file": "Wybierz plik konfiguracji",
            "file_type": "Typ plików: {pattern}",
            "selected_directory": "Wybrany katalog:",
            "selected_file": "Wybrany plik:",
            
            # Browser i nawigacja
            "navigation_help": "Nawigacja: ↑↓ - poruszanie, Enter/Spacja - rozwiń",
            "file_navigation_help": "Nawigacja: ↑↓ - poruszanie, Enter - wybierz plik",
            "select_this_directory": "Wybierz ten katalog",
            "select_this_file": "Wybierz ten plik",
            
            # Tworzenie katalogów
            "create_new_directory": "Utwórz nowy katalog",
            "enter_directory_name": "Podaj nazwę nowego katalogu:",
            "directory_name_placeholder": "nazwa_katalogu",
            
            # Informacje o sprzęcie
            "hardware_type": "Typ sprzętu",
            "system": "System",
            "architecture": "Architektura",
            "ram_memory": "Pamięć RAM",
            "physical_cores": "Rdzenie fizyczne",
            "logical_cores": "Rdzenie logiczne",
            "avx_support": "Obsługa AVX",
            "avx2_support": "Obsługa AVX2",
            "suggested_optimizations": "Sugerowane optymalizacje",
            "cmake_flags": "Flagi CMAKE",
            "required_dependencies": "Wymagane zależności",
            
            # Instalacja
            "installation_for": "Instalacja llama.cpp dla: {hardware_type}",
            "installation_directory_label": "Katalog instalacji: {install_dir}",
            "start_install": "Rozpocznij instalację",
            "cancel_install": "Anuluj",
            "finish": "Zakończ",
            
            # Logi instalacji
            "starting_installation": "Rozpoczynam instalację...",
            "checking_dependencies": "Sprawdzanie zależności...",
            "missing_dependencies": "Brakuje zależności: {deps}",
            "installing_dependencies": "Instalowanie zależności...",
            "dependency_install_error": "Błąd instalacji zależności!",
            "dependencies_not_installed": "⚠️  Wymagane zależności systemowe nie są zainstalowane",
            "install_dependencies_manually": "Aby zainstalować brakujące zależności, wykonaj poniższe komendy:",
            "run_installer_again": "Następnie uruchom ponownie instalator.",
            "installation_interrupted": "Instalacja przerwana - brakują zależności systemowe",
            "downloading_llama": "Pobieranie llama.cpp z GitHub...",
            "download_error": "Błąd pobierania llama.cpp!",
            "starting_compilation": "Rozpoczynam kompilację...",
            "compilation_error": "Błąd kompilacji!",
            "creating_wrapper_scripts": "Tworzenie wrapper scripts...",
            "installation_complete": "Instalacja zakończona pomyślnie!",
            "installation_error": "Błąd instalacji: {error}",
            
            # Powiadomienia i błędy
            "select_hardware_type": "Wybierz typ sprzętu!",
            "enter_install_dir": "Podaj katalog instalacji!",
            "config_file_not_exists": "Plik z optymalizacjami nie istnieje!",
            "invalid_directory_path": "Nieprawidłowa ścieżka do katalogu!",
            "invalid_file_path": "Nieprawidłowa ścieżka do pliku!",
            "enter_directory_name_error": "Podaj nazwę katalogu!",
            "invalid_characters": "Nieprawidłowe znaki w nazwie!",
            "directory_exists": "Katalog '{name}' już istnieje!",
            "directory_creation_error": "Błąd tworzenia katalogu: {error}",
            "directory_created": "Utworzono katalog: {name}",
            "error": "Błąd",
            "cannot_create_directory": "Nie można utworzyć katalogu: {directory}",
            
            # Skróty klawiszowe
            "toggle_shortcuts": "Przełącz skróty",
            "shortcuts_panel": "Panel skrótów {status} (F1 lub Ctrl+H)",
            "enabled": "włączony",
            "disabled": "wyłączony",
            
            # CLI
            "cli_description": "Automatyczny instalator llama.cpp | by Fibogacci (fibogacci.pl)",
            "detect_command": "wykryj typ sprzętu i pokaż informacje",
            "install_command": "zainstaluj llama.cpp z optymalizacjami",
            "list_configs_command": "wyświetl dostępne konfiguracje optymalizacji",
            "hardware_option": "typ sprzętu (użyj 'list-configs' aby zobaczyć opcje)",
            "dir_option": "katalog instalacji",
            "config_option": "plik z własnymi flagami CMAKE",
            "auto_detect_option": "automatyczne wykrywanie sprzętu",
            "language_option": "język interfejsu (pl/en)",
            "hardware_info_table": "informacje o sprzęcie",
            "property": "właściwość",
            "value": "wartość",
            "description": "opis",
            "cmake_flags_label": "flagi CMAKE",
            "dependencies_label": "zależności",
            "more_flags": "... i {count} więcej",
            "more_deps": "... i {count} więcej",
            
            # Opisy typów sprzętu
            "hardware_rpi5_8gb": "Raspberry Pi 5 8GB - pełne optymalizacje ARM64 z OpenBLAS i RPC",
            "hardware_rpi5_16gb": "Raspberry Pi 5 16GB - maksymalne optymalizacje ARM64 z OpenBLAS i RPC",
            "hardware_rpi5_4gb": "Raspberry Pi 5 4GB - zrównoważone optymalizacje ARM64",
            "hardware_rpi4": "Raspberry Pi 4 - optymalizacje Cortex-A72 z OpenBLAS",
            "hardware_rpi_other": "Inne Raspberry Pi - podstawowe optymalizacje ARM",
            "hardware_termux": "Termux Android - minimalne optymalizacje bez BLAS",
            "hardware_dynamic": "Linux x86_64 - automatyczne wykrywanie i optymalizacja CPU",
            "hardware_x86_linux": "Linux x86_64 - pełne optymalizacje AVX2 z OpenBLAS",
            "hardware_x86_linux_old": "Linux x86_64 (starsze CPU) - optymalizacje AVX bez AVX2",
            "hardware_x86_linux_minimal": "Linux x86_64 (bardzo stare CPU) - minimalne optymalizacje bez AVX",
            "hardware_no_optimization": "Bez optymalizacji - kompatybilność maksymalna",
            "hardware_unknown": "Nieznany typ sprzętu"
        }
    
    def _get_english_translations(self) -> Dict[str, str]:
        """English translations"""
        return {
            # Main interface
            "app_title": "Llama.cpp installer",
            "app_subtitle": "Automatic installer with hardware optimizations | by Fibogacci",
            "author": "by Fibogacci | fibogacci.pl",
            
            # Buttons and actions
            "exit": "Exit",
            "cancel": "Cancel",
            "select": "Select",
            "browse": "Browse",
            "back": "Back",
            "create": "Create",
            "refresh": "Refresh",
            "home": "Home",
            "up_folder": "↑ Up folder",
            "home_folder": "🏠 Home directory",
            "new_folder": "📁+ New folder",
            
            # Hardware selection
            "select_hardware": "Select hardware type:",
            "auto_detected": "Auto-detected: {hardware_type}",
            "hardware_info": "Hardware information",
            "start_installation": "Start installation",
            
            # Directories and files
            "installation_directory": "Installation directory:",
            "dir_placeholder": "installation directory path...",
            "config_placeholder": "Path to .txt file with CMAKE flags...",
            "select_directory": "Select directory",
            "select_install_dir": "Select installation directory",
            "select_config_file": "Select configuration file",
            "file_type": "File type: {pattern}",
            "selected_directory": "Selected directory:",
            "selected_file": "Selected file:",
            
            # Browser and navigation
            "navigation_help": "Navigation: ↑↓ - move, Enter/Space - expand",
            "file_navigation_help": "Navigation: ↑↓ - move, Enter - select file",
            "select_this_directory": "Select this directory",
            "select_this_file": "Select this file",
            
            # Directory creation
            "create_new_directory": "Create new directory",
            "enter_directory_name": "Enter new directory name:",
            "directory_name_placeholder": "directory_name",
            
            # Hardware information
            "hardware_type": "Hardware type",
            "system": "System",
            "architecture": "Architecture",
            "ram_memory": "RAM memory",
            "physical_cores": "Physical cores",
            "logical_cores": "Logical cores",
            "avx_support": "AVX support",
            "avx2_support": "AVX2 support",
            "suggested_optimizations": "Suggested optimizations",
            "cmake_flags": "CMAKE flags",
            "required_dependencies": "required dependencies",
            
            # Installation
            "installation_for": "llama.cpp installation for: {hardware_type}",
            "installation_directory_label": "installation directory: {install_dir}",
            "start_install": "start installation",
            "cancel_install": "cancel",
            "finish": "Finish",
            
            # Installation logs
            "starting_installation": "Starting installation...",
            "checking_dependencies": "Checking dependencies...",
            "missing_dependencies": "Missing dependencies: {deps}",
            "installing_dependencies": "Installing dependencies...",
            "dependency_install_error": "Dependency installation error!",
            "dependencies_not_installed": "⚠️  Required system dependencies are not installed",
            "install_dependencies_manually": "To install missing dependencies, run the following commands:",
            "run_installer_again": "Then run the installer again.",
            "installation_interrupted": "Installation interrupted - missing system dependencies",
            "downloading_llama": "Downloading llama.cpp from GitHub...",
            "download_error": "Llama.cpp download error!",
            "starting_compilation": "Starting compilation...",
            "compilation_error": "Compilation error!",
            "creating_wrapper_scripts": "Creating wrapper scripts...",
            "installation_complete": "Installation completed successfully!",
            "installation_error": "Installation error: {error}",
            
            # Notifications and errors
            "select_hardware_type": "Select hardware type!",
            "enter_install_dir": "Enter installation directory!",
            "config_file_not_exists": "Optimization file does not exist!",
            "invalid_directory_path": "Invalid directory path!",
            "invalid_file_path": "Invalid file path!",
            "enter_directory_name_error": "Enter directory name!",
            "invalid_characters": "Invalid characters in name!",
            "directory_exists": "Directory '{name}' already exists!",
            "directory_creation_error": "Directory creation error: {error}",
            "directory_created": "Created directory: {name}",
            "error": "Error",
            "cannot_create_directory": "Cannot create directory: {directory}",
            
            # Keyboard shortcuts
            "toggle_shortcuts": "Toggle shortcuts",
            "shortcuts_panel": "Shortcuts panel {status} (F1 or Ctrl+H)",
            "enabled": "enabled",
            "disabled": "disabled",
            
            # CLI
            "cli_description": "Automatic llama.cpp installer | by Fibogacci (fibogacci.pl)",
            "detect_command": "detect hardware type and show information",
            "install_command": "install llama.cpp with optimizations",
            "list_configs_command": "display available optimization configurations",
            "hardware_option": "hardware type (use 'list-configs' to see options)",
            "dir_option": "installation directory",
            "config_option": "file with custom CMAKE flags",
            "auto_detect_option": "automatic hardware detection",
            "language_option": "interface language (pl/en)",
            "hardware_info_table": "hardware information",
            "property": "property",
            "value": "value",
            "description": "description",
            "cmake_flags_label": "CMAKE flags",
            "dependencies_label": "dependencies",
            "more_flags": "... and {count} more",
            "more_deps": "... and {count} more",
            
            # Hardware type descriptions
            "hardware_rpi5_8gb": "Raspberry Pi 5 8GB - full ARM64 optimizations with OpenBLAS and RPC",
            "hardware_rpi5_16gb": "Raspberry Pi 5 16GB - maximum ARM64 optimizations with OpenBLAS and RPC",
            "hardware_rpi5_4gb": "Raspberry Pi 5 4GB - balanced ARM64 optimizations",
            "hardware_rpi4": "Raspberry Pi 4 - Cortex-A72 optimizations with OpenBLAS",
            "hardware_rpi_other": "Other Raspberry Pi - basic ARM optimizations",
            "hardware_termux": "Termux Android - minimal optimizations without BLAS",
            "hardware_dynamic": "Linux x86_64 - automatic CPU detection and optimization",
            "hardware_x86_linux": "Linux x86_64 - full AVX2 optimizations with OpenBLAS",
            "hardware_x86_linux_old": "Linux x86_64 (older CPUs) - AVX optimizations without AVX2",
            "hardware_x86_linux_minimal": "Linux x86_64 (very old CPUs) - minimal optimizations without AVX",
            "hardware_no_optimization": "No optimizations - maximum compatibility",
            "hardware_unknown": "Unknown hardware type"
        }


# Globalna instancja menedżera tłumaczeń
_translator = TranslationManager()


def set_language(language: str) -> None:
    """Ustaw język dla całej aplikacji"""
    _translator.set_language(language)


def get_language() -> str:
    """Pobierz aktualny język"""
    return _translator.language


def t(key: str, **kwargs) -> str:
    """Skrócona funkcja do pobierania tłumaczeń"""
    return _translator.get(key, **kwargs)


def get_language_from_env() -> str:
    """Pobierz język z zmiennych środowiskowych lub argumentów"""
    # Sprawdź zmienną środowiskową
    env_lang = os.getenv('LLAMACPP_INSTALLER_LANG', '').lower()
    if env_lang in ['pl', 'en']:
        return env_lang
    
    # Domyślnie polski
    return 'pl'


# Inicjalizuj język na podstawie środowiska
_translator.set_language(get_language_from_env())