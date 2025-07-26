import streamlit as st
import pandas as pd
import os
from google.cloud import firestore
from google.oauth2 import service_account
import json
import time
from executor import extract_details_from_img, extract_details_from_txt, find_best_candidate

# --- Firestore Connection ---

def get_firestore_client():
    """Connects to Firestore using service account credentials."""
    creds_path = os.path.join("src/.streamlit", "firestore-creds.json")
    if os.path.exists(creds_path):
        with open(creds_path) as f:
            creds_json = json.load(f)
        creds = service_account.Credentials.from_service_account_info(creds_json)
        return firestore.Client(credentials=creds, project=creds.project_id)
    else:
        try:
            creds = service_account.Credentials.from_service_account_info(st.secrets["firestore"])
            return firestore.Client(credentials=creds, project=st.secrets["firestore"]["project_id"])
        except (KeyError, FileNotFoundError):
            st.error("Firestore credentials not found. Please ensure `.streamlit/firestore-creds.json` is correct.")
            return None

db = get_firestore_client()

# --- Data Loading from Firestore (Corrected Caching) ---

# This function is NO LONGER cached individually.
def load_single_collection(_collection_name):
    """Loads a single collection from Firestore."""
    if db is None: return pd.DataFrame()
    
    collection_ref = db.collection(f"artifacts/default-app-id/public/data/{_collection_name}")
    docs = collection_ref.stream()
    data_list = [doc.to_dict() for doc in docs]
    return pd.DataFrame(data_list)

# The CACHE is now applied to the function that loads ALL data.
@st.cache_data(ttl=300)
def load_all_data_cached():
    """Loads all necessary collections from Firestore and caches the result."""
    collections_to_load = ["individuals", "properties", "microcourses", "skills", "jobs"]
    data = {name: load_single_collection(name) for name in collections_to_load}
    
    # Add sample jobs if the collection is empty or doesn't exist
    if 'jobs' not in data or data['jobs'].empty:
        data['jobs'] = pd.DataFrame([
            {"job_id": "JOB001", "job_title": "Part-Time Administrative Assistant", "required_skills": ["SKILL002", "SKILL009", "SKILL020"]},
            {"job_id": "JOB002", "job_title": "Entry-Level IT Support", "required_skills": ["SKILL001", "SKILL018"]},
        ])
    return data

# --- Agentic Workflow ---
# (No changes needed in this class)
class PathfinderAgent:
    """Agent for generating educational and career paths."""
    def __init__(self, data):
        self.data = data

    def get_user_profile(self, individual_id):
        user_profile_df = self.data["individuals"][self.data["individuals"]["individual_id"] == individual_id]
        return user_profile_df.to_dict('records')[0] if not user_profile_df.empty else None

    def generate_educational_path(self, user_profile):
        if not user_profile: return None
        user_interests = user_profile.get("preferences", {}).get("learning_interests", [])
        recommended_courses = []
        microcourses_df = self.data.get("microcourses", pd.DataFrame())
        COURSE_TITLE_COLUMN = 'course_title'

        if not microcourses_df.empty and COURSE_TITLE_COLUMN in microcourses_df.columns:
            for interest in user_interests:
                # This logic checks if any word from the interest matches in the course title.
                # A better long-term solution would be to use skill_ids for matching.
                mask = microcourses_df[COURSE_TITLE_COLUMN].astype(str).str.contains(interest, case=False, na=False)
                matching_courses = microcourses_df[mask]
                if not matching_courses.empty:
                    recommended_courses.extend(matching_courses.to_dict('records'))
        else:
             st.warning(f"Warning: The '{COURSE_TITLE_COLUMN}' column was not found in the 'microcourses' data.")

        gained_skill_ids = set()
        for course in recommended_courses:
            for skill_id in course.get("skill_ids", []):
                gained_skill_ids.add(skill_id)

        all_skills = self.data.get("skills", pd.DataFrame())
        gained_skills = []
        if not all_skills.empty and 'skill_id' in all_skills.columns:
            gained_skills = all_skills[all_skills["skill_id"].isin(list(gained_skill_ids))].to_dict('records')

        job_opportunities = []
        all_jobs = self.data.get("jobs", pd.DataFrame())
        if not all_jobs.empty and 'required_skills' in all_jobs.columns:
            for _, job in all_jobs.iterrows():
                if set(job.get("required_skills", [])).issubset(gained_skill_ids):
                    job_opportunities.append(job.to_dict())

        return {
            "individual_id": user_profile["individual_id"],
            "recommended_courses": recommended_courses,
            "gained_skills": gained_skills,
            "job_opportunities": job_opportunities,
            "generated_at": firestore.SERVER_TIMESTAMP
        }


