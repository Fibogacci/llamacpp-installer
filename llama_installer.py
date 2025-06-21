"""
Automatyczny instalator llama.cpp
Copyright (c) 2025 Fibogacci
Licencja: MIT

Website: https://fibogacci.pl
GitHub: https://github.com/fibogacci
Projekt: https://fibogacci.pl/ai/llamacpp
LinkedIn: https://linkedin.com/in/Fibogacci

Główny moduł instalatora llama.cpp
"""
import os
import subprocess
import asyncio
import shutil
import tempfile
import requests
from pathlib import Path
from typing import Optional, List, Tuple
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

from hardware_detector import HardwareDetector
from optimization_configs import OptimizationConfigs
from logger_config import setup_logging, get_logger, get_installer_logger
from translations import t


class LlamaInstaller:
    """Klasa do instalacji llama.cpp"""
    
    def __init__(self, install_dir: str = None, gui_callback=None):
        self.console = Console()
        self.detector = HardwareDetector()
        self.hardware_info = self.detector.get_detailed_info()
        self.base_dir = Path(install_dir or os.getcwd())
        self.install_dir = self.base_dir / "llama.cpp"
        self.logger = get_logger()
        self.installer_logger = get_installer_logger()
        self.gui_callback = gui_callback  # Callback do wysyłania komunikatów do GUI
    
    def _print(self, message: str, color: str = None, progress: int = None):
        """Wysyła komunikat zarówno do konsoli jak i GUI"""
        if color:
            console_message = f"[{color}]{message}[/{color}]"
        else:
            console_message = message
            
        self.console.print(console_message)
        
        if self.gui_callback:
            # Usuń markup Rich dla GUI
            import re
            clean_message = re.sub(r'\[/?[a-z_]+\]', '', message)
            try:
                self.gui_callback(clean_message, progress)
            except TypeError:
                # Fallback dla starszego callback bez progress
                self.gui_callback(clean_message)
        
    def show_hardware_info(self):
        """Wyświetla informacje o wykrytym sprzęcie"""
        info = self.hardware_info
        
        panel_content = f"""
[bold cyan]Typ sprzętu:[/bold cyan] {info['hardware_type']}
[bold cyan]System:[/bold cyan] {info['system_info']['system']} {info['system_info']['release']}
[bold cyan]Architektura:[/bold cyan] {info['system_info']['machine']}
[bold cyan]Pamięć RAM:[/bold cyan] {info['memory_gb']} GB
[bold cyan]Rdzenie fizyczne:[/bold cyan] {info['cpu_info']['physical_cores']}
[bold cyan]Rdzenie logiczne:[/bold cyan] {info['cpu_info']['logical_cores']}
"""
        
        if info['hardware_type'] == 'x86_linux':
            panel_content += f"""[bold cyan]Obsługa AVX:[/bold cyan] {info['cpu_info']['has_avx']}
[bold cyan]Obsługa AVX2:[/bold cyan] {info['cpu_info']['has_avx2']}"""
            
        panel_content += f"""

[bold green]Sugerowane optymalizacje:[/bold green]
{OptimizationConfigs.get_description(info['hardware_type'])}
"""
        
        self.console.print(Panel(panel_content, title="Informacje o sprzęcie", expand=False))
    
    def check_dependencies(self, hardware_type: str) -> Tuple[bool, List[str]]:
        """Sprawdza czy wymagane zależności są zainstalowane"""
        self.logger.info(f"Sprawdzanie zależności dla typu sprzętu: {hardware_type}")
        required_deps = OptimizationConfigs.get_dependencies(hardware_type)
        self.installer_logger.log_dependencies(required_deps)
        
        missing_deps = []
        
        for dep in required_deps:
            if not self._check_command_exists(dep):
                missing_deps.append(dep)
                self.logger.warning(f"Brakująca zależność: {dep}")
            else:
                self.logger.debug(f"Zależność dostępna: {dep}")
        
        if missing_deps:
            self.logger.warning(f"Brakujące zależności: {missing_deps}")
        else:
            self.logger.info("Wszystkie zależności są dostępne")
            
        return len(missing_deps) == 0, missing_deps
    
    def _check_command_exists(self, command: str) -> bool:
        """Sprawdza czy komenda istnieje w systemie"""
        # build-essential to pakiet, nie komenda - sprawdź gcc/g++
        if command == 'build-essential':
            return shutil.which('gcc') is not None and shutil.which('g++') is not None
        
        # Pakiety *-dev nie mają komend - sprawdź przez dpkg
        dev_packages = {
            'libopenblas-dev': 'libopenblas-dev',
            'libomp-dev': 'libomp-dev', 
            'libvulkan-dev': 'libvulkan-dev'
        }
        
        if command in dev_packages:
            try:
                result = subprocess.run(['dpkg', '-l', command], 
                                      capture_output=True, text=True)
                return result.returncode == 0 and 'ii' in result.stdout
            except:
                return False
        
        
        return shutil.which(command) is not None
    
    def install_dependencies(self, hardware_type: str) -> bool:
        """Instaluje wymagane zależności"""
        self.logger.info("Rozpoczęcie instalacji zależności")
        deps_ok, missing_deps = self.check_dependencies(hardware_type)
        
        if deps_ok:
            self._print("Wszystkie zależności są już zainstalowane", "green")
            self.logger.info("Wszystkie zależności już zainstalowane")
            return True
        
        self.logger.info(f"Instalacja brakujących zależności: {missing_deps}")
        
        if hardware_type == 'termux':
            return self._install_termux_dependencies(missing_deps)
        else:
            return self._install_linux_dependencies(missing_deps)
    
    def _install_termux_dependencies(self, missing_deps: List[str]) -> bool:
        """Instaluje zależności w Termux"""
        self.logger.info(f"Instalacja zależności Termux: {missing_deps}")
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Instalowanie zależności Termux...", total=None)
                
                cmd = ['pkg', 'install', '-y'] + missing_deps
                self.logger.debug(f"Wykonywanie komendy: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                progress.stop()
                
                if result.returncode == 0:
                    self._print("Zależności Termux zainstalowane pomyślnie", "green")
                    self.logger.info("Zależności Termux zainstalowane pomyślnie")
                    if result.stdout:
                        self.logger.debug(f"Stdout: {result.stdout}")
                    return True
                else:
                    self._print(f"Błąd instalacji zależności: {result.stderr}", "red")
                    self.logger.error(f"Błąd instalacji zależności Termux - kod: {result.returncode}")
                    self.logger.error(f"Stderr: {result.stderr}")
                    if result.stdout:
                        self.logger.debug(f"Stdout: {result.stdout}")
                    return False
                    
        except Exception as e:
            self._print(f"Błąd podczas instalacji zależności: {e}", "red")
            self.installer_logger.log_error_with_context(e, "Instalacja zależności Termux")
            return False
    
    def _install_linux_dependencies(self, missing_deps: List[str]) -> bool:
        """Pokazuje użytkownikowi instrukcje instalacji zależności"""
        self._print(f"\n{t('dependencies_not_installed')}", "yellow")
        self._print(f"{t('install_dependencies_manually')}\n", "cyan")
        
        # Wykryj system operacyjny i pokaż odpowiednie komendy
        if os.path.exists('/etc/apt/sources.list'):
            # Ubuntu/Debian
            self._print("sudo apt update", "green")
            deps_str = ' '.join(missing_deps)
            self._print(f"sudo apt install -y {deps_str}", "green")
        elif os.path.exists('/etc/yum.conf'):
            # CentOS/RHEL/Fedora
            deps_str = ' '.join(missing_deps)
            self._print(f"sudo yum install -y {deps_str}", "green")
        elif os.path.exists('/etc/pacman.conf'):
            # Arch Linux
            deps_str = ' '.join(missing_deps)
            self._print(f"sudo pacman -S --noconfirm {deps_str}", "green")
        else:
            self._print("Nie wykryto znanego menedżera pakietów", "yellow")
            self._print("Zainstaluj ręcznie następujące pakiety:")
            for dep in missing_deps:
                self._print(f"  - {dep}", "green")
        
        self._print(f"\n{t('run_installer_again')}", "cyan")
        self.logger.info(f"Wyświetlono instrukcje instalacji dla brakujących zależności: {missing_deps}")
        return False
    
    async def download_llama_cpp(self) -> bool:
        """Pobiera najnowszą wersję llama.cpp z GitHub (asynchronicznie)"""
        self.logger.info("Rozpoczęcie pobierania llama.cpp z GitHub")
        try:
            if self.install_dir.exists():
                self._print(f"Katalog {self.install_dir} już istnieje, usuwam...", "yellow")
                self.logger.info(f"Usuwanie istniejącego katalogu: {self.install_dir}")
                shutil.rmtree(self.install_dir)
            
            cmd = [
                'git', 'clone', 
                'https://github.com/ggerganov/llama.cpp.git',
                str(self.install_dir)
            ]
            
            self.logger.debug(f"Wykonywanie komendy: {' '.join(cmd)}")
            self._print("Klonowanie repozytorium z GitHub...")
            
            # Asynchroniczne uruchomienie procesu z widocznym wyjściem
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT  # Przekieruj stderr do stdout dla lepszego wyświetlania
            )
            
            # Odczytuj i wyświetlaj wyjście w czasie rzeczywistym
            output_lines = []
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                    
                line_text = line.decode().strip()
                if line_text:
                    # Wyświetl linie z git w czasie rzeczywistym
                    self._print(f"  {line_text}", "dim")
                    output_lines.append(line_text)
                    self.logger.debug(f"Git output: {line_text}")
            
            await process.wait()
            full_output = '\n'.join(output_lines)
            
            if process.returncode == 0:
                self._print(f"Llama.cpp pobrane do {self.install_dir}", "green")
                self.logger.info(f"Pomyślnie pobrano llama.cpp do {self.install_dir}")
                if full_output:
                    self.logger.debug(f"Git output: {full_output}")
                return True
            else:
                self._print(f"Błąd pobierania - kod wyjścia: {process.returncode}", "red")
                self.logger.error(f"Błąd pobierania llama.cpp - kod: {process.returncode}")
                if full_output:
                    self.logger.error(f"Git output: {full_output}")
                return False
                    
        except Exception as e:
            self._print(f"Błąd podczas pobierania: {e}", "red")
            self.installer_logger.log_error_with_context(e, "Pobieranie llama.cpp z GitHub")
            return False
    
    async def compile_llama_cpp(self, hardware_type: str, custom_config: str = None) -> bool:
        """Kompiluje llama.cpp z odpowiednimi optymalizacjami (asynchronicznie)"""
        self.logger.info(f"Rozpoczęcie kompilacji llama.cpp dla typu sprzętu: {hardware_type}")
        if custom_config:
            self.logger.info(f"Użyta własna konfiguracja: {custom_config}")
        
        try:
            # Sprawdź czy katalog llama.cpp istnieje przed kompilacją
            if not self.install_dir.exists():
                self._print(f"Błąd: katalog llama.cpp nie istnieje: {self.install_dir}", "red")
                self.logger.error(f"Katalog llama.cpp nie istnieje: {self.install_dir}")
                return False
            
            # Nie zmieniamy katalogu roboczego - używamy absolutnych ścieżek
            self.logger.debug(f"Katalog llama.cpp: {self.install_dir}")
            
            # Utwórz katalog build
            build_dir = self.install_dir / "build"
            if build_dir.exists():
                self.logger.debug("Usuwanie istniejącego katalogu build")
                shutil.rmtree(build_dir)
            
            # Utwórz katalog build z lepszą obsługą błędów
            try:
                build_dir.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Utworzono katalog build: {build_dir}")
                
                # Sprawdź czy katalog naprawdę istnieje
                if not build_dir.exists():
                    raise FileNotFoundError(f"Katalog build nie został utworzony: {build_dir}")
                    
                # Krótka pauza aby upewnić się że katalog jest dostępny
                import time
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Błąd tworzenia katalogu build: {e}")
                self._print(f"Błąd tworzenia katalogu build: {e}", "red")
                return False
            
            # Pobierz flagi CMAKE
            cmake_flags = OptimizationConfigs.get_cmake_flags(hardware_type, custom_config)
            self.installer_logger.log_compilation_flags(cmake_flags)
            
            self._print("Kompilacja z flagami optymalizacji:", "cyan")
            for flag in cmake_flags:
                self._print(f"  {flag}")
            self._print("")  # Pusta linia dla czytelności
            
            # Konfiguracja CMake
            self._print("Konfiguracja CMake...")
            cmake_cmd = ['cmake', '-B', str(build_dir), '-S', str(self.install_dir)] + cmake_flags
            self.logger.debug(f"Wykonywanie komendy CMake: {' '.join(cmake_cmd)}")
            self.logger.debug(f"Katalog build: {build_dir} (istnieje: {build_dir.exists()})")
            
            process = await asyncio.create_subprocess_exec(
                *cmake_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT  # Przekieruj stderr do stdout
            )
            
            # Czytaj output w czasie rzeczywistym
            stdout_lines = []
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                line_text = line.decode().strip()
                if line_text:
                    # Filtruj ważne komunikaty CMAKE
                    if any(keyword in line_text.lower() for keyword in ['found', 'not found', 'enabled', 'disabled', 'configuring', 'generating', 'build files']):
                        self._print(f"CMAKE: {line_text}")
                    stdout_lines.append(line_text)
            
            await process.wait()
            
            if process.returncode != 0:
                self._print("Błąd konfiguracji CMake", "red")
                self.logger.error("Błąd konfiguracji CMake")
                return False
            
            self._print("Konfiguracja CMake zakończona pomyślnie", "green")
            
            # Kompilacja
            cores = self.hardware_info['cpu_info']['physical_cores']
            self._print(f"Rozpoczynam kompilację na {cores} rdzeniach...", "cyan")
            make_cmd = ['cmake', '--build', str(build_dir), '--config', 'Release', '-j', str(cores)]
            self.logger.debug(f"Wykonywanie komendy kompilacji: {' '.join(make_cmd)}")
            self.logger.debug(f"Katalog build dla kompilacji: {build_dir} (istnieje: {build_dir.exists()})")
            
            process = await asyncio.create_subprocess_exec(
                *make_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT  # Przekieruj stderr do stdout
            )
            
            # Czytaj output kompilacji w czasie rzeczywistym
            compile_lines = []
            compile_progress = 70  # Startowy progress dla kompilacji
            total_files_estimate = 100  # Estymacja liczby plików do kompilacji
            compiled_files = 0
            
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                line_text = line.decode().strip()
                if line_text:
                    compile_lines.append(line_text)
                    
                    # Szukaj wskaźników postępu
                    show_line = False
                    current_progress = compile_progress
                    
                    # Aktualizuj postęp na podstawie zawartości linii
                    if any(keyword in line_text.lower() for keyword in ['building', 'linking', 'compiling']):
                        compiled_files += 1
                        # Oblicz postęp (70% -> 90% podczas kompilacji)
                        progress_increment = min(20, (compiled_files / total_files_estimate) * 20)
                        current_progress = 70 + progress_increment
                        show_line = True
                    elif any(keyword in line_text.lower() for keyword in ['error', 'warning']):
                        show_line = True
                    elif '[' in line_text and '%' in line_text:
                        # Szukaj procentowego postępu w formacie [XX%]
                        import re
                        percent_match = re.search(r'\[(\d+)%\]', line_text)
                        if percent_match:
                            percent = int(percent_match.group(1))
                            current_progress = 70 + (percent * 0.2)  # 70% -> 90%
                            show_line = True
                    
                    if show_line:
                        self._print(f"MAKE: {line_text}", progress=int(current_progress))
            
            await process.wait()
            
            if process.returncode == 0:
                self._print("Kompilacja zakończona pomyślnie!", "green")
                self.logger.info("Kompilacja zakończona pomyślnie")
                
                # Sprawdź czy pliki wykonywalne zostały utworzone
                main_executable = build_dir / "bin" / "llama-cli"
                if not main_executable.exists():
                    main_executable = build_dir / "llama-cli"
                
                if main_executable.exists():
                    self._print(f"Główny plik wykonywalny: {main_executable}", "green")
                
                return True
            else:
                self._print("Błąd kompilacji", "red")
                self.logger.error("Błąd kompilacji")
                return False
                    
        except Exception as e:
            self._print(f"Błąd podczas kompilacji: {e}", "red")
            self.installer_logger.log_error_with_context(e, "Kompilacja llama.cpp")
            return False
    
    def create_wrapper_scripts(self) -> bool:
        """Tworzy wygodne skrypty uruchamiające"""
        try:
            # Znajdź pliki wykonywalne
            build_dir = self.install_dir / "build"
            bin_dir = build_dir / "bin"
            
            if not bin_dir.exists():
                bin_dir = build_dir
            
            executables = []
            for name in ["llama-cli", "llama-server", "llama-simple"]:
                exe_path = bin_dir / name
                if exe_path.exists():
                    executables.append((name, exe_path))
            
            if not executables:
                self._print("Nie znaleziono plików wykonywalnych", "yellow")
                return False
            
            # Utwórz wrapper scripts w katalogu głównym
            for name, exe_path in executables:
                wrapper_path = self.install_dir / f"{name}.sh"
                # Użyj względnej ścieżki względem katalogu skryptu
                rel_exe_path = exe_path.relative_to(self.install_dir)
                wrapper_content = f"""#!/bin/bash
# Wrapper script dla {name}
cd "$(dirname "$0")"
exec "./{rel_exe_path}" "$@"
"""
                with open(wrapper_path, 'w') as f:
                    f.write(wrapper_content)
                
                # Nadaj uprawnienia wykonywalne
                os.chmod(wrapper_path, 0o755)
                
                self._print(f"Utworzono wrapper: {wrapper_path}", "green")
            
            return True
            
        except Exception as e:
            self._print(f"Błąd tworzenia wrapper scripts: {e}", "red")
            return False
    
    async def install_full(self, hardware_type: str = None, custom_config: str = None) -> bool:
        """Pełna instalacja llama.cpp (asynchroniczna)"""
        if hardware_type is None:
            hardware_type = self.hardware_info['hardware_type']
        
        self.logger.info(f"Rozpoczęcie pełnej instalacji llama.cpp dla typu sprzętu: {hardware_type}")
        self.installer_logger.log_installation_start(str(self.install_dir))
        
        self.console.print(Panel("[bold green]Rozpoczynam instalację llama.cpp[/bold green]", expand=False))
        
        # Pokaż informacje o sprzęcie
        self.show_hardware_info()
        
        # Sprawdź i zainstaluj zależności
        self.console.print("\n[cyan]1. Sprawdzanie zależności...[/cyan]")
        if not self.install_dependencies(hardware_type):
            self.logger.error("Wymagane zainstalowanie zależności systemowych")
            self.console.print(f"\n[red]❌ {t('installation_interrupted')}[/red]")
            return False
        
        # Pobierz llama.cpp
        self.console.print("\n[cyan]2. Pobieranie llama.cpp...[/cyan]")
        if not await self.download_llama_cpp():
            self.logger.error("Błąd podczas pobierania llama.cpp")
            return False
        
        # Kompiluj
        self.console.print("\n[cyan]3. Kompilacja...[/cyan]")
        if not await self.compile_llama_cpp(hardware_type, custom_config):
            self.logger.error("Błąd podczas kompilacji llama.cpp")
            return False
        
        # Utwórz wrapper scripts
        self.console.print("\n[cyan]4. Tworzenie wrapper scripts...[/cyan]")
        self.create_wrapper_scripts()
        self.logger.info("Utworzono skrypty wrapper")
        
        self.console.print(Panel(
            f"[bold green]Instalacja zakończona pomyślnie![/bold green]\n"
            f"Katalog instalacji: {self.install_dir}\n"
            f"Uruchom: {self.install_dir}/llama-cli.sh --help",
            title="Sukces",
            expand=False
        ))
        
        self.logger.info("Instalacja zakończona pomyślnie")
        return True


if __name__ == "__main__":
    installer = LlamaInstaller()
    installer.install_full()