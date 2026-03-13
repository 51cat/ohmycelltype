import time
from functools import wraps
from datetime import timedelta
from typing import Any, Callable

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme
from rich.status import Status


custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "success": "green",
    "highlight": "magenta bold",
    "muted": "dim",
    "model": "blue",
    "score_high": "green bold",
    "score_medium": "yellow bold",
    "score_low": "red bold",
})

console = Console(theme=custom_theme)


def get_timestamp() -> str:
    return time.strftime("%H:%M:%S")


def log_info(message: str, highlight: bool = False) -> None:
    style = "highlight" if highlight else "info"
    console.print(f"[{get_timestamp()}] ", style="muted", end="")
    console.print(message, style=style)


def log_success(message: str) -> None:
    console.print(f"[{get_timestamp()}] ", style="muted", end="")
    console.print(f"✅ {message}", style="success")


def log_warning(message: str) -> None:
    console.print(f"[{get_timestamp()}] ", style="muted", end="")
    console.print(f"⚠️  {message}", style="warning")


def log_error(message: str) -> None:
    console.print(f"[{get_timestamp()}] ", style="muted", end="")
    console.print(f"❌ {message}", style="error")


def log_start(func_name: str) -> None:
    console.print(f"[{get_timestamp()}] ", style="muted", end="")
    console.print(f"🚀 [bold]{func_name}[/bold] 开始执行...", style="info")


def log_done(func_name: str, elapsed: float) -> None:
    elapsed_str = str(timedelta(seconds=elapsed)).split(".")[0]
    if elapsed < 1:
        elapsed_str = f"{elapsed:.2f}s"
    elif elapsed < 60:
        elapsed_str = f"{elapsed:.1f}s"
    
    console.print(f"[{get_timestamp()}] ", style="muted", end="")
    console.print(f"✅ [bold]{func_name}[/bold] 完成 ⏱ {elapsed_str}", style="success")


def rich_log(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        log_start(func.__name__)
        start = time.time()
        
        result = func(*args, **kwargs)
        
        elapsed = time.time() - start
        log_done(func.__name__, elapsed)
        
        return result
    
    wrapper.logger = RichLoggerAdapter(func.__name__)
    return wrapper


class RichLoggerAdapter:
    def __init__(self, func_name: str):
        self.func_name = func_name
    
    def info(self, message: str) -> None:
        console.print(f"[{get_timestamp()}] ", style="muted", end="")
        console.print(f"   {message}", style="info")
    
    def warning(self, message: str) -> None:
        console.print(f"[{get_timestamp()}] ", style="muted", end="")
        console.print(f"   ⚠️  {message}", style="warning")
    
    def error(self, message: str) -> None:
        console.print(f"[{get_timestamp()}] ", style="muted", end="")
        console.print(f"   ❌ {message}", style="error")


def display_annotation_table(results: list[dict], title: str = "注释结果对比") -> None:
    table = Table(title=title, show_header=True, header_style="bold cyan")
    
    table.add_column("模型", style="model", width=18)
    table.add_column("细胞类型", width=20)
    table.add_column("亚型", width=22)
    table.add_column("可靠性", justify="center", width=8)
    table.add_column("状态", justify="center", width=10)
    
    for result in results:
        model = result.get("model", "unknown")
        cell_type = result.get("cell_type", "-")
        cell_subtype = result.get("cell_subtype", "-")
        score = result.get("score", 0)
        
        if score >= 80:
            score_str = f"[score_high]{score}[/score_high]"
            status = "[success]可靠[/success]"
        elif score >= 60:
            score_str = f"[score_medium]{score}[/score_medium]"
            status = "[warning]一般[/warning]"
        else:
            score_str = f"[score_low]{score}[/score_low]"
            status = "[error]不可靠[/error]"
        
        table.add_row(model, cell_type, cell_subtype, score_str, status)
    
    console.print()
    console.print(table)
    console.print()


def display_status_panel(title: str, content: dict[str, Any]) -> None:
    lines = []
    for key, value in content.items():
        lines.append(f"[bold]{key}:[/bold] {value}")
    
    panel = Panel(
        "\n".join(lines),
        title=f"[bold cyan]{title}[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(panel)


def display_section_header(title: str, icon: str = "📌") -> None:
    console.print()
    console.rule(f"{icon} [bold cyan]{title}[/bold cyan]")
    console.print()


def stream_print(text: str, style: str = None) -> None:
    if style:
        console.print(text, style=style, end="")
    else:
        console.print(text, end="")


def print_stream_header(model_name: str) -> None:
    console.print()
    console.print(f"[bold magenta]✨ {model_name}[/bold magenta]")
    console.print("[dim magenta]─[/dim magenta]" * 50)


def print_stream_footer() -> None:
    console.print()
    console.print("[dim magenta]─[/dim magenta]" * 50)
    console.print()


def chat_ai_start(model_name: str) -> None:
    console.print()
    console.print(f"[bold magenta]✨ {model_name}[/bold magenta]")
    console.print("[dim magenta]─[/dim magenta]" * 50)


def chat_ai_chunk(text: str) -> None:
    console.print(text, style="white", end="")


def chat_ai_end() -> None:
    console.print()
    console.print("[dim magenta]─[/dim magenta]" * 50)
    console.print()


def chat_user_input(prompt_text: str = "Your Input") -> str:
    console.print()
    console.print(f"[bold yellow]🔬 {prompt_text}[/bold yellow]")
    console.print("[dim yellow]─[/dim yellow]" * 50)
    
    try:
        user_text = console.input("[yellow]> [/yellow]")
    except (EOFError, KeyboardInterrupt):
        console.print()
        return ""
    
    console.print("[dim yellow]─[/dim yellow]" * 50)
    console.print()
    
    return user_text


def chat_session_header() -> None:
    console.clear()
    console.print()
    panel = Panel(
        "[bold]CelltypeAgent Chat Session[/bold]\n[dim]",
        title="[bold magenta]✨ 对话模式[/bold magenta]",
        border_style="magenta",
        padding=(1, 2)
    )
    console.print(panel)
    console.print()


def wait_animation() -> Status:
    return Status("", spinner="moon", console=console)


def is_valid_response(content: str | None) -> bool:
    if content is None:
        return False
    if not isinstance(content, str):
        return False
    stripped = content.strip()
    if stripped == "":
        return False
    if stripped.lower() in ("none", "null"):
        return False
    return True


def log_retry(attempt: int, delay: float, error_type: str) -> None:
    console.print(f"[{get_timestamp()}] ", style="muted", end="")
    console.print(
        f"🔄 调用失败 ({error_type})，{delay}秒后第 {attempt} 次重试...",
        style="warning"
    )