# --- Data Persistence Functions ---

def save_new_individual(name, email, interests, location_id):
    """Saves a new individual to the Firestore database."""
    if db is None: return
    
    individuals_ref = db.collection("artifacts/default-app-id/public/data/individuals")
    new_doc_ref = individuals_ref.document()
    
    new_individual_data = {
        "individual_id": new_doc_ref.id,
        "contact_name": name,
        "contact_email": email,
        "assigned_location_id": location_id, # <-- NEWLY ADDED
        "preferences": { "learning_interests": interests, "past_experiences": [] },
        "notes": "Newly created user.",
        "enrollment_date": firestore.SERVER_TIMESTAMP
    }
    
    new_doc_ref.set(new_individual_data)
    st.cache_data.clear() # Clear the entire cache to force a reload

def save_generated_path(path_data):
    """Saves a generated path to the 'generated_paths' collection."""
    if db is None: return
    paths_ref = db.collection("artifacts/default-app-id/public/data/generated_paths")
    individual_id = path_data["individual_id"]
    paths_ref.document(individual_id).set(path_data)


# --- Streamlit UI ---

st.set_page_config(page_title="Hope Pathways", layout="wide")
st.title("🏡 Hope Pathways: From Housing to Career")

if db:
    # Call the new cached function to load all data
    data = load_all_data_cached()
    agent = PathfinderAgent(data)

    with st.expander("Click here to see the actual column names loaded from Firestore"):
        st.write("`individuals` columns:", data.get("individuals", pd.DataFrame()).columns.tolist())
        st.write("`properties` columns:", data.get("properties", pd.DataFrame()).columns.tolist())
        st.write("`microcourses` columns:", data.get("microcourses", pd.DataFrame()).columns.tolist())
        st.write("`skills` columns:", data.get("skills", pd.DataFrame()).columns.tolist())


    tab1, tab2, tab3 = st.tabs(["👣 Generate Path", "➕ Create New User", "💼 Add Job"])

    # The rest of the UI code remains the same
    with tab1:
        st.header("Select an Individual to Generate a Path")
        individuals_df = data.get("individuals", pd.DataFrame())
        if individuals_df.empty or 'contact_name' not in individuals_df.columns:
             st.warning("No individuals found. Please add a new user in the 'Create New User' tab.")
        else:
            individual_names = individuals_df["contact_name"].tolist()
            selected_name = st.selectbox("Choose a person:", individual_names, key="path_user_select")
            
            if selected_name:
                selected_id = individuals_df[individuals_df["contact_name"] == selected_name]["individual_id"].values[0]
                user_profile = agent.get_user_profile(selected_id)

                st.subheader(f"Profile for: {user_profile['contact_name']}")
                st.write(f"**Learning Interests:** {', '.join(user_profile.get('preferences', {}).get('learning_interests', ['N/A']))}")
                
                if st.button("Generate & Save Educational Path", key="generate_path"):
                    with st.spinner("Agent is generating a personalized path..."):
                        path = agent.generate_educational_path(user_profile)
                        
                        if not path or not path["recommended_courses"]:
                            st.error("Could not generate a path. The user may not have learning interests, or no matching courses were found.")
                        else:
                            save_generated_path(path)
                            st.success(f"Path successfully generated and saved for {user_profile['contact_name']}!")
                            
                            st.subheader("Step 1: Recommended Micro-Courses")
                            for course in path["recommended_courses"]:
                                st.markdown(f"- **{course.get('course_title', 'N/A Title')}** by {course.get('provider_name', 'N/A')}")

                            st.subheader("Step 2: Skills You Will Gain")
                            st.markdown(" ".join([f"`{skill.get('skill_name', 'N/A')}`" for skill in path["gained_skills"]]))

                            st.subheader("Step 3: Potential Job Opportunities")
                            if not path["job_opportunities"]:
                                st.info("Complete the recommended courses to unlock job opportunities.")
                            else:
                                for job in path["job_opportunities"]:
                                    st.markdown(f"- **{job.get('job_title', 'N/A')}**")
    with tab2:
        st.header("Create a New Individual Profile")
        with st.form("new_user_form", clear_on_submit=True):
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")

            # --- UPDATED: Dynamic Location Dropdown ---
            properties_df = data.get("properties", pd.DataFrame())
            selected_location_name = None
            if not properties_df.empty and 'name' in properties_df.columns:
                location_names = sorted(properties_df["name"].dropna().unique().tolist())
                all_locations = ["None"] + location_names
                selected_location_name = st.selectbox("Assign to a Location (Optional)", all_locations)
            else:
                st.info("No locations found in the database to assign.")

            # --- UPDATED: Dynamic Skills Multiselect ---
            skills_df = data.get("skills", pd.DataFrame())
            if not skills_df.empty and 'skill_name' in skills_df.columns:
                available_interests = sorted(skills_df['skill_name'].dropna().unique().tolist())
            else:
                available_interests = [] # Default to empty list if no skills are found
            interests = st.multiselect("Select Learning Interests", available_interests)
            
            submitted = st.form_submit_button("Save New User")
            if submitted:
                if name and email and interests:
                    location_id = None
                    # Find the property_id for the selected location name
                    if selected_location_name and selected_location_name != "None":
                        location_id = properties_df[properties_df["name"] == selected_location_name]["property_id"].values[0]

                    with st.spinner("Saving new user..."):
                        save_new_individual(name, email, interests, location_id) # Pass the new location_id
                        st.success(f"Successfully created user: {name}")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.warning("Please fill out all fields.")
    with tab3:
        st.header("Add a New Job Opportunity")
        st.write("Upload a screenshot of a job posting or paste the full text description below.")

        with st.form("new_job_form"):
            # Input for Image Upload
            uploaded_file = st.file_uploader(
                "Upload Job Description Image",
                type=['png', 'jpg', 'jpeg'],
                help="Upload a clear screenshot of the entire job posting."
            )

            st.markdown("---") # Visual separator

            # Input for Text
            job_text = st.text_area(
                "Or Paste Job Description Text Here",
                height=250,
                placeholder="e.g., 'Job Title: Administrative Assistant\nCompany: Acme Corp\nSkills: Microsoft Office, Data Entry...'"
            )

            # Submit button for the form
            submitted = st.form_submit_button("Extract Job Details")

            if submitted:
                # --- Logic to handle the submitted data ---
                # Case 1: User uploaded a file
                if uploaded_file is not None:
                    # Ensure text area is empty to avoid confusion
                    if job_text:
                        st.warning("Please provide either an image OR text, not both. The image will be processed.")
                    
                    with st.spinner("Analyzing image with agentic workflow..."):
                        # Read the image bytes from the uploaded file
                        image_bytes = uploaded_file.getvalue()

                        st.success("Image received! Ready for processing.")
                        st.image(image_bytes, caption="Uploaded Job Description")

                        extracted_details = extract_details_from_img(image_bytes=image_bytes, mime_type="image/jpeg")
                        st.success("Successfully extracted details from image!")
                        st.json(extracted_details) # Display extracted details
                        st.json(extracted_details["skills"])
                        

                # Case 2: User pasted text
                elif job_text:
                    with st.spinner("Analyzing text with agentic workflow..."):
                        
                        st.success("Text received! Ready for processing.")
                        st.code(job_text, language="text")
                        
                        extracted_details = extract_details_from_txt(job_text)
                        st.success("Successfully extracted details from text!")
                        st.json(extracted_details) # Display extracted details

                        st.json(extracted_details["skills"])

                        # 2. Load all your user data (you already do this with load_all_data_cached)
                        all_users_df = data.get("individuals", pd.DataFrame())
                        # Convert DataFrame to list of dictionaries for the function
                        all_users_list = all_users_df.to_dict('records')

                        # 3. Call the function to get the best match
                        if all_users_list:
                            best_candidate = find_best_candidate(extracted_details["skills"], all_users_list, extracted_details)

                            if best_candidate:
                                st.subheader("Top Candidate Recommendation")
                                # st.success(f"The best match for this job is **{best_candidate['contact_name']}**.")
                                
                                # You can display more details about the candidate here
                                # candidate_skills = best_candidate.get("preferences", {}).get("learning_interests", [])
                                st.write(best_candidate)
                            else:
                                st.warning("Could not find a suitable candidate. No users with relevant skills were found.")
                        else:
                            st.info("No users in the database to match against.")

                # Case 3: User submitted the form empty
                else:
                    st.error("Please upload an image or paste the job description text.")

else:
    st.error("Could not connect to the database. Please check your Firestore credentials setup.")