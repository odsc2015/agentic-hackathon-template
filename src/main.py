from planner import plan
from executor import execute
from memory import save_memory, get_memory

def run_agent():
    print("📰 Fake News Detection Agent Started! (Type 'exit' to quit)")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Agent stopped. Bye!")
            break

        tasks = plan(user_input)
        print(f"\nPlanned Tasks: {tasks}")

        results = execute(tasks, user_input)
        final_answer = "\n\n".join(results)

        print(f"\n✅ Verification Result:\n{final_answer}")

        save_memory(user_input, final_answer)
        print(f"\n📝 Recent Memory: {get_memory()}")

if __name__ == "__main__":
    run_agent()