"""
CLI入口模块

使用click库实现命令行接口，提供交互式聊天、快速提问、配置管理等功能。
"""

import sys
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from termwise import __version__
from termwise.config import ConfigManager
from termwise.utils.cost_tracker import CostTracker
from termwise.providers.registry import ProviderRegistry
from termwise.agent.core import AgentCore
from termwise.agent.conversation import ConversationManager

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="termwise")
def cli():
    """Termwise - 终端AI编码助手

    一个支持多LLM后端的终端AI编码助手，提供交互式TUI界面和命令行工具。
    """
    pass


@cli.command()
@click.option("--provider", "-p", default=None, help="指定LLM Provider")
@click.option("--model", "-m", default=None, help="指定模型")
def chat(provider, model):
    """启动交互式TUI聊天界面。"""
    config = ConfigManager()
    if provider:
        config.set_default_provider(provider)
    if model:
        config.set(f"providers.{config.get_default_provider()}.model", model)

    try:
        from termwise.tui.app import TermwiseApp
        app = TermwiseApp(config=config)
        app.run()
    except ImportError as e:
        console.print(f"[red]无法启动TUI界面: {e}[/red]")
        console.print("[yellow]请确保已安装textual: pip install textual[/yellow]")
        sys.exit(1)


@cli.command()
@click.argument("question", nargs=-1, required=True)
@click.option("--provider", "-p", default=None, help="指定LLM Provider")
@click.option("--model", "-m", default=None, help="指定模型")
@click.option("--verbose", "-v", is_flag=True, help="显示详细信息")
def ask(question, provider, model, verbose):
    """快速提问模式，直接在终端获取回答。"""
    config = ConfigManager()
    provider_name = provider or config.get_default_provider()
    model_name = model or config.get_provider_config(provider_name).get("model", "")

    question_text = " ".join(question)

    with console.status("[bold green]正在思考...[/bold green]"):
        try:
            registry = ProviderRegistry(config)
            llm_provider = registry.get_provider(provider_name)
            if not llm_provider:
                console.print(f"[red]未找到Provider: {provider_name}[/red]")
                console.print(f"[yellow]可用的Provider: {', '.join(registry.list_providers())}[/yellow]")
                sys.exit(1)

            messages = [
                {"role": "system", "content": "你是一个AI编码助手，请用中文回答问题。"},
                {"role": "user", "content": question_text},
            ]

            response = llm_provider.complete(
                messages=messages,
                model=model_name,
            )

            console.print()
            console.print(Panel(response, title="[bold blue]回答[/bold blue]", border_style="blue"))

            if verbose:
                usage = llm_provider.last_usage
                if usage:
                    console.print(f"\n[dim]Token使用: 输入={usage.get('prompt_tokens', 0)}, "
                                  f"输出={usage.get('completion_tokens', 0)}, "
                                  f"总计={usage.get('total_tokens', 0)}[/dim]")

        except Exception as e:
            console.print(f"[red]请求失败: {e}[/red]")
            sys.exit(1)


@cli.command(name="config")
@click.option("--get", "get_key", default=None, help="获取配置值")
@click.option("--set", "set_value", nargs=2, default=None, help="设置配置值 (key value)")
@click.option("--list", "list_all", is_flag=True, help="列出所有配置")
@click.option("--edit", is_flag=True, help="打开配置文件编辑")
def config_cmd(get_key, set_value, list_all, edit):
    """配置管理，设置API key、默认模型等。"""
    config = ConfigManager()

    if edit:
        import subprocess
        editor = os.environ.get("EDITOR", "vim")
        config_path = str(config.config_path)
        console.print(f"[dim]正在使用 {editor} 编辑配置文件: {config_path}[/dim]")
        try:
            subprocess.run([editor, config_path], check=True)
        except Exception as e:
            console.print(f"[red]无法打开编辑器: {e}[/red]")
            sys.exit(1)
        return

    if list_all:
        _display_config(config.config)
        return

    if get_key:
        value = config.get(get_key)
        if value is None:
            console.print(f"[yellow]配置项 '{get_key}' 不存在[/yellow]")
        else:
            console.print(f"{get_key} = {value}")
        return

    if set_value:
        key, value = set_value
        config.set(key, value)
        config.save()
        console.print(f"[green]已设置 {key} = {value}[/green]")
        return

    # 无参数时显示当前配置概览
    _display_config_summary(config)


