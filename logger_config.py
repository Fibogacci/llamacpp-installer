"""
Automatyczny instalator llama.cpp
Copyright (c) 2025 Fibogacci
Licencja: MIT

Website: https://fibogacci.pl
GitHub: https://github.com/fibogacci
Projekt: https://fibogacci.pl/ai/llamacpp
LinkedIn: https://linkedin.com/in/Fibogacci

Konfiguracja logowania dla debugowania
"""
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class LlamaInstallerLogger:
    """Klasa konfigurująca logowanie dla instalatora llama.cpp"""
    
    def __init__(self, 
                 log_level: str = "INFO",
                 log_to_file: bool = True,
                 log_to_console: bool = True,
                 log_dir: Optional[str] = None,
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5):
        """
        Inicjalizuje konfigurację logowania
        
        Args:
            log_level: Poziom logowania (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Czy logować do pliku
            log_to_console: Czy logować do konsoli
            log_dir: Katalog dla plików logów (domyślnie ./logs)
            max_file_size: Maksymalny rozmiar pliku loga w bajtach
            backup_count: Liczba kopii zapasowych plików logów
        """
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_to_file = log_to_file
        self.log_to_console = log_to_console
        self.log_dir = Path(log_dir) if log_dir else Path("logs")
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        
        # Utworz katalog dla logów jeśli nie istnieje
        if self.log_to_file:
            self.log_dir.mkdir(exist_ok=True)
        
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Konfiguruje i zwraca logger"""
        logger = logging.getLogger("llamacpp_installer")
        logger.setLevel(self.log_level)
        
        # Usuń istniejące handlery aby uniknąć duplikowania
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Format logów
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Handler dla konsoli
        if self.log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(simple_formatter)
            logger.addHandler(console_handler)
        
        # Handler dla pliku z rotacją
        if self.log_to_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = self.log_dir / f"llamacpp_installer_{timestamp}.log"
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)  # Plik dostaje wszystkie logi
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
            
            # Log informacji o starcie
            logger.info(f"Logowanie skonfigurowane. Plik loga: {log_file}")
            logger.info(f"Poziom logowania konsoli: {logging.getLevelName(self.log_level)}")
            logger.info(f"Maksymalny rozmiar pliku: {self.max_file_size / 1024 / 1024:.1f} MB")
            logger.info(f"Liczba kopii zapasowych: {self.backup_count}")
        
        return logger
    
    def get_logger(self) -> logging.Logger:
        """Zwraca skonfigurowany logger"""
        return self.logger
    
    def log_system_info(self):
        """Loguje informacje o systemie na początku działania programu"""
        import platform
        import psutil
        
        logger = self.logger
        logger.info("=" * 60)
        logger.info("Rozpoczęcie sesji llamacpp installer")
        logger.info("=" * 60)
        logger.info(f"Python: {sys.version}")
        logger.info(f"System: {platform.system()} {platform.release()}")
        logger.info(f"Architektura: {platform.machine()}")
        logger.info(f"Procesor: {platform.processor()}")
        logger.info(f"Pamięć RAM: {psutil.virtual_memory().total / 1024**3:.2f} GB")
        logger.info(f"Katalog roboczy: {os.getcwd()}")
        logger.info(f"Argumenty CLI: {sys.argv}")
        logger.info("=" * 60)
    
    def log_hardware_detection(self, hardware_info: dict):
        """Loguje szczegóły wykrywania sprzętu"""
        logger = self.logger
        logger.info("Wykrywanie sprzętu:")
        logger.info(f"- Typ sprzętu: {hardware_info.get('hardware_type', 'unknown')}")
        logger.info(f"- System: {hardware_info.get('system_info', {}).get('system', 'unknown')}")
        logger.info(f"- Architektura: {hardware_info.get('system_info', {}).get('machine', 'unknown')}")
        logger.info(f"- Pamięć: {hardware_info.get('memory_gb', 0)} GB")
        
        cpu_info = hardware_info.get('cpu_info', {})
        logger.info(f"- Rdzenie fizyczne: {cpu_info.get('physical_cores', 0)}")
        logger.info(f"- Rdzenie logiczne: {cpu_info.get('logical_cores', 0)}")
        
        if hardware_info.get('hardware_type') == 'x86_linux':
            logger.info(f"- AVX: {cpu_info.get('has_avx', False)}")
            logger.info(f"- AVX2: {cpu_info.get('has_avx2', False)}")
    
    def log_compilation_flags(self, flags: list):
        """Loguje flagi kompilacji CMAKE"""
        logger = self.logger
        logger.info("Flagi kompilacji CMAKE:")
        for flag in flags:
            logger.info(f"- {flag}")
    
    def log_dependencies(self, dependencies: list):
        """Loguje zależności systemowe"""
        logger = self.logger
        logger.info("Zależności systemowe:")
        for dep in dependencies:
            logger.info(f"- {dep}")
    
    def log_installation_start(self, install_dir: str):
        """Loguje rozpoczęcie instalacji"""
        logger = self.logger
        logger.info("=" * 60)
        logger.info("Rozpoczęcie instalacji llama.cpp")
        logger.info("=" * 60)
        logger.info(f"Katalog instalacji: {install_dir}")
    
    def log_installation_end(self, success: bool, duration: float = None):
        """Loguje zakończenie instalacji"""
        logger = self.logger
        logger.info("=" * 60)
        if success:
            logger.info("Instalacja zakończona pomyślnie")
            if duration:
                logger.info(f"Czas instalacji: {duration:.2f} sekund")
        else:
            logger.error("Instalacja zakończona błędem")
        logger.info("=" * 60)
    
    def log_error_with_context(self, error: Exception, context: str = ""):
        """Loguje błąd z kontekstem"""
        logger = self.logger
        logger.error(f"Błąd: {context}")
        logger.error(f"Typ błędu: {type(error).__name__}")
        logger.error(f"Komunikat: {str(error)}")
        
        # Loguj stack trace jeśli dostępny
        import traceback
        logger.debug("Stack trace:", exc_info=True)


# Globalna instancja loggera
_global_logger: Optional[LlamaInstallerLogger] = None

def setup_logging(log_level: str = "INFO", 
                 log_to_file: bool = True,
                 log_to_console: bool = True,
                 log_dir: Optional[str] = None) -> LlamaInstallerLogger:
    """
    Konfiguruje globalne logowanie dla aplikacji
    
    Args:
        log_level: Poziom logowania (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Czy logować do pliku
        log_to_console: Czy logować do konsoli
        log_dir: Katalog dla plików logów
    
    Returns:
        Skonfigurowana instancja LlamaInstallerLogger
    """
    global _global_logger
    _global_logger = LlamaInstallerLogger(
        log_level=log_level,
        log_to_file=log_to_file,
        log_to_console=log_to_console,
        log_dir=log_dir
    )
    return _global_logger

def get_logger() -> logging.Logger:
    """
    Zwraca globalny logger. Jeśli nie został skonfigurowany, 
    konfiguruje go z domyślnymi ustawieniami.
    
    Returns:
        Instancja logging.Logger
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = setup_logging()
    return _global_logger.get_logger()

def get_installer_logger() -> LlamaInstallerLogger:
    """
    Zwraca globalną instancję LlamaInstallerLogger
    
    Returns:
        Instancja LlamaInstallerLogger
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = setup_logging()
    return _global_logger


if __name__ == "__main__":
    # Test konfiguracji logowania
    logger_config = setup_logging(log_level="DEBUG")
    logger = get_logger()
    
    logger_config.log_system_info()
    
    logger.debug("To jest wiadomość debug")
    logger.info("To jest wiadomość info")
    logger.warning("To jest ostrzeżenie warning")
    logger.error("To jest błąd error")
    logger.critical("To jest krytyczny błąd critical")
    
    # Test logowania błędu z kontekstem
    try:
        raise ValueError("Testowy błąd")
    except Exception as e:
        logger_config.log_error_with_context(e, "Test obsługi błędów")