-- This data should be used only for testing purposes

INSERT INTO `competitions_index`(`track_id`, `code`, `name`, `description`) VALUES
    (1, 'santos-endurance-2023-02-26', 'Resistencia Los Santos 26-02-2023', 'Resistencia de 3h en Karting Los Santos'),
    (1, 'santos-endurance-2023-03-25', 'Resistencia Los Santos 25-03-2023', 'Resistencia de 3h en Karting Los Santos'),
    (2, 'burgueno-endurance-2023-03-26', 'Resistencia Burgueño 26-03-2023', 'Resistencia de 3h en Karting Burgueño');

INSERT INTO `competitions_teams`(`competition_id`, `code`, `name`, `number`, `reference_time_offset`) VALUES
  (1, 'team-1', 'CKM 1', 41, 0),
  (1, 'team-2', 'CKM 2', 42, 0),
  (1, 'team-3', 'CKM 3', 43, 0),
  (2, 'team-1', 'CKM 1', 41, 0),
  (2, 'team-2', 'CKM 2', 42, 0),
  (3, 'team-1', 'CKM 1', 41, 0);

INSERT INTO `competitions_drivers`(`competition_id`, `team_id`, `code`, `name`, `number`, `total_driving_time`, `partial_driving_time`, `reference_time_offset`) VALUES
  (1, 1, 'team-1', 'CKM 1 Driver 1', 41, 0, 0, 0),
  (1, 1, 'team-1', 'CKM 1 Driver 2', 41, 0, 0, 0),
  (1, 2, 'team-2', 'CKM 2 Driver 1', 42, 0, 0, 0),
  (1, 2, 'team-2', 'CKM 2 Driver 2', 42, 0, 0, 0),
  -- Note that the team 3 does not have any driver yet
  (2, 3, 'team-1', 'CKM 1 Driver 1', 41, 0, 0, 0),
  (2, 3, 'team-1', 'CKM 1 Driver 2', 41, 0, 0, 0),
  (2, 4, 'team-2', 'CKM 2 Driver 1', 42, 0, 0, 0),
  (2, 4, 'team-2', 'CKM 2 Driver 2', 42, 0, 0, 0),
  (3, 5, 'team-1', 'CKM 1 Driver 1', 41, 0, 0, 0),
  (3, 5, 'team-1', 'CKM 1 Driver 2', 41, 0, 0, 0);
