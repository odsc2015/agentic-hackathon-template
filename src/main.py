# src/main.py

from onboarding import collect_user_info
from memory import load_user_profile, save_user_profile
from executor import generate_response

def main():
    # Step 1: Load profile from root directory
    user_profile = load_user_profile()

    # Step 2: If no profile found, onboard new user
    if user_profile is None:
        print("No user profile found. Starting onboarding...\n")
        user_profile = collect_user_info()
        save_user_profile(user_profile)
        print(f"\nOnboarding complete. Welcome, {user_profile['name']}!\n")
    else:
        print(f"Welcome back, {user_profile['name']}!")

    # Step 3: Ready for interaction loop (placeholder for now)
    while True:
        user_input = input("\n🗣️  You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break

        # Placeholder: future planner + executor logic
        response = generate_response(user_input)
        print("Assistant:", response)

if __name__ == "__main__":
    main()
