"""
Automatyczny instalator llama.cpp
Copyright (c) 2025 Fibogacci
Licencja: MIT

Website: https://fibogacci.pl
GitHub: https://github.com/fibogacci
Projekt: https://fibogacci.pl/ai/llamacpp
LinkedIn: https://linkedin.com/in/Fibogacci

Interfejs CLI z użyciem typer
"""
import typer
import asyncio
from pathlib import Path
from typing import Optional
import time
from rich.console import Console
from rich.table import Table

from hardware_detector import HardwareDetector
from optimization_configs import OptimizationConfigs
from llama_installer import LlamaInstaller
from translations import set_language, t
from logger_config import setup_logging, get_logger, get_installer_logger
from __version__ import __version__, PROJECT_NAME, PROJECT_AUTHOR, PROJECT_URL

def get_app_help():
    """Get app help text based on current environment language"""
    import os
    lang = os.getenv('LLAMACPP_INSTALLER_LANG', 'pl').lower()
    if lang == 'en':
        return """Automatic llama.cpp installer with hardware optimizations | by Fibogacci (fibogacci.pl)

Automatically detects hardware and applies optimal compilation flags for:
• Raspberry Pi 5 (8GB/16GB/4GB) - ARM64 + OpenBLAS + Vulkan
• Raspberry Pi 4 - ARM64 + OpenBLAS  
• Termux Android - Minimal optimizations
• Linux x86_64 - AVX/AVX2 + OpenBLAS

Use --lang en for English interface on all commands."""
    else:
        return """automatyczny instalator llama.cpp z optymalizacjami sprzętowymi | by Fibogacci (fibogacci.pl)

Automatycznie wykrywa sprzęt i stosuje optymalne flagi kompilacji dla:
• Raspberry Pi 5 (8GB/16GB/4GB) - ARM64 + OpenBLAS + Vulkan
• Raspberry Pi 4 - ARM64 + OpenBLAS  
• Termux Android - Minimalne optymalizacje
• Linux x86_64 - AVX/AVX2 + OpenBLAS

Użyj --lang en dla angielskiego interfejsu we wszystkich komendach."""

app = typer.Typer(
    name="llama-installer", 
    help=get_app_help(),
    epilog="Dla GUI użyj: python main.py | For GUI use: python main.py",
    rich_markup_mode="rich"
)
console = Console()

def version_callback(value: bool):
    """Show version information"""
    if value:
        import os
        lang = os.getenv('LLAMACPP_INSTALLER_LANG', 'pl').lower()
        if lang == 'en':
            console.print(f"[bold cyan]{PROJECT_NAME} v{__version__}[/bold cyan]")
            console.print(f"Copyright (c) 2025 {PROJECT_AUTHOR}")
            console.print(f"Website: {PROJECT_URL}")
            console.print("License: MIT")
        else:
            console.print(f"[bold cyan]{PROJECT_NAME} v{__version__}[/bold cyan]")
            console.print(f"Copyright (c) 2025 {PROJECT_AUTHOR}")
            console.print(f"Strona: {PROJECT_URL}")
            console.print("Licencja: MIT")
        raise typer.Exit()

@app.callback()
def main_callback(
    version: bool = typer.Option(
        False, 
        "--version", "-v", 
        callback=version_callback,
        help="Show version / Pokaż wersję"
    )
):
    """
    Automatyczny instalator llama.cpp z optymalizacjami sprzętowymi
    
    Automatic llama.cpp installer with hardware optimizations
    """
    pass


