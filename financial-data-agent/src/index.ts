import express from 'express';
import { setCompanyRoutes } from './routes/companyRoutes';

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());

// Routes
setCompanyRoutes(app);

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});