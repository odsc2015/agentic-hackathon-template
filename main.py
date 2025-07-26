import argparse
from agent.agent import KatalystAgent

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", required=True, help="Path to resume PDF")
    parser.add_argument("--job_url", required=True, help="Job posting URL")
    args = parser.parse_args()

    agent = KatalystAgent(args.resume, args.job_url)
    output = agent.execute_plan()
    
    print("\n=== Final Output ===")
    for step, result in output.items():
        print(f"\n[{step}]:")
        print(result)
