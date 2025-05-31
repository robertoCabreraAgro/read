from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, ForeignKey, Float, DateTime, Table
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# --- Association Tables for Many-to-Many Relationships ---
character_inventory_association = Table(
    'character_inventory_items',
    Base.metadata,
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True),
    Column('inventory_item_id', Integer, ForeignKey('inventory_items.id'), primary_key=True),
    Column('quantity', Integer, default=1),
    Column('is_equipped', Boolean, default=False)
)

character_attack_association = Table(
    'character_attacks',
    Base.metadata,
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True),
    Column('attack_id', Integer, ForeignKey('attacks.id'), primary_key=True)
)

party_member_association = Table(
    'party_members',
    Base.metadata,
    Column('party_id', Integer, ForeignKey('parties.id'), primary_key=True),
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True),
    Column('role', String, default='member'),
    Column('joined_date', DateTime, default=datetime.utcnow),
    Column('is_active', Boolean, default=True)
)

# --- Core Models ---

class CultivationRealm(Base):
    """Cultivation realms for Wuxia progression system."""
    __tablename__ = "cultivation_realms"
    
    id = Column(Integer, primary_key=True, index=True)
    realm_order = Column(Integer, default=0, nullable=False)
    name = Column(String, nullable=False)
    level_range = Column(String, nullable=True)
    theme = Column(Text, nullable=True)
    estado = Column(String, nullable=True)
    subetapa = Column(String, nullable=True)
    exp_required = Column(Integer, nullable=True)
    
    # Relationships
    lore_topic_id = Column(Integer, ForeignKey('lore_topics.id'), nullable=True)
    characters = relationship("Character", back_populates="cultivation_realm")

    def __repr__(self):
        return f"<CultivationRealm(name='{self.name}', order={self.realm_order})>"

class LoreTopic(Base):
    """Lore and world-building information."""
    __tablename__ = "lore_topics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    topic_type = Column(String, default="general")
    additional_data_json = Column(JSON, nullable=True)
    
    # Relationships
    cultivation_realms = relationship("CultivationRealm", backref="lore_topic")

class Character(Base):
    """Main character model with full D&D 5e support."""
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    
    # Core D&D Stats
    level = Column(Integer, default=1)
    character_class = Column(String)
    subclass = Column(String)
    race = Column(String)
    alignment = Column(String)
    background = Column(String)
    experience_points = Column(Integer, default=0)
    proficiency_bonus = Column(Integer, default=2)
    
    # Ability Scores
    strength_score = Column(Integer, default=10)
    dexterity_score = Column(Integer, default=10)
    constitution_score = Column(Integer, default=10)
    intelligence_score = Column(Integer, default=10)
    wisdom_score = Column(Integer, default=10)
    charisma_score = Column(Integer, default=10)
    
    # Combat Stats
    hp_max = Column(Integer, default=8)
    hp_current = Column(Integer, default=8)
    armor_class = Column(Integer, default=10)
    speed = Column(Integer, default=30)
    initiative_bonus = Column(Integer, default=0)
    
    # Spellcasting
    spellcasting_ability = Column(String, nullable=True)  # intelligence, wisdom, charisma
    spell_attack_bonus = Column(Integer, default=0)
    spell_save_dc = Column(Integer, default=8)
    
    # Wuxia-specific Stats
    mana_max = Column(Integer, nullable=True)
    mana_current = Column(Integer, nullable=True)
    dao_philosophy = Column(String, nullable=True)
    affiliation = Column(String, nullable=True)
    status_general = Column(String, default="active")
    
    # Foreign Keys
    cultivation_realm_id = Column(Integer, ForeignKey('cultivation_realms.id'), nullable=True)
    
    # Custom Properties
    custom_props_json = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cultivation_realm = relationship("CultivationRealm", back_populates="characters")
    saving_throw_proficiencies = relationship("CharacterSavingThrowProficiency", back_populates="character", cascade="all, delete-orphan")
    skill_proficiencies = relationship("CharacterSkillProficiency", back_populates="character", cascade="all, delete-orphan")
    languages = relationship("CharacterLanguage", back_populates="character", cascade="all, delete-orphan")
    features_traits = relationship("CharacterFeatureTrait", back_populates="character", cascade="all, delete-orphan")
    resources = relationship("CharacterResource", back_populates="character", cascade="all, delete-orphan")
    titles = relationship("CharacterTitle", back_populates="character", cascade="all, delete-orphan")
    compatible_elements = relationship("CharacterCompatibleElement", back_populates="character", cascade="all, delete-orphan")
    reclusion_state = relationship("CharacterReclusionState", back_populates="character", uselist=False, cascade="all, delete-orphan")
    known_techniques = relationship("CharacterKnownTechniques", back_populates="character", cascade="all, delete-orphan")
    inventory_items = relationship("InventoryItem", secondary=character_inventory_association, back_populates="characters")
    attacks = relationship("Attack", secondary=character_attack_association, back_populates="characters")
    conditions = relationship("CharacterCondition", back_populates="character", cascade="all, delete-orphan")
    spell_slots = relationship("CharacterSpellSlot", back_populates="character", cascade="all, delete-orphan")
    known_spells = relationship("CharacterKnownSpell", back_populates="character", cascade="all, delete-orphan")
    parties = relationship("Party", secondary=party_member_association, back_populates="members")
    dice_rolls = relationship("DiceRollHistory", back_populates="character")
    encounter_participants = relationship("EncounterParticipant", back_populates="character")

