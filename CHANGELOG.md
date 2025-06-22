# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-06-22

### Initial Release
- **Automatic llama.cpp installer** with hardware-specific optimizations
- **Dynamic CPU detection system** - Automatic hardware capability testing and optimization
- **Multi-platform support**: Raspberry Pi 4/5, Linux x86_64, Termux Android
- **Dual interface**: Interactive GUI (Textual) and CLI (Typer)
- **Multi-language support**: Polish and English interface
- **Real-time progress tracking** with detailed logging
- **Hardware configurations**:
  - `dynamic` - Automatic detection and optimization (recommended)
  - `rpi5_8gb`, `rpi5_16gb`, `rpi5_4gb` - Raspberry Pi 5 variants
  - `rpi4` - Raspberry Pi 4 optimizations
  - `x86_linux` - Modern x86_64 with AVX2 support
  - `x86_linux_old` - Legacy x86_64 CPUs (2010-2013) with AVX but without AVX2
  - `x86_linux_minimal` - Very old hardware without AVX
  - `termux` - Android Termux environment
  - `no_optimization` - Maximum compatibility
- **Custom configuration support** - User-defined CMAKE flags
- **Comprehensive logging** with installation progress tracking
- **Wrapper scripts** for easy llama.cpp execution


---

For Polish changelog, see [CHANGELOG_PL.md](CHANGELOG_PL.md)