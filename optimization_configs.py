"""
Automatyczny instalator llama.cpp
Copyright (c) 2025 Fibogacci
Licencja: MIT

Website: https://fibogacci.pl
GitHub: https://github.com/fibogacci
Projekt: https://fibogacci.pl/ai/llamacpp
LinkedIn: https://linkedin.com/in/Fibogacci

Konfiguracje optymalizacji dla różnych typów sprzętu
"""
from typing import Dict, List


class OptimizationConfigs:
    """Klasa zawierająca predefiniowane konfiguracje optymalizacji"""
    
    @staticmethod
    def get_cmake_flags(hardware_type: str, custom_config: str = None) -> List[str]:
        """
        Zwraca flagi cmake dla danego typu sprzętu
        
        Args:
            hardware_type: typ sprzętu wykryty przez HardwareDetector
            custom_config: opcjonalna ścieżka do pliku z własnymi flagami
        
        Returns:
            Lista flag CMAKE
        """
        
        if custom_config:
            return OptimizationConfigs._load_custom_config(custom_config)
        
        # Dynamiczna konfiguracja
        if hardware_type == 'dynamic':
            try:
                from dynamic_config import DynamicConfigGenerator
                generator = DynamicConfigGenerator()
                return generator.generate_optimal_config()
            except ImportError as e:
                print(f"Nie można załadować DynamicConfigGenerator: {e}")
                return OptimizationConfigs.get_cmake_flags('no_optimization')
        
        configs = {
            'rpi5_8gb': [
                '-DGGML_RPC=ON',
                '-DGGML_BLAS=ON',
                '-DGGML_OPENMP=ON',
                '-DCMAKE_C_FLAGS=-march=armv8.2-a+fp16+rcpc+dotprod -mtune=cortex-a76 -O3',
                '-DCMAKE_CXX_FLAGS=-march=armv8.2-a+fp16+rcpc+dotprod -mtune=cortex-a76 -O3',
                '-DGGML_NATIVE=OFF',
                '-DGGML_LTO=ON',
                '-DCMAKE_BUILD_TYPE=Release',
                '-DGGML_CUDA=OFF'
            ],
            
            'rpi5_16gb': [
                '-DGGML_RPC=ON',
                '-DGGML_BLAS=ON',
                '-DGGML_OPENMP=ON',
                '-DCMAKE_C_FLAGS=-march=armv8.2-a+fp16+rcpc+dotprod -mtune=cortex-a76 -O3',
                '-DCMAKE_CXX_FLAGS=-march=armv8.2-a+fp16+rcpc+dotprod -mtune=cortex-a76 -O3',
                '-DGGML_NATIVE=OFF',
                '-DGGML_LTO=ON',
                '-DCMAKE_BUILD_TYPE=Release',
                '-DGGML_CUDA=OFF'
            ],
            
            'rpi5_4gb': [
                '-DGGML_BLAS=ON',
                '-DGGML_OPENMP=ON',
                '-DCMAKE_C_FLAGS=-march=armv8.2-a+fp16+rcpc+dotprod -mtune=cortex-a76 -O2',
                '-DCMAKE_CXX_FLAGS=-march=armv8.2-a+fp16+rcpc+dotprod -mtune=cortex-a76 -O2',
                '-DGGML_NATIVE=OFF',
                '-DCMAKE_BUILD_TYPE=Release'
            ],
            
            'rpi4': [
                '-DGGML_BLAS=ON',
                '-DGGML_OPENMP=ON',
                '-DCMAKE_C_FLAGS=-march=armv8-a+crc -mtune=cortex-a72 -O2',
                '-DCMAKE_CXX_FLAGS=-march=armv8-a+crc -mtune=cortex-a72 -O2',
                '-DGGML_NATIVE=OFF',
                '-DCMAKE_BUILD_TYPE=Release'
            ],
            
            'rpi_other': [
                '-DGGML_BLAS=ON',
                '-DGGML_OPENMP=ON',
                '-DCMAKE_C_FLAGS=-O2',
                '-DCMAKE_CXX_FLAGS=-O2',
                '-DGGML_NATIVE=OFF',
                '-DCMAKE_BUILD_TYPE=Release'
            ],
            
            'termux': [
                '-DGGML_BLAS=OFF',
                '-DGGML_OPENMP=ON',
                '-DCMAKE_C_FLAGS=-O2',
                '-DCMAKE_CXX_FLAGS=-O2',
                '-DGGML_NATIVE=OFF',
                '-DCMAKE_BUILD_TYPE=Release',
                '-DGGML_CUDA=OFF',
                '-DGGML_VULKAN=OFF'
            ],
            
            'x86_linux': [
                '-DGGML_AVX=ON',
                '-DGGML_AVX2=ON',
                '-DGGML_FMA=ON',
                '-DGGML_BLAS=ON',
                '-DGGML_OPENMP=ON',
                '-DGGML_NATIVE=ON',
                '-DGGML_LTO=ON',
                '-DCMAKE_BUILD_TYPE=Release',
                '-DGGML_CUDA=OFF'  # Można włączyć jeśli wykryta CUDA
            ],
            
            'x86_linux_old': [  # Starsze procesory x86_64 bez AVX2 / Older x86_64 CPUs without AVX2
                '-DGGML_AVX=ON',
                '-DGGML_AVX2=OFF',
                '-DGGML_FMA=OFF',  # Wyłączone - starsze procesory mogą nie obsługiwać FMA
                '-DGGML_BMI2=OFF',  # Wyłączone - unika SIGILL na starszych CPU
                '-DGGML_F16C=OFF',  # Wyłączone - unika SIGILL na starszych CPU
                '-DGGML_BLAS=OFF',  # Wyłączone - problemy z konfiguracją na starszych systemach
                '-DGGML_OPENMP=ON',
                '-DGGML_NATIVE=OFF',  # Wyłączone dla lepszej kompatybilności / Disabled for better compatibility
                '-DGGML_LTO=OFF',  # Wyłączone - może powodować problemy linkowania na starszych systemach
                '-DCMAKE_BUILD_TYPE=Release',
                '-DGGML_CUDA=OFF',
                '-DLLAMA_CURL=OFF'  # Wyłączone - unika problemów z brakującą biblioteką CURL
            ],
            
            'x86_linux_minimal': [  # Bardzo stary sprzęt bez AVX / Very old hardware without AVX
                '-DGGML_AVX=OFF',
                '-DGGML_AVX2=OFF', 
                '-DGGML_FMA=OFF',
                '-DGGML_BMI2=OFF',  # Wyłączone - unika SIGILL na starszych CPU
                '-DGGML_F16C=OFF',  # Wyłączone - unika SIGILL na starszych CPU
                '-DGGML_BLAS=OFF',
                '-DGGML_OPENMP=OFF',
                '-DGGML_NATIVE=OFF',
                '-DGGML_LTO=OFF',
                '-DCMAKE_BUILD_TYPE=Release',
                '-DGGML_CUDA=OFF',
                '-DLLAMA_CURL=OFF'
            ],
            
            'no_optimization': [
                '-DCMAKE_BUILD_TYPE=Release',
                '-DGGML_CUDA=OFF',
                '-DGGML_BLAS=OFF',
                '-DGGML_OPENMP=OFF',
                '-DGGML_NATIVE=OFF',
                '-DGGML_AVX=OFF',
                '-DGGML_AVX2=OFF',
                '-DGGML_FMA=OFF',
                '-DGGML_BMI2=OFF',
                '-DGGML_F16C=OFF',
                '-DGGML_LTO=OFF',
                '-DLLAMA_CURL=OFF'
            ],
            
            'dynamic': []  # Specjalna opcja - zostanie wypełniona przez DynamicConfigGenerator
        }
        
        return configs.get(hardware_type, configs['no_optimization'])
    
    @staticmethod
    def _load_custom_config(config_file: str) -> List[str]:
        """Wczytuje własne flagi z pliku tekstowego"""
        try:
            with open(config_file, 'r') as f:
                lines = f.readlines()
            
            flags = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    flags.append(line)
            
            return flags
        except Exception as e:
            print(f"błąd wczytywania konfiguracji z {config_file}: {e}")
            return ['-DCMAKE_BUILD_TYPE=Release']
    
    @staticmethod
    def get_dependencies(hardware_type: str) -> List[str]:
        """Zwraca listę zależności systemowych do zainstalowania"""
        
        base_deps = [
            'git',
            'build-essential',
            'cmake',
            'pkg-config'
        ]
        
        deps_map = {
            'rpi5_8gb': base_deps + [
                'libopenblas-dev',
                'libomp-dev'
            ],
            'rpi5_16gb': base_deps + [
                'libopenblas-dev',
                'libomp-dev'
            ],
            'rpi5_4gb': base_deps + [
                'libopenblas-dev',
                'libomp-dev'
            ],
            'rpi4': base_deps + [
                'libopenblas-dev',
                'libomp-dev'
            ],
            'rpi_other': base_deps + [
                'libopenblas-dev',
                'libomp-dev'
            ],
            'termux': [
                'git',
                'clang',
                'cmake',
                'make',
                'pkg-config'
            ],
            'x86_linux': base_deps + [
                'libopenblas-dev',
                'libomp-dev'
            ],
            'x86_linux_old': base_deps + [
                'libomp-dev'  # Tylko OpenMP, bez BLAS dla lepszej kompatybilności
            ],
            'x86_linux_minimal': base_deps  # Tylko podstawowe narzędzia kompilacji
        }
        
        return deps_map.get(hardware_type, base_deps)
    
    @staticmethod
    def get_description(hardware_type: str) -> str:
        """Zwraca opis optymalizacji dla danego sprzętu"""
        # Specjalne traktowanie dla dynamicznej konfiguracji
        if hardware_type == 'dynamic':
            try:
                from dynamic_config import DynamicConfigGenerator
                generator = DynamicConfigGenerator()
                return generator.get_description()
            except ImportError:
                return "Dynamic optimization (fallback to safe mode)"
        
        from translations import t
        
        # Mapowanie nazw sprzętu na klucze tłumaczeń
        hardware_key = f"hardware_{hardware_type}"
        
        return t(hardware_key, default=t("hardware_unknown"))


if __name__ == "__main__":
    # Test konfiguracji
    for hw_type in ['rpi5_8gb', 'rpi4', 'termux', 'x86_linux']:
        print(f"\\n=== {hw_type} ===")
        print(f"Opis: {OptimizationConfigs.get_description(hw_type)}")
        print("Flagi CMAKE:")
        for flag in OptimizationConfigs.get_cmake_flags(hw_type):
            print(f"  {flag}")
        print("Zależności:")
        for dep in OptimizationConfigs.get_dependencies(hw_type):
            print(f"  {dep}")