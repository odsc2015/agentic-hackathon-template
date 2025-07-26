-- Sample users
INSERT OR IGNORE INTO users (id, email, username, password_hash)
VALUES
  ('afe8f231-783b-4b9c-9400-a7b15e732689', 'alice@example.com', 'alice', '$2b$10$gsUnMzivi1KrVcPOOr7s0uKtwTGCGXxocgsr1MFosIjoaBxXe35Q.'),
  ('7cce15a3-1e35-4f94-916a-3ea9064ac1d2', 'dave@example.com', 'dave', '$2b$10$G35wXxA1ZZhyYFVYUff1KOqBlGELEHEMWHsxiBCkwCnCzsEAAbL9S'),
  ('dbf06ff7-a49b-4136-87ae-749713ae5363', 'eve@example.com', 'eve', '$2b$10$76cKWXA/yW4S2.0dpfheyOs8whpqGHcMIEOGmoVJOeT8mZA4HQUrq'),
  ('dd0f58c2-239d-47e2-9295-9dd03ea2622e', 'frank@example.com', 'frank', '$2b$10$xvHViAHFAaiSInUwFFfzBeJvM1MGX/0AwvHjLDKtmk0WHPzBdK9wC');

-- Sample learning plans
INSERT OR IGNORE INTO learning_plans (id, user_id, title, goal, difficulty_level, plan_data, status, progress_percentage, started_at, completed_at)
VALUES
  ('plan-001', 'user-001', 'Learn Python Basics', 'Understand Python fundamentals', 3, '{"modules":["Variables","Loops","Functions"]}', 'active', 25.0, '2025-07-01 10:00:00', NULL),
  ('plan-002', 'user-001', 'Data Science Intro', 'Get started with data science', 5, '{"modules":["Numpy","Pandas","Matplotlib"]}', 'paused', 40.0, '2025-07-10 09:00:00', NULL),
  ('plan-003', 'user-002', 'Web Development', 'Build a personal website', 4, '{"modules":["HTML","CSS","JavaScript"]}', 'completed', 100.0, '2025-06-15 14:00:00', '2025-07-15 16:00:00'),
  ('plan-004', 'user-003', 'Machine Learning', 'Train a simple ML model', 7, '{"modules":["Regression","Classification"]}', 'active', 10.0, '2025-07-20 11:00:00', NULL);