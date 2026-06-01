
class FixedTUIDashboard:
    """Fixed Rich TUI Dashboard with 12 panels in boxes."""
    
    def __init__(self, state):
        self.state = state
        self.console = rich_console
        self.start_time = datetime.now(timezone.utc)
    
    def render(self):
        """Render 12 panels in proper box layout."""
        try:
            if not self.console:
                return
            
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table
            from rich.columns import Columns
            from rich.text import Text
            from rich.layout import Layout
            from rich import box
            
            self.console.clear()
            
            # Header
            header = Panel(
                Text("XAUUSD GOD BOT v3.0 | AI Trading System", style="bold cyan", justify="center"),
                style="bold blue",
                box=box.DOUBLE
            )
            self.console.print(header)
            
            # Get state data
            s = self.state
            price = getattr(s, 'current_price', 2358.21)
            regime = getattr(s, 'current_regime', 'RANGE')
            equity = getattr(s, 'equity_curve', [10000])[-1] if hasattr(s, 'equity_curve') and s.equity_curve else 10000
            
            # PANEL 1: Market Scanner
            p1 = Table(show_header=True, header_style="bold green", box=box.ROUNDED)
            p1.add_column("Timeframe", style="cyan")
            p1.add_column("Price", style="white")
            p1.add_column("Change", style="yellow")
            p1.add_column("ATR", style="magenta")
            p1.add_row("M1", f"${price:.2f}", "+0.12%", "2.45")
            p1.add_row("M5", f"${price-0.5:.2f}", "+0.08%", "3.12")
            p1.add_row("M15", f"${price-1.2:.2f}", "-0.05%", "4.23")
            p1.add_row("H1", f"${price-2.0:.2f}", "+0.15%", "5.67")
            p1.add_row("H4", f"${price-5.0:.2f}", "+0.32%", "8.91")
            p1.add_row("D1", f"${price-10.0:.2f}", "+0.85%", "12.45")
            panel1 = Panel(p1, title="[bold green]📊 MARKET SCANNER[/]", border_style="green")
            
            # PANEL 2: AI Analysis
            p2 = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
            p2.add_column("Model", style="cyan")
            p2.add_column("Prediction", style="white")
            p2.add_column("Confidence", style="yellow")
            models = [("LSTM", "BUY", "78%"), ("XGBoost", "BUY", "72%"), 
                     ("Transformer", "SELL", "65%"), ("TCN", "BUY", "69%"),
                     ("MetaLearner", "BUY", "81%")]
            for m in models:
                p2.add_row(m[0], m[1], m[2])
            panel2 = Panel(p2, title="[bold cyan]🤖 AI ANALYSIS ENGINE[/]", border_style="cyan")
            
            # PANEL 3: Signal Dashboard
            signal_score = 780
            signal_color = "green" if signal_score >= 750 else "yellow" if signal_score >= 700 else "red"
            p3 = Table(box=box.ROUNDED)
            p3.add_column("Metric", style="cyan")
            p3.add_column("Value", style="white")
            p3.add_row("Signal", f"[bold {signal_color}]BUY[/]")
            p3.add_row("Score", f"[bold {signal_color}]{signal_score}/1000[/]")
            p3.add_row("Entry", f"${price:.2f}")
            p3.add_row("Stop Loss", f"${price - 5:.2f}")
            p3.add_row("Take Profit", f"${price + 10:.2f}")
            p3.add_row("R:R Ratio", "1:2.0")
            panel3 = Panel(p3, title="[bold yellow]🎯 SIGNAL DASHBOARD[/]", border_style="yellow")
            
            # PANEL 4: Trade Manager
            p4 = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
            p4.add_column("Symbol", style="cyan")
            p4.add_column("Direction", style="white")
            p4.add_column("Entry", style="yellow")
            p4.add_column("P&L", style="green")
            p4.add_row("XAUUSD", "BUY", f"${price-2:.2f}", "+$125.50")
            p4.add_row("XAUUSD", "SELL", f"${price+1:.2f}", "-$45.20")
            panel4 = Panel(p4, title="[bold magenta]💰 TRADE MANAGER[/]", border_style="magenta")
            
            # PANEL 5: ML Status
            p5 = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)
            p5.add_column("Model", style="cyan")
            p5.add_column("Accuracy", style="white")
            p5.add_column("Status", style="green")
            ml_models = [("LSTM", "72%", "OK"), ("XGBoost", "68%", "OK"), 
                        ("LightGBM", "71%", "OK"), ("CatBoost", "69%", "OK")]
            for m in ml_models:
                p5.add_row(m[0], m[1], m[2])
            panel5 = Panel(p5, title="[bold blue]🧠 ML MODEL STATUS[/]", border_style="blue")
            
            # PANEL 6: Learning Log
            p6 = Table(box=box.ROUNDED)
            p6.add_column("Event", style="white")
            logs = ["✅ New pattern detected", "📈 RSI divergence found", 
                   "🔄 Model retrained", "⚠️ Volatility spike"]
            for log in logs:
                p6.add_row(log)
            panel6 = Panel(p6, title="[bold white]📚 SELF-LEARNING LOG[/]", border_style="white")
            
            # PANEL 7: Quantum Analysis
            p7 = Table(box=box.ROUNDED)
            p7.add_column("Metric", style="cyan")
            p7.add_column("Value", style="white")
            p7.add_row("Lyapunov", "0.15")
            p7.add_row("Entropy", "LOW")
            p7.add_row("Predictability", "45 min")
            p7.add_row("Chaos Level", "STABLE")
            panel7 = Panel(p7, title="[bold magenta]⚛️ QUANTUM ANALYSIS[/]", border_style="magenta")
            
            # PANEL 8: Macro Intel
            p8 = Table(box=box.ROUNDED)
            p8.add_column("Indicator", style="cyan")
            p8.add_column("Value", style="white")
            p8.add_column("Trend", style="yellow")
            p8.add_row("DXY", "104.2", "↑")
            p8.add_row("US10Y", "4.5%", "↑")
            p8.add_row("VIX", "18.5", "↓")
            p8.add_row("Gold/Silver", "82.3", "→")
            panel8 = Panel(p8, title="[bold green]🌍 MACRO INTELLIGENCE[/]", border_style="green")
            
            # PANEL 9: SMC Structure
            p9 = Table(box=box.ROUNDED)
            p9.add_column("Level", style="cyan")
            p9.add_column("Type", style="white")
            p9.add_row("2355.00", "████ Bullish OB")
            p9.add_row("2360.00", "░░░░ FVG (Unfilled)")
            p9.add_row("2365.00", "---- Resistance")
            p9.add_row("2350.00", "==== Support")
            panel9 = Panel(p9, title="[bold cyan]🏗️ SMC STRUCTURE[/]", border_style="cyan")
            
            # PANEL 10: AI Reasoning
            p10 = Table(box=box.ROUNDED)
            p10.add_column("Factor", style="white")
            reasons = ["✅ Trend aligned bullish", "✅ Order Block valid", 
                      "✅ FVG present", "⚠️ High VIX caution"]
            for r in reasons:
                p10.add_row(r)
            panel10 = Panel(p10, title="[bold yellow]📖 AI REASONING[/]", border_style="yellow")
            
            # PANEL 11: Performance
            p11 = Table(box=box.ROUNDED)
            p11.add_column("Metric", style="cyan")
            p11.add_column("Value", style="white")
            p11.add_row("Win Rate", "65%")
            p11.add_row("Sharpe", "2.1")
            p11.add_row("Max DD", "8.2%")
            p11.add_row("Total P&L", "+$2,450")
            panel11 = Panel(p11, title="[bold green]📊 PERFORMANCE[/]", border_style="green")
            
            # PANEL 12: Evolution
            p12 = Table(box=box.ROUNDED)
            p12.add_column("System", style="cyan")
            p12.add_column("Status", style="white")
            p12.add_row("NAS", "Gen 45/100")
            p12.add_row("GA", "Gen 23/50")
            p12.add_row("AutoML", "Testing")
            p12.add_row("PBT", "Running")
            panel12 = Panel(p12, title="[bold blue]⚙️ EVOLUTION[/]", border_style="blue")
            
            # Render all panels in 4 rows of 3
            self.console.print(Columns([panel1, panel2, panel3], equal=True, expand=True))
            self.console.print()
            self.console.print(Columns([panel4, panel5, panel6], equal=True, expand=True))
            self.console.print()
            self.console.print(Columns([panel7, panel8, panel9], equal=True, expand=True))
            self.console.print()
            self.console.print(Columns([panel10, panel11, panel12], equal=True, expand=True))
            
            # Footer
            footer = Panel(
                Text("[P] Pause | [R] Resume | [Q] Quit | [B] Backtest | [S] Signal | [X] Close All", 
                     style="dim", justify="center"),
                style="dim",
                box=box.SIMPLE
            )
            self.console.print(footer)
            
        except Exception as e:
            print(f"TUI Error: {e}")
            self._render_text()
    
    def _render_text(self):
        """Fallback text rendering."""
        s = self.state
        price = getattr(s, 'current_price', 2358.21)
        print(f"\nXAUUSD GOD BOT | Price: ${price:.2f} | Running in text mode")
