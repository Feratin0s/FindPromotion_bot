class User:
    def __init__(self, user_id):
        self.id = str(user_id)
        self.authenticated = False
        self.state = None
        self.keywords = []
        
    def authenticate(self):
        self.authenticated = True
    
    def add_keyword(self, keyword):
        keyword = keyword.strip().replace("-", " ")
        if keyword and keyword not in self.keywords:
            self.keywords.append(keyword)
            return True
        return False
    
    def remove_keyword(self, keyword):
        if keyword in self.keywords:
            self.keywords.remove(keyword)
            return True
        return False
    
    def get_keywords_string(self):
        return ", ".join(self.keywords) if self.keywords else "Nenhuma"
