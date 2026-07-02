from models import characters as character_model
from utils.constants import MAX_CHARACTERS
from models import pending_characters as pending_model


def submit_character_service(
    user_id: str,
    name: str,
    race: str,
    age: int,
    gender: str,
    appearance: str,
    personality: str,
    backstory: str,
    image_url: str,
):
    characters = character_model.get_characters(user_id)

    if len(characters) >= MAX_CHARACTERS:
        return False, f"Character limit reached ({MAX_CHARACTERS})."

    pending = pending_model.create_pending_character(
        user_id=user_id,
        name=name,
        race=race,
        age=age,
        gender=gender,
        appearance=appearance,
        personality=personality,
        backstory=backstory,
        image_url=image_url,
    )

    return True, pending[0]


def approve_character_service(pending_id: int):
    pending = pending_model.get_pending_by_id(pending_id)
    if not pending:
        return False, "Pending character not found."

    pending = pending[0]

    if pending.get("is_processing"):
        return False, "Already being processed."

    pending_model.set_processing(pending_id, True)

    try:
        created = character_model.create_character(
            user_id=pending["user_id"],
            name=pending["name"],
            race=pending["race"],
            age=pending["age"],
            gender=pending["gender"],
            appearance=pending["appearance"],
            personality=pending["personality"],
            backstory=pending["backstory"],
            image_url=pending["image_url"],
        )

        pending_model.delete_pending_character(pending_id)

        return True, created[0]

    finally:
        pending_model.set_processing(pending_id, False)

def reject_character_service(pending_id: int):
    pending = pending_model.get_pending_by_id(pending_id)
    if not pending:
        return False, "Pending character not found."

    pending = pending[0]

    if pending.get("is_processing"):
        return False, "Already being processed."

    pending_model.set_processing(pending_id, True)

    try:
        pending_model.delete_pending_character(pending_id)
        return True, "Character rejected."
    finally:
        pending_model.set_processing(pending_id, False)

def get_user_characters_service(user_id: str):
    return character_model.get_characters(user_id)

def get_pending_characters_service(user_id: str):
    return pending_model.get_pending_characters(user_id)