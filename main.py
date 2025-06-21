"""
Automatyczny instalator llama.cpp
Copyright (c) 2025 Fibogacci
Licencja: MIT

Website: https://fibogacci.pl
GitHub: https://github.com/fibogacci
Projekt: https://fibogacci.pl/ai/llamacpp
LinkedIn: https://linkedin.com/in/Fibogacci

Główny plik aplikacji z interfejsem Textual
"""
import asyncio
from pathlib import Path
from typing import Optional
import time
import signal
import sys

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Header, Footer, Button, Static, SelectionList, Input, 
    TextArea, ProgressBar, Log, Rule, DirectoryTree
)
from textual.screen import Screen, ModalScreen
from textual import work
from rich.text import Text

from hardware_detector import HardwareDetector
from optimization_configs import OptimizationConfigs
from llama_installer import LlamaInstaller
from translations import set_language, t, get_language_from_env
from logger_config import setup_logging, get_logger, get_installer_logger
from __version__ import __version__, PROJECT_NAME, PROJECT_AUTHOR, PROJECT_URL


class DirectoryBrowserScreen(ModalScreen):
    """Ekran przeglądarki katalogów"""
    
    BINDINGS = [
        ("escape", "cancel", "Anuluj"),
        ("enter", "select", "Wybierz"),
    ]
    
    def __init__(self, current_path: str = None, title: str = "Wybierz katalog"):
        super().__init__()
        self.current_path = Path(current_path) if current_path else Path.cwd()
        self.title = title
        self.selected_path = str(self.current_path)
    
    def on_mount(self) -> None:
        """Po zamontowaniu ekranu"""
        self._check_screen_size()
    
    def _check_screen_size(self) -> None:
        """Sprawdz rozmiar ekranu i włącz compact mode jeśli potrzeba"""
        try:
            size = self.app.console.size
            if size.width < 80 or size.height < 25:
                self.add_class("compact")
            else:
                self.remove_class("compact")
        except:
            pass
    
    def compose(self) -> ComposeResult:
        """Komponuj UI dla przeglądarki katalogów"""
        yield Container(
            Static(self.title, id="browser-title"),
            Horizontal(
                Button("Wybierz ten katalog", id="select-btn", variant="success"),
                Button("Anuluj", id="cancel-btn", variant="error"),
                id="action-buttons"
            ),
            Static("Wybrany katalog:", id="selected-label"),
            Input(
                value=str(self.current_path),
                placeholder="Wpisz ścieżkę...",
                id="path-input"
            ),
            Horizontal(
                Button("↑ Folder wyżej", id="up-btn", variant="default"),
                Button("🏠 Katalog domowy", id="home-btn", variant="default"),
                Button("🔄 Odśwież", id="refresh-btn", variant="default"),
                Button("📁+ Nowy katalog", id="new-dir-btn", variant="primary"),
                id="navigation-buttons"
            ),
            Static("Nawigacja: ↑↓ - poruszanie, Enter/Spacja - rozwiń", id="browser-help"),
            DirectoryTree(str(self.current_path), id="dir-tree"),
            id="browser-container"
        )
    
    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        """Gdy wybrano katalog w drzewie"""
        event.stop()
        self.selected_path = str(event.path)
        path_input = self.query_one("#path-input", Input)
        path_input.value = self.selected_path
    
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Gdy wybrano plik w drzewie - wybieramy katalog rodzica"""
        event.stop()
        parent_path = str(Path(event.path).parent)
        self.selected_path = parent_path
        path_input = self.query_one("#path-input", Input)
        path_input.value = self.selected_path
    
    def on_input_changed(self, event) -> None:
        """Gdy zmieniono ścieżkę w polu input"""
        if event.input.id == "path-input":
            self.selected_path = event.value
    
    def on_button_pressed(self, event) -> None:
        """Obsługa przycisków"""
        if event.button.id == "select-btn":
            if self.selected_path and Path(self.selected_path).is_dir():
                self.dismiss(self.selected_path)
            else:
                self.app.notify("Nieprawidłowa ścieżka do katalogu!", severity="error")
        elif event.button.id == "cancel-btn":
            self.dismiss(None)
        elif event.button.id == "up-btn":
            self._go_up()
        elif event.button.id == "home-btn":
            self._go_home()
        elif event.button.id == "refresh-btn":
            self._refresh_tree()
        elif event.button.id == "new-dir-btn":
            self._create_new_directory()
    
    def _go_up(self) -> None:
        """Przejdź do katalogu wyżej"""
        current = Path(self.selected_path)
        parent = current.parent
        if parent != current:  # Nie jesteśmy w root
            self.selected_path = str(parent)
            self._update_tree_and_input()
    
    def _go_home(self) -> None:
        """Przejdź do katalogu domowego"""
        self.selected_path = str(Path.home())
        self._update_tree_and_input()
    
    def _refresh_tree(self) -> None:
        """Odśwież drzewo katalogów"""
        self._update_tree_and_input()
    
    def _update_tree_and_input(self) -> None:
        """Aktualizuj drzewo i pole input"""
        path_input = self.query_one("#path-input", Input)
        path_input.value = self.selected_path
        
        # Aktualizuj ścieżkę istniejącego drzewa
        tree = self.query_one("#dir-tree", DirectoryTree)
        tree.path = self.selected_path
    
    def _create_new_directory(self) -> None:
        """Stwórz nowy katalog"""
        def create_directory(name):
            if name:
                try:
                    new_path = Path(self.selected_path) / name
                    new_path.mkdir(parents=True, exist_ok=False)
                    self.selected_path = str(new_path)
                    self._update_tree_and_input()
                    self.app.notify(f"Utworzono katalog: {name}", severity="success")
                except FileExistsError:
                    self.app.notify(f"Katalog '{name}' już istnieje!", severity="error")
                except Exception as e:
                    self.app.notify(f"Błąd tworzenia katalogu: {e}", severity="error")
        
        self.app.push_screen(CreateDirectoryScreen(), create_directory)
    
    def action_select(self) -> None:
        """Akcja wyboru (Enter)"""
        if self.selected_path and Path(self.selected_path).is_dir():
            self.dismiss(self.selected_path)
        else:
            self.app.notify("Nieprawidłowa ścieżka do katalogu!", severity="error")
    
    def action_cancel(self) -> None:
        """Akcja anulowania (Escape)"""
        self.dismiss(None)


class CreateDirectoryScreen(ModalScreen):
    """Ekran tworzenia nowego katalogu"""
    
    BINDINGS = [
        ("escape", "cancel", "Anuluj"),
        ("enter", "create", "Utwórz"),
    ]
    
    def compose(self) -> ComposeResult:
        """Komponuj UI dla tworzenia katalogu"""
        yield Container(
            Static("Utwórz nowy katalog", id="create-title"),
            Static("Podaj nazwę nowego katalogu:", id="create-help"),
            Input(
                placeholder="nazwa_katalogu",
                id="dir-name-input"
            ),
            Horizontal(
                Button("Utwórz", id="create-btn", variant="success"),
                Button("Anuluj", id="cancel-btn", variant="default"),
                id="create-buttons"
            ),
            id="create-container"
        )
    
    def on_mount(self) -> None:
        """Po zamontowaniu - focus na input"""
        self.query_one("#dir-name-input", Input).focus()
    
    def on_button_pressed(self, event) -> None:
        """Obsługa przycisków"""
        if event.button.id == "create-btn":
            self._create_directory()
        elif event.button.id == "cancel-btn":
            self.dismiss(None)
    
    def _create_directory(self) -> None:
        """Pobierz nazwę i utwórz katalog"""
        name_input = self.query_one("#dir-name-input", Input)
        name = name_input.value.strip()
        
        if not name:
            self.app.notify("Podaj nazwę katalogu!", severity="error")
            return
        
        # Sprawdz czy nazwa jest prawidłowa
        if any(char in name for char in r'<>:"/\|?*'):
            self.app.notify("Nieprawidłowe znaki w nazwie!", severity="error")
            return
        
        self.dismiss(name)
    
    def action_create(self) -> None:
        """Akcja tworzenia (Enter)"""
        self._create_directory()
    
    def action_cancel(self) -> None:
        """Akcja anulowania (Escape)"""
        self.dismiss(None)


class FileBrowserScreen(ModalScreen):
    """Ekran przeglądarki plików"""
    
    BINDINGS = [
        ("escape", "cancel", "Anuluj"),
        ("enter", "select", "Wybierz"),
    ]
    
    def __init__(self, current_path: str = None, file_pattern: str = "*.txt", title: str = "Wybierz plik"):
        super().__init__()
        self.current_path = Path(current_path) if current_path else Path.cwd()
        self.file_pattern = file_pattern
        self.title = title
        self.selected_path = None
    
    def on_mount(self) -> None:
        """Po zamontowaniu ekranu"""
        self._check_screen_size()
    
    def _check_screen_size(self) -> None:
        """Sprawdz rozmiar ekranu i włącz compact mode jeśli potrzeba"""
        try:
            size = self.app.console.size
            if size.width < 80 or size.height < 25:
                self.add_class("compact")
            else:
                self.remove_class("compact")
        except:
            pass
    
    def compose(self) -> ComposeResult:
        """Komponuj UI dla przeglądarki plików"""
        yield Container(
            Static(self.title, id="browser-title"),
            Horizontal(
                Button("Wybierz ten plik", id="select-btn", variant="success"),
                Button("Anuluj", id="cancel-btn", variant="error"),
                id="action-buttons"
            ),
            Static(f"Typ plików: {self.file_pattern}", id="browser-pattern"),
            Static("Wybrany plik:", id="selected-label"),
            Input(
                value="",
                placeholder=f"Wpisz ścieżkę do pliku ({self.file_pattern})...",
                id="path-input"
            ),
            Horizontal(
                Button("↑ Folder wyżej", id="up-btn", variant="default"),
                Button("🏠 Dom", id="home-btn", variant="default"),
                Button("🔄 Odśwież", id="refresh-btn", variant="default"),
                id="navigation-buttons"
            ),
            Static("Nawigacja: ↑↓ - poruszanie, Enter - wybierz plik", id="browser-help"),
            DirectoryTree(str(self.current_path), id="dir-tree"),
            id="browser-container"
        )
    
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Gdy wybrano plik w drzewie"""
        event.stop()
        file_path = str(event.path)
        if file_path.endswith('.txt') or self.file_pattern == "*":
            self.selected_path = file_path
            path_input = self.query_one("#path-input", Input)
            path_input.value = self.selected_path
    
    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        """Gdy wybrano katalog w drzewie"""
        event.stop()
        # Nie rób nic specjalnego, pozwól na nawigację
        pass
    
    def on_input_changed(self, event) -> None:
        """Gdy zmieniono ścieżkę w polu input"""
        if event.input.id == "path-input":
            self.selected_path = event.value
    
    def on_button_pressed(self, event) -> None:
        """Obsługa przycisków"""
        if event.button.id == "select-btn":
            if self.selected_path and Path(self.selected_path).is_file():
                self.dismiss(self.selected_path)
            else:
                self.app.notify("Nieprawidłowa ścieżka do pliku!", severity="error")
        elif event.button.id == "cancel-btn":
            self.dismiss(None)
        elif event.button.id == "up-btn":
            self._go_up()
        elif event.button.id == "home-btn":
            self._go_home()
        elif event.button.id == "refresh-btn":
            self._refresh_tree()
    
    def _go_up(self) -> None:
        """Przejdź do katalogu wyżej"""
        current = Path(self.current_path)
        parent = current.parent
        if parent != current:  # Nie jesteśmy w root
            self.current_path = parent
            self._update_tree()
    
    def _go_home(self) -> None:
        """Przejdź do katalogu domowego"""
        self.current_path = Path.home()
        self._update_tree()
    
    def _refresh_tree(self) -> None:
        """Odśwież drzewo katalogów"""
        self._update_tree()
    
    def _update_tree(self) -> None:
        """Aktualizuj drzewo katalogów"""
        # Aktualizuj ścieżkę istniejącego drzewa
        tree = self.query_one("#dir-tree", DirectoryTree)
        tree.path = str(self.current_path)
    
    def action_select(self) -> None:
        """Akcja wyboru (Enter)"""
        if self.selected_path and Path(self.selected_path).is_file():
            self.dismiss(self.selected_path)
        else:
            self.app.notify("Nieprawidłowa ścieżka do pliku!", severity="error")
    
    def action_cancel(self) -> None:
        """Akcja anulowania (Escape)"""
        self.dismiss(None)


