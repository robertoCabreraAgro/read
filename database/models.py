class RuleSet:
    def __init__(self, rules: list):
        self.rules = rules

class LoreTopic:
    def __init__(self, name: str, description: str, related_topics: list):
        self.name = name
        self.description = description
        self.related_topics = related_topics

class Character:
    def __init__(self, name: str, attributes: dict, inventory: list, status: str):
        self.name = name
        self.attributes = attributes
        self.inventory = inventory
        self.status = status

class WorldState:
    def __init__(self, current_event: str, active_effects: list):
        self.current_event = current_event
        self.active_effects = active_effects
