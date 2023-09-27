-- Initial data to insert into the database

INSERT INTO `tracks`(`name`) VALUES
  ('Karting North'),
  ('Karting South');

INSERT INTO `api_auth` (`key`, `bearer`, `name`, `role`) VALUES
  ('6a204bd89f3c8348afd5c77c717a097a', 'e1ec4ca719196937f17f9914bf5a2a8c072ba0f9bc9225875e6a1286b2f350e9', 'Test batch with bearer', 'batch');
