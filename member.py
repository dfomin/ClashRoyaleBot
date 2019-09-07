class Member:
    def __init__(self, member):
        self.tag = member["tag"]
        self.name = member["name"]
        self.role = member["role"]
        self.last_seen = member["lastSeen"]
