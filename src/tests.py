import unittest
import random
from model import CurrentUsers, User

# Test users
class TestUsers(unittest.TestCase):
    def generatePhoneNumbers(self):
        return random.randint(1000000000, 9999999999)

    def testUserList(self):
        """
        Test keeping track of current users.
        """

        self.currentUsers = CurrentUsers()

    def addUser(self, user_id):




