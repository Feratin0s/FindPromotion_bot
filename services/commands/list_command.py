from services.commands import Command

class ListCommand(Command):
    def __init__(self, storage_service):
        self.storage_service = storage_service
    
    async def execute(self, **kwargs):
        user = kwargs.get('user')
        event = kwargs.get('event')
        
        if not user or not event:
            return False
            
        keywords = self.storage_service.get_user_keywords(user.id)
        await event.reply(
            f"Sua lista atual de palavras é: {', '.join(keywords)}" 
            if keywords else "Sua lista está vazia."
        )
        return True