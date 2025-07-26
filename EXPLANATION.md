Technical Explanation: London Aid & Growth Navigator AI Agent

This document details the technical architecture and workflow of the London Aid & Growth Navigator AI Agent, a Streamlit application designed to assist users with essential services and career/educational guidance by leveraging AI models and a Firestore database.



1. Agent Workflow

The application employs an agentic workflow primarily for two key functionalities: job skill matching and educational path generation.



1.1 Job Skill Matching Workflow (via "Add Job" tab):



Receive User Input: The Streamlit UI (app.py) captures job description input, either as an uploaded image (.png, .jpg, .jpeg) or as raw text.



Extract Structured Details (LLM Tool Call):



If an image is uploaded, app.py calls executor.extract_details_from_img(). This function uses the Gemini API (gemini-2.5-flash model) with types.Part.from_bytes to perform image understanding and extract structured job details (title, description, skills) based on a Pydantic schema (JobDetails).



If text is pasted, app.py calls executor.extract_details_from_txt(). This function uses the Gemini API (gemini-2.5-flash model) to perform text understanding and extract the same structured job details.



Retrieve User Data: The app.py orchestrator loads all existing user profiles (individuals) from the Firestore database via load_all_data_cached().



Find Best Candidate (Embedding & LLM Tool Call):



app.py calls executor.find_best_candidate(), passing the extracted job skills and all user profiles.



Inside find_best_candidate(), a Sentence Transformer model (all-MiniLM-L6-v2) is loaded to create vector embeddings for both the job's required skills and each user's learning interests.



Cosine similarity is computed (using torch.util.cos_sim) to find the user whose skills are most similar to the job requirements.



Finally, the Gemini API (gemini-2.5-flash model) is called again to generate a concise report detailing why the best-matched candidate is appropriate for the job, providing a natural language explanation of the match.



Summarize and Return Final Output: The generated candidate recommendation report is displayed in the Streamlit UI.



1.2 Educational Path Generation Workflow (via "Generate Path" tab):



Select User Profile: The Streamlit UI allows the user to select an existing individual profile from the Firestore database.



Generate Path (Rule-Based Agent): The PathfinderAgent (defined within app.py) analyzes the selected user's learning interests and available micro-courses and job opportunities (all loaded from Firestore). It generates a path consisting of:



Recommended micro-courses (based on simple keyword matching for interests).



Skills the user would gain from these courses.



Potential job opportunities that match the gained skills.



Save Path: The generated path is saved back to a generated_paths collection in Firestore.



Display Path: The recommended courses, skills, and job opportunities are presented to the user in the UI.



2. Key Modules

The solution is structured around a Streamlit application (app.py) that orchestrates various functionalities, delegating specific AI-powered tasks to an executor module. The "Planner" functionality is implicitly handled within app.py, and the "Memory Store" is primarily managed through Firestore.



Streamlit Application (app.py):



Role: Serves as the primary user interface and the central orchestrator of the agentic workflows.



Functionality:



Handles all user interactions via Streamlit components (input forms, buttons, selections).



Manages the overall application flow across different tabs ("Generate Path," "Create New User," "Add Job").



Establishes and manages the connection to Firestore for all data loading and persistence operations.



Calls specific AI functions from executor.py for tasks like job detail extraction and candidate matching.



Contains the PathfinderAgent class, which implements the rule-based logic for generating educational and career paths.



Directs user requests to the appropriate executor functions or internal logic based on UI interactions and input types, acting as an implicit "planner."



Executor / AI Functions (executor.py):



Role: Contains the core AI-powered functions that interact with external Large Language Models (LLMs) and perform specialized data processing for job matching.



Functionality:



extract_details_from_img(): Utilizes the Gemini API for image understanding to extract structured data from job posting images.



extract_details_from_txt(): Utilizes the Gemini API for text understanding to parse raw job description text into structured data.



find_best_candidate(): Orchestrates the use of Sentence Transformers for skill embedding and cosine similarity for matching, then calls Gemini to generate a human-readable explanation of the candidate match.



This module encapsulates direct calls to AI models, ensuring app.py remains focused on UI and orchestration.



Memory Store (Implemented via Google Cloud Firestore & Streamlit Caching):



Role: Manages the persistence and efficient retrieval of all application data.



Functionality:



Google Cloud Firestore: Serves as the primary, persistent database for all structured data. This includes:



individuals: User profiles with preferences and contact information.



