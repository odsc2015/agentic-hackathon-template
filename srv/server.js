const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Routes
const authRoutes = require('./routes/auth');
const userRoutes = require('./routes/users');
const learningPlanRoutes = require('./routes/learningPlans');

app.use('/api/auth', authRoutes);
app.use('/api/users', userRoutes);
app.use('/api/learning-plans', learningPlanRoutes);

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'NeuroLearn API is running' });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});