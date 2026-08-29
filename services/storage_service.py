import json
import os
from dotenv import load_dotenv

load_dotenv()

KEYWORDS_FILE = os.getenv('KEYWORDS_FILE')

class StorageService:
    def __init__(self):
        self.users_data = self._load_data()
    
    def _load_data(self):
        if os.path.exists(KEYWORDS_FILE):
            with open(KEYWORDS_FILE, "r") as file:
                return json.load(file).get("users", {})
        return {}
    
    def save_data(self):
        with open(KEYWORDS_FILE, "w") as file:
            json.dump({"users": self.users_data}, file, indent=4)
    
    def add_user(self, user_id):
        if str(user_id) not in self.users_data:
            self.users_data[str(user_id)] = []
            self.save_data()
    
    def get_user_keywords(self, user_id):
        return self.users_data.get(str(user_id), [])
    
    def add_keyword_to_user(self, user_id, keyword):
        if str(user_id) in self.users_data:
            if keyword not in self.users_data[str(user_id)]:
                self.users_data[str(user_id)].append(keyword)
                self.save_data()
                return True
        return False
    
    def remove_keyword_from_user(self, user_id, keyword):
        if str(user_id) in self.users_data and keyword in self.users_data[str(user_id)]:
            self.users_data[str(user_id)].remove(keyword)
            self.save_data()
            return True
        return False