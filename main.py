import os
import sys
import tty
import termios

import game_logic
import airport_service
import db_manager
import config
import action_game

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


# ---------------------------------------------------------------------------
# Arrow-key interactive menu
# ---------------------------------------------------------------------------

def _read_key() -> str | None:
    """Read a single keypress, returning 'UP', 'DOWN', 'LEFT', 'RIGHT', 'ENTER', 'ESC', or the char."""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            seq = sys.stdin.read(2)
            if seq == '[A':
                return 'UP'
            if seq == '[B':
                return 'DOWN'
            if seq == '[D':
                return 'LEFT'
            if seq == '[C':
                return 'RIGHT'
            return 'ESC'
        if ch in ('\r', '\n'):
            return 'ENTER'
        if ch == '\x03':
            raise KeyboardInterrupt
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _clear_screen():
    """Clear terminal and move cursor to top-left."""
    console.clear()


def interactive_menu(title: str, options: list[str], header_fn=None) -> int:
    """Display a menu navigable with arrow keys and Enter. Returns 1-based index.

    header_fn: optional callable that prints extra content above the menu (e.g. status panel).
    """
    selected = 0
    n = len(options)

    while True:
        _clear_screen()
        if header_fn:
            header_fn()
        console.print(f"\n[bold]{title}[/bold]")
        for i, opt in enumerate(options):
            if i == selected:
                console.print(f"  [bold cyan]▸ {i + 1}. {opt}[/bold cyan]")
            else:
                console.print(f"    {i + 1}. {opt}")
        console.print("[dim]  ↑↓ arrows / type number / Enter[/dim]")

        key = _read_key()
        if key == 'UP':
            selected = (selected - 1) % n
        elif key == 'DOWN':
            selected = (selected + 1) % n
        elif key == 'ENTER':
            return selected + 1
        elif key and key.isdigit():
            num = int(key)
            if 1 <= num <= n:
                return num


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def show_status(state: dict) -> None:
    """Display current game status as a rich panel (always shown as menu header)."""
    battery_remaining = config.MAX_BATTERY - state["battery_used"]
    unlocked = db_manager.get_unlocked_count()

    status_text = (
        f"[bold]Battery:[/bold]  {battery_remaining:.0f} / {config.MAX_BATTERY}  |  "
        f"[bold]Money:[/bold] ${state['money']:,}  |  "
        f"[bold]Levels beaten:[/bold] {unlocked}"
    )
    console.print(Panel(status_text, title="✈  THE AVIATOR", border_style="cyan"))


