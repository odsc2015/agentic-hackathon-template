import { Request, Response } from 'express';
import { CompanyDataController } from '../src/controllers/companyDataController';
import { FinancialDataService } from '../src/services/financialDataService';
import { GeminiClient } from '../src/services/geminiClient';

jest.mock('../src/services/financialDataService');
jest.mock('../src/services/geminiClient');

describe('CompanyDataController', () => {
    let companyDataController: CompanyDataController;
    let mockRequest: Partial<Request>;
    let mockResponse: Partial<Response>;
    let financialDataService: FinancialDataService;

    beforeEach(() => {
        financialDataService = new FinancialDataService();
        companyDataController = new CompanyDataController(financialDataService);
        mockRequest = {};
        mockResponse = {
            json: jest.fn(),
            status: jest.fn().mockReturnThis(),
        };
    });

    it('should return company data successfully', async () => {
        mockRequest = {
            params: { companyId: '123' },
        } as Request;

        const mockData = { name: 'Test Company', revenue: 1000000 };
        (financialDataService.getFinancialData as jest.Mock).mockResolvedValue(mockData);

        await companyDataController.getCompanyData(mockRequest as Request, mockResponse as Response);

        expect(mockResponse.status).toHaveBeenCalledWith(200);
        expect(mockResponse.json).toHaveBeenCalledWith(mockData);
    });

    it('should handle errors when fetching company data', async () => {
        mockRequest = {
            params: { companyId: '123' },
        } as Request;

        const mockError = new Error('Error fetching data');
        (financialDataService.getFinancialData as jest.Mock).mockRejectedValue(mockError);

        await companyDataController.getCompanyData(mockRequest as Request, mockResponse as Response);

        expect(mockResponse.status).toHaveBeenCalledWith(500);
        expect(mockResponse.json).toHaveBeenCalledWith({ error: 'Error fetching data' });
    });
});