class CharacterSavingThrowProficiency(Base):
    """Character saving throw proficiencies."""
    __tablename__ = "character_saving_throw_proficiencies"
    
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    attribute_name = Column(String, nullable=False)  # strength, dexterity, etc.
    is_proficient = Column(Boolean, default=False)
    
    character = relationship("Character", back_populates="saving_throw_proficiencies")

class CharacterSkillProficiency(Base):
    """Character skill proficiencies."""
    __tablename__ = "character_skill_proficiencies"
    
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    skill_name = Column(String, nullable=False)
    is_proficient = Column(Boolean, default=False)
    expertise = Column(Boolean, default=False)  # Double proficiency bonus
    
    character = relationship("Character", back_populates="skill_proficiencies")

class CharacterLanguage(Base):
    """Languages known by character."""
    __tablename__ = "character_languages"
    
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    language_name = Column(String, nullable=False)
    
    character = relationship("Character", back_populates="languages")

class CharacterFeatureTrait(Base):
    """Character features and traits."""
    __tablename__ = "character_features_traits"
    
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    feature_type = Column(String, nullable=True)  # class_feature, racial_trait, feat, etc.
    uses_per_rest = Column(Integer, nullable=True)
    uses_remaining = Column(Integer, nullable=True)
    rest_type = Column(String, default="long")  # short, long
    
    character = relationship("Character", back_populates="features_traits")

class CharacterResource(Base):
    """Character resources (Ki, Spell Slots, etc.)."""
    __tablename__ = "character_resources"
    
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    resource_name = Column(String, nullable=False)
    current_value = Column(Integer, default=0)
    max_value = Column(Integer, default=0)
    
    character = relationship("Character", back_populates="resources")

class CharacterTitle(Base):
    """Character titles for Wuxia setting."""
    __tablename__ = "character_titles"
    
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    title_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    earned_date = Column(DateTime, default=datetime.utcnow)
    
    character = relationship("Character", back_populates="titles")

class CharacterCompatibleElement(Base):
    """Character elemental compatibilities."""
    __tablename__ = "character_compatible_elements"
    
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    element_description = Column(String, nullable=False)
    affinity_level = Column(String, default="basic")  # basic, intermediate, advanced, master
    
    character = relationship("Character", back_populates="compatible_elements")

class CharacterReclusionState(Base):
    """Character reclusion state for Wuxia cultivation."""
    __tablename__ = "character_reclusion_states"
    
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False, unique=True)
    start_day = Column(Integer, nullable=True)
    end_day = Column(Integer, nullable=True)
    days_remaining = Column(Integer, nullable=True)
    reclusion_type = Column(String, nullable=True)  # meditation, training, etc.
    
    character = relationship("Character", back_populates="reclusion_state")

class CharacterSpellSlot(Base):
    """Character spell slots for spellcasters."""
    __tablename__ = "character_spell_slots"
    
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    spell_level = Column(Integer, nullable=False)  # 1-9
    total_slots = Column(Integer, default=0)
    used_slots = Column(Integer, default=0)
    
    character = relationship("Character", back_populates="spell_slots")

