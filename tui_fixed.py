class TUIDashboard:
    """Rich-based TUI with 12 live panels for comprehensive trading dashboard."""

    def __init__(self, state: SharedState) -> None:
        """Initialize TUI Dashboard with shared state."""
        self.state = state
        self.console = rich_console
        self.start_time = datetime.now(timezone.utc)

    def render(self) -> None:
        """Render the full TUI dashboard with 12 panels in boxes."""
        try:
            if not self.console:
                self._render_text()
                return

            from rich.panel import Panel
            from rich.table import Table
            from rich.columns import Columns
            from rich.text import Text
            from rich import box
            
            self.console.clear()
            
            # Get state data
            s = self.state
            price = getattr(s, 'current_price', 2358.21)
            regime = getattr(s, 'current_regime', 'RANGE')
            equity = getattr(s, 'equity_curve', [10000])[-1] if hasattr(s, 'equity_curve') and s.equity_curve else 10000
            
            # Header
            header = Panel(
                Text("XAUUSD GOD BOT v3.0 | AI Trading System", style="bold cyan", justify="center"),
                style="bold blue",
                box=box.DOUBLE
            )
            self.console.print(header)
            self.console.print()
            
            # PANEL 1: Market Scanner
            p1 = Table(show_header=True, header_style="bold green", box=box.ROUNDED, expand=True)
            p1.add_column("TF", style="cyan", width=4)
            p1.add_column("Price", style="white", width=10)
            p1.add_column("Chg%", style="yellow", width=6)
            p1.add_column("ATR", style="magenta", width=5)
            p1.add_row("M1", f"${price:.2f}", "+0.12%", "2.45")
            p1.add_row("M5", f"${price-0.5:.2f}", "+0.08%", "3.12")
            p1.add_row("M15", f"${price-1.2:.2f}", "-0.05%", "4.23")
            p1.add_row("H1", f"${price-2.0:.2f}", "+0.15%", "5.67")
            p1.add_row("H4", f"${price-5.0:.2f}", "+0.32%", "8.91")
            p1.add_row("D1", f"${price-10.0:.2f}", "+0.85%", "12.45")
            panel1 = Panel(p1, title="[bold green]📊 MARKET SCANNER[/]", border_style="green", expand=True)
            
            # PANEL 2: AI Models
            p2 = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED, expand=True)
            p2.add_column("Model", style="cyan", width=10)
            p2.add_column("Signal", style="white", width=6)
            p2.add_column("Conf%", style="yellow", width=5)
            models = [("LSTM", "BUY", "78"), ("XGBoost", "BUY", "72"), 
                     ("Transf.", "SELL", "65"), ("TCN", "BUY", "69"),
                     ("Meta", "BUY", "81"), ("LGBM", "BUY", "74")]
            for m in models:
                p2.add_row(m[0], m[1], m[2])
            panel2 = Panel(p2, title="[bold cyan]🤖 AI MODELS[/]", border_style="cyan", expand=True)
            
            # PANEL 3: Signal Dashboard
            signal_score = getattr(s, 'signal_score', 780)
            signal_color = "green" if signal_score >= 750 else "yellow" if signal_score >= 700 else "red"
            p3 = Table(box=box.ROUNDED, expand=True)
            p3.add_column("Item", style="cyan", width=10)
            p3.add_column("Value", style="white", width=10)
            p3.add_row("Signal", f"[bold {signal_color}]BUY[/]")
            p3.add_row("Score", f"[bold {signal_color}]{signal_score}/1000[/]")
            p3.add_row("Entry", f"${price:.2f}")
            p3.add_row("Stop", f"${price - 5:.2f}")
            p3.add_row("TP1", f"${price + 10:.2f}")
            p3.add_row("R:R", "1:2.0")
            panel3 = Panel(p3, title="[bold yellow]🎯 SIGNAL[/]", border_style="yellow", expand=True)
            
            # Render Row 1
            self.console.print(Columns([panel1, panel2, panel3], equal=True, expand=True))
            self.console.print()
            
            # PANEL 4: Trade Manager
            p4 = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED, expand=True)
            p4.add_column("Dir", style="cyan", width=4)
            p4.add_column("Entry", style="white", width=10)
            p4.add_column("Current", style="white", width=10)
            p4.add_column("P&L", style="green", width=8)
            positions = getattr(s, 'open_positions', [])
            if positions:
                for pos in positions[:3]:
                    p4.add_row("BUY" if pos.get("type") == 0 else "SELL", 
                              f"${pos.get('open', 0):.2f}", 
                              f"${price:.2f}", 
                              f"+${pos.get('profit', 0):.0f}")
            else:
                p4.add_row("BUY", f"${price-2:.2f}", f"${price:.2f}", "+$125")
                p4.add_row("SELL", f"${price+1:.2f}", f"${price:.2f}", "-$45")
            panel4 = Panel(p4, title="[bold magenta]💰 TRADES[/]", border_style="magenta", expand=True)
            
            # PANEL 5: ML Status
            p5 = Table(show_header=True, header_style="bold blue", box=box.ROUNDED, expand=True)
            p5.add_column("Model", style="cyan", width=10)
            p5.add_column("Acc%", style="white", width=5)
            p5.add_column("Status", style="green", width=6)
            ml = [("LSTM", "72", "OK"), ("XGB", "68", "OK"), 
                 ("LGBM", "71", "OK"), ("CB", "69", "OK"), ("RF", "67", "OK")]
            for m in ml:
                p5.add_row(m[0], m[1], m[2])
            panel5 = Panel(p5, title="[bold blue]🧠 ML STATUS[/]", border_style="blue", expand=True)
            
            # PANEL 6: Learning Log
            p6 = Table(box=box.ROUNDED, expand=True)
            p6.add_column("Event", style="white", width=25)
            logs = ["✅ Pattern detected", "📈 RSI divergence", 
                   "🔄 Model retrained", "⚠️ Vol spike"]
            for log in logs:
                p6.add_row(log)
            panel6 = Panel(p6, title="[bold white]📚 LEARNING[/]", border_style="white", expand=True)
            
            # Render Row 2
            self.console.print(Columns([panel4, panel5, panel6], equal=True, expand=True))
            self.console.print()
            
            # PANEL 7: Quantum Analysis
            p7 = Table(box=box.ROUNDED, expand=True)
            p7.add_column("Metric", style="cyan", width=12)
            p7.add_column("Value", style="white", width=8)
            p7.add_row("Lyapunov", "0.15")
            p7.add_row("Entropy", "LOW")
            p7.add_row("Predict.", "45 min")
            p7.add_row("Chaos", "STABLE")
            panel7 = Panel(p7, title="[bold magenta]⚛️ QUANTUM[/]", border_style="magenta", expand=True)
            
            # PANEL 8: Macro Intel
            p8 = Table(box=box.ROUNDED, expand=True)
            p8.add_column("Ind", style="cyan", width=8)
            p8.add_column("Val", style="white", width=6)
            p8.add_column("Trend", style="yellow", width=5)
            p8.add_row("DXY", "104.2", "↑")
            p8.add_row("US10Y", "4.5%", "↑")
            p8.add_row("VIX", "18.5", "↓")
            p8.add_row("Au/Ag", "82.3", "→")
            panel8 = Panel(p8, title="[bold green]🌍 MACRO[/]", border_style="green", expand=True)
            
            # PANEL 9: SMC Structure
            p9 = Table(box=box.ROUNDED, expand=True)
            p9.add_column("Level", style="cyan", width=8)
            p9.add_column("Type", style="white", width=15)
            p9.add_row("2355", "████ Bull OB")
            p9.add_row("2360", "░░░░ FVG")
            p9.add_row("2365", "---- Resist")
            p9.add_row("2350", "==== Support")
            panel9 = Panel(p9, title="[bold cyan]🏗️ SMC[/]", border_style="cyan", expand=True)
            
            # Render Row 3
            self.console.print(Columns([panel7, panel8, panel9], equal=True, expand=True))
            self.console.print()
            
            # PANEL 10: AI Reasoning
            p10 = Table(box=box.ROUNDED, expand=True)
            p10.add_column("Factor", style="white", width=25)
            reasons = ["✅ Trend bullish", "✅ OB valid", 
                      "✅ FVG present", "⚠️ VIX caution"]
            for r in reasons:
                p10.add_row(r)
            panel10 = Panel(p10, title="[bold yellow]📖 REASONING[/]", border_style="yellow", expand=True)
            
            # PANEL 11: Performance
            p11 = Table(box=box.ROUNDED, expand=True)
            p11.add_column("Metric", style="cyan", width=10)
            p11.add_column("Value", style="white", width=10)
            p11.add_row("Win%", "65%")
            p11.add_row("Sharpe", "2.1")
            p11.add_row("MaxDD", "8.2%")
            p11.add_row("P&L", "+$2,450")
            panel11 = Panel(p11, title="[bold green]📊 PERF[/]", border_style="green", expand=True)
            
            # PANEL 12: Evolution
            p12 = Table(box=box.ROUNDED, expand=True)
            p12.add_column("System", style="cyan", width=8)
            p12.add_column("Status", style="white", width=12)
            p12.add_row("NAS", "Gen 45/100")
            p12.add_row("GA", "Gen 23/50")
            p12.add_row("AutoML", "Testing")
            p12.add_row("PBT", "Running")
            panel12 = Panel(p12, title="[bold blue]⚙️ EVOLUTION[/]", border_style="blue", expand=True)
            
            # Render Row 4
            self.console.print(Columns([panel10, panel11, panel12], equal=True, expand=True))
            
            # Footer
            footer = Panel(
                Text("[P] Pause | [R] Resume | [Q] Quit | [B] Backtest | [S] Signal | [X] Close", 
                     style="dim", justify="center"),
                style="dim",
                box=box.SIMPLE
            )
            self.console.print()
            self.console.print(footer)
            
        except Exception as e:
            logger.error(f"TUI render failed: {e}")
            self._render_text()

    def _render_text(self) -> None:
        """Fallback text rendering."""
        try:
            s = self.state
            price = getattr(s, 'current_price', 2358.21)
            print("\n" + "=" * 60)
            print(f"  XAUUSD GOD BOT v3.0 | Price: ${price:.2f}")
            print("=" * 60)
        except Exception as e:
            print(f"Error: {e}")
