"""
QUANTUM SWARM INTELLIGENCE TUI - Fixed Layout Engine
Uses Rich Layout for strict 3-column responsive grid.
"""
import sys
import time
import asyncio
import random
from datetime import datetime
from typing import Dict, Any, Optional

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich import box

console = Console()


class SharedMemory:
    """Shared memory rings for 7 agents."""

    def __init__(self) -> None:
        self.agents: Dict[int, Dict[str, Any]] = {
            1: {"name": "Data", "latency": 12.4, "status": "ONLINE"},
            2: {"name": "Exec", "latency": 8.1, "status": "ONLINE"},
            3: {"name": "Topol", "latency": 24.2, "status": "ONLINE"},
            4: {"name": "Fluid", "latency": 45.1, "status": "ONLINE"},
            5: {"name": "HoTT", "latency": 19.7, "status": "ONLINE"},
            6: {"name": "Noise", "latency": 11.3, "status": "ONLINE"},
            7: {"name": "Risk", "latency": 4.2, "status": "ONLINE"},
        }
        self.price: float = 1.08412
        self.spread: float = 0.1
        self.tick_count: int = 842100
        self.latency: float = 0.8
        self.dd_current: float = 0.14
        self.dd_max: float = 2.00
        self.reynolds: float = 4812.94
        self.buy_pressure: float = 94.2
        self.sell_pressure: float = 12.1

    def update(self) -> None:
        """Simulate real-time data updates from agents."""
        self.price += random.uniform(-0.00005, 0.00005)
        self.price = round(self.price, 5)
        self.spread = round(random.uniform(0.05, 0.15), 1)
        self.tick_count += random.randint(100, 500)
        self.latency = round(random.uniform(0.5, 1.5), 1)
        self.dd_current = round(random.uniform(0.05, 0.25), 2)
        self.reynolds = round(random.uniform(4000, 6000), 2)
        self.buy_pressure = round(random.uniform(80, 99), 1)
        self.sell_pressure = round(random.uniform(5, 20), 1)
        for agent in self.agents.values():
            agent["latency"] = round(random.uniform(3, 50), 1)


def build_header() -> Panel:
    """Build the main header panel."""
    return Panel(
        Text(
            "QUANTUM SWARM INTELLIGENCE TRADING ENGINE [v7.0.1-PROD]  |  SYSTEM: OPERATIONAL",
            style="bold cyan",
            justify="center",
        ),
        style="bold blue",
        box=box.DOUBLE,
        expand=True,
    )


def build_panel1(state: SharedMemory) -> Panel:
    """Panel 1: Agent Swarm Telemetry."""
    tbl = Table(box=None, expand=True, show_header=True, header_style="bold cyan", padding=(0, 1))
    tbl.add_column("Agent", style="white", width=22, no_wrap=True, overflow="ellipsis")
    tbl.add_column("Latency", style="yellow", width=10, no_wrap=True)
    tbl.add_column("Status", style="green", width=8, no_wrap=True)
    for num, agent in state.agents.items():
        tbl.add_row(
            f"Agent {num} ({agent['name']})",
            f"{agent['latency']}\u03bcs",
            f"[{agent['status']}]",
        )
    return Panel(tbl, title="[1] AGENT SWARM TELEMETRY", border_style="cyan", expand=True)


def build_panel2(state: SharedMemory) -> Panel:
    """Panel 2: p-ADIC Liquidity Density Matrix."""
    tbl = Table(box=None, expand=True, show_header=True, header_style="bold magenta", padding=(0, 1))
    tbl.add_column("Prime", style="yellow", width=6, no_wrap=True)
    tbl.add_column("Pattern", style="white", width=20, no_wrap=True, overflow="ellipsis")
    tbl.add_column("Status", style="green", width=9, no_wrap=True)
    tbl.add_row("p=2:", f"[{''.join(str(random.randint(0,1)) for _ in range(10))}..]", "Dense")
    tbl.add_row("p=3:", f"[{''.join(str(random.randint(0,2)) for _ in range(10))}..]", "Cluster")
    tbl.add_row("p=5:", f"[{''.join(str(random.randint(0,5)) for _ in range(10))}..]", "Scatter")
    tbl.add_row("", f"Dist: 2^(-{random.randint(2,8)})", "")
    tbl.add_row("", f"Reversal: {random.uniform(90,99):.1f}%", "")
    return Panel(tbl, title="[2] p-ADIC LIQUIDITY MATRIX", border_style="magenta", expand=True)


