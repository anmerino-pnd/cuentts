from rich.console import Console

console = Console()


def log_event(event: str, color: str = "cyan", **fields) -> None:
    parts = " ".join(f"{k}={v!r}" for k, v in fields.items())
    console.log(f"[{color}]{event}[/{color}] {parts}".rstrip())


def log_exception() -> None:
    console.print_exception(show_locals=False)
