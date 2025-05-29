from sqlalchemy import create_engine, Column, Integer, String, Text, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

class RuleSet(Base):
    __tablename__ = 'rulesets'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True) # Added a name for the rule set
    rules = Column(JSON) # Storing rules as JSON, can be a list of strings or dicts

    def __init__(self, name: str, rules: list):
        self.name = name
        self.rules = rules

class LoreTopic(Base):
    __tablename__ = 'loretipics' # Corrected typo: loretipics -> loretopics
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    # Basic relationship: a lore topic can have multiple related topics (self-referential)
    # This requires a secondary association table for many-to-many, or a simple ForeignKey for one-to-many
    # For now, let's keep related_topics as a JSON field for simplicity, will refine if needed
    related_topics_json = Column(JSON) # Storing as JSON for now

    # If we want actual relationships later, it would look something like:
    # parent_id = Column(Integer, ForeignKey('loretipics.id'))
    # children = relationship("LoreTopic", backref=backref('parent', remote_side=[id]))

    def __init__(self, name: str, description: str, related_topics: list = None):
        self.name = name
        self.description = description
        self.related_topics_json = related_topics if related_topics is not None else []

class Character(Base):
    __tablename__ = 'characters'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    attributes = Column(JSON) # e.g., {"strength": 10, "dexterity": 12}
    inventory = Column(JSON) # e.g., [{"item_name": "sword", "quantity": 1}, {"item_name": "potion", "quantity": 3}]
    status = Column(String) # e.g., "healthy", "poisoned"

    def __init__(self, name: str, attributes: dict, inventory: list, status: str):
        self.name = name
        self.attributes = attributes
        self.inventory = inventory
        self.status = status

class WorldState(Base):
    __tablename__ = 'worldstates'
    id = Column(Integer, primary_key=True) # Typically, there'd be only one row for current world state
    current_event = Column(String)
    active_effects = Column(JSON) # e.g., ["magic_aura_active", "time_distortion_field"]
    # Could also have a timestamp for when this state was last updated

    def __init__(self, current_event: str, active_effects: list):
        self.current_event = current_event
        self.active_effects = active_effects

# Example of how one might initialize and use these (not part of the file itself):
# if __name__ == '__main__':
#     engine = create_engine('sqlite:///:memory:') # Example using SQLite in-memory
#     Base.metadata.create_all(engine)
#
#     Session = sessionmaker(bind=engine)
#     session = Session()
#
#     # Create a ruleset
#     generic_rules = RuleSet(name="Generic D20", rules=[{"rule": "Roll D20 for success", "threshold": 10}])
#     session.add(generic_rules)
#     session.commit()
#
#     retrieved_ruleset = session.query(RuleSet).filter_by(name="Generic D20").first()
#     print(retrieved_ruleset.name, retrieved_ruleset.rules)
