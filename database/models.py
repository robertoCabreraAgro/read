from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# --- Modelos de Lore y Reglas ---

class CultivationRealm(Base):
    __tablename__ = "cultivation_realms"
    id = Column(Integer, primary_key=True, index=True)
    realm_order = Column(Integer, default=0)
    name = Column(String, nullable=False)
    level_range = Column(String, nullable=True)
    theme = Column(Text, nullable=True)
    estado = Column(String, nullable=True)
    subetapa = Column(String, nullable=True)
    exp = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<CultivationRealm(name='{self.name}')>"

# --- Modelo de Secta ---

class Sect(Base):
    __tablename__ = "sects"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    ciudad_origen_id = Column(Integer)
    fundador = Column(String)
    alineamiento = Column(String)
    especialidad = Column(JSON)
    reputacion = Column(String)
    requisitos_ingreso = Column(String)

# --- Modelo de Personaje ---

class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    level = Column(Integer, default=1)
    character_class = Column(String)
    subclass = Column(String)
    race = Column(String)
    alignment = Column(String)
    background = Column(String)
    experience_points = Column(Integer)
    proficiency_bonus = Column(Integer)
    status = Column(JSON)
    attributes = Column(JSON)
    attribute_modifiers = Column(JSON)
    saving_throws_proficiencies = Column(JSON)
    skills = Column(JSON)
    skill_proficiencies = Column(JSON)
    languages = Column(JSON)
    features_traits = Column(JSON)
    spellcasting = Column(JSON)
    attacks_ids = Column(JSON)
    inventory_ids = Column(JSON)
    affinity_ids = Column(JSON)
    afiliaciones_ids = Column(JSON)
    condiciones_ids = Column(JSON)
    estado_actual = Column(String)
    custom_data = Column(JSON)

# --- Modelo de NPC ---

class Npc(Base):
    __tablename__ = "npcs"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    tipo = Column(String)
    nivel = Column(Integer)
    rol = Column(String)
    afiliaciones_ids = Column(JSON)
    ciudad_origen_id = Column(Integer)
    estado_actual = Column(String)
    condiciones_ids = Column(JSON)
    caracteristicas = Column(JSON)
    idiomas = Column(JSON)
    personalidad = Column(String)
    notas = Column(Text)

# --- Modelo de Técnica ---

class Technique(Base):
    __tablename__ = "techniques"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    nombre_chino = Column(String)
    elemento = Column(String)
    rango = Column(String)
    version = Column(String)
    nivel = Column(Integer)
    efecto = Column(Text)
    daño = Column(String)
    defensa = Column(String)
    daño_detonacion = Column(String)
    daño_continuo = Column(String)
    daño_explosion = Column(String)
    mana_cost_inicial = Column(Integer)
    costo_micronucleo = Column(String)

# --- Modelo de Afinidad ---

class Affinity(Base):
    __tablename__ = "affinities"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    filosofia = Column(String)
    efectos_comunes = Column(JSON)

# --- Modelo de Afinidad de Personaje ---

class CharacterAffinity(Base):
    __tablename__ = "character_affinities"
    id = Column(Integer, primary_key=True)
    personaje_id = Column(Integer)
    elemento_id = Column(Integer)
    nivel_afinidad = Column(String)
    dominancia_actual = Column(Boolean)
    notas = Column(Text)

# --- Modelo de Afiliación ---

class Affiliation(Base):
    __tablename__ = "affiliations"
    id = Column(Integer, primary_key=True)
    origen_id = Column(Integer)
    origen_tipo = Column(String)
    objetivo_id = Column(Integer)
    objetivo_tipo = Column(String)
    estado = Column(String)
    reputacion = Column(Integer)
    notas = Column(Text)

# --- Modelo de Estado/Condición ---

class Condition(Base):
    __tablename__ = "conditions"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    tipo = Column(String)
    efectos_mecanicos = Column(JSON)

# --- Modelo de Evento Narrativo ---

class NarrativeEvent(Base):
    __tablename__ = "narrative_events"
    id = Column(Integer, primary_key=True)
    nombre_campaña = Column(String)
    session = Column(JSON)

# --- Modelo de Elemento ---

class Element(Base):
    __tablename__ = "elements"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    filosofia = Column(String)
    efectos_comunes = Column(JSON)

# --- Modelo de Inventario ---

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer)
    item_name = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    description = Column(Text)
    is_equipped = Column(Boolean, default=False)

class Enemy(Base):
    __tablename__ = "enemies"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    tipo = Column(String)
    rango = Column(String)
    nivel_desafio = Column(String)
    pv = Column(Integer)
    ac = Column(Integer)
    velocidad = Column(Integer)
    ataques_ids = Column(JSON)
    afinidad_ids = Column(JSON)
    idiomas = Column(JSON)
    notas = Column(Text)
