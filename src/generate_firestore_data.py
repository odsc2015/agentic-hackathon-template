# src/generate_firestore_data.py

import json
import random
from datetime import datetime, timedelta
from geopy.distance import geodesic
from geopy.point import Point
import os
import math # Import math for math.cos

# --- Configuration for Data Generation ---
NUM_INDIVIDUALS = 10
NUM_PROPERTIES = 20 # Shelters/Hostels
NUM_SKILLS = 25
NUM_MICROCOURSES = 25 # Corrected to match the number of titles in MICROCOURSE_TITLES

OUTPUT_DIR = 'src/data' # Directory to save JSON files

# Define a few central London points to base our synthetic data around for realism
# These are approximate centroids for various London areas
LONDON_CENTRAL_POINTS = [
    Point(51.5074, -0.1278), # Westminster
    Point(51.5150, -0.1419), # Oxford Circus
    Point(51.5323, -0.0769), # Shoreditch
    Point(51.4939, -0.1989), # Kensington
    Point(51.4632, -0.0638), # Greenwich
    Point(51.5450, -0.0734), # Islington
    Point(51.5045, -0.0865), # Southwark
    Point(51.5098, -0.1180)  # Covent Garden
]

# --- Common Data Lists for Realism ---

SHELTER_NAMES = [
    "Hope Haven Night Shelter", "St. Jude's Community Hostel", "The Compassion House",
    "London Bridge Refuge", "Westminster Outreach Centre", "Camden Safe Space",
    "Islington Crisis Accommodation", "Southwark Sanctuary", "Greenwich Helping Hand",
    "The Haven for All", "City Road Shelter", "Victoria Street Housing",
    "Euston Road Hostel", "Pimlico Place", "Bow Road Shelter", "King's Cross Hostel",
    "Angel Islington Shelter", "Waterloo Wayfarer's Rest", "Canary Wharf Haven", "Stratford Lodge"
]

FOOD_BANK_NAMES = [
    "East London Food Pantry", "Westminster Food Hub", "Southwark Community Kitchen",
    "Camden Food Aid", "Islington Food Bank Plus", "The Daily Bread Project",
    "London Food Rescue", "Borough Market Food Collective", "Greenwich Groceries",
    "The Nourish Network", "City Harvest London", "Victoria Food Support",
    "Euston Food Distribution", "Pimlico Pantry", "Bow Food Station", "King's Cross Kitchen",
    "Angel Food Centre", "Waterloo Food Share", "Canary Wharf Food Stop", "Stratford Meals"
]

SKILL_NAMES = [
    "Basic IT Literacy", "Microsoft Office Suite", "Customer Service Excellence",
    "Digital Marketing Fundamentals", "Web Development (HTML/CSS)", "Data Entry",
    "English Language Skills", "CV Writing & Interview Prep", "Financial Literacy",
    "Health & Safety in Construction", "Food Hygiene Certificate", "Basic Coding (Python)",
    "Project Management Basics", "Time Management", "Communication Skills",
    "Critical Thinking", "Problem Solving", "Teamwork & Collaboration",
    "Social Media Management", "Graphic Design Basics", "Cybersecurity Awareness",
    "Cloud Computing Fundamentals", "Mobile App Development (Basic)", "Networking Basics",
    "Public Speaking"
]

MICROCOURSE_TITLES = [
    "Intro to Word & Excel", "Customer Service Essentials", "Build Your First Website",
    "Digital Marketing for Beginners", "Python for Absolute Beginners", "Effective CVs & Cover Letters",
    "Budgeting & Saving", "Health & Safety at Work", "Food Safety Level 1",
    "Advanced Excel Techniques", "Social Media for Business", "Introduction to UX Design",
    "Public Speaking Confidence", "Online Job Search Strategies", "Basic Photography Skills",
    "Mindfulness for Stress Reduction", "Conflict Resolution", "Introduction to AI",
    "Data Analysis with Spreadsheets", "Professional Email Etiquette", "Time Management for Productivity",
    "Introduction to Cloud Platforms", "Basic Mobile App UI Design", "Networking for Career Growth",
    "Interview Skills Workshop"
]

