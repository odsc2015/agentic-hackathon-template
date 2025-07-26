from agent.agent import KatalystAgent

if __name__ == "__main__":
    resume_path = "/Users/bupesh/Desktop/Resume/Cognizant/BupeshResume.txt"
    job_url = "https://jobs.lever.co/hive/fb175ecc-b6ba-4242-a84a-8699f9b0e971"  # Replace with a real JD URL if needed

    agent = KatalystAgent(resume_path, job_url)
    output = agent.execute_plan()

    print("\n📄 Final Output:")
    for key, value in output.items():
        print(f"\n--- {key.upper()} ---")
        print(value)