class Spell(Base):
    """D&D 5e spells and their Wuxia technique equivalents."""
    __tablename__ = "spells"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    spell_level = Column(Integer, nullable=False)  # 0-9 (0 = cantrip)
    school = Column(String, nullable=False)  # evocation, abjuration, etc.
    casting_time = Column(String, default="1 action")
    range_distance = Column(String, default="touch")
    duration = Column(String, default="instantaneous")
    components = Column(String, nullable=True)  # V, S, M
    description = Column(Text, nullable=True)
    damage_dice = Column(String, nullable=True)
    damage_type = Column(String, nullable=True)
    save_type = Column(String, nullable=True)  # dexterity, constitution, etc.
    ritual = Column(Boolean, default=False)
    concentration = Column(Boolean, default=False)
    classes_json = Column(JSON, nullable=True)  # List of classes that can cast this
    wuxia_equivalent = Column(String, nullable=True)  # Link to technique name
    upcast_formula = Column(String, nullable=True)
    
    # Relationships
    known_by_characters = relationship("CharacterKnownSpell", back_populates="spell")

class CharacterKnownSpell(Base):
    """Association table for character known spells."""
    __tablename__ = "character_known_spells"
    
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    spell_id = Column(Integer, ForeignKey('spells.id'), nullable=False)
    is_prepared = Column(Boolean, default=False)
    always_prepared = Column(Boolean, default=False)  # Domain spells, etc.
    
    character = relationship("Character", back_populates="known_spells")
    spell = relationship("Spell", back_populates="known_by_characters")

class Technique(Base):
    """Wuxia techniques and their D&D spell equivalents."""
    __tablename__ = "techniques"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    name_chinese = Column(String, nullable=True)
    element_association = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    level_required = Column(Integer, default=1)
    rank = Column(String, nullable=True)  # Basic, Intermediate, Advanced, Master
    damage_string = Column(String, nullable=True)
    mana_cost = Column(Integer, nullable=True)
    version = Column(String, nullable=True)
    source_dao = Column(String, nullable=True)
    casting_time = Column(String, default="1 action")
    range_distance = Column(String, default="touch")
    duration = Column(String, default="instantaneous")
    components = Column(String, nullable=True)  # Chi manipulation requirements
    dnd_equivalent = Column(String, nullable=True)  # Link to spell name
    other_properties_json = Column(JSON, nullable=True)
    
    # Relationships
    known_by_characters = relationship("CharacterKnownTechniques", back_populates="technique")

class CharacterKnownTechniques(Base):
    """Association table for character known techniques."""
    __tablename__ = "character_known_techniques"
    
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    technique_id = Column(Integer, ForeignKey('techniques.id'), nullable=False)
    mastery_level = Column(String, default="learned")  # learned, practiced, mastered, perfected
    times_used = Column(Integer, default=0)
    
    character = relationship("Character", back_populates="known_techniques")
    technique = relationship("Technique", back_populates="known_by_characters")

class Attack(Base):
    """Attack actions available to characters."""
    __tablename__ = "attacks"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    attack_bonus = Column(Integer, default=0)
    damage_dice = Column(String, nullable=True)  # "1d8+3"
    damage_type = Column(String, nullable=True)  # slashing, piercing, etc.
    range_distance = Column(String, default="5 ft")
    attack_type = Column(String, default="melee")  # melee, ranged, spell
    description = Column(Text, nullable=True)
    
    characters = relationship("Character", secondary=character_attack_association, back_populates="attacks")

class InventoryItem(Base):
    """Inventory items."""
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    item_type = Column(String, nullable=True)  # weapon, armor, consumable, etc.
    rarity = Column(String, default="common")
    description = Column(Text, nullable=True)
    weight = Column(Float, default=0.0)
    value_gold = Column(Integer, default=0)
    magical = Column(Boolean, default=False)
    properties_json = Column(JSON, nullable=True)
    
    characters = relationship("Character", secondary=character_inventory_association, back_populates="inventory_items")

class Condition(Base):
    """Status conditions."""
    __tablename__ = "conditions"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    condition_type = Column(String, nullable=True)  # debuff, buff, neutral
    effects_json = Column(JSON, nullable=True)

class CharacterCondition(Base):
    """Active conditions on characters."""
    __tablename__ = "character_conditions"
    
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    condition_id = Column(Integer, ForeignKey('conditions.id'), nullable=False)
    duration_rounds = Column(Integer, nullable=True)
    save_dc = Column(Integer, nullable=True)
    applied_at = Column(DateTime, default=datetime.utcnow)
    
    character = relationship("Character", back_populates="conditions")
    condition = relationship("Condition")

class Party(Base):
    """Adventuring parties."""
    __tablename__ = "parties"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    formation_date = Column(DateTime, default=datetime.utcnow)
    shared_gold = Column(Integer, default=0)
    shared_resources_json = Column(JSON, nullable=True)
    reputation_json = Column(JSON, nullable=True)
    current_location = Column(String, nullable=True)
    goals_json = Column(JSON, nullable=True)
    
    # Relationships
    members = relationship("Character", secondary=party_member_association, back_populates="parties")
    sessions = relationship("Session", back_populates="party")