LEARNING_FORMATS = ["Online Self-Paced", "Online Live", "In-Person (Library)", "In-Person (Community Centre)"]
COURSE_COSTS = [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 10.00, 25.00, 50.00] # Mostly free for this context

# Common London street types and suffixes for realistic addresses
STREET_TYPES = ["Road", "Street", "Lane", "Avenue", "Place", "Square", "Gardens", "Walk"]
POSTCODE_PREFIXES = ["EC1", "WC1", "SW1", "SE1", "N1", "NW1", "E1", "W1", "E2", "N7", "SE11", "SW8"] # Expanded for more variety

# --- Helper Functions for Generating Realistic Data ---

def generate_random_london_coordinates(base_point: Point, max_offset_km=7):
    """Generates a random coordinate within a given radius of a base London point."""
    # Access the float value of latitude and longitude directly for calculations
    base_lat = base_point.latitude
    base_lon = base_point.longitude

    # Convert km offset to degrees (approximate for small distances)
    lat_offset_deg = random.uniform(-max_offset_km, max_offset_km) / 111.0
    lon_offset_deg = random.uniform(-max_offset_km, max_offset_km) / (111.0 * math.cos(math.radians(base_lat)))

    new_lat = base_lat + lat_offset_deg
    new_lon = base_lon + lon_offset_deg
    return new_lat, new_lon

def generate_london_address(base_point: Point):
    """Generates a synthetic London address with a plausible postcode."""
    street_number = random.randint(1, 200)
    street_name_part1 = random.choice(["High", "Church", "Park", "Main", "Oak", "Elm", "Station", "Market", "Green", "White"])
    street_name_part2 = random.choice(["Road", "Street", "Lane", "Avenue", "Place", "Square", "Gardens", "Walk", "Close", "Terrace"])
    street_name = f"{street_name_part1} {street_name_part2}"

    # More diverse London postcodes
    postcode_areas = ["SW", "SE", "NW", "N", "E", "W", "WC", "EC"]
    postcode_prefix = random.choice(postcode_areas) + str(random.randint(1, 9))
    postcode_suffix = f"{random.randint(1,9)}{random.choice('ABCDEFGHJKLMNPQRSTUVWXY')}{random.choice('ABCDEFGHJKLMNPQRSTUVWXY')}"
    return f"{street_number} {street_name}, London {postcode_prefix} {postcode_suffix}"

def generate_uk_phone_number():
    """Generates a synthetic UK phone number."""
    return f"020 {random.randint(7000, 8999)} {random.randint(1000, 9999)}"

def generate_email(name_prefix):
    """Generates a synthetic email address."""
    domains = ["example.com", "mail.org", "service.co.uk"]
    return f"{name_prefix.lower().replace(' ', '.')}{random.randint(1, 99)}@{random.choice(domains)}"

def generate_website(name_prefix):
    """Generates a synthetic website URL."""
    return f"https://www.{name_prefix.lower().replace(' ', '').replace('.', '')}.org.uk"