class HardwareInfoScreen(Screen):
    """Ekran z informacjami o sprzęcie"""
    
    BINDINGS = [
        ("escape", "back", "Powrót"),
        ("q", "back", "Powrót"),
    ]
    
    def __init__(self, hardware_info: dict):
        super().__init__()
        self.hardware_info = hardware_info
    
    def compose(self) -> ComposeResult:
        """Komponuj UI dla informacji o sprzęcie"""
        info = self.hardware_info
        
        info_text = f"""Typ sprzętu: {info['hardware_type']}
System: {info['system_info']['system']} {info['system_info']['release']}
Architektura: {info['system_info']['machine']}
Pamięć RAM: {info['memory_gb']} GB
Rdzenie fizyczne: {info['cpu_info']['physical_cores']}
Rdzenie logiczne: {info['cpu_info']['logical_cores']}"""
        
        if info['hardware_type'] == 'x86_linux':
            info_text += f"""
Obsługa AVX: {info['cpu_info']['has_avx']}
Obsługa AVX2: {info['cpu_info']['has_avx2']}"""
        
        info_text += f"""

Sugerowane optymalizacje:
{OptimizationConfigs.get_description(info['hardware_type'])}

Flagi CMAKE:"""
        
        flags = OptimizationConfigs.get_cmake_flags(info['hardware_type'])
        for flag in flags:
            info_text += f"\n  {flag}"
        
        info_text += "\n\nWymagane zależności:"
        deps = OptimizationConfigs.get_dependencies(info['hardware_type'])
        for dep in deps:
            info_text += f"\n  {dep}"
        
        yield Header()
        yield Container(
            Static(info_text, id="hardware-info"),
            Button("Powrót", id="back-button", variant="primary"),
            id="hardware-container"
        )
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back-button":
            self.dismiss()
    
    def action_back(self) -> None:
        """Akcja powrotu (Escape/Q)"""
        self.dismiss()


