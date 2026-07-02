from database import supabase

def get_pending_characters(user_id: str):
    response = (
        supabase
        .table("pending_characters")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    return response.data


def create_pending_character(
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
    response = (
        supabase
        .table("pending_characters")
        .insert({
            "user_id": user_id,
            "name": name,
            "race": race,
            "age": age,
            "gender": gender,
            "appearance": appearance,
            "personality": personality,
            "backstory": backstory,
            "image_url": image_url,
        })
        .execute()
    )

    return response.data


def delete_pending_character(pending_id: int):
    response = (
        supabase
        .table("pending_characters")
        .delete()
        .eq("pending_id", pending_id)
        .execute()
    )

    return response.data

def set_processing(pending_id: int, value: bool):
    return (
        supabase
        .table("pending_characters")
        .update({"is_processing": value})
        .eq("pending_id", pending_id)
        .execute()
    )