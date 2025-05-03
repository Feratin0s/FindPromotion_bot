from models.user import User

class AuthService:
    def __init__(self):
        self.authenticated_users = {}
    
    def authenticate_user(self, user_id, password, correct_password):
        if password == correct_password:
            user = User(user_id)
            user.authenticate()
            self.authenticated_users[str(user_id)] = user
            return user
        return None
    
    def is_authenticated(self, user_id):
        return str(user_id) in self.authenticated_users
    
    def get_user(self, user_id):
        return self.authenticated_users.get(str(user_id))