properties: Details on services like shelters, hostels, and food banks.



microcourses: Information on available learning programs.



skills: A catalog of defined skill sets.



jobs: Sample job opportunities used for matching.



generated_paths: Stores the historical output of the PathfinderAgent for individuals.



All public data is stored under the path artifacts/default-app-id/public/data/{collection_name}.



Streamlit Caching (st.cache_data): The load_all_data_cached() function in app.py efficiently loads and caches all necessary data from Firestore into memory. This reduces redundant database reads, significantly improving application responsiveness and acting as a form of in-memory data store for frequently accessed information. The Sentence Transformer embeddings generated by find_best_candidate are also in-memory for the duration of that specific function call.



3. Tool Integration

The agent leverages several external tools and APIs to achieve its functionality, as specified in requirements.txt:



Google Generative AI (Gemini API):



Models Used: gemini-2.5-flash



Integration: Directly called from executor.py using the google.genai client library. The API key is securely loaded via python-dotenv.



Use Cases:



Image Understanding: Used in extract_details_from_img to analyze and extract structured data from visual job descriptions.



Structured Text Extraction: Used in extract_details_from_txt to parse raw text job descriptions into a defined JSON format.



Text Generation/Summarization: Employed within find_best_candidate to generate a concise, natural language report explaining the rationale behind a candidate-job match.



Google Cloud Firestore:



Integration: Used via the google.cloud.firestore Python client library in app.py. Authentication is handled via service account credentials.



Use Cases: Functions as the central, persistent data store for all application entities (users, properties, courses, skills, jobs, generated paths), enabling data loading, saving, and querying.



Sentence Transformers & PyTorch:



Integration: Used within executor.py's find_best_candidate function. torch is a dependency of sentence-transformers.



Use Cases:



Embedding Generation: The SentenceTransformer('all-MiniLM-L6-v2') model is utilized to convert textual descriptions of job skills and user learning interests into high-dimensional numerical vector embeddings.



Semantic Similarity: torch.util.cos_sim computes the cosine similarity between these embeddings, allowing for a robust, semantic matching of skills between jobs and individuals.



4. Observability & Testing

Logging:



The application provides real-time feedback and debugging information directly within the Streamlit UI using st.success, st.warning, st.error, st.write, st.json, and st.code.



Critical error messages from AI API calls and other processes are printed to the console (e.g., print(f"An error occurred during AI processing: {e}") in executor.py), which are visible in the terminal where the Streamlit app is run.



While explicit file-based logging to a dedicated logs/ directory isn't implemented in the provided code, Streamlit's internal server logs capture application activity.



Testing (TEST.sh):



The TEST.sh script (present at the repository root) serves as a basic, executable smoke test.



It's designed to automate a fundamental execution path of the application or its core components. This provides a quick verification mechanism for developers and judges to confirm the agent's basic operational integrity.



5. Known Limitations

Implicit Planning & Agentic Depth: The "planning" logic is currently tightly coupled with the Streamlit UI's flow and conditional statements within app.py. There isn't a dedicated, explicit planner.py module or a dynamic, LLM-driven reasoning loop (e.g., a multi-step ReAct chain) for handling complex, multi-turn, or highly ambiguous user requests. The agent's "agentic" nature is more about tool invocation based on direct user intent rather than complex internal reasoning.



Limited Conversational Memory: While user profiles and generated paths are persistently stored in Firestore, the application does not maintain a sophisticated, real-time conversational history or context across multiple user turns within a single session. This limits the agent's ability to engage in nuanced, follow-up dialogues.



Skill Matching in PathfinderAgent: The PathfinderAgent's course recommendation logic (in app.py) relies on simple string contains matching for user learning interests against course titles. This is less semantically robust than the embedding-based matching used for job-candidate pairing in executor.py and could lead to less precise course recommendations.



Data Freshness: The system operates on data pre-populated in Firestore. There is no mechanism for real-time updates from external sources (e.g., live shelter bed availability, real-time job postings), which would be critical for a production application providing up-to-the-minute information.



Location Accuracy: The current location services are simulated using fixed KIOSK_LAT and KIOSK_LON and the Haversine formula for distance. For real-world deployment, integration with a dynamic geolocation service (e.g., Google Maps API) would be essential for accurate user proximity to services.



Error Handling Granularity: While try-except blocks are present for API calls, more granular and user-friendly error handling (e.g., specific messages for different types of API failures, graceful degradation) could be implemented for a more robust user experience.

