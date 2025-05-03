from services.commands import Command

class AddCommand(Command):
    def __init__(self, storage_service):
        self.storage_service = storage_service
    
    async def execute(self, **kwargs):
        user = kwargs.get('user')
        event = kwargs.get('event')
        msg = kwargs.get('msg')
        
        if not all([user, event, msg]):
            return False
            
        palavras_adicionadas = []
        input_palavras = msg[len("/adicionar"):].split(",")
        
        for palavra in input_palavras:
            palavra = palavra.strip()
            if palavra and self.storage_service.add_keyword_to_user(user.id, palavra):
                palavras_adicionadas.append(palavra)
        
        response = "Palavras adicionadas ✅: " 
        response += ", ".join(palavras_adicionadas) if palavras_adicionadas else "Nenhuma"
        await event.reply(response)
        return True