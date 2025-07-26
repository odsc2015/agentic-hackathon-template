import requests
from bs4 import BeautifulSoup
import os
from typing import Dict, List, Optional
from tools.llm_client import GeminiClient

class JobScraper:
    def __init__(self, job_url: str, api_key: Optional[str] = None):
        self.job_url = job_url
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        
        if not self.api_key:
            raise ValueError("Google API key is required.")
        
        self.client = GeminiClient(self.api_key)
    
    def fetch_html(self) -> str:
        """Fetch HTML content from the job URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.job_url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Failed to fetch HTML from {self.job_url}: {e}")
            raise
    
    def parse_html(self, html_content: str) -> str:
        """Parse HTML and extract relevant text content."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            print(f"Failed to parse HTML: {e}")
            raise
    
    def extract_job_details_with_gemini(self, parsed_text: str) -> Dict[str, any]:
        """Use Gemini to extract job details from parsed text."""
        try:
            prompt = f"""
            Analyze the following job posting text and extract the key details. Return the information in exactly this format:

            company_name: [Company name]
            title: [Job title]
            skills_required: [List of required skills, separated by commas]
            description: [Job description summary]

            Job posting text:
            {parsed_text[:8000]}
            """
            
            response = self.client.generate(prompt)
            
            # Parse the response
            result_text = response.strip()
            
            # Extract the details from the response
            details = {}
            lines = result_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('company_name:'):
                    details['company_name'] = line.replace('company_name:', '').strip()
                elif line.startswith('title:'):
                    details['title'] = line.replace('title:', '').strip()
                elif line.startswith('skills_required:'):
                    skills_text = line.replace('skills_required:', '').strip()
                    details['skills_required'] = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
                elif line.startswith('description:'):
                    details['description'] = line.replace('description:', '').strip()
            
            return details
            
        except Exception as e:
            print(f"Failed to extract job details with Gemini: {e}")
            raise
    
    def scrape(self) -> Dict[str, any]:
        """Main method to scrape job details from the URL."""
        try:
            print(f"Starting to scrape job details from: {self.job_url}")
            
            # Step 1: Fetch HTML
            html_content = self.fetch_html()
            print("Successfully fetched HTML content")
            
            # Step 2: Parse HTML
            parsed_text = self.parse_html(html_content)
            print("Successfully parsed HTML content")
            
            # Step 3: Extract job details using Gemini
            job_details = self.extract_job_details_with_gemini(parsed_text)
            print("Successfully extracted job details with Gemini")
            
            return job_details
            
        except Exception as e:
            print(f"Error during job scraping: {e}")
            raise
