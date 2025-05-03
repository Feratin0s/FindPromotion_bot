from services.commands import Command

class RemoveCommand(Command):
    def __init__(self, storage_service):
        self.storage_service = storage_service
    
    async def execute(self, **kwargs):
        user = kwargs.get('user')
        event = kwargs.get('event')
        msg = kwargs.get('msg')
        is_state_removing = kwargs.get('is_state_removing', False)
        
        if not all([user, event]):
            return False
            
        if is_state_removing and msg:
            if self.storage_service.remove_keyword_from_user(user.id, msg):
                await event.reply(f"🗑️ Palavra '{msg}' removida com sucesso.")
            else:
                await event.reply(f"⚠️ A palavra '{msg}' não está na sua lista.")
            user.state = None
            return True
        else:
            user.state = "removendo"
            keywords = self.storage_service.get_user_keywords(user.id)
            await event.reply(f"✂️ Digite a palavra que deseja remover. Lista atual: {', '.join(keywords)}")
            return True