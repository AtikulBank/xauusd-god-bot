#!/bin/bash

# ╔══════════════════════════════════════════════════════════════════╗
# ║   QUANTUM HFT BOT - ONE-CLICK INSTALLER                       ║
# ║   Clone থেকে সম্পূর্ণ Auto-Setup                              ║
# ╚══════════════════════════════════════════════════════════════════╝

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║   ██████╗ ██╗   ██╗ ██████╗ ███████╗███████╗               ║"
    echo "║   ██╔══██╗██║   ██║██╔═══██╗██╔════╝██╔════╝               ║"
    echo "║   ██████╔╝██║   ██║██║   ██║███████╗███████╗               ║"
    echo "║   ██╔═══╝ ██║   ██║██║   ██║╚════██║╚════██║               ║"
    echo "║   ██║     ╚██████╔╝╚██████╔╝███████║███████║               ║"
    echo "║   ╚═╝      ╚═════╝  ╚═════╝ ╚══════╝╚══════╝               ║"
    echo "║                                                              ║"
    echo "║   🤖 AUTONOMOUS AI TRADING SYSTEM                           ║"
    echo "║   95+ Mathematical Models + 28 ML Models                   ║"
    echo "║   Ultra-Low Latency Cython Execution                        ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "\n${GREEN}[$1/4]${NC} ${YELLOW}$2${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Main installation
main() {
    print_banner
    
    # Get current directory
    INSTALL_DIR="${1:-.}"
    
    echo -e "${CYAN}📁 Install Directory: ${INSTALL_DIR}${NC}\n"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 1: Check Python Version
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print_step 1 "Checking Python Version"
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 not found! Please install Python 3.10+"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo -e "   Python: ${GREEN}$PYTHON_VERSION${NC}"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 2: Install Python Packages
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print_step 2 "Installing Python Packages"
    
    # Core packages
    echo -e "   Installing core packages..."
    pip install --quiet --upgrade pip
    pip install --quiet numpy pandas scikit-learn scipy
    
    # ML packages
    echo -e "   Installing ML packages..."
    pip install --quiet xgboost lightgbm catboost
    
    # Deep Learning
    echo -e "   Installing PyTorch (CPU version)..."
    pip install --quiet torch torchvision --index-url https://download.pytorch.org/whl/cpu 2>/dev/null || \
        pip install --quiet torch torchvision
    
    # NLP
    echo -e "   Installing transformers..."
    pip install --quiet transformers
    
    # Compilation
    echo -e "   Installing build tools..."
    pip install --quiet cython setuptools wheel
    
    # UI
    echo -e "   Installing UI packages..."
    pip install --quiet rich textual
    
    # Utilities
    echo -e "   Installing utilities..."
    pip install --quiet requests beautifulsoup4 aiohttp pyyaml cryptography schedule psutil
    
    # Statistics
    echo -e "   Installing statistics packages..."
    pip install --quiet statsmodels arch numba
    
    print_success "All packages installed!"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 3: Compile Cython Extensions
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print_step 3 "Compiling Cython Extensions"
    
    if [ -d "${INSTALL_DIR}/compilation" ]; then
        cd "${INSTALL_DIR}/compilation"
        echo -e "   Building Cython modules..."
        python3 setup.py build_ext --inplace 2>/dev/null || \
            echo -e "   ${YELLOW}⚠ Cython compilation skipped (optional)${NC}"
        cd "${INSTALL_DIR}"
        print_success "Cython compilation complete!"
    else
        echo -e "   ${YELLOW}⚠ No compilation directory found, skipping${NC}"
    fi
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 4: Create Required Directories
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print_step 4 "Creating Required Directories"
    
    mkdir -p "${INSTALL_DIR}/data"
    mkdir -p "${INSTALL_DIR}/models"
    mkdir -p "${INSTALL_DIR}/logs"
    mkdir -p "${INSTALL_DIR}/backups"
    mkdir -p "${INSTALL_DIR}/reports"
    
    print_success "Directories created!"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # DONE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo -e "\n${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                              ║${NC}"
    echo -e "${GREEN}║   ✅ INSTALLATION COMPLETE!                                  ║${NC}"
    echo -e "${GREEN}║                                                              ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    
    echo -e "\n${CYAN}🚀 TO RUN THE BOT:${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "   cd ${INSTALL_DIR}"
    echo -e "   python3 xauusd_god_bot.py"
    echo ""
}

# Run main function
main "$@"