def get_random_date(start_year=2020, end_year=2025):
    """Generates a random date within a given year range."""
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    time_diff = end_date - start_date
    random_days = random.randint(0, time_diff.days)
    return (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")

# --- Individual Data Generation ---

def generate_individual(individual_id):
    """Generates a synthetic individual profile."""
    first_names = ["Alex", "Jamie", "Chris", "Sam", "Pat", "Taylor", "Jordan", "Casey"]
    last_names = ["Smith", "Jones", "Brown", "Williams", "Johnson", "Davies", "Evans", "Wilson"]
    contact_name = f"{random.choice(first_names)} {random.choice(last_names)}"
    gender = random.choice(["Male", "Female", "Non-binary", "Prefer not to say"])
    dob = get_random_date(1970, 2000) # Educated demographic implies adult age range

    # Simulate preferences for matching
    shelter_preferences = random.sample([
        "women_only", "men_only", "family_friendly", "quiet_environment",
        "pet_friendly", "disability_access", "mental_health_support", "no_religious_affiliation"
    ], k=random.randint(1, 3))
    learning_interests = random.sample(SKILL_NAMES, k=random.randint(1, 4))
    past_experiences = random.sample([
        "negative_shelter_experience", "positive_shelter_experience",
        "struggled_with_online_learning", "successful_online_learning"
    ], k=random.randint(0, 1)) # Can be empty

    return {
        "individual_id": f"IND{individual_id:03d}",
        "contact_name": contact_name,
        "contact_email": generate_email(contact_name),
        "contact_phone": generate_uk_phone_number(),
        "date_of_birth": dob,
        "gender": gender,
        "current_address": "Mobile/Temporary (e.g., Library, Day Centre)",
        "enrollment_date": get_random_date(2024, 2025),
        "status": "Active",
        "preferences": {
            "shelter_preferences": shelter_preferences,
            "learning_interests": learning_interests,
            "past_experiences": past_experiences
        },
        "notes": "User has high digital literacy, seeks skill development."
    }

# --- Property (Shelter/Hostel) Data Generation ---

def generate_property(property_id):
    """Generates a synthetic property (shelter/hostel) entry."""
    base_point = random.choice(LONDON_CENTRAL_POINTS)
    lat, lon = generate_random_london_coordinates(base_point)
    property_type = random.choice(["Hostel Room", "Shelter Bed", "Temporary Flat"])
    housing_type = "Temporary"
    capacity = random.randint(5, 50)
    
    # Simulate availability
    availability_status = random.choice(["Available", "Occupied", "Allocated"])
    if availability_status == "Available":
        beds_available = random.randint(1, capacity // 2) # Some beds available
        capacity_info = f"{beds_available} beds available (as of {datetime.now().strftime('%I:%M %p GMT')})."
    elif availability_status == "Occupied":
        capacity_info = "Currently full."
    else: # Allocated
        capacity_info = "Allocated, check back later."

    accessibility_features = random.sample([
        "Wheelchair accessible", "Ground floor", "Lift access", "Sensory friendly"
    ], k=random.randint(0, 2))

    notes_options = [
        "Quiet environment.", "Communal kitchen available.", "Strict no-alcohol policy.",
        "Women and children only.", "Men only.", "Pet-friendly (small animals).",
        "On-site mental health support.", "No religious affiliation.", "Referral required."
    ]
    notes = random.sample(notes_options, k=random.randint(1, 3))

    return {
        "property_id": f"PROP{property_id:03d}",
        "name": random.choice(SHELTER_NAMES if property_type != "Temporary Flat" else ["London Affordable Housing", "City Respite Homes"]),
        "address": generate_london_address(base_point),
        "city": "London",
        "postcode": random.choice(POSTCODE_PREFIXES) + " " + f"{random.randint(1,9)}{random.choice('ABCDEFGHJKLMNPQRSTUVWXY')}{random.choice('ABCDEFGHJKLMNPQRSTUVWXY')}",
        "property_type": property_type,
        "housing_type": housing_type,
        "capacity": capacity,
        "accessibility_features": accessibility_features,
        "availability_status": availability_status, # For filtering
        "capacity_info": capacity_info, # For display
        "last_available_date": get_random_date(2024, 2025), # Date it last became available
        "provider_name": random.choice(["London Housing Charity", "City Council Housing", "Homeless Aid UK"]),
        "weekly_cost": 0.00, # Assuming free for target users
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
        "notes": ". ".join(notes)
    }

# --- Skill Data Generation ---

def generate_skill(skill_id):
    """Generates a synthetic skill entry."""
    skill_name = SKILL_NAMES[skill_id - 1] # Use pre-defined names
    category_map = {
        "IT": ["Basic IT Literacy", "Microsoft Office Suite", "Web Development (HTML/CSS)", "Basic Coding (Python)", "Cybersecurity Awareness", "Cloud Computing Fundamentals", "Mobile App Development (Basic)", "Networking Basics", "Data Analysis with Spreadsheets"],
        "Soft Skills": ["Customer Service Excellence", "CV Writing & Interview Prep", "Financial Literacy", "Project Management Basics", "Time Management", "Communication Skills", "Critical Thinking", "Problem Solving", "Teamwork & Collaboration", "Public Speaking", "Professional Email Etiquette", "Mindfulness for Stress Reduction", "Conflict Resolution", "Interview Skills Workshop"],
        "Digital Marketing": ["Digital Marketing Fundamentals", "Social Media Management", "Graphic Design Basics", "Introduction to UX Design"],
        "Vocational": ["Health & Safety in Construction", "Food Hygiene Certificate"],
        "General": ["English Language Skills", "Online Job Search Strategies", "Basic Photography Skills", "Introduction to AI"]
    }
    skill_category = "Other"
    for cat, skills in category_map.items():
        if skill_name in skills:
            skill_category = cat
            break
            
    descriptions = {
        "Basic IT Literacy": "Fundamental computer operation skills for everyday tasks.",
        "Microsoft Office Suite": "Proficiency in Word, Excel, and PowerPoint for professional use.",
        "Customer Service Excellence": "Develop skills to provide outstanding customer support.",
        "Digital Marketing Fundamentals": "Introduction to online marketing strategies and tools.",
        "Web Development (HTML/CSS)": "Learn to build basic websites using HTML and CSS.",
        "Data Entry": "Accurate and efficient data input techniques.",
        "English Language Skills": "Improve reading, writing, and conversational English.",
        "CV Writing & Interview Prep": "Craft compelling CVs and prepare for job interviews.",
        "Financial Literacy": "Understand personal finance, budgeting, and saving.",
        "Health & Safety in Construction": "Essential safety knowledge for construction sites.",
        "Food Hygiene Certificate": "Learn food safety practices for working with food.",
        "Basic Coding (Python)": "Foundational programming concepts using Python.",
        "Project Management Basics": "Introduction to planning and executing projects.",
        "Time Management": "Strategies for effective time allocation and productivity.",
        "Communication Skills": "Enhance verbal and non-verbal communication.",
        "Critical Thinking": "Develop analytical and problem-solving abilities.",
        "Problem Solving": "Systematic approaches to identifying and resolving issues.",
        "Teamwork & Collaboration": "Skills for effective group work and cooperation.",
        "Social Media Management": "Manage and grow social media presence for businesses.",
        "Graphic Design Basics": "Introduction to visual communication and design tools.",
        "Cybersecurity Awareness": "Understand common cyber threats and protective measures.",
        "Cloud Computing Fundamentals": "Basics of cloud services and platforms.",
        "Mobile App Development (Basic)": "Introduction to creating simple mobile application interfaces.",
        "Networking Basics": "Building professional connections and leveraging them for career growth.",
        "Public Speaking": "Overcome fear and deliver engaging presentations."
    }

    return {
        "skill_id": f"SKILL{skill_id:03d}",
        "skill_name": skill_name,
        "skill_category": skill_category,
        "description": descriptions.get(skill_name, f"Detailed description for {skill_name}.")
    }

# --- Microcourse Data Generation ---

def generate_microcourse(course_id, all_skills):
    """Generates a synthetic microcourse entry."""
    course_title = MICROCOURSE_TITLES[course_id - 1] # Use pre-defined titles
    description = f"This course, '{course_title}', covers essential topics for skill development."
    duration = random.randint(5, 40) # 5 to 40 hours
    learning_format = random.choice(LEARNING_FORMATS)
    cost = random.choice(COURSE_COSTS)
    
    # Link to relevant skills
    num_skills = random.randint(1, 3)
    associated_skills = random.sample(all_skills, k=num_skills)
    skill_ids = [skill['skill_id'] for skill in associated_skills]

    start_date = get_random_date(2024, 2025)
    end_date = None
    if random.random() < 0.3: # Some courses have an end date (cohort-based)
        end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=random.randint(7, 90))).strftime("%Y-%m-%d")

    return {
        "course_id": f"COURSE{course_id:03d}",
        "course_title": course_title,
        "description": description,
        "duration_hours": duration,
        "learning_format": learning_format,
        "cost": cost,
        "provider_name": random.choice(["London Skills Hub", "Future Learn UK", "Digital Growth Institute", "Community Learning London"]),
        "start_date": start_date,
        "end_date": end_date,
        "is_active": random.choice([True, True, True, False]), # Mostly active
        "skill_ids": skill_ids # Array of skill IDs
    }

