from django.conf import settings
from google import genai


def generate_recipe_recommendations(ingredients):
    """
    Generate recipe recommendations based on ingredients supplied by the user.
    """

    if not settings.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is not configured.")

    client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    prompt = f"""
You are an AI recipe recommendation assistant.

The user currently has these ingredients:

{ingredients}

Suggest 3 practical recipes that can be prepared mainly using these ingredients.

For each recipe provide:

Recipe Name:
Ingredients:
Cooking Time:
Difficulty:
Instructions:

Use common basic ingredients such as salt, water, oil, and spices when necessary.

Do not suggest recipes requiring many major ingredients that the user did not provide.

Make the cooking instructions clear and beginner-friendly.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    if not response.text:
        return "No recipe recommendations were generated."

    return response.text