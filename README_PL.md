# Automatyczny instalator llama.cpp

[English](README.md) | **Polski**

Automatyczny instalator llama.cpp z optymalizacjami sprzętowymi. Projekt wykrywa typ sprzętu (Raspberry Pi 5, Raspberry Pi 4, Termux Android, Linux x86_64) i automatycznie dobiera optymalne flagi kompilacji dla maksymalnej wydajności.

**Autor:** Fibogacci (https://fibogacci.pl)  
**Licencja:** MIT  
**Technologie:** Python, Textual (GUI), Typer (CLI), Rich, psutil

## Funkcje

- 🔍 **Automatyczne wykrywanie sprzętu**: Raspberry Pi, Android Termux, Linux x86_64
- ⚡ **Optymalizowana kompilacja**: Flagi CMAKE dostosowane do sprzętu dla maksymalnej wydajności
- 🖥️ **Podwójny interfejs**: Interaktywny GUI (Textual) i CLI (Typer)
- 🌍 **Wielojęzyczność**: Polski i angielski interfejs
- 📊 **Postęp na żywo**: Postęp instalacji ze szczegółowym logowaniem
- 🛠️ **Własne konfiguracje**: Wsparcie dla plików optymalizacji zdefiniowanych przez użytkownika
- 🔄 **Dynamiczne wykrywanie**: Automatyczne testowanie możliwości CPU (NOWOŚĆ)

## Obsługiwany sprzęt

### Raspberry Pi
- **Raspberry Pi 5 (8GB/16GB)** - Maksymalne optymalizacje ARM64 Cortex-A76 z OpenBLAS i RPC
- **Raspberry Pi 5 (4GB)** - Zrównoważone optymalizacje ARM64 z OpenBLAS
- **Raspberry Pi 4** - Optymalizacje Cortex-A72 z OpenBLAS

### Linux x86_64
- **Dynamiczne** ⭐ - Automatyczne wykrywanie i optymalizacja (ZALECANE)
- **Standardowe** - Pełne optymalizacje AVX2 z OpenBLAS (nowsze CPU)
- **Starsze** - Optymalizacje AVX bez AVX2 (CPU 2010-2013)
- **Minimalne** - Podstawowe optymalizacje (bardzo stary sprzęt)
- **Bez optymalizacji** - Najszersza kompatybilność (działa wszędzie)

### Mobilne
- **Termux Android** - Minimalne optymalizacje bez BLAS

## Szybki start

### Instalacja

#### Instalacja bezpośrednia (zalecana)
```bash
# Sklonuj repozytorium
git clone https://github.com/fibogacci/llamacpp-installer.git
cd llamacpp-installer

# Zainstaluj zależności globalnie
pip install -r requirements.txt
```

#### Alternatywnie: środowisko wirtualne (opcjonalne)
Jeśli masz problemy z instalacją globalną lub chcesz izolować zależności:

```bash
# Sklonuj repozytorium
git clone https://github.com/fibogacci/llamacpp-installer.git
cd llamacpp-installer

# Utwórz środowisko wirtualne
python -m venv venv-llamacpp-installer

# Aktywuj środowisko wirtualne
source venv-llamacpp-installer/bin/activate

# Zainstaluj zależności w środowisku wirtualnym
pip install -r requirements.txt

# Aby deaktywować środowisko wirtualne (po zakończeniu pracy)
deactivate
```

### Użycie

#### Interfejs GUI (zalecany)
```bash
# Polski (domyślny)
python main.py

# Angielski
python main.py --lang en
```

#### Interfejs CLI

```bash
# Wykrywanie sprzętu
python cli.py detect
python cli.py detect --lang en

# Automatyczna instalacja (zalecana)
python cli.py install --hardware dynamic --dir /ścieżka/do/instalacji

# Ręczny wybór sprzętu
python cli.py install --hardware rpi5_8gb --dir /home/user/llama
python cli.py install --hardware x86_linux --dir /opt/llama --lang en

# Własna konfiguracja
python cli.py install --config example_configs/x86_avx512.txt --dir /ścieżka/do/instalacji
```

## Typy sprzętu

| Sprzęt | Typ | Opis |
|--------|-----|------|
| Raspberry Pi 5 8/16GB | `rpi5_8gb` | Maksymalna wydajność z RPC |
| Raspberry Pi 5 4GB | `rpi5_4gb` | Zrównoważona optymalizacja |
| Raspberry Pi 4 | `rpi4` | Optymalizowany dla Cortex-A72 |
| Linux x86_64 Auto | `dynamic` | **Automatyczne wykrywanie** ⭐ |
| Linux x86_64 Nowe | `x86_linux` | AVX2 + OpenBLAS |
| Linux x86_64 Starsze | `x86_linux_old` | AVX bez AVX2 |
| Linux x86_64 Minimalne | `x86_linux_minimal` | Podstawowe optymalizacje |
| Bez optymalizacji | `no_optimization` | Maksymalna kompatybilność |
| Termux Android | `termux` | Optymalizowany dla urządzeń mobilnych |

## Własne konfiguracje

Utwórz własne pliki `.txt` z flagami CMAKE:

```cmake
# example_configs/moja_konfiguracja.txt
-DGGML_NATIVE=ON
-DGGML_AVX2=ON
-DGGML_OPENMP=ON
-DGGML_OPENBLAS=ON
```

Użycie:
```bash
python cli.py install --config moja_konfiguracja.txt --dir /ścieżka/do/instalacji
```

## Struktura katalogów

Po instalacji struktura będzie następująca:
```
/twoja/wybrana/ścieżka/
└── llama.cpp/
    ├── build/
    │   └── bin/
    │       ├── llama-cli
    │       ├── llama-server
    │       └── ...
    ├── logs/
    │   └── llamacpp_installer_*.log
    ├── llama-cli.sh      # Skrypt wrapper
    ├── llama-server.sh   # Skrypt wrapper
    └── llama-simple.sh   # Skrypt wrapper
```

## Obsługa języków

### CLI
```bash
# Polski (domyślny)
python cli.py detect
python cli.py install --hardware dynamic --dir /ścieżka

# Angielski
python cli.py detect --lang en
python cli.py install --hardware dynamic --dir /ścieżka --lang en
```

### GUI
```bash
# Polski (domyślny)
python main.py

# Angielski
python main.py --lang en
python main.py --en
```

### Zmienna środowiskowa
```bash
export LLAMACPP_INSTALLER_LANG=en
python main.py  # Użyje angielskiego
```

## Zaawansowane użycie

### Tryb debugowania
```bash
# Włącz szczegółowe logowanie
python cli.py detect --debug
python cli.py install --hardware dynamic --dir /ścieżka --debug
```

### Testowanie wykrywania sprzętu
```bash
# Test wykrywania sprzętu
python hardware_detector.py

# Test dynamicznego wykrywania CPU
python dynamic_config.py

# Test konfiguracji optymalizacji
python optimization_configs.py
```

## Rozwiązywanie problemów

### Częste problemy

1. **Błędy kompilacji na starszych CPU**
   - Użyj `--hardware x86_linux_old` lub `--hardware dynamic`
   - Sprawdź logi w `{katalog_instalacji}/logs/`

2. **Brakujące zależności**
   - Zainstaluj narzędzia budowania: `sudo apt install build-essential cmake git`
   - Dla Ubuntu/Debian z OpenBLAS: `sudo apt install libopenblas-dev`

3. **Błędy uprawnień**
   - Upewnij się, że masz uprawnienia zapisu do katalogu instalacji
   - Używaj `sudo` tylko przy instalacji do katalogów systemowych

4. **Problemy specyficzne dla Termux**
   - Zainstaluj wymagane pakiety: `pkg install python cmake git`
   - Użyj `--hardware termux` dla optymalizacji mobilnej

### Pliki logów

Logi instalacji są zapisywane w `{katalog_instalacji}/logs/` w formacie:
`llamacpp_installer_YYYYMMDD_HHMMSS.log`

## Wymagania

- Python 3.7+
- Narzędzia budowania (gcc, cmake, git)
- Połączenie internetowe do pobierania llama.cpp
- Wystarczające miejsce na dysku (2-3 GB dla pełnej kompilacji)

## Współpraca

1. Zrób fork repozytorium
2. Utwórz gałąź funkcji
3. Wprowadź zmiany
4. Przetestuj na różnym sprzęcie jeśli to możliwe
5. Wyślij pull request

## Licencja

Licencja MIT - zobacz plik [LICENSE](LICENSE) dla szczegółów.

## Autor

**Fibogacci**
- Strona: https://fibogacci.pl
- GitHub: https://github.com/fibogacci

---

Dla dokumentacji angielskiej, zobacz [README.md](README.md)