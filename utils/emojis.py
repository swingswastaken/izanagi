HEAD = "<:limbus_heads:1463921098394439774>"
TAIL = "<:limbus_tails:1463921048704647188>"
UNBREAKABLE_HEAD = "<:limbus_unbreakable_heads:1463921190228721684>"
UNBREAKABLE_TAIL = "<:limbus_unbreakable_tails:1463921283946512566>"
UNBREAKABLE_CRACKED_HEAD = "<:limbus_cracked_unbreakable_heads:1508202401620955378>"
UNBREAKABLE_CRACKED_TAIL = "<:limbus_cracked_unbreakable_tails:1508202503349469264>"

EMOJIS_ATK_TYPE = {
"SLASH": "<:Slash:1522219386553893004>",
"PIERCE": "<:Pierce:1522219452081377363>",
"BLUNT": "<:Blunt:1522219327246569674>"
}

EMOJIS_ROLE = {
    "GUARD": "<:Guard:1522249542232445162>",
    "EVADE": "<:Evade:1522249608473083975>",
    "COUNTER": "<:Counter:1522249683228037190>"
}   

EMOJIS_SIN = {
    "WRATH": "<:Wrath:1522217247924420758>",
    "LUST": "<:Lust:1522217675257020477>",
    "SLOTH": "<:Sloth:1522218057508978878>",
    "GLUTTONY": "<:Gluttony:1522218412753813705>",
    "GLOOM": "<:Gloom:1522218451827949628>",
    "PRIDE": "<:Pride:1522218559005003808>",
    "ENVY": "<:Envy:1522218636549554256>" 
}

# helper function for emojis
def get_skill_emojis(attack_type=None, sin_affinity=None, role=None):

    role = (role or "").upper()
    attack_type = (attack_type or "").upper()
    sin_affinity = (sin_affinity or "").upper()

    emoji_part = ""

    # Role emoji has priority
    if role and role in EMOJIS_ROLE:
        emoji_part += EMOJIS_ROLE[role]

    # If no role emoji, fallback to attack type emoji
    elif attack_type and attack_type in EMOJIS_ATK_TYPE:
        emoji_part += EMOJIS_ATK_TYPE[attack_type]

    sin_emoji = EMOJIS_SIN.get(sin_affinity, "")

    return emoji_part, sin_emoji
