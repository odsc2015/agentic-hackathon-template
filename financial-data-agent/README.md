# Financial Data Agent

This project is designed to retrieve financial data for requested companies using the Gemini AI model. It provides a structured approach to interact with the Gemini API and serves financial data through a RESTful API.

## Project Structure

- **src/**: Contains the source code for the application.
  - **index.ts**: Entry point of the application.
  - **services/**: Contains service classes for interacting with the Gemini AI model and processing financial data.
    - **geminiClient.ts**: Client for interacting with the Gemini AI model.
    - **financialDataService.ts**: Service for retrieving and formatting financial data.
  - **controllers/**: Contains controllers for handling incoming requests.
    - **companyDataController.ts**: Controller for managing company data requests.
  - **routes/**: Contains route definitions for the application.
    - **companyRoutes.ts**: Routes for company data requests.
  - **types/**: Contains TypeScript interfaces for data structures.
    - **index.ts**: Defines interfaces for CompanyData and FinancialData.

- **config/**: Contains configuration files.
  - **geminiConfig.ts**: Configuration for the Gemini AI model, including API keys and endpoints.

- **tests/**: Contains unit tests for the application.
  - **geminiClient.test.ts**: Tests for the GeminiClient class.
  - **financialDataService.test.ts**: Tests for the FinancialDataService class.
  - **companyDataController.test.ts**: Tests for the CompanyDataController class.

- **package.json**: Lists project dependencies and scripts.
- **tsconfig.json**: TypeScript configuration file.
- **README.md**: Documentation for the project.

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   ```

2. Navigate to the project directory:
   ```
   cd financial-data-agent
   ```

3. Install dependencies:
   ```
   npm install
   ```

4. Configure the Gemini AI model by updating the `config/geminiConfig.ts` file with your API keys and endpoint URLs.

5. Start the application:
   ```
   npm start
   ```

## Usage

To retrieve financial data for a specific company, send a GET request to the `/api/company-data/:companyName` endpoint, where `:companyName` is the name of the company you want to query.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.