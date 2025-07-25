import dotenv from 'dotenv';

class GeminiClient {
    private apiKey: string;
    private apiUrl: string;

    constructor(apiKey: string, apiUrl: string) {
        this.apiKey = process.env.GEMINI_API_KEY || '';
        this.apiUrl = process.env.GEMINI_API_URL || '';

        if (!this.apiKey || !this.apiUrl) {
            throw new Error('Gemini API key or URL is missing in environment variables');
        }
        
    }

    async fetchData(companyName: string): Promise<any> {
        const response = await fetch(`${this.apiUrl}/data?company=${companyName}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${this.apiKey}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch data from Gemini AI');
        }

        return await response.json();
    }

    processResponse(data: any): any {
        // Process the data as needed
        return data; // Placeholder for actual processing logic
    }
}

export default GeminiClient;