# --- Main Data Generation Function ---

def generate_all_synthetic_data():
    """Generates all synthetic data for Firestore collections."""
    all_data = {}

    # Individuals
    individuals_data = [generate_individual(i + 1) for i in range(NUM_INDIVIDUALS)]
    all_data['individuals'] = individuals_data

    # Properties (Shelters/Hostels)
    properties_data = []
    for i in range(NUM_PROPERTIES):
        prop = generate_property(i + 1)
        # Add food banks as properties too, for simplicity in this combined resource
        if random.random() < 0.4: # 40% chance of being a food bank
            prop["name"] = random.choice(FOOD_BANK_NAMES)
            prop["property_type"] = "Food Bank"
            prop["housing_type"] = "N/A"
            prop["capacity"] = 0 # N/A for food banks
            prop["availability_status"] = "Always Available"
            prop["capacity_info"] = random.choice(["Well-stocked.", "Limited supplies, call ahead."])
            prop["hours"] = generate_hours(is_shelter=False) # Re-use hours logic
            prop["notes"] = random.choice(["Requires referral.", "Walk-ins welcome.", "Offers hygiene kits."])
        else: # It's a shelter/hostel
            prop["hours"] = generate_hours(is_shelter=True) # Re-use hours logic
        properties_data.append(prop)

    all_data['properties'] = properties_data

    # Skills
    skills_data = [generate_skill(i + 1) for i in range(NUM_SKILLS)]
    all_data['skills'] = skills_data

    # Microcourses
    microcourses_data = [generate_microcourse(i + 1, skills_data) for i in range(NUM_MICROCOURSES)]
    all_data['microcourses'] = microcourses_data

    return all_data

