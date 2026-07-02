from database import supabase

def get_characters(user_id: str):
    response = (
        supabase
        .table("characters")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    return response.data

def get_character(character_id: int):
    response = (
        supabase
        .table("characters")
        .select("*")
        .eq("character_id", character_id)
        .execute()
    )

    return response.data

def create_character(
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
        .table("characters")
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

# update_character(...)

 # delete_character(character_id)





