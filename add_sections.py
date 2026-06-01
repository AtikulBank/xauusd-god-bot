#!/usr/bin/env python3
"""Add all missing sections to xauusd_god_bot.py."""
import os

FILE = '/workspace/project/xauusd_god_bot.py'

def a(content):
    with open(FILE, 'a') as f:
        f.write(content)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 03 — FIRST-RUN SETUP WIZARD
# ═══════════════════════════════════════════════════════════════════════════════
a('''
# SECTION 03 - FIRST-RUN SETUP WIZARD

class SetupWizard:
    """Interactive first-run setup wizard for MT5 broker configuration."""

    MAJOR_BROKERS: List[Dict[str, str]] = [
        {"name": "IC Markets", "server": "ICMarketsSC-Demo", "country": "Australia"},
        {"name": "XM Global", "server": "XMGlobal-MT5", "country": "Cyprus"},
        {"name": "Exness", "server": "Exness-MT5Trial", "country": "Cyprus"},
        {"name": "FBS", "server": "FBS-Demo", "country": "Belize"},
        {"name": "RoboForex", "server": "RoboForex-MT5", "country": "Belize"},
        {"name": "Pepperstone", "server": "Pepperstone-MT5", "country": "Australia"},
        {"name": "FP Markets", "server": "FPMarkets-Demo", "country": "Australia"},
        {"name": "Tickmill", "server": "Tickmill-Demo", "country": "UK"},
        {"name": "AvaTrade", "server": "AvaTrade-Demo", "country": "Ireland"},
        {"name": "Plus500", "server": "Plus500-Demo", "country": "Israel"},
        {"name": "Oanda", "server": "Oanda-Demo", "country": "USA"},
        {"name": "FXCM", "server": "FXCM-Demo", "country": "UK"},
        {"name": "IG Markets", "server": "IG-Demo", "country": "UK"},
        {"name": "Saxo Bank", "server": "Saxo-Demo", "country": "Denmark"},
        {"name": "Interactive Brokers", "server": "IBKR-Demo", "country": "USA"},
        {"name": "Alpari", "server": "Alpari-MT5", "country": "Russia"},
        {"name": "JustMarkets", "server": "JustMarkets-Demo", "country": "Cyprus"},
        {"name": "HFM", "server": "HFMarkets-Demo", "country": "Cyprus"},
        {"name": "FXTM", "server": "FXTM-Demo", "country": "Cyprus"},
        {"name": "Forex.com", "server": "ForexDotCom-Demo", "country": "USA"},
        {"name": "CMC Markets", "server": "CMC-Demo", "country": "UK"},
        {"name": "City Index", "server": "CityIndex-Demo", "country": "UK"},
        {"name": "OANDA", "server": "OANDA-Demo", "country": "USA"},
        {"name": "Dukascopy", "server": "Dukascopy-Demo", "country": "Switzerland"},
        {"name": "Swissquote", "server": "Swissquote-Demo", "country": "Switzerland"},
        {"name": "LMAX Exchange", "server": "LMAX-Demo", "country": "UK"},
        {"name": "Gain Capital", "server": "GainCapital-Demo", "country": "USA"},
        {"name": "OANDA Europe", "server": "OANDA-EU-Demo", "country": "UK"},
        {"name": "Axiory", "server": "Axiory-Demo", "country": "Japan"},
        {"name": "ThinkMarkets", "server": "ThinkMarkets-Demo", "country": "Australia"},
        {"name": "Vantage FX", "server": "Vantage-Demo", "country": "Australia"},
        {"name": "GO Markets", "server": "GOMarkets-Demo", "country": "Australia"},
        {"name": "ACM Global", "server": "ACM-Demo", "country": "Switzerland"},
        {"name": "Tradeview", "server": "Tradeview-Demo", "country": "Cayman Islands"},
        {"name": "ForexTB", "server": "ForexTB-Demo", "country": "Cyprus"},
        {"name": "Admiral Markets", "server": "Admiral-MT5", "country": "Estonia"},
        {"name": "Fondex", "server": "Fondex-Demo", "country": "Cyprus"},
        {"name": "Titan FX", "server": "TitanFX-Demo", "country": "Vanuatu"},
        {"name": "IronFX", "server": "IronFX-Demo", "country": "Cyprus"},
        {"name": "Naga", "server": "Naga-Demo", "country": "Germany"},
        {"name": "EagleFX", "server": "EagleFX-Demo", "country": "Dominica"},
        {"name": "CryptoAltum", "server": "CryptoAltum-Demo", "country": "Vanuatu"},
        {"name": "LegacyFX", "server": "LegacyFX-Demo", "country": "Cyprus"},
        {"name": "Valutrades", "server": "Valutrades-Demo", "country": "UK"},
        {"name": "Errante", "server": "Errante-Demo", "country": "Cyprus"},
        {"name": "Trade Nation", "server": "TradeNation-Demo", "country": "UK"},
        {"name": "Global Prime", "server": "GlobalPrime-Demo", "country": "Australia"},
        {"name": "BlackBull", "server": "BlackBull-Demo", "country": "New Zealand"},
        {"name": "Eightcap", "server": "Eightcap-Demo", "country": "Australia"},
        {"name": "Moneta Markets", "server": "Moneta-Demo", "country": "Cyprus"},
    ]

    def __init__(self, config: Config) -> None:
        self.config = config
        self._mt5 = _safe_import("MetaTrader5")

    def run(self) -> Config:
        """Run the complete setup wizard.
        
        Returns:
            Updated Config with user-provided settings
        """
        try:
            self._print_welcome()
            self._select_broker()
            self._enter_account()
            self._enter_password()
            self._test_connection()
            self._configure_notifications()
            self._configure_risk()
            self._run_benchmark()
            self.config.wizard_complete = True
            self.config.save()
            print("\\n[SETUP] Configuration saved successfully!")
            return self.config
        except KeyboardInterrupt:
            print("\\n[SETUP] Wizard cancelled. Using defaults.")
            return self.config
        except Exception as e:
            logger.error(f"Setup wizard failed: {e}")
            return self.config

    def _print_welcome(self) -> None:
        """Print welcome banner."""
        try:
            print("""
╔══════════════════════════════════════════════════════════════════╗
║           XAUUSD GOD BOT - FIRST TIME SETUP WIZARD             ║
║                                                                  ║
║  Welcome! This wizard will configure your trading bot.          ║
║  Follow the prompts to set up your MT5 broker connection.       ║
║                                                                  ║
║  You can re-run this wizard anytime by deleting config.yaml     ║
╚══════════════════════════════════════════════════════════════════╝
""")
        except Exception as e:
            logger.error(f"_print_welcome failed: {e}")

    def _select_broker(self) -> None:
        """Prompt user to select broker from list."""
        try:
            print("\\n[SETUP] Select your MT5 broker:")
            print("-" * 60)
            for i, broker in enumerate(self.MAJOR_BROKERS, 1):
                print(f"  {i:2d}. {broker['name']:<25} ({broker['country']})")
            print(f"  {len(self.MAJOR_BROKERS) + 1:2d}. Custom (enter manually)")
            print("-" * 60)

            while True:
                try:
                    choice = input("\\nEnter broker number (1-51): ").strip()
                    idx = int(choice) - 1
                    if 0 <= idx < len(self.MAJOR_BROKERS):
                        broker = self.MAJOR_BROKERS[idx]
                        self.config.mt5_server = broker["server"]
                        print(f"[SETUP] Selected: {broker['name']} ({broker['server']})")
                        break
                    elif idx == len(self.MAJOR_BROKERS):
                        server = input("Enter MT5 server name: ").strip()
                        if server:
                            self.config.mt5_server = server
                            break
                    else:
                        print("Invalid selection. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
        except Exception as e:
            logger.error(f"_select_broker failed: {e}")

    def _enter_account(self) -> None:
        """Prompt for MT5 account number."""
        try:
            while True:
                try:
                    account = input("\\nEnter MT5 account number: ").strip()
                    if account.isdigit() and len(account) >= 6:
                        self.config.mt5_account = int(account)
                        break
                    else:
                        print("Invalid account number. Must be at least 6 digits.")
                except ValueError:
                    print("Please enter a valid number.")
        except Exception as e:
            logger.error(f"_enter_account failed: {e}")

    def _enter_password(self) -> None:
        """Prompt for MT5 password (masked)."""
        try:
            import getpass
            password = getpass.getpass("\\nEnter MT5 password: ")
            if password:
                self.config.mt5_password = password
            else:
                print("[SETUP] Warning: No password entered. Trading will use simulated mode.")
        except Exception as e:
            logger.error(f"_enter_password failed: {e}")

    def _test_connection(self) -> None:
        """Test MT5 connection with provided credentials."""
        try:
            print("\\n[SETUP] Testing MT5 connection...")
            if self._mt5:
                try:
                    result = self._mt5.initialize(
                        login=self.config.mt5_account,
                        password=self.config.mt5_password,
                        server=self.config.mt5_server
                    )
                    if result:
                        info = self._mt5.account_info()
                        if info:
                            print(f"[SETUP] Connected! Balance: ${info.balance:.2f}, Server: {info.server}")
                            self._mt5.shutdown()
                            return
                except Exception as e:
                    print(f"[SETUP] Connection test failed: {e}")
            
            print("[SETUP] MT5 not available. Using simulated mode.")
            print("[SETUP] The bot will use simulated trading for testing.")
        except Exception as e:
            logger.error(f"_test_connection failed: {e}")

    def _configure_notifications(self) -> None:
        """Configure Telegram/Discord notifications."""
        try:
            print("\\n[SETUP] Configure notifications (optional):")
            telegram = input("  Telegram bot token (or press Enter to skip): ").strip()
            if telegram:
                self.config.telegram_bot_token = telegram
                chat_id = input("  Telegram chat ID: ").strip()
                if chat_id:
                    self.config.telegram_chat_id = chat_id

            discord = input("  Discord webhook URL (or press Enter to skip): ").strip()
            if discord:
                self.config.discord_webhook_url = discord
        except Exception as e:
            logger.error(f"_configure_notifications failed: {e}")

    def _configure_risk(self) -> None:
        """Configure risk tolerance."""
        try:
            print("\\n[SETUP] Select risk tolerance:")
            print("  1. Conservative (1% risk per trade)")
            print("  2. Moderate (2% risk per trade)")
            print("  3. Aggressive (5% risk per trade)")

            choice = input("  Enter choice (1-3, default=1): ").strip() or "1"
            risk_map = {"1": 0.01, "2": 0.02, "3": 0.05}
            self.config.max_risk_per_trade = risk_map.get(choice, 0.01)
            print(f"[SETUP] Risk per trade: {self.config.max_risk_per_trade:.1%}")
        except Exception as e:
            logger.error(f"_configure_risk failed: {e}")

    def _run_benchmark(self) -> None:
        """Run quick system benchmark."""
        try:
            print("\\n[SETUP] Running system benchmark...")
            start = time.time()
            
            # CPU benchmark
            n = 1000000
            arr = np.random.randn(n)
            _ = np.mean(arr)
            cpu_time = time.time() - start
            
            # Memory check
            try:
                import psutil as psutil_mod
                ram = psutil_mod.virtual_memory()
                print(f"[SETUP] CPU benchmark: {cpu_time:.3f}s ({n:,} ops)")
                print(f"[SETUP] RAM: {ram.total / (1024**3):.1f} GB ({ram.percent:.0f}% used)")
            except Exception:
                print(f"[SETUP] CPU benchmark: {cpu_time:.3f}s")
            
            print("[SETUP] Benchmark complete!")
        except Exception as e:
            logger.error(f"_run_benchmark failed: {e}")

    def __repr__(self) -> str:
        return f"SetupWizard(wizard_complete={self.config.wizard_complete})"
''')

print(f"After Section 03: {len(open(FILE).readlines())} lines")
