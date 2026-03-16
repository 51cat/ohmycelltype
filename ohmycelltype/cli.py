import click
import time
from ohmycelltype.workflow import CelltypeWorkflow
from ohmycelltype.tools.logger import (
    console, log_error, log_success, display_status_panel
)


VERSION = "1.0.0"


@click.group()
def cli():
    """✨ ohmycelltype - 单细胞 RNA 序列数据细胞类型注释工具"""
    pass


@cli.command()
def init_config():
    """初始化配置文件"""
    console.print("[bold magenta]✨ 初始化配置文件...[/bold magenta]")
    
    from ohmycelltype.config import Config
    config = Config()
    config.init()
    
    log_success("配置文件已创建！请执行 ohmycelltype set-api 命令填入 API Key等信息。")

    
@cli.command()
def set_api():
    """设置API Key"""
    console.print("[bold magenta]✨ 设置API Key...[/bold magenta]")
    
    from ohmycelltype.config import Config
    config = Config()
    
    is_correct_provider = False
    while not is_correct_provider:
        provider = click.prompt("请输入API提供商名称（可选：openrouter、n1n），不填则使用默认值", default="openrouter")
        if provider in config.config:
            is_correct_provider = True
        else:
            log_error(f"提供商 {provider} 不受支持，请重新输入。")
    api_key = click.prompt("请输入API Key", hide_input=False)
    
    try:
        config.set_api(provider, api_key)
        log_success(f"{provider} API Key 已更新！")
    except Exception as e:
        log_error(f"设置API Key失败: {str(e)}")
        raise click.Abort()


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', required=True, help='输出目录')
@click.option('-p', '--provider', default='openrouter', help='API provider (默认: openrouter)')
def annotate(input_file, output, provider):
    """执行完整的细胞类型注释流程
    
    INPUT: 输入文件路径 (CSV 格式的 marker 基因表)
    """
    console.clear()
    
    display_status_panel("运行参数", {
        "输入文件": input_file,
        "输出目录": output,
        "Provider": provider
    })
    
    try:
        console.print()
        console.print("[bold magenta]✨ 初始化工作流...[/bold magenta]")
        
        runner = CelltypeWorkflow(input_file, output, provider)
        time.sleep(3) 
        console.print()
        console.print("[bold magenta]✨ 开始参数收集...[/bold magenta]")
        
        runner.collect_parms()
        
        console.print()
        console.print("[bold magenta]✨ 开始多 Cluster 注释...[/bold magenta]")
        
        runner.multi_cluster_annotation()
        
        console.print()
        log_success("所有任务完成！")
        
    except Exception as e:
        console.print()
        log_error(f"执行失败: {str(e)}")
        raise click.Abort()


@cli.command()
def version():
    """显示版本信息"""
    console.print(f"[bold magenta]✨ ohmycelltype[/bold magenta] version [cyan]{VERSION}[/cyan]")

@cli.command()
def show():
    """显示当前配置"""
    from ohmycelltype.config import Config
    config = Config()

    console.print(f"\n配置文件路径: {config.get_path()}\n")
    
    try:
        console.print()
        console.print("[bold magenta]✨ 当前配置...[/bold magenta]")
        config.show()
    except Exception as e:
        log_error(f"显示配置失败: {str(e)}")
        raise click.Abort()

def main():
    cli()


if __name__ == '__main__':
    main()