def build_panel3(state: SharedMemory) -> Panel:
    """Panel 3: Navier-Stokes Fluid Turbulence."""
    re = state.reynolds
    turb = "HIGH" if re > 5000 else "MED" if re > 3000 else "LOW"
    tbl = Table(box=None, expand=True, show_header=False, padding=(0, 0))
    tbl.add_column("G", style="white", width=40, no_wrap=True)
    tbl.add_row("100% |         \u25b2   \u25b2")
    tbl.add_row(" 75% |        \u25b2\u25b2\u25b2 \u25b2\u25b2\u25b2\u25b2")
    tbl.add_row(" 50% |      \u25b2\u25b2\u25b2\u25b2\u25b2\u25b2\u25b2\u25b2\u25b2\u25b2\u25b2")
    tbl.add_row(" 25% |\u25b2\u25b2\u25b2\u25b2\u25b2\u25b2\u25b2\u25b2\u25b2\u25b2\u25b2\u25b2\u25b2\u25b2\u25b2\u25b2")
    tbl.add_row("  0% \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500")
    tbl.add_row(f"Flow: {turb} TURBULENCE")
    tbl.add_row(f"Re: {re:,.2f}")
    return Panel(tbl, title="[3] NAVIER-STOKES FLUID", border_style="green", expand=True)


def build_panel4(state: SharedMemory) -> Panel:
    """Panel 4: Order Book Vacuum Line."""
    bid_v = round(random.uniform(1.5, 3.0), 1)
    ask_v = round(random.uniform(3.0, 6.0), 1)
    ask_bar = "\u2593" * int(ask_v * 2)
    bid_bar = "\u2591" * int(bid_v * 2)
    tbl = Table(box=None, expand=True, show_header=True, header_style="bold yellow", padding=(0, 1))
    tbl.add_column("Lvl", style="cyan", width=8, no_wrap=True)
    tbl.add_column("Price", style="white", width=10, no_wrap=True)
    tbl.add_column("Vol", style="magenta", width=22, no_wrap=True, overflow="ellipsis")
    tbl.add_row("ASK", f"[{state.price + 0.00008:.5f}]", f"{ask_bar} {ask_v}M")
    tbl.add_row("BID", f"[{state.price - 0.00002:.5f}]", f"{bid_bar} {bid_v}M")
    tbl.add_row("TGT", f"[{state.price - 0.00015:.5f}]", "TOPO HOLE DETECTED")
    return Panel(tbl, title="[4] ORDER BOOK VACUUM LINE", border_style="yellow", expand=True)


def build_panel5(state: SharedMemory) -> Panel:
    """Panel 5: Riemann Zeta Critical Strip."""
    tbl = Table(box=None, expand=True, show_header=True, header_style="bold cyan", padding=(0, 1))
    tbl.add_column("Metric", style="white", width=18, no_wrap=True)
    tbl.add_column("Value", style="green", width=14, no_wrap=True)
    tbl.add_row("Zeros Line:", "\u03c3 = 1/2")
    tbl.add_row("Wave Interf.:", "HARMONIC")
    tbl.add_row("Reversal:", f"T-{random.randint(50,200)}ms")
    return Panel(tbl, title="[5] RIEMANN ZETA", border_style="cyan", expand=True)


def build_panel6(state: SharedMemory) -> Panel:
    """Panel 6: Ergodic Noise Filtering."""
    trend = random.choice(["BULLISH", "BEARISH", "NEUTRAL"])
    tbl = Table(box=None, expand=True, show_header=True, header_style="bold green", padding=(0, 1))
    tbl.add_column("Metric", style="white", width=18, no_wrap=True)
    tbl.add_column("Value", style="cyan", width=16, no_wrap=True, overflow="ellipsis")
    tbl.add_row("Raw Variance:", f"{random.uniform(70,95):.1f}%")
    tbl.add_row("Clean Vector:", f"[{random.uniform(0.5,0.9):.3f}]")
    tbl.add_row("Trend:", f"\u2500\u2500\u25ba [{trend}]")
    return Panel(tbl, title="[6] ERGODIC NOISE", border_style="green", expand=True)


