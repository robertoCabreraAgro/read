from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# --- Modelos de Reglas y Lore (DM y Mundo) ---

class DmGuidelineSet(Base):
    __tablename__ = "dm_guideline_sets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    system_base = Column(String, nullable=True)
    setting_description = Column(Text, nullable=True)
    mode_directed = Column(Text, nullable=True)
    dice_roll_responsible = Column(String, nullable=True)
    dice_roll_rules = Column(Text, nullable=True)
    tone_difficulty = Column(String, nullable=True)
    tone_focus = Column(Text, nullable=True)
    tone_style = Column(Text, nullable=True)
    relevant_chars_narration = Column(Text, nullable=True)
    intro_chars_restriction = Column(Text, nullable=True)

    session_structure_items = relationship("DmSessionStructureItem", back_populates="guideline_set", cascade="all, delete-orphan")
    intro_chars_show_fields = relationship("DmIntroCharShowField", back_populates="guideline_set", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DmGuidelineSet(name='{self.name}')>"

class DmSessionStructureItem(Base):
    __tablename__ = "dm_session_structure_items"
    id = Column(Integer, primary_key=True, index=True)
    guideline_set_id = Column(Integer, ForeignKey("dm_guideline_sets.id", ondelete="CASCADE"), nullable=False)
    item_description = Column(String, nullable=False)
    guideline_set = relationship("DmGuidelineSet", back_populates="session_structure_items")

class DmIntroCharShowField(Base):
    __tablename__ = "dm_intro_char_show_fields"
    id = Column(Integer, primary_key=True, index=True)
    guideline_set_id = Column(Integer, ForeignKey("dm_guideline_sets.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String, nullable=False)
    guideline_set = relationship("DmGuidelineSet", back_populates="intro_chars_show_fields")

class LoreTopic(Base):
    __tablename__ = "loretopics"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True) 
    additional_data_json = Column(JSON, nullable=True) 
    cultivation_realms = relationship("CultivationRealm", back_populates="lore_topic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<LoreTopic(name='{self.name}')>"

class CultivationRealm(Base):
    __tablename__ = "cultivation_realms"
    id = Column(Integer, primary_key=True, index=True)
    lore_topic_id = Column(Integer, ForeignKey("loretopics.id", ondelete="SET NULL"), nullable=True) 
    realm_order = Column(Integer, default=0) 
    name = Column(String, nullable=False)
    level_range = Column(String, nullable=True) 
    theme = Column(Text, nullable=True)
    lore_topic = relationship("LoreTopic", back_populates="cultivation_realms")

    def __repr__(self):
        return f"<CultivationRealm(name='{self.name}')>"

# --- Modelos de Personaje y relacionados ---


class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    level = Column(Integer, default=1)
    character_class = Column(String)
    race = Column(String)
    affiliation = Column(String)
    dao_philosophy = Column(String)
    hp_max = Column(Integer)
    hp_current = Column(Integer)
    mana_max = Column(Integer)
    mana_current = Column(Integer)
    status_general = Column(String)

    known_techniques = relationship("CharacterKnownTechnique", back_populates="character")
    talents = relationship("CharacterTalent", back_populates="character")
    inventory_items = relationship("InventoryItem", back_populates="character")
    titles = relationship("CharacterTitle", back_populates="character")
    compatible_elements = relationship("CharacterCompatibleElement", back_populates="character")
    resources = relationship("CharacterResource", back_populates="character")

class CharacterTitle(Base):
    __tablename__ = "character_titles"
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey("characters.id"))
    title_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    character = relationship("Character", back_populates="titles")

class CharacterCompatibleElement(Base):
    __tablename__ = "character_compatible_elements"
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey("characters.id"))
    element_name = Column(String, nullable=False)
    character = relationship("Character", back_populates="compatible_elements")

class CharacterResource(Base):
    __tablename__ = "character_resources"
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey("characters.id"))
    resource_name = Column(String, nullable=False)
    current_value = Column(Integer, default=0)
    max_value = Column(Integer, default=0)
    character = relationship("Character", back_populates="resources")

class Technique(Base):
    __tablename__ = "techniques"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    element_association = Column(String)
    description = Column(Text)
    level_required = Column(Integer)
    rank = Column(String)
    mana_cost = Column(Integer)
    damage_string = Column(String)
    version = Column(String)
    source_dao = Column(String)

class CharacterKnownTechnique(Base):
    __tablename__ = "character_known_techniques"
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey("characters.id"))
    technique_id = Column(Integer, ForeignKey("techniques.id"))
    mastery_level = Column(String)
    notes = Column(Text)

    character = relationship("Character", back_populates="known_techniques")
    technique = relationship("Technique")

class Talent(Base):
    __tablename__ = "talents"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    source = Column(String)

class CharacterTalent(Base):
    __tablename__ = "character_talents"
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey("characters.id"))
    talent_id = Column(Integer, ForeignKey("talents.id"))

    character = relationship("Character", back_populates="talents")
    talent = relationship("Talent")

class Affinity(Base):
    __tablename__ = "affinities"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)

class Sect(Base):
    __tablename__ = "sects"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    philosophy = Column(Text)
    benefits = Column(Text)
    power_rating = Column(String)

class CultivationRealm(Base):
    __tablename__ = "cultivation_realms"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    realm_order = Column(Integer)
    level_range = Column(String)

class CampaignEvent(Base):
    __tablename__ = "campaign_events"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    day_range_start = Column(Integer)
    day_range_end = Column(Integer)
    summary_content = Column(Text)
    full_details = Column(Text)
    event_tags = Column(String)

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey("characters.id"))
    item_name = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    description = Column(Text)
    is_equipped = Column(Boolean, default=False)

    character = relationship("Character", back_populates="inventory_items")

class DmGuidelineSet(Base):
    __tablename__ = "dm_guideline_sets"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    tone_style = Column(String)
    tone_focus = Column(String)
    dice_roll_rules = Column(Text)
    system_base = Column(String)
    intro_chars_show_fields = Column(Text)
    session_structure_items = Column(Text)

class LoreTopic(Base):
    __tablename__ = "lore_topics"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    related_elements = Column(String)

class WorldState(Base):
    __tablename__ = "world_state"
    id = Column(Integer, primary_key=True)
    current_event = Column(String)
    active_effects = Column(String)