@app.command("detect")
def detect_hardware(
    language: str = typer.Option(
        "pl",
        "--lang", "-l",
        help="interface language (pl/en) / język interfejsu (pl/en)"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging / Włącz logowanie debug"
    )
):
    """
    Detect hardware type and show optimization information.
    
    Wykrywa typ sprzętu i pokazuje informacje o optymalizacjach.
    
    This command analyzes your system and recommends the best optimization
    settings for llama.cpp compilation. Shows CPU info, RAM, and suggested
    CMAKE flags for your hardware.
    
    Ta komenda analizuje twój system i rekomenduje najlepsze ustawienia
    optymalizacji dla kompilacji llama.cpp. Pokazuje info o CPU, RAM i
    sugerowane flagi CMAKE dla twojego sprzętu.
    """
    set_language(language)
    
    # Konfiguruj logowanie
    log_level = "DEBUG" if debug else "INFO"
    logger_config = setup_logging(log_level=log_level)
    logger = get_logger()
    
    logger_config.log_system_info()
    logger.info("Uruchomiono komendę 'detect' z CLI")
    
    detector = HardwareDetector()
    info = detector.get_detailed_info()
    
    # Loguj wykryte informacje o sprzęcie
    logger_config.log_hardware_detection(info)
    
    table = Table(title=t("hardware_info_table"))
    table.add_column(t("property"), style="cyan")
    table.add_column(t("value"), style="green")
    
    table.add_row(t("hardware_type"), info['hardware_type'])
    table.add_row(t("system"), f"{info['system_info']['system']} {info['system_info']['release']}")
    table.add_row(t("architecture"), info['system_info']['machine'])
    table.add_row(t("ram_memory"), f"{info['memory_gb']} GB")
    table.add_row(t("physical_cores"), str(info['cpu_info']['physical_cores']))
    table.add_row(t("logical_cores"), str(info['cpu_info']['logical_cores']))
    
    if info['hardware_type'] == 'x86_linux':
        table.add_row(t("avx_support"), str(info['cpu_info']['has_avx']))
        table.add_row(t("avx2_support"), str(info['cpu_info']['has_avx2']))
    
    console.print(table)
    
    console.print(f"\n[bold green]{t('suggested_optimizations')}:[/bold green]")
    console.print(OptimizationConfigs.get_description(info['hardware_type']))


@app.command("list-configs")
def list_configurations(
    language: str = typer.Option(
        "pl",
        "--lang", "-l",
        help="interface language (pl/en) / język interfejsu (pl/en)"
    )
):
    """
    Display all available hardware optimization configurations.
    
    Wyświetla wszystkie dostępne konfiguracje optymalizacji sprzętowych.
    
    Shows detailed information about CMAKE flags and system dependencies
    for each supported hardware platform. Use this to understand what
    optimizations will be applied for each hardware type.
    
    Pokazuje szczegółowe informacje o flagach CMAKE i zależnościach systemowych
    dla każdej obsługiwanej platformy sprzętowej. Użyj tego aby zrozumieć jakie
    optymalizacje będą zastosowane dla każdego typu sprzętu.
    """
    set_language(language)
    
    configs = [
        'dynamic', 'rpi5_8gb', 'rpi5_16gb', 'rpi5_4gb', 'rpi4', 'rpi_other',
        'termux', 'x86_linux', 'x86_linux_old', 'x86_linux_minimal', 'no_optimization'
    ]
    
    for config in configs:
        console.print(f"\n[bold cyan]{config}[/bold cyan]")
        console.print(f"{t('description')}: {OptimizationConfigs.get_description(config)}")
        
        console.print(f"{t('cmake_flags_label')}:")
        flags = OptimizationConfigs.get_cmake_flags(config)
        for flag in flags[:3]:
            console.print(f"  {flag}")
        if len(flags) > 3:
            console.print(f"  {t('more_flags', count=len(flags) - 3)}")
        
        console.print(f"{t('dependencies_label')}:")
        deps = OptimizationConfigs.get_dependencies(config)
        console.print(f"  {', '.join(deps[:5])}")
        if len(deps) > 5:
            console.print(f"  {t('more_deps', count=len(deps) - 5)}")


