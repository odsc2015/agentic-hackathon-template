from google import genai
from google.genai import types
from pydantic import BaseModel
import json
from dotenv import load_dotenv
import os

load_dotenv()

class JobDetails(BaseModel):
    title: str
    desc: str
    skills: list[str]

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(
    api_key=os.getenv("api_key")
)

# response = client.models.generate_content(
#     model="gemini-2.5-flash", contents="Explain how AI works in a few words"
# )
# print(response.text)



# with open('src/job-test.png', 'rb') as f:
#     image_bytes = f.read()

# response = client.models.generate_content(
# model='gemini-2.5-flash',
# contents=[
#     types.Part.from_bytes(
#     data=image_bytes,
#     mime_type='image/jpeg',
#     ),
#     'Extract job details',
#     ],
#     config={
#         "response_mime_type": "application/json",
#         "response_schema": JobDetails
#     }
# )

# print(response.text)

def extract_details_from_img(image_bytes: bytes, mime_type: str):
    """
    Analyzes an image of a job description using the Gemini API 
    and returns structured job details as a JSON object.

    Args:
        image_bytes: The image data in bytes.
        mime_type: The MIME type of the image (e.g., 'image/jpeg').

    Returns:
        A dictionary containing the extracted job details (title, company, description, skills)
        or None if an error occurs.
    """
    try:

        response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type,
            ),
            'Extract job details',
            ],
            config={
                "response_mime_type": "application/json",
                "response_schema": JobDetails
            }
        )

        # The response.text will be a JSON string, so we parse it into a Python dict
        return json.loads(response.text)

    except Exception as e:
        print(f"An error occurred during AI processing: {e}")
        return None

def extract_details_from_txt(job_desc: str):
    """Analyzes job description text to extract structured details using the Gemini API.

    This function sends a string containing a job description to the Gemini model
    and instructs it to extract key information based on the `JobDetails` Pydantic
    schema. The model's output is expected to be a JSON object, which is then
    parsed into a Python dictionary.

    Args:
        job_desc (str): The raw text of the job description to be analyzed.

    Returns:
        dict | None: A dictionary containing the structured job details (title,
        company, description, skills) if the API call is successful. 
        Returns None if an error occurs during the API call or processing.
    """
    try:
        response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=[
            f"Extract job details from the following: ```{job_desc}```",
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": JobDetails
        }
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"An error occurred during AI processing: {e}")
        return None