# --- Script Execution ---

def generate_hours(is_shelter: bool):
    """Generates plausible opening hours for shelters or food banks."""
    if is_shelter:
        # Shelters typically open in late afternoon/evening and close in morning
        open_hour = random.randint(17, 19) # 5 PM to 7 PM
        close_hour = random.randint(7, 9) # 7 AM to 9 AM
        return f"Open {open_hour}:00 - {close_hour}:00 daily"
    else:
        # Food banks typically open during day, often limited days
        start_hour = random.randint(9, 11)
        end_hour = random.randint(13, 16)
        days = random.sample(["Mon", "Tue", "Wed", "Thu", "Fri"], k=random.randint(2, 4))
        days_str = ", ".join(sorted(days))
        return f"{days_str}: {start_hour}:00 - {end_hour}:00"


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True) # Ensure the output directory exists

    print("Generating synthetic data for Firestore collections...")
    synthetic_data_collections = generate_all_synthetic_data()

    for collection_name, data_list in synthetic_data_collections.items():
        file_path = os.path.join(OUTPUT_DIR, f"{collection_name}.json")
        with open(file_path, 'w') as f:
            json.dump(data_list, f, indent=4)
        print(f"Generated {len(data_list)} items for '{collection_name}' to {file_path}")

    print("\n--- Sample of Generated Individuals Data ---")
    for i, individual in enumerate(synthetic_data_collections['individuals'][:2]):
        print(f"Individual {i+1}:")
        for key, value in individual.items():
            print(f"  {key}: {value}")
    print("...")

    print("\n--- Sample of Generated Properties (Shelters/Food Banks) Data ---")
    for i, prop in enumerate(synthetic_data_collections['properties'][:2]):
        print(f"Property {i+1}:")
        for key, value in prop.items():
            print(f"  {key}: {value}")
    print("...")

    print("\n--- Sample of Generated Microcourses Data ---")
    for i, course in enumerate(synthetic_data_collections['microcourses'][:2]):
        print(f"Microcourse {i+1}:")
        for key, value in course.items():
            print(f"  {key}: {value}")
    print("...")
