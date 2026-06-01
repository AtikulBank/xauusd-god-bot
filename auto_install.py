"""
auto_install.py - Automatic Dependency Installer

This script automatically installs all required packages for the trading bot.
Run this first before starting the bot.
"""

import subprocess
import sys
import importlib
import os
from typing import List, Tuple, Optional

# ============================================================================
# Color Codes for Terminal Output
# ============================================================================

class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    """Print installation banner."""
    print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   █████╗ ██╗   ██╗████████╗ ██████╗       ██╗   ██╗ ██████╗ ██╗██████╗     ║
║  ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗      ██║   ██║██╔═══██╗██║██╔══██╗    ║
║  ███████║██║   ██║   ██║   ██║   ██║█████╗██║   ██║██║   ██║██║██║  ██║    ║
║  ██╔══██║██║   ██║   ██║   ██║   ██║╚════╝╚██╗ ██╔╝██║   ██║██║██║  ██║    ║
║  ██║  ██║╚██████╔╝   ██║   ╚██████╔╝       ╚████╔╝ ╚██████╔╝██║██████╔╝    ║
║  ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝         ╚═══╝   ╚═════╝ ╚═╝╚═════╝     ║
║                                                                              ║
║                    AUTO-INSTALLER - সব কিছু নিজেই install করবে               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}
""")

def check_python_version() -> bool:
    """Check if Python version is 3.10+."""
    print(f"{Colors.BLUE} checking Python version...{Colors.END}")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"{Colors.RED}✗ Python 3.10+ required (current: {version.major}.{version.minor}){Colors.END}")
        return False
    
    print(f"{Colors.GREEN}✓ Python {version.major}.{version.minor}.{version.micro}{Colors.END}")
    return True

def check_package(package_name: str) -> bool:
    """Check if a package is installed."""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name: str, pip_name: Optional[str] = None) -> bool:
    """Install a package using pip."""
    if pip_name is None:
        pip_name = package_name
    
    print(f"{Colors.YELLOW}  Installing {pip_name}...{Colors.END}")
    
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", pip_name, "--quiet", "--disable-pip-version-check"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"{Colors.GREEN}  ✓ {pip_name} installed successfully{Colors.END}")
        return True
    except subprocess.CalledProcessError:
        print(f"{Colors.RED}  ✗ Failed to install {pip_name}{Colors.END}")
        return False

def get_required_packages() -> List[Tuple[str, Optional[str], bool]]:
    """
    Get list of required packages.
    Returns: [(import_name, pip_name, is_required), ...]
    """
    return [
        # Core packages (required)
        ("numpy", "numpy", True),
        ("scipy", "scipy", True),
        
        # Data handling
        ("pandas", "pandas", False),
        ("sklearn", "scikit-learn", False),
        
        # Visualization
        ("matplotlib", "matplotlib", False),
        
        # Machine Learning
        ("xgboost", "xgboost", False),
        ("lightgbm", "lightgbm", False),
        
        # Deep Learning (optional)
        ("torch", "torch", False),
        
        # Technical Analysis
        ("ta", "ta", False),
        
        # Utilities
        ("yaml", "pyyaml", False),
        ("requests", "requests", False),
    ]

def get_optional_packages() -> List[Tuple[str, Optional[str]]]:
    """Get list of optional advanced packages."""
    return [
        ("catboost", "catboost"),
        ("tensorflow", "tensorflow"),
        ("keras", "keras"),
        ("optuna", "optuna"),
        ("shap", "shap"),
    ]

def install_all_packages():
    """Install all required and optional packages."""
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}  STEP 1: CORE PACKAGES ইনস্টল করছে...{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
    
    required = get_required_packages()
    success_count = 0
    fail_count = 0
    
    for import_name, pip_name, is_required in required:
        if check_package(import_name):
            print(f"{Colors.GREEN}  ✓ {pip_name} already installed{Colors.END}")
            success_count += 1
        else:
            if install_package(import_name, pip_name):
                success_count += 1
            else:
                fail_count += 1
                if is_required:
                    print(f"{Colors.RED}  ⚠ {pip_name} is REQUIRED but failed to install!{Colors.END}")
    
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}  STEP 2: OPTIONAL PACKAGES ইনস্টল করছে...{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
    
    optional = get_optional_packages()
    
    for import_name, pip_name in optional:
        if check_package(import_name):
            print(f"{Colors.GREEN}  ✓ {pip_name} already installed{Colors.END}")
            success_count += 1
        else:
            print(f"{Colors.YELLOW}  → Installing {pip_name} (optional)...{Colors.END}")
            if install_package(import_name, pip_name):
                success_count += 1
            else:
                print(f"{Colors.YELLOW}  ⚠ {pip_name} skipped (optional){Colors.END}")
                fail_count += 1
    
    return success_count, fail_count

def create_directories():
    """Create required directories."""
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}  STEP 3: DIRECTORIES তৈরি করছে...{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
    
    directories = [
        "data",
        "data/models",
        "data/logs",
        "data/reports",
        "data/cache",
        "super_intelligence",
        "engines",
        "risk",
        "core",
        "core/ull",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"{Colors.GREEN}  ✓ {directory}/{Colors.END}")

def verify_installation():
    """Verify all installations."""
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}  STEP 4: ইনস্টলেশন ভেরিফাই করছে...{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
    
    checks = [
        ("numpy", "NumPy"),
        ("scipy", "SciPy"),
        ("pandas", "Pandas"),
        ("sklearn", "Scikit-learn"),
        ("matplotlib", "Matplotlib"),
    ]
    
    all_ok = True
    
    for module_name, display_name in checks:
        if check_package(module_name):
            try:
                mod = importlib.import_module(module_name)
                version = getattr(mod, '__version__', 'unknown')
                print(f"{Colors.GREEN}  ✓ {display_name} {version}{Colors.END}")
            except Exception:
                print(f"{Colors.YELLOW}  ⚠ {display_name} installed but version unknown{Colors.END}")
        else:
            print(f"{Colors.RED}  ✗ {display_name} NOT installed{Colors.END}")
            all_ok = False
    
    return all_ok

def run_quick_test():
    """Run a quick test of the bot."""
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}  STEP 5: দ্রুত টেস্ট চালাচ্ছে...{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
    
    test_code = '''
import sys
sys.path.insert(0, '.')

try:
    from bot import QuantumTradingBot
    print("  ✓ Bot import: OK")
    
    from super_intelligence.integration import create_super_intelligence
    print("  ✓ Super-Intelligence: OK")
    
    from core.ull.bitmask_trader import create_trader
    trader = create_trader(10000.0)
    print(f"  ✓ Trader created: OK (Balance: ${trader.balance:.2f})")
    
    print("\\n" + "="*60)
    print("  ALL TESTS PASSED!")
    print("="*60)
    
except Exception as e:
    print(f"  ✗ Test failed: {e}")
'''
    
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    print(result.stdout)
    if result.stderr:
        print(f"{Colors.YELLOW}  Warnings: {result.stderr[:200]}...{Colors.END}")
    
    return result.returncode == 0

def main():
    """Main installation function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        print(f"\n{Colors.RED}Please install Python 3.10+ first!{Colors.END}")
        print(f"{Colors.YELLOW}Download: https://www.python.org/downloads/{Colors.END}")
        return False
    
    # Install packages
    success, fail = install_all_packages()
    
    # Create directories
    create_directories()
    
    # Verify installation
    all_ok = verify_installation()
    
    # Run quick test
    test_ok = run_quick_test()
    
    # Final summary
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}  ইনস্টলেশন সমাপ্ত!{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}")
    
    if all_ok and test_ok:
        print(f"""
{Colors.GREEN}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                        ✅ সব কিছু সফলভাবে ইনস্টল হয়েছে!                     ║
║                                                                              ║
║   Bot চালু করতে এই কমান্ড চালান:                                            ║
║                                                                              ║
║                        python3 bot.py                                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}""")
        return True
    else:
        print(f"""
{Colors.YELLOW}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                        ⚠️  কিছু packages install হয়নি                        ║
║                                                                              ║
║   Bot তবুও চালানো যাবে (basic features সহ)                                   ║
║                                                                              ║
║                        python3 bot.py                                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}""")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