class Session(Base):
    """Game sessions."""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True)
    session_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    duration_minutes = Column(Integer, nullable=True)
    dm_name = Column(String, default="Sistema IA")
    session_summary = Column(Text, nullable=True)
    events_json = Column(JSON, nullable=True)
    experience_awarded = Column(Integer, default=0)
    treasure_found_json = Column(JSON, nullable=True)
    character_changes_json = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String, default="active")  # active, completed, paused
    
    # Foreign Keys
    party_id = Column(Integer, ForeignKey('parties.id'), nullable=True)
    
    # Relationships
    party = relationship("Party", back_populates="sessions")
    encounters = relationship("Encounter", back_populates="session")
    dice_rolls = relationship("DiceRollHistory", back_populates="session")

class Location(Base):
    """Game world locations."""
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    location_type = Column(String, nullable=True)  # city, dungeon, wilderness, etc.
    region = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    environmental_effects_json = Column(JSON, nullable=True)
    notable_features_json = Column(JSON, nullable=True)
    current_status = Column(String, default="active")
    loot_available = Column(Boolean, default=False)
    enemies_present = Column(Boolean, default=False)
    connections_json = Column(JSON, nullable=True)  # Connections to other locations
    
    # Relationships
    encounters = relationship("Encounter", back_populates="location")

class Encounter(Base):
    """Combat and non-combat encounters."""
    __tablename__ = "encounters"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    encounter_type = Column(String, default="combat")  # combat, social, exploration, trap
    difficulty = Column(String, nullable=True)  # trivial, easy, medium, hard, deadly
    expected_party_level = Column(Integer, default=1)
    environment = Column(String, nullable=True)
    current_round = Column(Integer, default=1)
    current_turn = Column(Integer, default=0)
    status = Column(String, default="pending")  # pending, active, completed, fled
    turn_order_json = Column(JSON, nullable=True)
    environmental_effects_json = Column(JSON, nullable=True)
    rewards_json = Column(JSON, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Foreign Keys
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=True)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=True)
    
    # Relationships
    session = relationship("Session", back_populates="encounters")
    location = relationship("Location", back_populates="encounters")
    participants = relationship("EncounterParticipant", back_populates="encounter", cascade="all, delete-orphan")
    dice_rolls = relationship("DiceRollHistory", back_populates="encounter")

class EncounterParticipant(Base):
    """Participants in encounters (characters, NPCs, enemies)."""
    __tablename__ = "encounter_participants"
    
    id = Column(Integer, primary_key=True)
    encounter_id = Column(Integer, ForeignKey('encounters.id'), nullable=False)
    participant_type = Column(String, nullable=False)  # character, npc, enemy
    entity_id = Column(Integer, nullable=False)  # ID in respective table
    entity_name = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    initiative = Column(Integer, default=10)
    position_x = Column(Integer, nullable=True)
    position_y = Column(Integer, nullable=True)
    has_acted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Foreign Keys (optional, for direct relationships)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=True)
    npc_id = Column(Integer, ForeignKey('npcs.id'), nullable=True)
    
    # Relationships
    encounter = relationship("Encounter", back_populates="participants")
    character = relationship("Character", back_populates="encounter_participants")
    npc = relationship("Npc", back_populates="encounter_participants")

class DiceRollHistory(Base):
    """History of all dice rolls for transparency."""
    __tablename__ = "dice_roll_history"
    
    id = Column(Integer, primary_key=True)
    roller_name = Column(String, nullable=False)
    roller_type = Column(String, nullable=False)  # character, npc, enemy, dm
    roller_id = Column(Integer, nullable=True)
    roll_type = Column(String, nullable=False)  # initiative, attack, damage, save, skill, etc.
    dice_expression = Column(String, nullable=False)  # "1d20+5"
    individual_rolls_json = Column(JSON, nullable=False)  # [15, 3, 8] for multiple dice
    modifiers = Column(Integer, default=0)
    total_result = Column(Integer, nullable=False)
    target_dc = Column(Integer, nullable=True)
    success = Column(Boolean, nullable=True)
    context = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=True)
    encounter_id = Column(Integer, ForeignKey('encounters.id'), nullable=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=True)
    
    # Relationships
    session = relationship("Session", back_populates="dice_rolls")
    encounter = relationship("Encounter", back_populates="dice_rolls")
    character = relationship("Character", back_populates="dice_rolls")

