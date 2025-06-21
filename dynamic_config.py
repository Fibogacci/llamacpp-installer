"""
Automatyczny instalator llama.cpp
Copyright (c) 2025 Fibogacci
Licencja: MIT

Dynamiczne wykrywanie możliwości CPU i generowanie optymalnych flag CMAKE
"""
import platform
import subprocess
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Tuple
from logger_config import get_logger


class DynamicConfigGenerator:
    """Klasa do dynamicznego generowania konfiguracji na podstawie możliwości systemu"""
    
    def __init__(self):
        self.logger = get_logger()
        self.system_info = self._get_system_info()
        self.cpu_features = self._detect_cpu_features()
        
    def _get_system_info(self) -> Dict[str, str]:
        """Pobiera podstawowe informacje o systemie"""
        return {
            'system': platform.system(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'architecture': platform.architecture()[0],
        }
    
    def _detect_cpu_features(self) -> Dict[str, bool]:
        """Wykrywa dostępne instrukcje CPU"""
        features = {
            'avx': False,
            'avx2': False,
            'fma': False,
            'sse4_1': False,
            'sse4_2': False,
            'f16c': False,
            'bmi2': False
        }
        
        try:
            if self.system_info['system'] == 'Linux':
                # Sprawdź /proc/cpuinfo
                with open('/proc/cpuinfo', 'r') as f:
                    cpuinfo = f.read().lower()
                    
                for feature in features.keys():
                    features[feature] = feature in cpuinfo
                    
                self.logger.debug(f"Wykryte funkcje CPU: {features}")
                
        except Exception as e:
            self.logger.warning(f"Nie można odczytać funkcji CPU: {e}")
            
        return features
    
    def _test_cmake_flag(self, flags: List[str], test_dir: Path) -> bool:
        """Testuje czy dana kombinacja flag CMAKE się kompiluje"""
        try:
            # Stwórz prosty test CMakeLists.txt
            cmake_content = f"""
cmake_minimum_required(VERSION 3.12)
project(test_flags)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Test flags
{' '.join(f'set({flag.split("=")[0].replace("-D", "")} {flag.split("=")[1] if "=" in flag else "ON"})' for flag in flags if flag.startswith('-D'))}

# Prosty test
add_executable(test_flags test.cpp)
"""
            
            # Stwórz prosty test.cpp
            cpp_content = """
#include <iostream>

#ifdef __AVX__
#include <immintrin.h>
#endif

int main() {
#ifdef __AVX__
    // Test AVX
    __m256 a = _mm256_set1_ps(1.0f);
    __m256 b = _mm256_set1_ps(2.0f);
    __m256 c = _mm256_add_ps(a, b);
#endif
    
#ifdef __FMA__
    // Test FMA
    __m256 d = _mm256_fmadd_ps(a, b, c);
#endif
    
    std::cout << "Test passed" << std::endl;
    return 0;
}
"""
            
            cmake_file = test_dir / "CMakeLists.txt"
            cpp_file = test_dir / "test.cpp"
            build_dir = test_dir / "build"
            
            # Zapisz pliki
            with open(cmake_file, 'w') as f:
                f.write(cmake_content)
            with open(cpp_file, 'w') as f:
                f.write(cpp_content)
                
            build_dir.mkdir(exist_ok=True)
            
            # Testuj konfigurację CMAKE
            cmd = ['cmake', '-B', str(build_dir), '-S', str(test_dir)] + flags
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                self.logger.debug(f"CMAKE test failed for flags {flags}: {result.stderr}")
                return False
                
            # Testuj kompilację
            cmd = ['cmake', '--build', str(build_dir)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                self.logger.debug(f"Build test failed for flags {flags}: {result.stderr}")
                return False
                
            # Testuj uruchomienie
            executable = build_dir / "test_flags"
            if executable.exists():
                result = subprocess.run([str(executable)], capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    self.logger.debug(f"Runtime test failed for flags {flags}: {result.stderr}")
                    return False
            
            self.logger.debug(f"Test passed for flags: {flags}")
            return True
            
        except Exception as e:
            self.logger.debug(f"Exception during test for flags {flags}: {e}")
            return False
    
    def _test_dependency(self, package: str) -> bool:
        """Testuje czy dana zależność jest dostępna"""
        try:
            if package == 'curl':
                # Test dla CURL - sprawdź czy można linkować z libcurl
                result = subprocess.run(['pkg-config', '--exists', 'libcurl'], 
                                     capture_output=True, timeout=5)
                return result.returncode == 0
            elif package == 'openblas':
                # Test dla OpenBLAS
                result = subprocess.run(['pkg-config', '--exists', 'openblas'], 
                                     capture_output=True, timeout=5)
                if result.returncode == 0:
                    return True
                # Fallback - sprawdź czy plik istnieje
                return os.path.exists('/usr/lib/x86_64-linux-gnu/libopenblas.so') or \
                       os.path.exists('/usr/lib/libopenblas.so')
            elif package == 'openmp':
                # Test dla OpenMP
                result = subprocess.run(['pkg-config', '--exists', 'openmp'], 
                                     capture_output=True, timeout=5)
                return result.returncode == 0
                
        except Exception as e:
            self.logger.debug(f"Dependency test failed for {package}: {e}")
            
        return False
    
    def generate_optimal_config(self, hardware_type: str = None) -> List[str]:
        """Generuje optymalną konfigurację na podstawie wykrytych możliwości"""
        config = ['-DCMAKE_BUILD_TYPE=Release']
        
        # Bazowe ustawienia zawsze bezpieczne
        config.extend([
            '-DGGML_CUDA=OFF',  # Można później dodać wykrywanie CUDA
            '-DGGML_NATIVE=OFF'  # Bezpieczniejsze dla dystrybucji
        ])
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir)
            
            # Test instrukcji CPU po kolei od najbardziej zaawansowanych
            if self.cpu_features.get('avx2', False):
                if self._test_cmake_flag(config + ['-DGGML_AVX=ON', '-DGGML_AVX2=ON'], test_dir):
                    config.extend(['-DGGML_AVX=ON', '-DGGML_AVX2=ON'])
                    self.logger.info("AVX2 support enabled")
                elif self._test_cmake_flag(config + ['-DGGML_AVX=ON', '-DGGML_AVX2=OFF'], test_dir):
                    config.extend(['-DGGML_AVX=ON', '-DGGML_AVX2=OFF'])
                    self.logger.info("AVX support enabled (AVX2 disabled)")
            elif self.cpu_features.get('avx', False):
                if self._test_cmake_flag(config + ['-DGGML_AVX=ON', '-DGGML_AVX2=OFF'], test_dir):
                    config.extend(['-DGGML_AVX=ON', '-DGGML_AVX2=OFF'])
                    self.logger.info("AVX support enabled")
                else:
                    config.extend(['-DGGML_AVX=OFF', '-DGGML_AVX2=OFF'])
                    self.logger.info("AVX disabled (compatibility)")
            else:
                config.extend(['-DGGML_AVX=OFF', '-DGGML_AVX2=OFF'])
                self.logger.info("No AVX support detected")
            
            # Test FMA
            if self.cpu_features.get('fma', False):
                if self._test_cmake_flag(config + ['-DGGML_FMA=ON'], test_dir):
                    config.append('-DGGML_FMA=ON')
                    self.logger.info("FMA support enabled")
                else:
                    config.append('-DGGML_FMA=OFF')
                    self.logger.info("FMA disabled (compatibility)")
            else:
                config.append('-DGGML_FMA=OFF')
                self.logger.info("No FMA support detected")
            
            # Test BMI2 - explicitly disable if not supported
            if self.cpu_features.get('bmi2', False):
                if self._test_cmake_flag(config + ['-DGGML_BMI2=ON'], test_dir):
                    config.append('-DGGML_BMI2=ON')
                    self.logger.info("BMI2 support enabled")
                else:
                    config.append('-DGGML_BMI2=OFF')
                    self.logger.info("BMI2 disabled (compatibility)")
            else:
                config.append('-DGGML_BMI2=OFF')
                self.logger.info("No BMI2 support detected")
            
            # Test F16C - explicitly disable if not supported
            if self.cpu_features.get('f16c', False):
                if self._test_cmake_flag(config + ['-DGGML_F16C=ON'], test_dir):
                    config.append('-DGGML_F16C=ON')
                    self.logger.info("F16C support enabled")
                else:
                    config.append('-DGGML_F16C=OFF')
                    self.logger.info("F16C disabled (compatibility)")
            else:
                config.append('-DGGML_F16C=OFF')
                self.logger.info("No F16C support detected")
            
            # Test BLAS
            if self._test_dependency('openblas'):
                if self._test_cmake_flag(config + ['-DGGML_BLAS=ON', '-DGGML_BLAS_PROVIDER=OpenBLAS'], test_dir):
                    config.extend(['-DGGML_BLAS=ON', '-DGGML_BLAS_PROVIDER=OpenBLAS'])
                    self.logger.info("OpenBLAS support enabled")
                elif self._test_cmake_flag(config + ['-DGGML_BLAS=ON'], test_dir):
                    config.append('-DGGML_BLAS=ON')
                    self.logger.info("Generic BLAS support enabled")
                else:
                    config.append('-DGGML_BLAS=OFF')
                    self.logger.info("BLAS disabled (compilation issues)")
            else:
                config.append('-DGGML_BLAS=OFF')
                self.logger.info("No BLAS library detected")
            
            # Test OpenMP
            if self._test_dependency('openmp'):
                if self._test_cmake_flag(config + ['-DGGML_OPENMP=ON'], test_dir):
                    config.append('-DGGML_OPENMP=ON')
                    self.logger.info("OpenMP support enabled")
                else:
                    config.append('-DGGML_OPENMP=OFF')
                    self.logger.info("OpenMP disabled (compilation issues)")
            else:
                config.append('-DGGML_OPENMP=OFF')
                self.logger.info("No OpenMP support detected")
            
            # Test CURL
            if self._test_dependency('curl'):
                if self._test_cmake_flag(config + ['-DLLAMA_CURL=ON'], test_dir):
                    # CURL domyślnie włączone, nie dodajemy flagi
                    self.logger.info("CURL support enabled")
                else:
                    config.append('-DLLAMA_CURL=OFF')
                    self.logger.info("CURL disabled (compilation issues)")
            else:
                config.append('-DLLAMA_CURL=OFF')
                self.logger.info("No CURL library detected")
            
            # Test LTO (Link Time Optimization)
            if self._test_cmake_flag(config + ['-DGGML_LTO=ON'], test_dir):
                config.append('-DGGML_LTO=ON')
                self.logger.info("LTO (Link Time Optimization) enabled")
            else:
                config.append('-DGGML_LTO=OFF')
                self.logger.info("LTO disabled (compatibility)")
        
        self.logger.info(f"Generated dynamic configuration: {config}")
        return config
    
    def get_description(self) -> str:
        """Zwraca opis wygenerowanej konfiguracji"""
        features = []
        if self.cpu_features.get('avx2', False):
            features.append("AVX2")
        elif self.cpu_features.get('avx', False):
            features.append("AVX")
        
        if self.cpu_features.get('fma', False):
            features.append("FMA")
            
        if features:
            return f"Dynamically optimized for {'+'.join(features)}"
        else:
            return "Dynamically optimized (safe compatibility mode)"


if __name__ == "__main__":
    # Test dynamicznego generatora
    generator = DynamicConfigGenerator()
    print("=== Wykryte funkcje CPU ===")
    for feature, enabled in generator.cpu_features.items():
        print(f"{feature.upper()}: {'✓' if enabled else '✗'}")
    
    print("\n=== Wygenerowana konfiguracja ===")
    config = generator.generate_optimal_config()
    for flag in config:
        print(f"  {flag}")
    
    print(f"\nOpis: {generator.get_description()}")