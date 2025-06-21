# Llama.cpp Automated Installer

**English** | [Polski](README_PL.md)

Automatic installer for llama.cpp with hardware-specific optimizations. The project detects your hardware type (Raspberry Pi 5, Raspberry Pi 4, Termux Android, Linux x86_64) and automatically selects optimal compilation flags for maximum performance.

**Author:** Fibogacci (https://fibogacci.pl)  
**License:** MIT  
**Technologies:** Python, Textual (GUI), Typer (CLI), Rich, psutil

## Features

- 🔍 **Automatic hardware detection**: Raspberry Pi, Android Termux, Linux x86_64
- ⚡ **Optimized compilation**: Hardware-specific CMAKE flags for maximum performance  
- 🖥️ **Dual interface**: Interactive GUI (Textual) and CLI (Typer)
- 🌍 **Multi-language**: Polish and English interface
- 📊 **Real-time progress**: Installation progress with detailed logging
- 🛠️ **Custom configs**: Support for user-defined optimization files
- 🔄 **Dynamic detection**: Automatic CPU capability testing (NEW)

## Supported Hardware

### Raspberry Pi
- **Raspberry Pi 5 (8GB/16GB)** - Maximum ARM64 Cortex-A76 optimizations with OpenBLAS and RPC
- **Raspberry Pi 5 (4GB)** - Balanced ARM64 optimizations with OpenBLAS
- **Raspberry Pi 4** - Cortex-A72 optimizations with OpenBLAS

### Linux x86_64
- **Dynamic** ⭐ - Automatic detection and optimization (RECOMMENDED)
- **Standard** - Full AVX2 optimizations with OpenBLAS (newer CPUs)
- **Legacy** - AVX optimizations without AVX2 (2010-2013 CPUs)  
- **Minimal** - Basic optimizations (very old hardware)
- **No optimization** - Widest compatibility (works everywhere)

### Mobile
- **Termux Android** - Minimal optimizations without BLAS

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/fibogacci/llamacpp-installer.git
cd llamacpp-installer

# Install dependencies  
pip install -r requirements.txt
```

### Usage

#### GUI Interface (Recommended)
```bash
# Polish (default)
python main.py

# English
python main.py --lang en
```

#### CLI Interface

```bash
# Hardware detection
python cli.py detect
python cli.py detect --lang en

# Automatic installation (recommended)
python cli.py install --hardware dynamic --dir /path/to/install

# Manual hardware selection
python cli.py install --hardware rpi5_8gb --dir /home/user/llama
python cli.py install --hardware x86_linux --dir /opt/llama --lang en

# Custom configuration
python cli.py install --config example_configs/x86_avx512.txt --dir /path/to/install
```

## Hardware Types

| Hardware | Type | Description |
|----------|------|-------------|
| Raspberry Pi 5 8/16GB | `rpi5_8gb` | Maximum performance with RPC |
| Raspberry Pi 5 4GB | `rpi5_4gb` | Balanced optimization |  
| Raspberry Pi 4 | `rpi4` | Cortex-A72 optimized |
| Linux x86_64 Auto | `dynamic` | **Automatic detection** ⭐ |
| Linux x86_64 New | `x86_linux` | AVX2 + OpenBLAS |
| Linux x86_64 Legacy | `x86_linux_old` | AVX without AVX2 |
| Linux x86_64 Minimal | `x86_linux_minimal` | Basic optimizations |
| No optimization | `no_optimization` | Maximum compatibility |
| Termux Android | `termux` | Mobile-optimized |

## Custom Configurations

Create your own `.txt` files with CMAKE flags:

```cmake
# example_configs/my_config.txt
-DGGML_NATIVE=ON
-DGGML_AVX2=ON  
-DGGML_OPENMP=ON
-DGGML_OPENBLAS=ON
```

Usage:
```bash
python cli.py install --config my_config.txt --dir /path/to/install
```

## Directory Structure

After installation, the structure will be:
```
/your/chosen/path/
└── llama.cpp/
    ├── build/
    │   └── bin/
    │       ├── llama-cli
    │       ├── llama-server  
    │       └── ...
    ├── logs/
    │   └── llamacpp_installer_*.log
    ├── llama-cli.sh      # Wrapper script
    ├── llama-server.sh   # Wrapper script
    └── llama-simple.sh   # Wrapper script
```

## Language Support

### CLI
```bash
# Polish (default)
python cli.py detect
python cli.py install --hardware dynamic --dir /path

# English  
python cli.py detect --lang en
python cli.py install --hardware dynamic --dir /path --lang en
```

### GUI
```bash
# Polish (default)
python main.py

# English
python main.py --lang en
python main.py --en
```

### Environment Variable
```bash
export LLAMACPP_INSTALLER_LANG=en
python main.py  # Will use English
```

## Advanced Usage

### Debug Mode
```bash
# Enable detailed logging
python cli.py detect --debug
python cli.py install --hardware dynamic --dir /path --debug
```

### Testing Hardware Detection
```bash
# Test hardware detection
python hardware_detector.py

# Test dynamic CPU detection  
python dynamic_config.py

# Test optimization configs
python optimization_configs.py
```

## Troubleshooting

### Common Issues

1. **Compilation errors on older CPUs**
   - Use `--hardware x86_linux_old` or `--hardware dynamic`
   - Check logs in `{install_dir}/logs/`

2. **Missing dependencies**
   - Install build essentials: `sudo apt install build-essential cmake git`
   - For Ubuntu/Debian with OpenBLAS: `sudo apt install libopenblas-dev`

3. **Permission errors**  
   - Ensure write permissions to installation directory
   - Use `sudo` only if installing to system directories

4. **Termux specific issues**
   - Install required packages: `pkg install python cmake git`
   - Use `--hardware termux` for mobile optimization

### Log Files

Installation logs are saved in `{installation_directory}/logs/` with format:
`llamacpp_installer_YYYYMMDD_HHMMSS.log`

## Requirements

- Python 3.7+
- Build tools (gcc, cmake, git)
- Internet connection for downloading llama.cpp
- Sufficient disk space (2-3 GB for full compilation)

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test on different hardware if possible
5. Submit pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

**Fibogacci**
- Website: https://fibogacci.pl
- GitHub: https://github.com/fibogacci

---

For Polish documentation, see [README_PL.md](README_PL.md)