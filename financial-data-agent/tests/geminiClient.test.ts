import { GeminiClient } from '../src/services/geminiClient';

describe('GeminiClient', () => {
    let client: GeminiClient;

    beforeEach(() => {
        client = new GeminiClient();
    });

    test('fetchData should return data for a valid company', async () => {
        const companyName = 'Test Company';
        const data = await client.fetchData(companyName);
        expect(data).toBeDefined();
        expect(data.companyName).toBe(companyName);
    });

    test('fetchData should throw an error for an invalid company', async () => {
        const companyName = 'Invalid Company';
        await expect(client.fetchData(companyName)).rejects.toThrow('Company not found');
    });

    test('processResponse should correctly format the response', () => {
        const response = {
            companyName: 'Test Company',
            financials: {
                revenue: 1000000,
                profit: 200000,
            },
        };
        const formattedData = client.processResponse(response);
        expect(formattedData).toEqual({
            companyName: 'Test Company',
            revenue: 1000000,
            profit: 200000,
        });
    });
});