def show_levels_table(levels: list, page: int = 0, cursor: int = 0) -> None:
    """Display up to 5 airports per page as a numbered level table with cursor highlight."""
    page_size = 5
    total_pages = max(1, (len(levels) + page_size - 1) // page_size)
    page = max(0, min(page, total_pages - 1))

    start = page * page_size
    page_levels = levels[start:start + page_size]

    table = Table(title=f"Select a Level  (page {page + 1}/{total_pages})")
    table.add_column("", width=2)
    table.add_column("#", style="bold", width=5)
    table.add_column("Airport")
    table.add_column("City")
    table.add_column("Difficulty", justify="center")
    table.add_column("Reward", justify="right")
    table.add_column("Status", justify="center")

    for i, lv in enumerate(page_levels):
        marker = "▸" if i == cursor else ""
        row_style = "bold cyan" if i == cursor else ""
        if lv["locked"]:
            prev = lv["level"] - 1
            table.add_row(
                marker,
                str(lv["level"]),
                "🔒 LOCKED",
                "—",
                "—",
                "—",
                f"[dim]Beat level {prev} first[/dim]",
                style=row_style,
            )
        elif lv["beaten"]:
            table.add_row(
                marker,
                str(lv["level"]),
                lv["name"] or "—",
                lv["city"] or "—",
                "⭐" * lv["difficulty"],
                f"${lv['speaker_fee']:,}",
                "[green]✓ BEATEN[/green]",
                style=row_style,
            )
        else:
            table.add_row(
                marker,
                str(lv["level"]),
                lv["name"] or "—",
                lv["city"] or "—",
                "⭐" * lv["difficulty"],
                f"${lv['speaker_fee']:,}",
                "[yellow]OPEN[/yellow]",
                style=row_style,
            )

    console.print(table)


def prompt_int(prompt_text: str, min_val: int, max_val: int) -> int:
    """Prompt user for an integer in [min_val, max_val]. Re-prompts on invalid input."""
    while True:
        raw = input(prompt_text).strip()
        try:
            val = int(raw)
            if min_val <= val <= max_val:
                return val
            console.print(f"[red]Please enter a number between {min_val} and {max_val}.[/red]")
        except ValueError:
            console.print("[red]Invalid input. Please enter a number.[/red]")


# ---------------------------------------------------------------------------
# Game actions
# ---------------------------------------------------------------------------

def action_deliver_lecture(state: dict) -> dict:
    """Show level selection (5 per page), launch action game, award on victory."""
    levels = airport_service.get_level_airports()

    if not levels:
        console.print("[yellow]No levels available.[/yellow]")
        return state

    page_size = 5
    total_pages = max(1, (len(levels) + page_size - 1) // page_size)
    page = 0
    selected = None
    cursor = 0  # index within current page

    while selected is None:
        _clear_screen()
        start = page * page_size
        page_levels = levels[start:start + page_size]

        show_levels_table(levels, page, cursor)

        nav_parts = []
        if total_pages > 1:
            nav_parts.append(f"page {page + 1}/{total_pages}")
        nav_parts.append("↑↓ select, ←→ page, Enter confirm, Esc/q cancel")
        console.print(f"  [dim]{' | '.join(nav_parts)}[/dim]")

        key = _read_key()
        if key == 'UP':
            cursor = (cursor - 1) % len(page_levels)
        elif key == 'DOWN':
            cursor = (cursor + 1) % len(page_levels)
        elif key == 'RIGHT':
            if page < total_pages - 1:
                page += 1
                cursor = 0
        elif key == 'LEFT':
            if page > 0:
                page -= 1
                cursor = 0
        elif key == 'ENTER':
            selected = page_levels[cursor]
        elif key == 'ESC' or key == 'q':
            return state
        elif key and key.isdigit():
            num = int(key)
            if 1 <= num <= len(levels):
                selected = levels[num - 1]

    if selected["locked"]:
        prev = selected["level"] - 1
        _clear_screen()
        console.print(f"[red]This level is locked. Beat level {prev} first![/red]")
        console.print("[dim]  Press any key to continue...[/dim]")
        _read_key()
        return state

    if selected["beaten"]:
        _clear_screen()
        console.print("[yellow]You already beat this level.[/yellow]")
        console.print("[dim]  Press any key to continue...[/dim]")
        _read_key()
        return state

    # Launch the Pygame action game
    battery = config.MAX_BATTERY - state["battery_used"]
    console.print(f"\n[bold]Launching Level {selected['level']}: {selected['name']}[/bold]")
    console.print(f"[dim]Difficulty: {'⭐' * selected['difficulty']}  |  Survive {config.LEVEL_DURATION}s  |  Fuel: {battery}[/dim]\n")

    result = action_game.run_level(
        level_number=selected["level"],
        difficulty=selected["difficulty"],
        battery=battery,
    )

    if result["victory"]:
        # Award speaker fee and mark level as beaten
        updated = game_logic.deliver_lecture(state, selected["ident"])
        if "error" in updated:
            _clear_screen()
            console.print(f"[red]{updated['error']}[/red]")
            console.print("[dim]  Press any key to continue...[/dim]")
            _read_key()
            return state
        _clear_screen()
        console.print(f"[green]Level complete! Earned ${selected['speaker_fee']:,}. 🎉[/green]")
        console.print("[dim]  Press any key to continue...[/dim]")
        _read_key()

        # Update battery from game result
        new_battery_used = config.MAX_BATTERY - result["battery_remaining"]
        db_manager.update_after_recharge(updated["id"], updated["money"], new_battery_used)
        updated["battery_used"] = new_battery_used

        return updated
    else:
        return {**state, "game_over": True}


def action_reload(state: dict) -> dict:
    """Reload battery to full for a flat cost."""
    result = game_logic.recharge(state)

    if "error" in result:
        _clear_screen()
        console.print(f"[red]{result['error']}[/red]")
        console.print("[dim]  Press any key to continue...[/dim]")
        _read_key()
        return state

    _clear_screen()
    console.print(f"[green]Battery reloaded! Cost: ${config.RELOAD_COST:,}. Ready to fight! 🔋[/green]")
    console.print("[dim]  Press any key to continue...[/dim]")
    _read_key()
    return result


# ---------------------------------------------------------------------------
# Game loop
# ---------------------------------------------------------------------------

def game_loop(state: dict) -> None:
    """Main game loop: show status header, present 3 actions, repeat."""
    while True:
        # Restart on game-over (level failed)
        if state.get("game_over"):
            _clear_screen()
            show_status(state)
            console.print(Panel(
                "[bold red]Your plane went down. Starting a new game![/bold red]",
                title="GAME OVER", border_style="red",
            ))
            console.print("[dim]  Press any key to start a new game...[/dim]")
            _read_key()
            state = game_logic.new_game(state["name"])
            continue

        # Check win from previous action
        if state.get("won"):
            _clear_screen()
            show_status(state)
            console.print(Panel(
                "[bold green]You conquered every level! "
                "Electric aviation dominates the skies! ⚡[/bold green]",
                title="YOU WIN!", border_style="green",
            ))
            return

        choice = interactive_menu("Actions:", [
            "Deliver lecture (play a level)",
            f"Reload battery (${config.RELOAD_COST:,})",
            "Quit",
        ], header_fn=lambda: show_status(state))

        if choice == 1:
            state = action_deliver_lecture(state)
        elif choice == 2:
            state = action_reload(state)
        elif choice == 3:
            console.print("[dim]Goodbye![/dim]")
            return


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    """Entry point: startup menu → game loop."""
    db_manager.run_migrations()

    _title_fn = lambda: console.print(Panel(
        "[bold]THE AVIATOR[/bold]\nPilot the world's first electric aircraft.\n"
        "Beat all levels to win!",
        border_style="blue"))

    while True:
        choice = interactive_menu("Main Menu:", [
            "New Game",
            "Continue Game",
            "Quit",
        ], header_fn=_title_fn)

        if choice == 1:
            name = input("Enter your name: ").strip()
            if not name:
                console.print("[red]Name cannot be empty.[/red]")
                continue
            state = game_logic.new_game(name)
            console.print(f"[green]Welcome, {name}! Let's fly![/green]")
            game_loop(state)
            break

        elif choice == 2:
            name = input("Enter your name: ").strip()
            if not name:
                console.print("[red]Name cannot be empty.[/red]")
                continue
            state = game_logic.load_game(name)
            if state is None:
                console.print(f"[red]No saved game found for '{name}'.[/red]")
                continue
            console.print(f"[green]Welcome back, {name}![/green]")
            game_loop(state)
            break

        elif choice == 3:
            console.print("[dim]Goodbye![/dim]")
            break


if __name__ == "__main__":
    main()
