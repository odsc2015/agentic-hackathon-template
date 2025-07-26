from google import genai
from google.genai import types
from pydantic import BaseModel
import json
from dotenv import load_dotenv
import os
from sentence_transformers import SentenceTransformer, util
import torch 

load_dotenv()

class JobDetails(BaseModel):
    title: str
    desc: str
    skills: list[str]

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(
    api_key=os.getenv("api_key")
)


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


def find_best_candidate(job_skills: list[str], all_users: list[dict], job_details):
    """
    Finds the best matching user for a job based on skill similarity using sentence embeddings.

    This function does not use any generative AI or Streamlit functions. It vectorizes the
    skills for the job and for each user, then calculates the cosine similarity to find the
    closest match.

    Args:
        job_skills (list[str]): A list of skills required for the job.
        all_users (list[dict]): A list of user objects (as dictionaries). Each dictionary
                                 is expected to have a 'preferences' key, which in turn
                                 contains a 'learning_interests' list of skills.

    Returns:
        dict | None: The user dictionary of the best matching candidate, or None if the
                     input list of users is empty or no valid users with skills are found.
    """
    if not all_users or not job_skills:
        return None

    # 1. Load a pre-trained sentence-transformer model.
    # 'all-MiniLM-L6-v2' is a good balance of speed and performance.
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # 2. Prepare and embed the target job skills.
    # We combine the list of skills into a single descriptive string.
    job_skills_text = ", ".join(job_skills)
    job_embedding = model.encode(job_skills_text, convert_to_tensor=True)

    # 3. Prepare and embed the skills for each user.
    user_skill_texts = []
    valid_users = [] # Keep track of users who actually have skills listed

    for user in all_users:
        # Access skills, handling cases where keys might be missing
        user_skills = user.get("preferences", {}).get("learning_interests", [])
        
        if user_skills:
            user_skill_texts.append(", ".join(user_skills))
            valid_users.append(user)

    # If no users have any skills, we cannot find a match.
    if not valid_users:
        return None

    # Create embeddings for all valid users in a single batch for efficiency
    user_embeddings = model.encode(user_skill_texts, convert_to_tensor=True)

    # 4. Compute cosine similarity between the job embedding and all user embeddings.
    # This will give a score for each user indicating how similar their skills are to the job's requirements.
    cosine_scores = util.cos_sim(job_embedding, user_embeddings)

    # 5. Find the user with the highest score.
    # The scores are in a tensor of shape (1, num_users), so we access the first row.
    best_match_index = torch.argmax(cosine_scores[0]).item()
    best_match_user = valid_users[best_match_index]
    response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[
        f'Generate a concise report detailing why this candidate ```{best_match_user}``` is approrpiate for this job: {job_details}',
        ]
    )
    return response.text