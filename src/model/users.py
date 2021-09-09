# users.py

class User:
    def __init__(self, id: str, phoneNumber: str):
        self.id = id
        self.phoneNumber = phoneNumber
        self.search_results = None
        self.set_stage(0)
    
    def set_search_results(self, search_results: list):
        self.search_results = search_results

    def get_search_results(self):
        return self.search_results

    def get_search_results_range(self, minRange: int, maxRange: int):
        return self.search_results[minRange:maxRange]

    def clear_search_results(self):
        self.search_results = None

    def set_stage(self, stage: int):
        stages = [
            'new_search',
            'page_1',
            'page_2'
        ]
        self.stage = stages[stage]