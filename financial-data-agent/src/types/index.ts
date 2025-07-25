export interface CompanyData {
    name: string;
    symbol: string;
    sector: string;
    industry: string;
    marketCap: number;
    revenue: number;
    earnings: number;
}

export interface FinancialData {
    date: string;
    revenue: number;
    netIncome: number;
    earningsPerShare: number;
    dividends: number;
    companyName: string;
    stockPrice: number;
    marketCap: number;
}