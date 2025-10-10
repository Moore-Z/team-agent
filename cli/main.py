# cli/main.py
import click
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
import asyncio

console = Console()

class TeamKnowledgeCLI:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.session = None
    
    async def ask_question(self, question: str):
        """发送问题到后端"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/ask",
                json={"question": question}
            ) as response:
                return await response.json()
    
    def interactive_mode(self):
        """交互式CLI模式 - 类似Claude Code界面"""
        console.print("[bold cyan]Team Knowledge Agent[/bold cyan]")
        console.print("Type 'help' for commands, 'exit' to quit\n")
        
        while True:
            question = Prompt.ask("[bold green]>>>[/bold green]")
            
            if question.lower() == 'exit':
                break
            elif question.lower() == 'help':
                self.show_help()
            elif question.startswith('/'):
                self.handle_command(question)
            else:
                with console.status("[bold yellow]Thinking..."):
                    response = asyncio.run(self.ask_question(question))
                    console.print(Markdown(response['answer']))
    
    def handle_command(self, command: str):
        """处理特殊命令"""
        if command == '/status':
            self.show_status()
        elif command == '/sources':
            self.show_sources()
        elif command == '/refresh':
            self.refresh_knowledge_base()

@click.command()
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode')
@click.option('--question', '-q', help='Ask a single question')
def main(interactive, question):
    cli = TeamKnowledgeCLI()
    
    if interactive:
        cli.interactive_mode()
    elif question:
        response = asyncio.run(cli.ask_question(question))
        console.print(Markdown(response['answer']))

if __name__ == '__main__':
    main()