@app.command("install")
def install_llama(
    hardware_type: Optional[str] = typer.Option(
        None,
        "--hardware", "-h",
        help="hardware type (use 'list-configs' to see options) / typ sprzętu (użyj 'list-configs' aby zobaczyć opcje)"
    ),
    install_dir: Optional[str] = typer.Option(
        None,
        "--dir", "-d", 
        help="installation directory / katalog instalacji"
    ),
    custom_config: Optional[str] = typer.Option(
        None,
        "--config", "-c",
        help="file with custom CMAKE flags / plik z własnymi flagami CMAKE"
    ),
    auto_detect: bool = typer.Option(
        True,
        "--auto/--no-auto",
        help="automatic hardware detection / automatyczne wykrywanie sprzętu"
    ),
    language: str = typer.Option(
        "pl",
        "--lang", "-l",
        help="interface language (pl/en) / język interfejsu (pl/en)"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging / Włącz logowanie debug"
    )
):
    """
    Install llama.cpp with hardware-optimized compilation.
    
    Instaluje llama.cpp z kompilacją zoptymalizowaną pod sprzęt.
    
    Downloads the latest llama.cpp from GitHub, installs system dependencies,
    and compiles with optimal flags for your hardware. Supports automatic
    hardware detection or manual hardware type specification.
    
    Pobiera najnowszy llama.cpp z GitHub, instaluje zależności systemowe
    i kompiluje z optymalnymi flagami dla twojego sprzętu. Obsługuje automatyczne
    wykrywanie sprzętu lub ręczne określenie typu sprzętu.
    
    Examples / Przykłady:
        llama-installer install                           # Auto-detect / Automatyczne wykrywanie
        llama-installer install --hardware rpi5_8gb      # Specific hardware / Określony sprzęt
        llama-installer install --config my_flags.txt    # Custom config / Własna konfiguracja
    """
    set_language(language)
    
    # Wykryj sprzęt jeśli nie podano typu
    detector = HardwareDetector()
    hardware_info = None
    
    start_time = time.time()
    
    if hardware_type is None and auto_detect:
        hardware_info = detector.get_detailed_info()
        hardware_type = hardware_info['hardware_type']
        console.print(f"[green]{t('auto_detected', hardware_type=hardware_type)}[/green]")
    elif hardware_type is None:
        console.print(f"[red]{t('select_hardware_type')}[/red]")
        console.print("Use: llama-installer list-configs")
        raise typer.Exit(1)
    
    # Ustaw domyślny katalog
    if install_dir is None:
        install_dir = str(Path.cwd())
    
    # Utwórz katalog instalacji jeśli nie istnieje
    install_path = Path(install_dir)
    try:
        install_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        console.print(f"[red]{t('error')}: {t('cannot_create_directory', directory=install_dir)}[/red]")
        raise typer.Exit(1)
    
    # Konfiguruj logowanie z katalogiem instalacji
    log_level = "DEBUG" if debug else "INFO"
    install_logs_dir = install_path / "logs"
    logger_config = setup_logging(log_level=log_level, log_dir=str(install_logs_dir))
    logger = get_logger()
    
    logger_config.log_system_info()
    logger.info("Uruchomiono komendę 'install' z CLI")
    
    # Loguj parametry instalacji
    logger.info(f"Parametry instalacji:")
    logger.info(f"- hardware_type: {hardware_type}")
    logger.info(f"- install_dir: {install_dir}")
    logger.info(f"- custom_config: {custom_config}")
    logger.info(f"- auto_detect: {auto_detect}")
    logger.info(f"- language: {language}")
    
    # Loguj wykrywanie sprzętu jeśli było automatyczne
    if hardware_info and auto_detect:
        logger_config.log_hardware_detection(hardware_info)
    
    # Sprawdź czy plik konfiguracji istnieje
    if custom_config and not Path(custom_config).exists():
        console.print(f"[red]{t('config_file_not_exists')}: {custom_config}[/red]")
        logger.error(f"Plik konfiguracji nie istnieje: {custom_config}")
        raise typer.Exit(1)
    
    # Loguj rozpoczęcie instalacji
    logger_config.log_installation_start(install_dir)
    logger.info(f"Instalacja dla typu sprzętu: {hardware_type}")
    if custom_config:
        logger.info(f"Użyta własna konfiguracja: {custom_config}")
    
    # Wykonaj instalację
    installer = LlamaInstaller(install_dir)
    
    console.print(f"[cyan]{t('installation_for', hardware_type=hardware_type)}[/cyan]")
    console.print(f"{t('hardware_type')}: {hardware_type}")
    console.print(f"{t('installation_directory').rstrip(':')}: {install_dir}")
    
    if custom_config:
        console.print(f"{t('config_option')}: {custom_config}")
    
    async def run_install():
        try:
            success = await installer.install_full(hardware_type, custom_config)
            
            # Oblicz czas instalacji
            duration = time.time() - start_time
            
            if success:
                console.print(f"[bold green]{t('installation_complete')}[/bold green]")
                logger_config.log_installation_end(True, duration)
            else:
                console.print(f"[bold red]{t('installation_error', error='unknown')}[/bold red]")
                logger_config.log_installation_end(False, duration)
                raise typer.Exit(1)
        except Exception as e:
            duration = time.time() - start_time
            logger_config.log_error_with_context(e, "Błąd podczas instalacji z CLI")
            logger_config.log_installation_end(False, duration)
            console.print(f"[bold red]{t('installation_error', error=str(e))}[/bold red]")
            raise typer.Exit(1)
    
    # Uruchom asynchroniczną instalację
    asyncio.run(run_install())


