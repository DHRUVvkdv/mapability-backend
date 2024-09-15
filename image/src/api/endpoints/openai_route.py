from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from core.config import settings
from openai import OpenAI
from services.user_service import UserService
from services.accessibility_service import plan_itinerary
from models.user_model import UserResponse

router = APIRouter()

DISABILITIES = {
    0: "Speech or Language Disorder",
    1: "Deaf or Hard of Hearing",
    2: "Mental Health Condition",
    3: "Autism Spectrum Disorder",
    4: "Chronic Pain",
    5: "Visual Impairment",
    6: "Cerebral Palsy",
    7: "Multiple Sclerosis",
    8: "Mobility Impairment",
    9: "Dyslexia",
}


async def get_openai_client():
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def process_disabilities(disabilities):
    return [
        DISABILITIES[i]
        for i, has_disability in enumerate(disabilities)
        if has_disability
    ]


@router.post("/test-openai")
async def test_openai_connection():
    try:
        client = await get_openai_client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, OpenAI!"},
            ],
        )
        return JSONResponse(
            content={
                "message": "OpenAI connection successful",
                "response": response.choices[0].message.content,
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error connecting to OpenAI: {str(e)}"
        )


@router.post("/plan-day/{user_id}")
async def plan_day(
    user_id: str, prompt: str, client: OpenAI = Depends(get_openai_client)
):
    try:
        # Fetch user information from the database
        user = await UserService.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Process user's disabilities
        user_disabilities = process_disabilities(user.disabilities)

        # Plan the itinerary based on the user's prompt and disabilities
        itinerary = plan_itinerary(prompt, user_disabilities)

        # Use OpenAI to generate a response about the planned itinerary
        itinerary_description = ", ".join(
            [f"{item['activity']} at {item['place']}" for item in itinerary]
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant providing information about a user's planned day, considering their disabilities.",
                },
                {
                    "role": "user",
                    "content": f"Provide a brief summary of the following itinerary, considering the user has these disabilities: {', '.join(user_disabilities)}. Itinerary: {itinerary_description}",
                },
            ],
        )

        # Combine the itinerary with the OpenAI response
        return JSONResponse(
            content={
                "user_id": user_id,
                "prompt": prompt,
                "disabilities": user_disabilities,
                "itinerary": itinerary,
                "ai_summary": response.choices[0].message.content,
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )
