"""
Automatyczny instalator llama.cpp
Copyright (c) 2025 Fibogacci
Licencja: MIT

Website: https://fibogacci.pl
GitHub: https://github.com/fibogacci
Projekt: https://fibogacci.pl/ai/llamacpp
LinkedIn: https://linkedin.com/in/Fibogacci

Moduł do wykrywania sprzętu i systemu
"""
import platform
import subprocess
import os
import psutil
from typing import Dict, Optional, Tuple
from logger_config import get_logger


class HardwareDetector:
    """Klasa do wykrywania rodzaju sprzętu i systemu"""
    
    def __init__(self):
        self.logger = get_logger()
        self.system_info = self._get_system_info()
        self.logger.debug("Zainicjalizowano HardwareDetector")
    
    def _get_system_info(self) -> Dict[str, str]:
        """Zbiera podstawowe informacje o systemie"""
        info = {
            'system': platform.system(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'architecture': platform.architecture()[0],
            'release': platform.release(),
        }
        self.logger.debug(f"Informacje o systemie: {info}")
        return info
    
    def _is_raspberry_pi(self) -> Tuple[bool, Optional[str]]:
        """Sprawdza czy to Raspberry Pi i jaka wersja"""
        self.logger.debug("Sprawdzanie czy to Raspberry Pi")
        try:
            # Sprawdź /proc/device-tree/model (najlepszy sposób na RPi)
            if os.path.exists('/proc/device-tree/model'):
                with open('/proc/device-tree/model', 'r') as f:
                    model = f.read().strip('\x00')
                    self.logger.debug(f"Model z /proc/device-tree/model: {model}")
                    if 'Raspberry Pi 5' in model:
                        self.logger.info("Wykryto Raspberry Pi 5")
                        return True, 'rpi5'
                    elif 'Raspberry Pi 4' in model:
                        self.logger.info("Wykryto Raspberry Pi 4")
                        return True, 'rpi4'
                    elif 'Raspberry Pi' in model:
                        self.logger.info("Wykryto Raspberry Pi (inny model)")
                        return True, 'rpi_other'
            
            # Alternatywnie sprawdź /proc/cpuinfo
            if os.path.exists('/proc/cpuinfo'):
                with open('/proc/cpuinfo', 'r') as f:
                    cpuinfo = f.read()
                    if 'BCM2712' in cpuinfo:  # RPi 5
                        self.logger.info("Wykryto Raspberry Pi 5 (BCM2712)")
                        return True, 'rpi5'
                    elif 'BCM2711' in cpuinfo:  # RPi 4
                        self.logger.info("Wykryto Raspberry Pi 4 (BCM2711)")
                        return True, 'rpi4'
                    elif 'Hardware' in cpuinfo and 'BCM' in cpuinfo:
                        self.logger.info("Wykryto Raspberry Pi (inny BCM)")
                        return True, 'rpi_other'
                        
        except Exception as e:
            self.logger.warning(f"Błąd podczas wykrywania Raspberry Pi: {e}")
            
        self.logger.debug("To nie jest Raspberry Pi")
        return False, None
    
    def _is_termux(self) -> bool:
        """Sprawdza czy to środowisko Termux na Androidzie"""
        self.logger.debug("Sprawdzanie czy to Termux")
        is_termux = (
            os.environ.get('TERMUX_VERSION') is not None or
            os.path.exists('/data/data/com.termux') or
            'com.termux' in os.environ.get('PREFIX', '')
        )
        if is_termux:
            self.logger.info("Wykryto środowisko Termux")
        else:
            self.logger.debug("To nie jest Termux")
        return is_termux
    
    def _get_memory_gb(self) -> int:
        """Zwraca ilość pamięci RAM w GB"""
        try:
            memory_bytes = psutil.virtual_memory().total
            memory_gb = round(memory_bytes / (1024**3))
            return memory_gb
        except:
            return 0
    
    def _get_cpu_info(self) -> Dict[str, any]:
        """Zbiera informacje o procesorze"""
        try:
            cpu_count = psutil.cpu_count(logical=False)  # fizyczne rdzenie
            cpu_count_logical = psutil.cpu_count(logical=True)  # logiczne rdzenie
            
            # Sprawdź czy dostępne są instrukcje AVX/AVX2 na x86
            has_avx = False
            has_avx2 = False
            
            if platform.machine().lower() in ['x86_64', 'amd64']:
                try:
                    result = subprocess.run(['grep', '-o', 'avx2\\|avx', '/proc/cpuinfo'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        flags = result.stdout.strip().split('\n')
                        has_avx2 = 'avx2' in flags
                        has_avx = 'avx' in flags or has_avx2
                except:
                    pass
            
            return {
                'physical_cores': cpu_count,
                'logical_cores': cpu_count_logical,
                'has_avx': has_avx,
                'has_avx2': has_avx2
            }
        except:
            return {
                'physical_cores': 1,
                'logical_cores': 1,
                'has_avx': False,
                'has_avx2': False
            }
    
    def detect_hardware_type(self) -> str:
        """
        Główna funkcja wykrywająca typ sprzętu
        Zwraca: 'rpi5_8gb', 'rpi5_16gb', 'rpi4', 'termux', 'x86_linux', 'unknown'
        """
        self.logger.info("Rozpoczęcie wykrywania typu sprzętu")
        
        # Sprawdź Termux
        if self._is_termux():
            self.logger.info("Wykryto typ sprzętu: termux")
            return 'termux'
        
        # Sprawdź Raspberry Pi
        is_rpi, rpi_version = self._is_raspberry_pi()
        if is_rpi:
            if rpi_version == 'rpi5':
                memory_gb = self._get_memory_gb()
                self.logger.debug(f"Raspberry Pi 5 z {memory_gb} GB RAM")
                if memory_gb >= 16:
                    self.logger.info("Wykryto typ sprzętu: rpi5_16gb")
                    return 'rpi5_16gb'
                elif memory_gb >= 8:
                    self.logger.info("Wykryto typ sprzętu: rpi5_8gb")
                    return 'rpi5_8gb'
                else:
                    self.logger.info("Wykryto typ sprzętu: rpi5_4gb")
                    return 'rpi5_4gb'
            elif rpi_version == 'rpi4':
                self.logger.info("Wykryto typ sprzętu: rpi4")
                return 'rpi4'
            else:
                self.logger.info("Wykryto typ sprzętu: rpi_other")
                return 'rpi_other'
        
        # Sprawdź Linux x86
        if (self.system_info['system'] == 'Linux' and 
            self.system_info['machine'].lower() in ['x86_64', 'amd64']):
            # Rozróżnij AVX2 vs AVX
            if self.system_info.get('avx2', False):
                self.logger.info("Wykryto typ sprzętu: x86_linux (z obsługą AVX2)")
                return 'x86_linux'
            else:
                self.logger.info("Wykryto typ sprzętu: x86_linux_old (bez obsługi AVX2)")
                return 'x86_linux_old'
        
        self.logger.warning("Nie można wykryć typu sprzętu - zwracam 'unknown'")
        return 'unknown'
    
    def get_detailed_info(self) -> Dict[str, any]:
        """Zwraca szczegółowe informacje o sprzęcie"""
        hardware_type = self.detect_hardware_type()
        cpu_info = self._get_cpu_info()
        memory_gb = self._get_memory_gb()
        
        return {
            'hardware_type': hardware_type,
            'system_info': self.system_info,
            'cpu_info': cpu_info,
            'memory_gb': memory_gb,
            'is_rpi': self._is_raspberry_pi(),
            'is_termux': self._is_termux()
        }


if __name__ == "__main__":
    detector = HardwareDetector()
    info = detector.get_detailed_info()
    
    print("=== Informacje o sprzęcie ===")
    print(f"Typ sprzętu: {info['hardware_type']}")
    print(f"System: {info['system_info']['system']} {info['system_info']['release']}")
    print(f"Architektura: {info['system_info']['machine']}")
    print(f"Pamięć RAM: {info['memory_gb']} GB")
    print(f"Rdzenie fizyczne: {info['cpu_info']['physical_cores']}")
    print(f"Rdzenie logiczne: {info['cpu_info']['logical_cores']}")
    
    if info['hardware_type'] == 'x86_linux':
        print(f"Obsługa AVX: {info['cpu_info']['has_avx']}")
        print(f"Obsługa AVX2: {info['cpu_info']['has_avx2']}")