class InstallationScreen(Screen):
    """Ekran instalacji"""
    
    def __init__(self, hardware_type: str, install_dir: str, custom_config: Optional[str] = None):
        super().__init__()
        self.hardware_type = hardware_type
        self.install_dir = install_dir
        self.custom_config = custom_config
        
        # Rekonfiguruj logowanie aby logi były w katalogu instalacji
        install_path = Path(install_dir)
        install_logs_dir = install_path / "logs"
        self.logger_config = setup_logging(log_level="INFO", log_dir=str(install_logs_dir))
        self.logger = get_logger()
        
        # Utwórz callback do przekazywania komunikatów z LlamaInstaller do Log widget
        def gui_callback(message, progress_update=None):
            if hasattr(self, '_log_widget') and self._log_widget:
                # Bezpośredni dostęp - jesteśmy już w kontekście async
                self._log_widget.write_line(message)
            
            # Opcjonalnie aktualizuj progress bar
            if progress_update and hasattr(self, '_progress_widget') and self._progress_widget:
                self._progress_widget.update(progress=progress_update)
        
        self.installer = LlamaInstaller(install_dir, gui_callback)
        self.installation_cancelled = False
        self.install_start_time = None
        self.timer_widget = None
    
    def update_elapsed_time(self):
        """Aktualizuj wyświetlany czas elapsed"""
        if self.install_start_time and self.timer_widget:
            import time
            elapsed = int(time.time() - self.install_start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            time_str = f"Czas: {minutes:02d}:{seconds:02d}"
            self.timer_widget.update(time_str)
    
    def compose(self) -> ComposeResult:
        """Komponuj UI dla instalacji"""
        yield Header()
        yield Container(
            Static(f"Instalacja llama.cpp dla: {self.hardware_type}", id="install-title"),
            Static(f"Katalog instalacji: {self.install_dir}", id="install-dir"),
            Static("Czas: 00:00", id="elapsed-time"),
            ProgressBar(total=100, show_eta=False, id="progress"),
            Log(id="install-log"),
            Horizontal(
                Button("Rozpocznij instalację", id="start-install", variant="success"),
                Button("Anuluj", id="cancel-install", variant="error"),
                id="install-buttons"
            ),
            id="install-container"
        )
        yield Footer()
    
    @work(exclusive=True)
    async def install_llama(self):
        """Wykonuje instalację w tle"""
        log_widget = self.query_one("#install-log", Log)
        progress_widget = self.query_one("#progress", ProgressBar)
        
        # Ustaw referencje do widgetów dla callback
        self._log_widget = log_widget
        self._progress_widget = progress_widget
        
        # Inicjalizuj timer elapsed time
        import time
        self.install_start_time = time.time()
        self.timer_widget = self.query_one("#elapsed-time", Static)
        
        # Inicjalizuj pasek postępu bez ETA
        progress_widget.update(progress=0)
        
        # Uruchom timer
        self.timer_handle = self.set_interval(1.0, self.update_elapsed_time)
        
        try:
            if self.installation_cancelled:
                log_widget.write_line("Instalacja anulowana przez użytkownika")
                self._finish_installation_with_error()
                return
                
            log_widget.write_line("Rozpoczynam instalację...")
            await asyncio.sleep(0.5)  # Krótka pauza dla stabilności ETA
            progress_widget.update(progress=20)
            
            # Sprawdź zależności
            if self.installation_cancelled:
                log_widget.write_line("Instalacja anulowana przez użytkownika")
                self._finish_installation_with_error()
                return
                
            log_widget.write_line("Sprawdzanie zależności...")
            await asyncio.sleep(0.3)
            progress_widget.update(progress=30)
            deps_ok, missing_deps = self.installer.check_dependencies(self.hardware_type)
            
            if not deps_ok:
                log_widget.write_line(f"Brakuje zależności: {', '.join(missing_deps)}")
                log_widget.write_line("Sprawdzanie instrukcji instalacji...")
                install_result = self.installer.install_dependencies(self.hardware_type)
                if not install_result:
                    log_widget.write_line("WYMAGANA RĘCZNA INSTALACJA ZALEŻNOŚCI:")
                    log_widget.write_line("")
                    
                    # Wykryj system operacyjny i pokaż instrukcje
                    import os
                    if os.path.exists('/etc/apt/sources.list'):
                        log_widget.write_line("Uruchom następujące komendy w terminalu:")
                        log_widget.write_line("sudo apt update")
                        deps_str = ' '.join(missing_deps)
                        log_widget.write_line(f"sudo apt install -y {deps_str}")
                    elif os.path.exists('/etc/yum.conf'):
                        log_widget.write_line("Uruchom następujące komendy w terminalu:")
                        deps_str = ' '.join(missing_deps)
                        log_widget.write_line(f"sudo yum install -y {deps_str}")
                    elif os.path.exists('/etc/pacman.conf'):
                        log_widget.write_line("Uruchom następujące komendy w terminalu:")
                        deps_str = ' '.join(missing_deps)
                        log_widget.write_line(f"sudo pacman -S --noconfirm {deps_str}")
                    else:
                        log_widget.write_line("Zainstaluj ręcznie następujące pakiety:")
                        for dep in missing_deps:
                            log_widget.write_line(f"  - {dep}")
                    
                    log_widget.write_line("")
                    log_widget.write_line("Po instalacji uruchom ponownie instalator.")
                    
                    # Ukryj przycisk rozpoczęcia i zmień przycisk anulowania
                    start_btn = self.query_one("#start-install", Button)
                    start_btn.disabled = True
                    start_btn.add_class("hidden")
                    
                    cancel_btn = self.query_one("#cancel-install", Button)
                    cancel_btn.disabled = False
                    cancel_btn.label = "Zakończ"
                    cancel_btn.variant = "error"
                    return
            
            await asyncio.sleep(0.3)
            progress_widget.update(progress=45)
            
            # Pobierz llama.cpp
            if self.installation_cancelled:
                log_widget.write_line("Instalacja anulowana przez użytkownika")
                self._finish_installation_with_error()
                return
                
            log_widget.write_line("Pobieranie llama.cpp z GitHub...")
            # Włącz przycisk anulowania podczas długotrwałych operacji
            self.query_one("#cancel-install", Button).disabled = False
            
            if not await self.installer.download_llama_cpp():
                log_widget.write_line("Błąd pobierania llama.cpp!")
                self._finish_installation_with_error()
                return
            
            await asyncio.sleep(0.3)
            progress_widget.update(progress=65)
            
            # Kompilacja
            if self.installation_cancelled:
                log_widget.write_line("Instalacja anulowana przez użytkownika")
                self._finish_installation_with_error()
                return
                
            log_widget.write_line("Rozpoczynam kompilację...")
            await asyncio.sleep(0.3)
            progress_widget.update(progress=70)
            
            if not await self.installer.compile_llama_cpp(self.hardware_type, self.custom_config):
                log_widget.write_line("Błąd kompilacji!")
                self._finish_installation_with_error()
                return
            
            await asyncio.sleep(0.3)
            progress_widget.update(progress=95)
            
            # Wrapper scripts
            log_widget.write_line("Tworzenie wrapper scripts...")
            self.installer.create_wrapper_scripts()
            
            await asyncio.sleep(0.3)
            progress_widget.update(progress=100)
            
            # Zatrzymaj timer
            if hasattr(self, 'timer_handle') and self.timer_handle:
                self.timer_handle.stop()
                
            log_widget.write_line("Instalacja zakończona pomyślnie!")
            log_widget.write_line(f"Pliki zainstalowane w: {self.install_dir}")
            log_widget.write_line("Możesz teraz zamknąć to okno.")
            
            # Ukryj przycisk rozpoczęcia i zmień przycisk anulowania
            start_btn = self.query_one("#start-install", Button)
            start_btn.disabled = True
            start_btn.add_class("hidden")
            
            cancel_btn = self.query_one("#cancel-install", Button)
            cancel_btn.disabled = False
            cancel_btn.label = "Zakończ"
            cancel_btn.variant = "success"
            
        except Exception as e:
            log_widget.write_line(f"Błąd instalacji: {e}")
            self._finish_installation_with_error()
    
    def _finish_installation_with_error(self):
        """Zakończ instalację z błędem - aktualizuj UI"""
        # Zatrzymaj timer
        if hasattr(self, 'timer_handle') and self.timer_handle:
            self.timer_handle.stop()
            
        # Ukryj przycisk rozpoczęcia i zmień przycisk anulowania
        start_btn = self.query_one("#start-install", Button)
        start_btn.disabled = True
        start_btn.add_class("hidden")
        
        cancel_btn = self.query_one("#cancel-install", Button)
        cancel_btn.disabled = False
        cancel_btn.label = "Zakończ"
        cancel_btn.variant = "error"
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start-install":
            event.button.disabled = True
            # Wyłącz możliwość anulowania na początku
            self.query_one("#cancel-install", Button).disabled = True
            self.install_llama()
        elif event.button.id == "cancel-install":
            if event.button.label == "Anuluj":
                # Anuluj instalację
                self.installation_cancelled = True
                event.button.label = "Zakończ"
                log_widget = self.query_one("#install-log", Log)
                log_widget.write_line("Prośba o anulowanie instalacji...")
            else:
                # Zakończ (instalacja jest skończona lub anulowana)
                self.dismiss()


class LlamaCppInstallerApp(App):
    """Główna aplikacja instalatora llama.cpp"""
    
    BINDINGS = [
        Binding("f1", "toggle_footer", "Toggle shortcuts / Przełącz skróty", show=False),
        Binding("ctrl+h", "toggle_footer", "Toggle shortcuts / Przełącz skróty", show=False),
        Binding("ctrl+c", "quit", "Wyjście / Exit", show=False),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Podstawowe logowanie - zostanie zastąpione w InstallationScreen
        self.logger_config = setup_logging(log_level="INFO")
        self.logger = get_logger()
        self.installation_start_time = None
        
        # Inicjalizuj flagę dla footera
        self.show_footer = False
    
    CSS = """
    #main-container {
        width: 100%;
        height: 100%;
        padding: 0;
    }
    
    #title {
        content-align: center middle;
        text-style: bold;
        color: cyan;
        height: 1;
    }
    
    #author {
        content-align: center middle;
        height: 1;
        margin-bottom: 0;
    }
    
    #hardware-selection {
        height: 10;
        min-height: 6;
        margin: 0;
    }
    
    #dir-input-container {
        margin: 0;
        height: 3;
    }
    
    #dir-input-container Input {
        width: 4fr;
    }
    
    #dir-input-container Button {
        width: 1fr;
        margin-left: 1;
    }
    
    #config-input-container {
        margin: 0;
        height: 3;
    }
    
    #config-input-container Input {
        width: 4fr;
    }
    
    #config-input-container Button {
        width: 1fr;
        margin-left: 1;
    }
    
    #buttons-container {
        height: 3;
        margin: 0;
    }
    
    /* Compact mode for narrow screens */
    .compact #buttons-container {
        layout: vertical;
        height: 9;
    }
    
    .compact #buttons-container Button {
        width: 100%;
        margin: 1 0;
    }
    
    .compact #dir-input-container,
    .compact #config-input-container {
        layout: vertical;
        height: 6;
    }
    
    .compact #dir-input-container Input,
    .compact #config-input-container Input {
        width: 100%;
        margin-bottom: 1;
    }
    
    .compact #dir-input-container Button,
    .compact #config-input-container Button {
        width: 100%;
        margin: 0;
    }
    
    .compact #hardware-selection {
        height: 8;
    }
    
    /* Compact browser screens */
    .compact #action-buttons,
    .compact #navigation-buttons {
        layout: vertical;
        height: 6;
    }
    
    .compact #action-buttons Button,
    .compact #navigation-buttons Button {
        width: 100%;
        margin: 0 0 1 0;
    }
    
    /* Create directory screen */
    #create-container {
        width: 60%;
        height: auto;
        min-height: 15;
        max-height: 20;
        padding: 2;
        border: solid green;
        background: $surface;
    }
    
    #create-title {
        content-align: center middle;
        text-style: bold;
        color: green;
        height: 2;
        margin-bottom: 1;
    }
    
    #create-help {
        height: 1;
        margin-bottom: 1;
    }
    
    #dir-name-input {
        margin-bottom: 2;
        height: 3;
    }
    
    #create-buttons {
        height: 3;
    }
    
    #create-buttons Button {
        width: 1fr;
        margin: 0 1;
    }
    
    Button {
        margin: 0;
    }
    
    Button.hidden {
        display: none;
    }
    
    #hardware-info {
        scrollbar-gutter: stable;
        padding: 0;
    }
    
    #install-container {
        padding: 0;
    }
    
    #install-log {
        height: 20;
        margin: 0;
    }
    
    /* Browser screens - responsive design */
    #browser-container {
        width: 100%;
        height: 100%;
        padding: 1;
        border: solid cyan;
        background: $surface;
    }
    
    #browser-title {
        content-align: center middle;
        text-style: bold;
        color: cyan;
        height: 2;
        margin-bottom: 1;
    }
    
    /* Action buttons at top */
    #action-buttons {
        height: 3;
        margin-bottom: 1;
    }
    
    #action-buttons Button {
        width: 1fr;
        margin: 0 1;
        min-width: 8;
    }
    
    #browser-help {
        color: yellow;
        text-style: italic;
        height: 1;
        margin-bottom: 1;
        content-align: center middle;
    }
    
    #browser-pattern {
        color: green;
        height: 1;
        margin-bottom: 1;
        content-align: center middle;
    }
    
    #selected-label {
        text-style: bold;
        height: 1;
        margin-bottom: 1;
    }
    
    #path-input {
        margin-bottom: 1;
        height: 3;
    }
    
    /* Navigation buttons */
    #navigation-buttons {
        height: 3;
        margin-bottom: 1;
    }
    
    #navigation-buttons Button {
        width: 1fr;
        margin: 0 1;
        min-width: 6;
    }
    
    /* Directory tree - adaptive height */
    #dir-tree {
        height: 1fr;
        min-height: 10;
        scrollbar-gutter: stable;
        border: solid $primary;
    }
    """
    
    @property
    def TITLE(self):
        return t("app_title")
    
    @property 
    def SUB_TITLE(self):
        return t("app_subtitle")
    
    def __init__(self):
        super().__init__()
        self.detector = HardwareDetector()
        self.hardware_info = self.detector.get_detailed_info()
        self.detected_type = self.hardware_info['hardware_type']
        self.show_footer = True
    
    def compose(self) -> ComposeResult:
        """Komponuj główny interfejs"""
        
        # Lista opcji sprzętu
        hardware_options = [
            ("auto-detect", t("auto_detected", hardware_type=self.detected_type)),
            ("dynamic", t("hardware_dynamic")),
            ("rpi5_8gb", "Raspberry Pi 5 8GB"),
            ("rpi5_16gb", "Raspberry Pi 5 16GB"), 
            ("rpi5_4gb", "Raspberry Pi 5 4GB"),
            ("rpi4", "Raspberry Pi 4"),
            ("rpi_other", "Inne Raspberry Pi"),
            ("termux", "Termux Android"),
            ("x86_linux", "Linux x86_64 (AVX2)"),
            ("x86_linux_old", t("hardware_x86_linux_old")),
            ("x86_linux_minimal", t("hardware_x86_linux_minimal")),
            ("no_optimization", "bez optymalizacji")
        ]
        
        yield Header()
        yield Container(
            Static(f"{t('app_title')} v{__version__}", id="title"),
            Static(t("author"), id="author", classes="dim"),
            Rule(),
            Static(t("select_hardware")),
            SelectionList(*hardware_options, id="hardware-selection"),
            Rule(),
            Static(t("installation_directory")),
            Horizontal(
                Input(
                    value=str(Path.cwd() / "llama.cpp"), 
                    placeholder=t("dir_placeholder"),
                    id="install-dir-input"
                ),
                Button(t("browse"), id="browse-dir-btn", variant="default"),
                id="dir-input-container"
            ),
            Horizontal(
                Input(
                    placeholder=t("config_placeholder"),
                    id="custom-config-input"
                ),
                Button(t("browse"), id="browse-config-btn", variant="default"),
                id="config-input-container"
            ),
            Horizontal(
                Button(t("hardware_info"), id="hardware-info-btn", variant="default"),
                Button(t("start_installation"), id="install-btn", variant="success"),
                Button(t("exit"), id="exit-btn", variant="error"),
                id="buttons-container"
            ),
            id="main-container"
        )
        if self.show_footer:
            yield Footer()
    
    def on_mount(self) -> None:
        """Po uruchomieniu aplikacji"""
        # Inicjalizacja logowania jeśli nie została wykonana w konstruktorze
        if not hasattr(self, 'logger_config') or self.logger_config is None:
            self.logger_config = setup_logging(log_level="INFO")
            self.logger = get_logger()
        
        # Loguj informacje o systemie
        self.logger_config.log_system_info()
        self.logger.info("Uruchomiono aplikację GUI")
        
        # Auto-select detected hardware
        selection_list = self.query_one("#hardware-selection", SelectionList)
        selection_list.select(0)  # Auto-detect option
        
        # Setup signal handlers for graceful shutdown
        self.setup_signal_handlers()
        
        # Enable compact mode for narrow screens
        self._check_screen_size()
    
    def on_resize(self, event) -> None:
        """Obsługa zmiany rozmiaru okna"""
        self._check_screen_size()
    
    def _check_screen_size(self) -> None:
        """Sprawdz rozmiar ekranu i włącz compact mode jeśli potrzeba"""
        # Get console size
        try:
            size = self.console.size
            if size.width < 80 or size.height < 25:
                self.add_class("compact")
            else:
                self.remove_class("compact")
        except:
            # Fallback for cases where console size is not available
            pass
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Obsługa naciśnięć przycisków"""
        if event.button.id == "exit-btn":
            self.exit()
        
        elif event.button.id == "hardware-info-btn":
            self.push_screen(HardwareInfoScreen(self.hardware_info))
        
        elif event.button.id == "browse-dir-btn":
            self._browse_directory()
        
        elif event.button.id == "browse-config-btn":
            self._browse_config_file()
        
        elif event.button.id == "install-btn":
            # Pobierz wybrane opcje
            selection_list = self.query_one("#hardware-selection", SelectionList)
            selected = selection_list.selected
            
            if not selected:
                self.notify(t("select_hardware_type"), severity="error")
                self.logger.warning("Próba instalacji bez wybrania typu sprzętu")
                return
            
            hardware_type = list(selected)[0]
            if hardware_type == "auto-detect":
                hardware_type = self.detected_type
            
            install_dir = self.query_one("#install-dir-input", Input).value
            if not install_dir:
                self.notify(t("enter_install_dir"), severity="error")
                self.logger.warning("Próba instalacji bez podania katalogu")
                return
            
            
            custom_config = self.query_one("#custom-config-input", Input).value
            if custom_config and not Path(custom_config).exists():
                self.notify(t("config_file_not_exists"), severity="error")
                self.logger.warning(f"Podany plik konfiguracji nie istnieje: {custom_config}")
                return
            
            custom_config = custom_config if custom_config else None
            
            # Loguj rozpoczęcie instalacji
            self.logger.info(f"Rozpoczęcie instalacji - typ sprzętu: {hardware_type}, katalog: {install_dir}")
            if custom_config:
                self.logger.info(f"Użyta własna konfiguracja: {custom_config}")
            self.installation_start_time = time.time()
            
            # Uruchom instalację
            self.push_screen(InstallationScreen(hardware_type, install_dir, custom_config))
    
    def _browse_directory(self) -> None:
        """Przeglądaj katalogi"""
        input_widget = self.query_one("#install-dir-input", Input)
        current_path = input_widget.value or str(Path.cwd())
        
        def on_directory_selected(selected_path):
            if selected_path:
                input_widget.value = selected_path
        
        self.push_screen(DirectoryBrowserScreen(current_path, t("select_install_dir")), on_directory_selected)
    
    def _browse_config_file(self) -> None:
        """Przeglądaj pliki konfiguracji"""
        input_widget = self.query_one("#custom-config-input", Input)
        current_path = str(Path.cwd())
        
        def on_file_selected(selected_path):
            if selected_path:
                input_widget.value = selected_path
        
        self.push_screen(FileBrowserScreen(current_path, "*.txt", t("select_config_file")), on_file_selected)
    
    def setup_signal_handlers(self) -> None:
        """Konfiguruje obsługę sygnałów dla graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info("Otrzymano sygnał przerwania - zamykanie aplikacji...")
            self.action_quit()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def action_quit(self) -> None:
        """Graceful shutdown via Ctrl+C"""
        self.logger.info("Zamykanie aplikacji przez użytkownika")
        self.exit()
    
    def action_toggle_footer(self) -> None:
        """Przełącz widoczność footera ze skrótami"""
        self.show_footer = not self.show_footer
        # Usuwamy wszystkie widgety i komponujemy na nowo
        self.query("Footer").remove()
        if self.show_footer:
            self.mount(Footer())
        status = t("enabled") if self.show_footer else t("disabled")
        self.notify(t("shortcuts_panel", status=status), severity="info")


def main(language: str = None):
    """Punkt wejścia aplikacji"""
    # Ustaw język
    if language:
        set_language(language)
    else:
        # Sprawdź argumenty wiersza poleceń
        import sys
        if '--lang' in sys.argv:
            lang_index = sys.argv.index('--lang')
            if lang_index + 1 < len(sys.argv):
                set_language(sys.argv[lang_index + 1])
        elif '--en' in sys.argv:
            set_language('en')
        else:
            set_language(get_language_from_env())
    
    app = LlamaCppInstallerApp()
    app.run()


def show_help(language='pl'):
    """Display help information for the GUI application"""
    from translations import set_language, t
    set_language(language)
    
    if language == 'en':
        help_text = """
llama.cpp Automatic Installer - GUI Version
Copyright (c) 2025 Fibogacci | https://fibogacci.pl

DESCRIPTION:
    Graphical interface for automatic installation of llama.cpp with hardware-specific 
    optimizations. Automatically detects hardware and applies optimal compilation flags.

USAGE:
    python main.py [OPTIONS]

OPTIONS:
    --lang LANG     Interface language (pl/en), default: pl
    --en            Shortcut for English interface
    --help, -h      Show this help message

SUPPORTED HARDWARE:
    • Raspberry Pi 5 (8GB/16GB/4GB) - ARM64 Cortex-A76 + OpenBLAS + Vulkan
    • Raspberry Pi 4                - ARM64 Cortex-A72 + OpenBLAS  
    • Termux Android                - Minimal optimizations (no BLAS)
    • Linux x86_64                  - Full AVX/AVX2 + OpenBLAS optimizations

ENVIRONMENT VARIABLES:
    LLAMACPP_INSTALLER_LANG         Set default language (pl/en)

EXAMPLES:
    python main.py                  # Polish interface (default)
    python main.py --en             # English interface
    python main.py --lang en        # English interface (alternative)
    
    # Set default language via environment
    export LLAMACPP_INSTALLER_LANG=en
    python main.py

GUI FEATURES:
    • Interactive hardware selection
    • Directory browser with folder creation
    • Configuration file browser  
    • Real-time installation progress
    • Responsive design (mobile/desktop)
    • Keyboard shortcuts (F1 for help toggle)

For command-line interface, use: python cli.py --help
"""
    else:
        help_text = """
Automatyczny instalator llama.cpp - Wersja GUI
Copyright (c) 2025 Fibogacci | https://fibogacci.pl

OPIS:
    Graficzny interfejs do automatycznej instalacji llama.cpp z optymalizacjami 
    dostosowanymi do sprzętu. Automatycznie wykrywa sprzęt i stosuje optymalne flagi.

UŻYCIE:
    python main.py [OPCJE]

OPCJE:
    --lang JĘZYK    Język interfejsu (pl/en), domyślny: pl
    --en            Skrót dla angielskiego interfejsu
    --help, -h      Pokaż tę pomoc

OBSŁUGIWANE PLATFORMY:
    • Raspberry Pi 5 (8GB/16GB/4GB) - ARM64 Cortex-A76 + OpenBLAS + Vulkan
    • Raspberry Pi 4                - ARM64 Cortex-A72 + OpenBLAS  
    • Termux Android                - Minimalne optymalizacje (bez BLAS)
    • Linux x86_64                  - Pełne optymalizacje AVX/AVX2 + OpenBLAS

ZMIENNE ŚRODOWISKOWE:
    LLAMACPP_INSTALLER_LANG         Ustaw domyślny język (pl/en)

PRZYKŁADY:
    python main.py                  # Polski interfejs (domyślny)
    python main.py --en             # Angielski interfejs
    python main.py --lang en        # Angielski interfejs (alternatywnie)
    
    # Ustaw domyślny język przez zmienną środowiskową
    export LLAMACPP_INSTALLER_LANG=en
    python main.py

FUNKCJE GUI:
    • Interaktywny wybór sprzętu
    • Przeglądarka katalogów z tworzeniem folderów
    • Przeglądarka plików konfiguracji
    • Postęp instalacji w czasie rzeczywistym
    • Responsywny design (mobile/desktop)
    • Skróty klawiszowe (F1 przełącza pomoc)

Aby użyć interfejsu wiersza poleceń: python cli.py --help
"""
    
    print(help_text.strip())


if __name__ == "__main__":
    import sys
    
    # Check for help first
    if '--help' in sys.argv or '-h' in sys.argv:
        # Determine language for help
        help_lang = 'pl'
        if '--lang' in sys.argv:
            try:
                lang_index = sys.argv.index('--lang')
                if lang_index + 1 < len(sys.argv):
                    help_lang = sys.argv[lang_index + 1]
            except (ValueError, IndexError):
                pass
        elif '--en' in sys.argv:
            help_lang = 'en'
        
        show_help(help_lang)
        sys.exit(0)
    
    # Parse language arguments
    language = None
    if '--lang' in sys.argv:
        try:
            lang_index = sys.argv.index('--lang')
            if lang_index + 1 < len(sys.argv):
                language = sys.argv[lang_index + 1]
                # Remove the arguments so they don't interfere with Textual
                sys.argv.pop(lang_index)  # Remove --lang
                sys.argv.pop(lang_index)  # Remove the language value
        except (ValueError, IndexError):
            pass
    elif '--en' in sys.argv:
        language = 'en'
        sys.argv.remove('--en')
    
    main(language)