def _display_config(config: dict) -> None:
    """以表格形式显示完整配置。"""
    import yaml
    config_str = yaml.dump(config, default_flow_style=False, allow_unicode=True)
    console.print(Panel(config_str, title="[bold]完整配置[/bold]", border_style="cyan"))


def _display_config_summary(config: ConfigManager) -> None:
    """显示配置概览。"""
    table = Table(title="Termwise 配置概览")
    table.add_column("配置项", style="cyan")
    table.add_column("值", style="green")

    table.add_row("默认Provider", config.get_default_provider())
    table.add_row("主题", config.get_setting("theme", "dark"))
    table.add_row("最大上下文Token", str(config.get_setting("max_context_tokens", 128000)))
    table.add_row("自动保存", str(config.get_setting("auto_save", True)))
    table.add_row("费用追踪", str(config.get_setting("cost_tracking", True)))

    console.print(table)

    # Provider配置
    providers = config.list_providers()
    for name, pconfig in providers.items():
        status = "[green]已配置[/green]" if config.is_provider_configured(name) else "[yellow]未配置[/yellow]"
        model = pconfig.get("model", "未设置")
        if name == "ollama":
            base_url = pconfig.get("base_url", "未设置")
            table2 = Table(title=f"Provider: {name} ({status})")
            table2.add_column("参数", style="cyan")
            table2.add_column("值", style="green")
            table2.add_row("Base URL", base_url)
            table2.add_row("模型", model)
        else:
            api_key = pconfig.get("api_key", "")
            masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else ("已设置" if api_key else "未设置")
            base_url = pconfig.get("base_url", "默认")
            table2 = Table(title=f"Provider: {name} ({status})")
            table2.add_column("参数", style="cyan")
            table2.add_column("值", style="green")
            table2.add_row("API Key", masked_key)
            table2.add_row("Base URL", base_url)
            table2.add_row("模型", model)
        console.print(table2)


@cli.command(name="list-models")
@click.option("--provider", "-p", default=None, help="指定Provider")
def list_models(provider):
    """列出可用模型。"""
    config = ConfigManager()
    provider_name = provider or config.get_default_provider()

    try:
        registry = ProviderRegistry(config)
        llm_provider = registry.get_provider(provider_name)
        if not llm_provider:
            console.print(f"[red]未找到Provider: {provider_name}[/red]")
            sys.exit(1)

        with console.status(f"[bold green]正在获取 {provider_name} 的模型列表...[/bold green]"):
            models = llm_provider.list_models()

        if not models:
            console.print(f"[yellow]未找到可用模型[/yellow]")
            return

        table = Table(title=f"可用模型 ({provider_name})")
        table.add_column("模型ID", style="cyan")
        table.add_column("说明", style="green")

        for model_info in models:
            if isinstance(model_info, dict):
                model_id = model_info.get("id", "")
                description = model_info.get("description", model_info.get("owned_by", ""))
            else:
                model_id = str(model_info)
                description = ""
            table.add_row(model_id, description)

        console.print(table)

    except Exception as e:
        console.print(f"[red]获取模型列表失败: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--provider", "-p", default=None, help="按Provider筛选")
@click.option("--days", "-d", default=7, help="显示最近N天的记录")
@click.option("--reset", is_flag=True, help="重置费用统计")
def cost(provider, days, reset):
    """查看费用统计。"""
    tracker = CostTracker()

    if reset:
        tracker.clear_history()
        console.print("[green]费用统计已重置[/green]")
        return

    summary = tracker.get_summary()

    if tracker.get_session_count() == 0:
        console.print("[yellow]暂无费用记录[/yellow]")
        return

    console.print(Panel(summary, title=f"[bold]费用统计 (最近{days}天)[/bold]", border_style="green"))


# 导入os用于config edit命令
import os


def main():
    """CLI入口点。"""
    cli()


if __name__ == "__main__":
    main()
