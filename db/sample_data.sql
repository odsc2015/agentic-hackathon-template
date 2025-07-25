-- Sample users
INSERT OR IGNORE INTO  users (id, email, username, password_hash)
VALUES
  ('user-001', 'alice@example.com', 'alice', 'hashed_pw_1'),
  ('user-002', 'bob@example.com', 'bob', 'hashed_pw_2'),
  ('user-003', 'carol@example.com', 'carol', 'hashed_pw_3');

-- Sample learning plans
INSERT OR IGNORE INTO  learning_plans (id, user_id, title, goal, difficulty_level, plan_data, status, progress_percentage, started_at, completed_at)
VALUES
  ('plan-001', 'user-001', 'Learn Python Basics', 'Understand Python fundamentals', 3, '{"modules":["Variables","Loops","Functions"]}', 'active', 25.0, '2025-07-01 10:00:00', NULL),
  ('plan-002', 'user-001', 'Data Science Intro', 'Get started with data science', 5, '{"modules":["Numpy","Pandas","Matplotlib"]}', 'paused', 40.0, '2025-07-10 09:00:00', NULL),
  ('plan-003', 'user-002', 'Web Development', 'Build a personal website', 4, '{"modules":["HTML","CSS","JavaScript"]}', 'completed', 100.0, '2025-06-15 14:00:00', '2025-07-15 16:00:00'),
  ('plan-004', 'user-003', 'Machine Learning', 'Train a simple ML model', 7, '{"modules":["Regression","Classification"]}', 'active', 10.0, '2025-07-20 11:00:00', NULL);