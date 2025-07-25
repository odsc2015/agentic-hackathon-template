const express = require('express');
const router = express.Router();
const LearningPlan = require('../models/LearningPlan');
const { authenticateToken } = require('../middleware/auth');

// Create learning plan
router.post('/', authenticateToken, async (req, res) => {
  try {
    const { title, goal, difficultyLevel, planData } = req.body;
    const userId = req.user.id;
    
    const planId = await LearningPlan.create(
      userId,
      title,
      goal,
      difficultyLevel,
      planData
    );
    
    res.status(201).json({ id: planId, message: 'Learning plan created' });
  } catch (error) {
    console.error('Create plan error:', error);
    res.status(500).json({ error: 'Failed to create learning plan' });
  }
});

// Get user's learning plans
router.get('/', authenticateToken, async (req, res) => {
  try {
    const plans = await LearningPlan.findByUserId(req.user.id);
    res.json(plans);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch learning plans' });
  }
});

// Get specific learning plan
router.get('/:id', authenticateToken, async (req, res) => {
  try {
    const plan = await LearningPlan.findById(req.params.id);
    
    if (!plan) {
      return res.status(404).json({ error: 'Learning plan not found' });
    }
    
    // Verify ownership
    if (plan.user_id !== req.user.id) {
      return res.status(403).json({ error: 'Access denied' });
    }
    
    res.json(plan);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch learning plan' });
  }
});

// Update progress
router.patch('/:id/progress', authenticateToken, async (req, res) => {
  try {
    const { progressPercentage } = req.body;
    
    await LearningPlan.updateProgress(req.params.id, progressPercentage);
    res.json({ message: 'Progress updated' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to update progress' });
  }
});

module.exports = router;