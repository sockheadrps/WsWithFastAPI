import json
import time
import keyboard

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.style import Style
from rich.align import Align
from rich.box import SIMPLE

console = Console()

def build_renderable(json_data: dict, highlight_step: int):
    """
    Build a single renderable (Rich Group) for display via Rich Live,
    containing:
      - from -> server -> to (with animated underline)
      - syntax-highlighted JSON
    Both centered horizontally, no borders, no event/file name.
    """

    # ------------------------------------------------------------
    # 1) Animated FROM -> SERVER -> TO
    # ------------------------------------------------------------
    sending_process = json_data.get("sending_process", "Unknown")
    receiving_process = json_data.get("receiving_process", "Unknown")
    event_data = json_data.get("event_data", {})

    # Which segment should be underlined?
    from_underline = (highlight_step == 0)
    server_underline = (highlight_step == 1)
    to_underline = (highlight_step == 2)

    from_text = Text(
        sending_process,
        style=Style(color="bright_red" if from_underline else "cyan", underline=from_underline),
    )
    arrow_text = Text("   →   ", style="dim")
    server_text = Text(
        "server", 
        style=Style(color="bright_red" if server_underline else "cyan", underline=server_underline),
    )
    to_text = Text(
        receiving_process,
        style=Style(color="bright_red" if to_underline else "cyan", underline=to_underline), 
    )

    routing_text = Text.assemble(from_text, arrow_text, server_text, arrow_text, to_text)

    routing_panel = Panel(
        routing_text,
        padding=(0, 4),   
        expand=True,
        style=Style(color="steel_blue1"),
    )
    

    # ------------------------------------------------------------
    # 2) Syntax-highlighted JSON (no border)
    # ------------------------------------------------------------
    json_str = json.dumps(event_data, indent=2)
    syntax_obj = Syntax(
        code=json_str,
        lexer="json",
        theme="coffee",  # Try "monokai", "dracula", "default", etc.
        line_numbers=True,
        word_wrap=True,
        padding=1,
        code_width=80,
        tab_size=4,


    )

    data_panel = Panel(
        syntax_obj,
        padding=(0, 4),
        box=SIMPLE,
    )

    # ------------------------------------------------------------
    # 3) Stack them vertically in a Group
    # ------------------------------------------------------------
    renderable = Group(
        Align(routing_panel, align="center"),
        Align(data_panel, align="center"),
    )

    # We'll center the entire group vertically too,
    # by wrapping it in another Align with vertical="middle".
    centered_renderable = Align(renderable, align="center", vertical="middle")

    return centered_renderable


def main():
    console.clear()  # Clear the terminal on initial run

    current_file = 0
    last_display = None
    highlight_step = 0
    last_highlight_time = time.time()

    with Live(console=console, refresh_per_second=10) as live:
        try:
            while True:
                # Load the JSON file
                filename = f"{current_file}.json"
                try:
                    with open(filename, "r") as f:
                        file_json = json.load(f)
                except FileNotFoundError:
                    if current_file > 0:
                        current_file -= 1
                    else:
                        live.update("[red]No events found. Run the server first to generate events.[/red]")
                        time.sleep(1)
                        break
                except json.JSONDecodeError as e:
                    live.update(f"[bold red]Error parsing JSON:[/bold red] {e}")
                    time.sleep(1)
                    break

                # Check if content changed
                current_display_str = json.dumps(file_json, indent=2)
                if current_display_str != last_display:
                    last_display = current_display_str

                # Update underline every 0.5s
                if time.time() - last_highlight_time > 0.5:
                    highlight_step = (highlight_step + 1) % 3
                    last_highlight_time = time.time()

                # Build the renderable, then show it
                renderable = build_renderable(file_json, highlight_step)
                live.update(renderable)

                # Keyboard navigation
                if keyboard.is_pressed("left") and current_file > 0:
                    current_file -= 1
                    time.sleep(0.3)  # Debounce
                elif keyboard.is_pressed("right"):
                    current_file += 1
                    time.sleep(0.3)  # Debounce
                elif keyboard.is_pressed("q"):
                    break

                time.sleep(0.1)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
