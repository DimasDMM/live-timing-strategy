-- This data should be used only for testing purposes

START TRANSACTION;

INSERT INTO tracks(`name`) VALUES
    ('Karting Los Santos de la Humosa'),
    ('Karting Burgueño');

INSERT INTO `competitions_index`(`track_id`, `code`, `name`, `description`) VALUES
    (1, 'endurance-2023-03-25', 'Resistencia Los Santos 25-03-2023', 'Resistencia de 3h en Karting Los Santos');

COMMIT;
