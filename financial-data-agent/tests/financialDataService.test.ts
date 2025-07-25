import { FinancialDataService } from '../src/services/financialDataService';
import { GeminiClient } from '../src/services/geminiClient';

describe('FinancialDataService', () => {
    let financialDataService: FinancialDataService;
    let geminiClient: GeminiClient;

    beforeEach(() => {
        geminiClient = new GeminiClient();
        financialDataService = new FinancialDataService(geminiClient);
    });

    describe('getFinancialData', () => {
        it('should retrieve financial data for a given company', async () => {
            const companyName = 'Test Company';
            const mockData = { /* mock financial data */ };
            jest.spyOn(geminiClient, 'fetchData').mockResolvedValue(mockData);

            const result = await financialDataService.getFinancialData(companyName);
            expect(result).toEqual(mockData);
            expect(geminiClient.fetchData).toHaveBeenCalledWith(companyName);
        });
    });

    describe('formatData', () => {
        it('should format the financial data correctly', () => {
            const rawData = { /* raw financial data */ };
            const formattedData = financialDataService.formatData(rawData);
            expect(formattedData).toEqual({ /* expected formatted data */ });
        });
    });
});