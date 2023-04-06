-- This data should be used only for testing purposes

INSERT INTO `api_tokens` (`token`, `name`, `role`) VALUES
  ('d265aed699f7409ac0ec6fe07ee9cb11', 'Batch', 'batch'),
  ('f9a23e776e199b52f12f60cd1ea0dfc3', 'Dimas', 'admin');

INSERT INTO `tracks`(`name`) VALUES
    ('Karting Los Santos'),
    ('Karting Burgueño');

INSERT INTO `competitions_index`(`track_id`, `code`, `name`, `description`) VALUES
    (1, 'endurance-2023-02-26', 'Resistencia Los Santos 26-02-2023', 'Resistencia de 3h en Karting Los Santos'),
    (1, 'endurance-2023-03-25', 'Resistencia Los Santos 25-03-2023', 'Resistencia de 3h en Karting Los Santos'),
    (2, 'endurance-2023-03-26', 'Resistencia Burgueño 26-03-2023', 'Resistencia de 3h en Karting Burgueño');
