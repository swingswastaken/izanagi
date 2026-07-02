from database import supabase


def get_user(user_id: str):
    response = (
        supabase
        .table("users")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    return response.data


def create_user(user_id: str, username: str):
    response = (
        supabase
        .table("users")
        .insert({
            "user_id": user_id,
            "username": username,
        })
        .execute()
    )

    return response.data