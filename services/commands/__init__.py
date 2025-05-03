from abc import ABC, abstractmethod
from typing import Any, Dict

class Command(ABC):
    @abstractmethod
    async def execute(self, **kwargs: Dict[str, Any]) -> bool:
        """Executa o comando com os argumentos fornecidos"""
        pass

class CommandHandler:
    def __init__(self):
        self.commands = {}
    
    def register_command(self, command_name: str, command: Command):
        self.commands[command_name] = command
    
    async def handle(self, command_name: str, *args, **kwargs):
        if command_name in self.commands:
            return await self.commands[command_name].execute(*args, **kwargs)
        return None