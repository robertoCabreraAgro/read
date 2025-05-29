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
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    level = Column(Integer, default=1)
    character_class = Column(String, nullable=True)
    race = Column(String, nullable=True)
    alignment = Column(String, nullable=True)
    background = Column(String, nullable=True)
    experience_points = Column(Integer, default=0)

    strength_score = Column(Integer, default=10)
    dexterity_score = Column(Integer, default=10)
    constitution_score = Column(Integer, default=10)
    intelligence_score = Column(Integer, default=10)
    wisdom_score = Column(Integer, default=10)
    charisma_score = Column(Integer, default=10)

    proficiency_bonus = Column(Integer, default=2)
    hp_max = Column(Integer, default=10)
    hp_current = Column(Integer, default=10)
    armor_class = Column(Integer, default=10)
    speed = Column(Integer, default=30)

    mana_max = Column(Integer, nullable=True)
    mana_current = Column(Integer, nullable=True)

    status_general = Column(String, nullable=True)
    dao_philosophy = Column(String, nullable=True) 
    affiliation = Column(String, nullable=True)   
    
    custom_props_json = Column(JSON, nullable=True) 

    saving_throw_proficiencies = relationship("CharacterSavingThrowProficiency", back_populates="character", cascade="all, delete-orphan")
    skill_proficiencies = relationship("CharacterSkillProficiency", back_populates="character", cascade="all, delete-orphan")
    languages = relationship("CharacterLanguage", back_populates="character", cascade="all, delete-orphan")
    features_traits = relationship("CharacterFeatureTrait", back_populates="character", cascade="all, delete-orphan")
    resources = relationship("CharacterResource", back_populates="character", cascade="all, delete-orphan")
    inventory_items = relationship("CharacterInventoryItem", back_populates="character", cascade="all, delete-orphan")
    known_techniques = relationship("CharacterKnownTechniques", back_populates="character", cascade="all, delete-orphan") 
    
    reclusion_state = relationship("CharacterReclusionState", uselist=False, back_populates="character", cascade="all, delete-orphan") 
    titles = relationship("CharacterTitle", back_populates="character", cascade="all, delete-orphan") 
    compatible_elements = relationship("CharacterCompatibleElement", back_populates="character", cascade="all, delete-orphan") 

    def __repr__(self):
        return f"<Character(name='{self.name}', level={self.level}, class='{self.character_class}')>"

class CharacterSavingThrowProficiency(Base):
    __tablename__ = "character_saving_throw_proficiencies"
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    attribute_name = Column(String, nullable=False)
    is_proficient = Column(Boolean, default=False)
    character = relationship("Character", back_populates="saving_throw_proficiencies")

class CharacterSkillProficiency(Base):
    __tablename__ = "character_skill_proficiencies"
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    skill_name = Column(String, nullable=False)
    is_proficient = Column(Boolean, default=False)
    character = relationship("Character", back_populates="skill_proficiencies")

class CharacterLanguage(Base):
    __tablename__ = "character_languages"
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    language_name = Column(String, nullable=False)
    character = relationship("Character", back_populates="languages")

class CharacterFeatureTrait(Base):
    __tablename__ = "character_features_traits"
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String, nullable=True)
    character = relationship("Character", back_populates="features_traits")

class CharacterResource(Base):
    __tablename__ = "character_resources"
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    resource_name = Column(String, nullable=False)
    current_value = Column(Integer, default=0)
    max_value = Column(Integer, default=0)
    character = relationship("Character", back_populates="resources")

class CharacterInventoryItem(Base):
    __tablename__ = "character_inventory_items"
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    item_name = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    description = Column(Text, nullable=True)
    is_equipped = Column(Boolean, default=False)
    character = relationship("Character", back_populates="inventory_items")

class CharacterReclusionState(Base):
    __tablename__ = "character_reclusion_states"
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), unique=True, nullable=False) 
    start_day = Column(Integer, nullable=True)
    end_day = Column(Integer, nullable=True)
    days_remaining = Column(Integer, nullable=True)
    character = relationship("Character", back_populates="reclusion_state")

class CharacterTitle(Base):
    __tablename__ = "character_titles"
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    title_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    character = relationship("Character", back_populates="titles")

class CharacterCompatibleElement(Base):
    __tablename__ = "character_compatible_elements"
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    element_description = Column(String, nullable=False) 
    character = relationship("Character", back_populates="compatible_elements")

class Technique(Base):
    __tablename__ = "techniques"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    name_chinese = Column(String, nullable=True)
    element_association = Column(String, index=True, nullable=True)
    description = Column(Text, nullable=True)
    level_required = Column(Integer, nullable=True)
    rank = Column(String, nullable=True)
    damage_string = Column(String, nullable=True)
    mana_cost = Column(Integer, nullable=True)
    version = Column(String, nullable=True)
    source_dao = Column(Text, nullable=True)
    other_properties_json = Column(JSON, nullable=True)
    def __repr__(self):
        return f"<Technique(name='{self.name}')>"

class CharacterKnownTechniques(Base):
    __tablename__ = "character_known_techniques"
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    technique_id = Column(Integer, ForeignKey("techniques.id", ondelete="CASCADE"), nullable=False)
    mastery_level = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    character = relationship("Character", back_populates="known_techniques")
    technique = relationship("Technique") 
    def __repr__(self):
        return f"<CharacterKnownTechniques(character_id={self.character_id}, technique_id={self.technique_id})>"

class CampaignEvent(Base):
    __tablename__ = "campaign_events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    day_range_start = Column(Integer, nullable=True)
    day_range_end = Column(Integer, nullable=True)
    summary_content = Column(Text, nullable=False)
    full_details_json = Column(JSON, nullable=True)
    event_tags_json = Column(JSON, nullable=True)
    def __repr__(self):
        return f"<CampaignEvent(title='{self.title}')>"

class RuleSet(Base):
    __tablename__ = "rulesets" 
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    rules = Column(JSON) 

class WorldState(Base): 
    __tablename__ = "worldstates"
    id = Column(Integer, primary_key=True, index=True)
    current_event = Column(String)
    active_effects = Column(JSON)

```
