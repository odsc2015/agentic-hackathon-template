# onboarding.py

def collect_user_info():
    print("Hello there! Please know that everything is alright. You're safe here, and I'm right here with you. There's nothing you need to worry about.")
    print("Let’s set things up so I can help you better.")

    name = input("1. What’s your name? ")

    wants_reminders = input("2. Would you like daily reminders? (yes/no) ").strip().lower() == 'yes'

    contacts = input("3. Name a few close family/friends (comma separated): ")
    contacts_list = [c.strip() for c in contacts.split(',')]

    print("4. Tell me your daily schedule (leave blank if unsure):")
    breakfast = input("   - Breakfast time (e.g., 8:00 AM): ")
    lunch = input("   - Lunch time (e.g., 1:00 PM): ")
    dinner = input("   - Dinner time (e.g., 7:00 PM): ")

    print("5. Do you take any daily medications?")
    med_name = input("   - Medication name (e.g., blue pill): ")
    med_time = input("   - When do you take it? (e.g., after dinner): ")

    # Bundle into profile dictionary
    user_profile = {
        "name": name,
        "preferences": {
            "wants_reminders": wants_reminders
        },
        "contacts": contacts_list,
        "routines": {
            "breakfast": breakfast,
            "lunch": lunch,
            "dinner": dinner,
            "medications": {
                med_name: med_time
            }
        }
    }

    return user_profile
