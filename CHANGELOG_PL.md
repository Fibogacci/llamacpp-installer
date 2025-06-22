# Historia zmian

Wszystkie istotne zmiany w tym projekcie będą dokumentowane w tym pliku.

Format oparty jest na [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
a projekt przestrzega [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-06-22

### Pierwsza wersja
- **Automatyczny instalator llama.cpp** z optymalizacjami sprzętowymi
- **System dynamicznego wykrywania CPU** - Automatyczne testowanie możliwości sprzętu i optymalizacja
- **Obsługa wielu platform**: Raspberry Pi 4/5, Linux x86_64, Termux Android
- **Podwójny interfejs**: Interaktywny GUI (Textual) i CLI (Typer)
- **Obsługa wielu języków**: Polski i angielski interfejs
- **Śledzenie postępu w czasie rzeczywistym** ze szczegółowym logowaniem
- **Konfiguracje sprzętowe**:
  - `dynamic` - Automatyczne wykrywanie i optymalizacja (zalecane)
  - `rpi5_8gb`, `rpi5_16gb`, `rpi5_4gb` - Warianty Raspberry Pi 5
  - `rpi4` - Optymalizacje Raspberry Pi 4
  - `x86_linux` - Nowoczesne x86_64 z obsługą AVX2
  - `x86_linux_old` - Starsze CPU x86_64 (2010-2013) z AVX ale bez AVX2
  - `x86_linux_minimal` - Bardzo stary sprzęt bez AVX
  - `termux` - Środowisko Android Termux
  - `no_optimization` - Maksymalna kompatybilność
- **Obsługa własnych konfiguracji** - Flagi CMAKE zdefiniowane przez użytkownika
- **Kompleksowe logowanie** ze śledzeniem postępu instalacji
- **Skrypty wrapper** dla łatwego uruchamiania llama.cpp


---

Dla angielskiej historii zmian, zobacz [CHANGELOG.md](CHANGELOG.md)