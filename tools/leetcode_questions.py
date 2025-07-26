from requests import exceptions
import json
import pandas as pd

class LeetcodeQuestions:
    def __init__(self, company: str):
        self.company = company
        self.cache = {}

    def get_github_csv(self,company: str): 
        """Finds leetcode questions for a given company based on snehasishroy/leetcode-companywise-interview-questions repository on github """
        company = company.replace(" ", "-").lower()
        if company in self.cache:
            print(f'Using cached data for {company}')
            return self.cache[company]
        url = f"https://raw.githubusercontent.com/snehasishroy/leetcode-companywise-interview-questions/refs/heads/master/{company}/all.csv"
        try:
            df = pd.read_csv(url)
            df['Frequency_Numeric'] = df['Frequency %'].str.replace('%', '').astype(float)
            df_sorted = df.sort_values(by="Frequency_Numeric", ascending=False)
            
            print("DataFrame loaded successfully from URL:")
            print(df_sorted.head())
            print(f"\nDataFrame shape: {df_sorted.shape}")
            df_sorted_json = df_sorted.to_json(orient="records")
            self.cache[company] = df_sorted_json
            
            return json.dumps(df_sorted_json)
        except exceptions.HTTPError as http_err:
            print(f"Could not find Leetcode Questions for {company}.")
            return "No data available for this company"
        except Exception as e:
            print(f"Error loading CSV from URL: {e}")
