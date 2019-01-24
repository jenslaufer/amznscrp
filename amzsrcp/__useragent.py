import random


class UserAgent:
    def __init__(self, useragentsfile='amzscrp/useragents.txt'):
        with open(useragentsfile, "r") as f:
            self.user_agents = f.readlines()

    def get(self):
        return random.choice(self.user_agents).strip()
