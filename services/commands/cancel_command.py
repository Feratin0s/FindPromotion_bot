from services.commands import Command

class CancelCommand(Command):
    async def execute(self, **kwargs):
        user = kwargs.get('user')
        event = kwargs.get('event')
        
        if not user or not event:
            return False
            
        user.state = None
        await event.reply("❌ Operação cancelada.")
        return True