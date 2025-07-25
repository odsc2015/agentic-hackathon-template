import { Request, Response } from 'express';
import { FinancialDataService } from '../services/financialDataService';

export class CompanyDataController {
    private financialDataService: FinancialDataService;
    constructor(financialDataService: FinancialDataService) {
        this.financialDataService = financialDataService;
    }

    public async getCompanyData(req: Request, res: Response): Promise<void> {
        const companyName = req.params.companyName;

        try {
            const data = await this.financialDataService.getFinancialData(companyName);
            res.status(200).json(data);
        } catch (error) {
            res.status(500).json({ message: 'Error retrieving company data', error: error.message });
        }
    }
}