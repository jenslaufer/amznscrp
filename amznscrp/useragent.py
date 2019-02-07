import random


class UserAgent:
    def __init__(self):
        path = 'amznscrp/resources/useragents.txt'
        useragentsfile = pkg_resources.resource_filename(__name__, path)
        with open(useragentsfile, "r") as f:
            self.user_agents = f.readlines()

    def get(self):
        return random.choice(self.user_agents).strip()
