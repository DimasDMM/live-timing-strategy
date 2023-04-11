-- This data should be used only for testing purposes

INSERT INTO `competitions_index`(`track_id`, `competition_code`, `name`, `description`) VALUES
    (1, 'north-endurance-2023-02-26', 'Endurance North 26-02-2023', 'Endurance in Karting North'),
    (1, 'north-endurance-2023-03-25', 'Endurance North 25-03-2023', 'Endurance in Karting North'),
    (2, 'south-endurance-2023-03-26', 'Endurance South 26-03-2023', 'Endurance in Karting South');

INSERT INTO `teams`(`competition_id`, `participant_code`, `name`, `number`, `reference_time_offset`) VALUES
  (1, 'team-1', 'CKM 1', 41, 0),
  (1, 'team-2', 'CKM 2', 42, 0),
  (1, 'team-3', 'CKM 3', 43, 0),
  (2, 'team-1', 'CKM 1', 41, 0),
  (2, 'team-2', 'CKM 2', 42, 0),
  (3, 'team-1', 'CKM 1', 41, 0);

INSERT INTO `drivers`(`competition_id`, `team_id`, `participant_code`, `name`, `number`, `total_driving_time`, `partial_driving_time`, `reference_time_offset`) VALUES
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
