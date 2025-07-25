import { Router } from 'express';
import { CompanyDataController } from '../controllers/companyDataController';

const router = Router();
const companyDataController = new CompanyDataController();

export function setCompanyRoutes(app: Router) {
    app.get('/api/company/:symbol', companyDataController.getCompanyData.bind(companyDataController));
}