def build_panel7(state: SharedMemory) -> Panel:
    """Panel 7: HoTT Binary Mutation Prover."""
    tbl = Table(box=None, expand=True, show_header=True, header_style="bold magenta", padding=(0, 1))
    tbl.add_column("Status", style="white", width=18, no_wrap=True)
    tbl.add_column("Detail", style="green", width=16, no_wrap=True)
    tbl.add_row("Mutation ID:", f"#0x{random.randint(10000,99999):05X}")
    tbl.add_row("Proof:", "SUCCESS")
    tbl.add_row("RAM Binary:", f"mutant_0x{random.randint(10,99):X}.bin")
    return Panel(tbl, title="[7] HoTT MUTATION", border_style="magenta", expand=True)


def build_panel8(state: SharedMemory) -> Panel:
    """Panel 8: Real-Time Position Matrices."""
    pnl = round(random.uniform(-500, 500), 0)
    pc = "green" if pnl > 0 else "red"
    tbl = Table(box=None, expand=True, show_header=True, header_style="bold cyan", padding=(0, 1))
    tbl.add_column("Pair", style="white", width=8, no_wrap=True)
    tbl.add_column("Type", style="green", width=5, no_wrap=True)
    tbl.add_column("Lots", style="yellow", width=5, no_wrap=True)
    tbl.add_column("Entry", style="cyan", width=10, no_wrap=True)
    tbl.add_column("PnL", style=pc, width=8, no_wrap=True)
    tbl.add_row("XAUUSD", "BUY", "1.0", f"{state.price - 0.002:.5f}", f"+${pnl:.0f}" if pnl > 0 else f"-${abs(pnl):.0f}")
    return Panel(tbl, title="[8] POSITION MATRICES", border_style="cyan", expand=True)


def build_panel9(state: SharedMemory) -> Panel:
    """Panel 9: Cybernetic Drawdown Controller."""
    dd_s = "STABLE" if state.dd_current < state.dd_max * 0.5 else "WARN" if state.dd_current < state.dd_max else "CRIT"
    tbl = Table(box=None, expand=True, show_header=True, header_style="bold yellow", padding=(0, 1))
    tbl.add_column("Metric", style="white", width=16, no_wrap=True)
    tbl.add_column("Value", style="green", width=12, no_wrap=True)
    tbl.add_row("Max DD:", f"{state.dd_max:.2f}%")
    tbl.add_row("Current:", f"{state.dd_current:.2f}%")
    tbl.add_row("Loop:", f"{dd_s}")
    return Panel(tbl, title="[9] DRAWDOWN CTRL", border_style="yellow", expand=True)


def build_panel10(state: SharedMemory) -> Panel:
    """Panel 10: Metrics & Spread Tracker."""
    tbl = Table(box=None, expand=True, show_header=True, header_style="bold green", padding=(0, 1))
    tbl.add_column("Metric", style="white", width=18, no_wrap=True)
    tbl.add_column("Value", style="cyan", width=14, no_wrap=True)
    tbl.add_row("Spread:", f"{state.spread} Pips")
    tbl.add_row("Ticks:", f"{state.tick_count:,}/s")
    tbl.add_row("Latency:", f"{state.latency} ms")
    return Panel(tbl, title="[10] METRICS TRACKER", border_style="green", expand=True)


def build_panel11(state: SharedMemory) -> Panel:
    """Panel 11: QCD Gluon Pressure Stream."""
    buy_b = "\u25a0" * int(state.buy_pressure / 3)
    sell_b = "\u25a0" * int(state.sell_pressure / 3)
    mult = state.buy_pressure / max(state.sell_pressure, 0.1)
    tbl = Table(box=None, expand=True, show_header=False, padding=(0, 1))
    tbl.add_column("C", style="white", width=70, no_wrap=True, overflow="ellipsis")
    tbl.add_row(f"BUY:  [{buy_b}] {state.buy_pressure} GW")
    tbl.add_row(f"SELL: [{sell_b}] {state.sell_pressure} GW")
    tbl.add_row(f"Force: {mult:.1f}x ({'BREAKOUT' if mult > 5 else 'STABLE'})")
    return Panel(tbl, title="[11] QCD GLUON STREAM", border_style="red", expand=True)


def build_panel12(state: SharedMemory) -> Panel:
    """Panel 12: Black Swan GAN Matrix."""
    tbl = Table(box=None, expand=True, show_header=True, header_style="bold red", padding=(0, 1))
    tbl.add_column("Metric", style="white", width=16, no_wrap=True)
    tbl.add_column("Value", style="green", width=14, no_wrap=True)
    tbl.add_row("Sim:", "Swiss Peg")
    tbl.add_row("Survival:", f"{random.uniform(99.5,99.99):.1f}%")
    tbl.add_row("Edge:", "OPTIMAL")
    tbl.add_row("Vuln:", "NONE")
    return Panel(tbl, title="[12] BLACK SWAN GAN", border_style="red", expand=True)


