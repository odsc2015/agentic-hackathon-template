const { runAsync, getAsync, allAsync } = require('../config/db');
const { v4: uuidv4 } = require('uuid');

class LearningPlan {
  static async create(userId, title, goal, difficultyLevel, planData) {
    const id = uuidv4();
    const planDataJson = JSON.stringify(planData);
    
    await runAsync(
      `INSERT INTO learning_plans 
       (id, user_id, title, goal, difficulty_level, plan_data, started_at) 
       VALUES (?, ?, ?, ?, ?, ?, datetime('now'))`,
      [id, userId, title, goal, difficultyLevel, planDataJson]
    );
    
    return id;
  }
  
  static async findByUserId(userId) {
    const plans = await allAsync(
      'SELECT * FROM learning_plans WHERE user_id = ? ORDER BY created_at DESC',
      [userId]
    );
    
    // Parse JSON data
    return plans.map(plan => ({
      ...plan,
      plan_data: JSON.parse(plan.plan_data)
    }));
  }
  
  static async findById(id) {
    const plan = await getAsync('SELECT * FROM learning_plans WHERE id = ?', [id]);
    if (plan) {
      plan.plan_data = JSON.parse(plan.plan_data);
    }
    return plan;
  }
  
  static async updateProgress(id, progressPercentage) {
    await runAsync(
      'UPDATE learning_plans SET progress_percentage = ?, updated_at = datetime("now") WHERE id = ?',
      [progressPercentage, id]
    );
    
    if (progressPercentage >= 100) {
      await runAsync(
        'UPDATE learning_plans SET status = "completed", completed_at = datetime("now") WHERE id = ?',
        [id]
      );
    }
  }
}

module.exports = LearningPlan;