# Historia zmian

Wszystkie istotne zmiany w tym projekcie będą dokumentowane w tym pliku.

Format oparty jest na [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
a projekt przestrzega [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-06-21

### Dodano
- **System dynamicznego wykrywania CPU** - Automatyczne testowanie możliwości sprzętu i optymalizacja
- Nowe konfiguracje sprzętowe dla systemów x86_64:
  - `x86_linux_old` - Dla CPU 2010-2013 z AVX ale bez AVX2
  - `x86_linux_minimal` - Dla bardzo starego sprzętu bez AVX
  - Ulepszona konfiguracja `no_optimization`
- Kompleksowe wykrywanie zestawu instrukcji CPU (parsowanie /proc/cpuinfo)
- Rzeczywiste testowanie kompilacji dla walidacji flag CMAKE
- Sprawdzanie dostępności bibliotek systemowych (CURL, OpenBLAS, OpenMP)
- Ulepszona obsługa błędów kompilacji

### Naprawiono
- **Błąd awarii timera GUI** - Naprawiono AttributeError w timerze postępu instalacji
- **Problemy ze strukturą katalogów** - Rozwiązano podwójne zagnieżdżenia w ścieżkach instalacji llama.cpp
- **Ścieżki skryptów wrapper** - Naprawiono nieprawidłowe ścieżki w llama-cli.sh, llama-server.sh, llama-simple.sh
- **Błędy kompilacji OpenBLAS64** - Usunięto problematyczne flagi BLAS_VENDOR
- Poprawiona kompatybilność flag CMAKE dla starszych procesorów x86_64
- Lepsze komunikaty błędów dla nieobsługiwanych konfiguracji sprzętowych

### Zmieniono
- Struktura katalogów instalacji teraz poprawnie tworzy `/katalog_bazowy/llama.cpp/` bez zagnieżdżania
- Proces kompilacji CMAKE używa ścieżek bezwzględnych zamiast względnych
- Skrypty wrapper używają teraz ścieżek względnych od lokalizacji skryptu
- Ulepszony system logowania z lepszym kontekstem błędów
- Poprawiona dokładność wykrywania sprzętu dla przypadków granicznych

### Bezpieczeństwo
- Dodano walidację wejścia dla nazw katalogów i ścieżek
- Ulepszona obsługa błędów zapobiegająca potencjalnym awariom

## [1.2.0] - 2025-06-20

### Dodano
- Zaawansowany przeglądark plików z możliwością tworzenia katalogów
- Responsywny projekt GUI z automatycznym wykrywaniem trybu kompaktowego
- Kompleksowe skróty klawiszowe (F1, Ctrl+H dla panelu pomocy)
- Śledzenie postępu instalacji w czasie rzeczywistym z czasem pozostałym
- Ulepszone raportowanie błędów i informacje zwrotne dla użytkownika
- System obsługi wielu języków (polski/angielski)

### Naprawiono
- Obsługa ścieżek instalacji i walidacja
- Responsywność GUI na różnych rozmiarach ekranu
- Nawigacja systemu plików i tworzenie katalogów

### Zmieniono
- Ulepszony interfejs użytkownika z lepszą informacją zwrotną wizualną
- Wzmocniony proces instalacji ze wskaźnikami postępu
- Lepsza obsługa błędów i mechanizmy odzyskiwania

## [1.1.0] - 2025-06-15

### Dodano
- Interfejs CLI z frameworkiem Typer
- System wykrywania sprzętu dla wielu platform
- Konfiguracje optymalizacji dla różnych typów sprzętu
- System logowania z rotacją plików
- Obsługa niestandardowych plików konfiguracyjnych
- Skrypty wrapper dla łatwego uruchamiania llama.cpp

### Naprawiono
- Dokładność wykrywania sprzętu
- Optymalizacja flag kompilacji dla różnych architektur CPU
- Obsługa katalogów instalacji

## [1.0.0] - 2025-06-10

### Dodano
- Pierwsza wersja automatycznego instalatora llama.cpp
- Podstawowy interfejs GUI używający frameworka Textual
- Obsługa Raspberry Pi 4, Raspberry Pi 5 i Linux x86_64
- Automatyczne wykrywanie sprzętu i optymalizacja  
- Wyświetlanie postępu instalacji w czasie rzeczywistym
- Obsługa wielu języków (polski/angielski)

### Obsługa sprzętu
- Raspberry Pi 5 (8GB/16GB) z maksymalnymi optymalizacjami
- Raspberry Pi 5 (4GB) ze zrównoważonymi optymalizacjami
- Raspberry Pi 4 z optymalizacjami Cortex-A72
- Linux x86_64 z obsługą AVX/AVX2
- Termux Android z minimalnymi optymalizacjami

### Funkcje
- Interaktywny GUI z przeglądarką plików
- Automatyczna instalacja zależności
- Wybór flag optymalizacji CMAKE
- Logowanie i debugowanie instalacji
- Obsługa niestandardowych konfiguracji

---

Dla angielskiej historii zmian, zobacz [CHANGELOG.md](CHANGELOG.md)