@app.command("gui")
def launch_gui(
    language: str = typer.Option(
        "pl",
        "--lang", "-l",
        help="interface language (pl/en) / język interfejsu (pl/en)"
    )
):
    """
    Launch the graphical user interface.
    
    Uruchamia graficzny interfejs użytkownika.
    
    Opens the Textual-based GUI with interactive hardware selection,
    directory browser, and real-time installation progress. The GUI
    provides a user-friendly alternative to command-line installation.
    
    Otwiera GUI bazujący na Textual z interaktywnym wyborem sprzętu,
    przeglądarką katalogów i postępem instalacji w czasie rzeczywistym.
    GUI zapewnia przyjazną dla użytkownika alternatywę dla instalacji
    z linii poleceń.
    """
    set_language(language)
    try:
        from main import main as gui_main
        gui_main()
    except ImportError:
        if language == 'en':
            console.print("[red]Error: cannot launch GUI. Check if textual is installed.[/red]")
        else:
            console.print("[red]Błąd: nie można uruchomić GUI. Sprawdź czy textual jest zainstalowany.[/red]")
        raise typer.Exit(1)


@app.command("create-config")
def create_config_template(
    output_file: str = typer.Argument(..., help="output file name / nazwa pliku do utworzenia"),
    hardware_type: str = typer.Option("x86_linux", "--type", "-t", help="hardware type as template / typ sprzętu jako szablon"),
    language: str = typer.Option(
        "pl",
        "--lang", "-l",
        help="interface language (pl/en) / język interfejsu (pl/en)"
    )
):
    """
    Create a custom configuration file template.
    
    Tworzy szablon pliku z niestandardową konfiguracją.
    
    Generates a .txt file with CMAKE flags for the specified hardware type.
    You can then edit this file to customize compilation flags and use it
    with --config option during installation.
    
    Generuje plik .txt z flagami CMAKE dla określonego typu sprzętu.
    Możesz następnie edytować ten plik aby dostosować flagi kompilacji
    i użyć go z opcją --config podczas instalacji.
    
    Examples / Przykłady:
        llama-installer create-config my_config.txt --type rpi5_8gb
        llama-installer create-config custom.txt --type x86_linux --lang en
    """
    set_language(language)
    
    flags = OptimizationConfigs.get_cmake_flags(hardware_type)
    
    if language == 'en':
        config_content = f"""# CMAKE configuration for llama.cpp
# Generated for hardware type: {hardware_type}
# 
# Edit these flags as needed, then use:
# llama-installer install --config {output_file}
#
# Lines starting with # are comments and will be ignored

"""
    else:
        config_content = f"""# Konfiguracja CMAKE dla llama.cpp
# Wygenerowane dla typu sprzętu: {hardware_type}
# 
# Edytuj te flagi według potrzeb, następnie użyj:
# llama-installer install --config {output_file}
#
# Linie zaczynające się od # są komentarzami i będą ignorowane

"""
    
    for flag in flags:
        config_content += f"{flag}\n"
    
    try:
        with open(output_file, 'w') as f:
            f.write(config_content)
        
        if language == 'en':
            console.print(f"[green]Created configuration file: {output_file}[/green]")
            console.print(f"Edit file and use: llama-installer install --config {output_file}")
        else:
            console.print(f"[green]utworzono plik konfiguracji: {output_file}[/green]")
            console.print(f"Edytuj plik i użyj: llama-installer install --config {output_file}")
        
    except Exception as e:
        error_msg = "File creation error" if language == 'en' else "błąd tworzenia pliku"
        console.print(f"[red]{error_msg}: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()