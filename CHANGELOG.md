# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-06-21

### Added
- **Dynamic CPU detection system** - Automatic hardware capability testing and optimization
- New hardware configurations for x86_64 systems:
  - `x86_linux_old` - For 2010-2013 CPUs with AVX but without AVX2
  - `x86_linux_minimal` - For very old hardware without AVX
  - Enhanced `no_optimization` configuration
- Comprehensive CPU instruction set detection (/proc/cpuinfo parsing)
- Real compilation testing for CMAKE flags validation
- System library availability checking (CURL, OpenBLAS, OpenMP)
- Enhanced error handling for compilation failures

### Fixed
- **GUI timer crash bug** - Fixed AttributeError in installation progress timer
- **Directory structure issues** - Resolved double nesting in llama.cpp installation paths
- **Wrapper script paths** - Fixed incorrect paths in llama-cli.sh, llama-server.sh, llama-simple.sh
- **OpenBLAS64 compilation errors** - Removed problematic BLAS_VENDOR flags
- Improved CMAKE flag compatibility for older x86_64 processors
- Better error messages for unsupported hardware configurations

### Changed
- Installation directory structure now correctly creates `/base_dir/llama.cpp/` without nesting
- CMAKE compilation process uses absolute paths instead of relative paths
- Wrapper scripts now use relative paths from script location
- Enhanced logging system with better error context
- Improved hardware detection accuracy for edge cases

### Security
- Added input validation for directory names and paths
- Enhanced error handling to prevent potential crashes

## [1.2.0] - 2025-06-20

### Added
- Advanced file browser with directory creation capability
- Responsive GUI design with automatic compact mode detection
- Comprehensive keyboard shortcuts (F1, Ctrl+H for help panel)
- Real-time installation progress tracking with elapsed time
- Enhanced error reporting and user feedback
- Multi-language support system (Polish/English)

### Fixed
- Installation path handling and validation
- GUI responsiveness on different screen sizes
- File system navigation and directory creation

### Changed
- Improved user interface with better visual feedback
- Enhanced installation process with progress indicators
- Better error handling and recovery mechanisms

## [1.1.0] - 2025-06-15

### Added
- CLI interface with Typer framework
- Hardware detection system for multiple platforms
- Optimization configurations for different hardware types
- Logging system with file rotation
- Custom configuration file support
- Wrapper scripts for easy llama.cpp execution

### Fixed
- Hardware detection accuracy
- Compilation flag optimization for different CPU architectures
- Installation directory handling

## [1.0.0] - 2025-06-10

### Added
- Initial release of llama.cpp automated installer
- Basic GUI interface using Textual framework
- Support for Raspberry Pi 4, Raspberry Pi 5, and Linux x86_64
- Automatic hardware detection and optimization
- Real-time installation progress display
- Multi-language support (Polish/English)

### Hardware Support
- Raspberry Pi 5 (8GB/16GB) with maximum optimizations
- Raspberry Pi 5 (4GB) with balanced optimizations
- Raspberry Pi 4 with Cortex-A72 optimizations
- Linux x86_64 with AVX/AVX2 support
- Termux Android with minimal optimizations

### Features
- Interactive GUI with file browser
- Automatic dependency installation
- CMAKE optimization flag selection
- Installation logging and debugging
- Custom configuration support

---

For Polish changelog, see [CHANGELOG_PL.md](CHANGELOG_PL.md)