def build_panel13(state: SharedMemory) -> Panel:
    """Panel 13: Live Interfaces & Execution Logs."""
    now = datetime.now()
    tbl = Table(box=None, expand=True, show_header=True, header_style="bold cyan", padding=(0, 1))
    tbl.add_column("Time", style="yellow", width=10, no_wrap=True)
    tbl.add_column("Event", style="white", width=40, no_wrap=True, overflow="ellipsis")
    tbl.add_row(f"{now:%H:%M:%S}.{random.randint(100,999)}", "Agent1 FIX Packet Ingested")
    tbl.add_row(f"{now:%H:%M:%S}.{random.randint(100,999)}", f"Agent3 Void at {state.price - 0.0002:.5f}")
    tbl.add_row(f"{now:%H:%M:%S}.{random.randint(100,999)}", f"Agent6 Vector {random.uniform(98,99.9):.0f}%")
    tbl.add_row(f"{now:%H:%M:%S}.{random.randint(100,999)}", "Agent2 BUY 1.0 LOT EXECUTED")
    return Panel(tbl, title="[13] EXECUTION LOGS", border_style="cyan", expand=True)


def build_layout(state: SharedMemory) -> Layout:
    """
    Build a strict 3-column layout:
      Left:   [1] Telemetry, [9] Drawdown, [10] Metrics, [11] Perf, [12] Evolution
      Middle: [2] p-Adic,    [5] Riemann,  [6] Ergodic,  [8] Positions
      Right:  [3] Fluid,     [4] OrderBook,[7] HoTT,     [13] Logs
    """
    # Create the root layout split into 3 columns
    root = Layout(name="root")
    root.split_row(
        Layout(name="left", ratio=1),
        Layout(name="middle", ratio=1),
        Layout(name="right", ratio=1),
    )

    # Left column: 5 panels stacked vertically
    left = Layout(name="left")
    left.split_column(
        Layout(name="p1", size=8),
        Layout(name="p9", size=6),
        Layout(name="p10", size=6),
        Layout(name="p11", size=5),
        Layout(name="p12", size=7),
    )
    left["p1"].update(build_panel1(state))
    left["p9"].update(build_panel9(state))
    left["p10"].update(build_panel10(state))
    left["p11"].update(build_panel11(state))
    left["p12"].update(build_panel12(state))

    # Middle column: 4 panels stacked vertically
    middle = Layout(name="middle")
    middle.split_column(
        Layout(name="p2", size=9),
        Layout(name="p5", size=6),
        Layout(name="p6", size=6),
        Layout(name="p8", size=7),
    )
    middle["p2"].update(build_panel2(state))
    middle["p5"].update(build_panel5(state))
    middle["p6"].update(build_panel6(state))
    middle["p8"].update(build_panel8(state))

    # Right column: 4 panels stacked vertically
    right = Layout(name="right")
    right.split_column(
        Layout(name="p3", size=9),
        Layout(name="p4", size=6),
        Layout(name="p7", size=6),
        Layout(name="p13", size=7),
    )
    right["p3"].update(build_panel3(state))
    right["p4"].update(build_panel4(state))
    right["p7"].update(build_panel7(state))
    right["p13"].update(build_panel13(state))

    root["left"].update(left)
    root["middle"].update(middle)
    root["right"].update(right)

    return root


async def run_tui() -> None:
    """Run the TUI with Rich Live at 60 FPS."""
    state = SharedMemory()

    console.clear()
    console.print("[bold cyan]Starting QUANTUM SWARM INTELLIGENCE TUI...[/]")
    console.print("[dim]Press Ctrl+C to exit[/]")
    await asyncio.sleep(1)

    header = build_header()

    with Live(
        Group(header, "", build_layout(state)),
        console=console,
        refresh_per_second=60,
        vertical_overflow="crop",
    ) as live:
        try:
            frame = 0
            while True:
                state.update()
                if frame % 10 == 0:
                    live.update(Group(header, "", build_layout(state)))
                frame += 1
                await asyncio.sleep(0.016)
        except KeyboardInterrupt:
            pass


def main() -> None:
    """Entry point."""
    try:
        asyncio.run(run_tui())
    except KeyboardInterrupt:
        console.print("\n[bold green]TUI stopped![/]")


if __name__ == "__main__":
    main()
