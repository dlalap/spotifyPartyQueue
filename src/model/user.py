class CurrentUsers:
    def __init__(self):
        self.users = []

    def add_user(self, user_id):
        user = User(user_id)
        if user not in self.users:
            self.users.add(user)

class User:
    def __init__(self, id):
        self.id = id

    def new_query(self, query, results):
        self.query = query
        self.query_results = results

    def select_result(self, choice):
        selected_result = self.query_results[choice] 
        return selected_result