class Sect(Base):
    """Wuxia sects and organizations."""
    __tablename__ = "sects"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    founder = Column(String, nullable=True)
    alignment = Column(String, nullable=True)
    specialties_json = Column(JSON, nullable=True)
    reputation = Column(String, nullable=True)
    requirements = Column(Text, nullable=True)
    current_leader = Column(String, nullable=True)
    founding_date = Column(String, nullable=True)
    headquarters_location = Column(String, nullable=True)
    
    # Relationships
    npcs = relationship("Npc", back_populates="sect")

class Npc(Base):
    """Non-player characters."""
    __tablename__ = "npcs"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    npc_type = Column(String, nullable=True)
    level = Column(Integer, default=1)
    role = Column(String, nullable=True)
    
    # Basic Stats (simplified for NPCs)
    hp_max = Column(Integer, default=10)
    hp_current = Column(Integer, default=10)
    armor_class = Column(Integer, default=10)
    challenge_rating = Column(String, nullable=True)
    
    # Relationships
    sect_id = Column(Integer, ForeignKey('sects.id'), nullable=True)
    sect = relationship("Sect", back_populates="npcs")
    encounter_participants = relationship("EncounterParticipant", back_populates="npc")
    
    # NPC-specific data
    personality = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    stats_json = Column(JSON, nullable=True)
    languages_json = Column(JSON, nullable=True)

class CampaignEvent(Base):
    """Campaign events and timeline."""
    __tablename__ = "campaign_events"
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    summary_content = Column(Text, nullable=True)
    day_range_start = Column(Integer, nullable=True)
    day_range_end = Column(Integer, nullable=True)
    event_tags_json = Column(JSON, nullable=True)
    full_details_json = Column(JSON, nullable=True)
    importance_level = Column(String, default="medium")  # low, medium, high, critical
    event_type = Column(String, default="narrative")  # narrative, combat, social, discovery
    created_at = Column(DateTime, default=datetime.utcnow)

class DmGuidelineSet(Base):
    """DM guidelines and rules."""
    __tablename__ = "dm_guideline_sets"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    system_base = Column(String, nullable=True)
    setting_description = Column(Text, nullable=True)
    mode_directed = Column(Text, nullable=True)
    dice_roll_responsible = Column(Text, nullable=True)
    dice_roll_rules = Column(Text, nullable=True)
    tone_difficulty = Column(Text, nullable=True)
    tone_focus = Column(Text, nullable=True)
    tone_style = Column(Text, nullable=True)
    relevant_chars_narration = Column(Text, nullable=True)
    intro_chars_restriction = Column(Text, nullable=True)
    
    # Relationships
    session_structure_items = relationship("DmSessionStructureItem", back_populates="guideline_set", cascade="all, delete-orphan")
    intro_chars_show_fields = relationship("DmIntroCharShowField", back_populates="guideline_set", cascade="all, delete-orphan")

class DmSessionStructureItem(Base):
    """Session structure items for DM guidelines."""
    __tablename__ = "dm_session_structure_items"
    
    id = Column(Integer, primary_key=True)
    guideline_set_id = Column(Integer, ForeignKey('dm_guideline_sets.id'), nullable=False)
    item_description = Column(Text, nullable=False)
    order_index = Column(Integer, default=0)
    
    guideline_set = relationship("DmGuidelineSet", back_populates="session_structure_items")

class DmIntroCharShowField(Base):
    """Fields to show when introducing characters."""
    __tablename__ = "dm_intro_char_show_fields"
    
    id = Column(Integer, primary_key=True)
    guideline_set_id = Column(Integer, ForeignKey('dm_guideline_sets.id'), nullable=False)
    field_name = Column(String, nullable=False)
    
    guideline_set = relationship("DmGuidelineSet", back_populates="intro_chars_show_fields")

class RuleSet(Base):
    """Rule sets for game mechanics."""
    __tablename__ = "rule_sets"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    rules_json = Column(JSON, nullable=True)
    
class WorldState(Base):
    """Current world state."""
    __tablename__ = "world_states"
    
    id = Column(Integer, primary_key=True)
    current_event = Column(Text, nullable=True)
    active_effects_json = Column(JSON, nullable=True)
    current_day = Column(Integer, default=1)
    weather = Column(String, nullable=True)
    time_of_day = Column(String, default="morning")
    season = Column(String, default="spring")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)