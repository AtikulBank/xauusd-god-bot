"""
install_and_run.py - Auto-Install & Run Bot

This script automatically installs all dependencies and runs the bot.
Just run: python3 install_and_run.py
"""

import subprocess
import sys
import os
import importlib

# ============================================================================
# Auto-Installer
# ============================================================================

def auto_install():
    """Automatically install all required packages."""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🔧 AUTO-INSTALLER - সব কিছু নিজেই install করবে            ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    packages = [
        "numpy",
        "scipy",
        "pandas",
        "scikit-learn",
        "matplotlib",
    ]
    
    installed = 0
    skipped = 0
    failed = 0
    
    for package in packages:
        # Check if already installed
        try:
            importlib.import_module(package)
            print(f"  ✓ {package} - ইতিমধ্যে ইনস্টল আছে")
            skipped += 1
            continue
        except ImportError:
            pass
        
        # Install package
        print(f"  → {package} ইনস্টল করছে...", end=" ")
        
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package, "-q"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("✓ সফল!")
            installed += 1
        except subprocess.CalledProcessError:
            print("✗ ব্যর্থ")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"  ইনস্টল সমাপ্ত: {installed} নতুন, {skipped} আগে থেকে, {failed} ব্যর্থ")
    print(f"{'='*60}\n")
    
    return failed == 0

# ============================================================================
# Bot Runner
# ============================================================================

def run_bot():
    """Run the trading bot."""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 TRADING BOT চালু করছে...                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from bot import QuantumTradingBot
        import asyncio
        
        async def main():
            bot = QuantumTradingBot(initial_balance=10000.0)
            report = await bot.run(duration=60.0)
            return report
        
        report = asyncio.run(main())
        
        print("\n" + "="*60)
        print("  PERFORMANCE REPORT")
        print("="*60)
        for key, value in report.items():
            if isinstance(value, float):
                print(f"  {key:.<30} {value:>10.4f}")
            else:
                print(f"  {key:.<30} {str(value):>10}")
        
        return True
        
    except Exception as e:
        print(f"\n  ✗ Bot error: {e}")
        return False

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  QUANTUM TRADING BOT - AUTO INSTALL & RUN")
    print("="*60 + "\n")
    
    # Step 1: Auto-install
    print("  STEP 1: Dependencies ইনস্টল করছে...")
    print("-"*60)
    
    if auto_install():
        print("\n  STEP 2: Bot চালু করছে...")
        print("-"*60)
        run_bot()
    else:
        print("\n  ⚠️  কিছু packages install হয়নি")
        print("  Bot তবুও চেষ্টা করা হচ্ছে...")
        run_bot()
