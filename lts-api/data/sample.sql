-- This data should be used only for testing purposes

INSERT INTO `api_auth` (`key`, `bearer`, `name`, `role`) VALUES
  ('d265aed699f7409ac0ec6fe07ee9cb11', NULL, 'Test viewer', 'viewer'),
  ('912ec803b2ce49e4a541068d495ab570', NULL, 'Test batch without bearer', 'batch'),
  ('6a204bd89f3c8348afd5c77c717a097a', 'e1ec4ca719196937f17f9914bf5a2a8c072ba0f9bc9225875e6a1286b2f350e9', 'Test batch with bearer', 'batch');

INSERT INTO `competitions_index`(`track_id`, `competition_code`, `name`, `description`) VALUES
  (1, 'north-endurance-2023-02-26', 'Endurance North 26-02-2023', 'Endurance in Karting North'),
  (1, 'north-endurance-2023-03-25', 'Endurance North 25-03-2023', 'Endurance in Karting North'),
  (2, 'south-endurance-2023-03-26', 'Endurance South 26-03-2023', 'Endurance in Karting South');

INSERT INTO `competitions_metadata_current`(`competition_id`, `reference_time`, `reference_current_offset`, `status`, `stage`, `remaining_length`, `remaining_length_unit`) VALUES
  (1, NULL, NULL, 'finished', 'race', 0, 'laps'),
  (2, NULL, NULL, 'ongoing', 'race', 348, 'laps'),
  (3, NULL, NULL, 'paused', 'free-practice', 0, 'laps');

INSERT INTO `competitions_metadata_history`(`competition_id`, `reference_time`, `reference_current_offset`, `status`, `stage`, `remaining_length`, `remaining_length_unit`) VALUES
  (1, NULL, NULL, 'paused', 'free-practice', 0, 'laps'),
  (1, NULL, NULL, 'ongoing', 'race', 350, 'laps'),
  (1, NULL, NULL, 'finished', 'race', 0, 'laps'),
  (2, NULL, NULL, 'paused', 'free-practice', 0, 'laps'),
  (2, NULL, NULL, 'ongoing', 'race', 350, 'laps'),
  (2, NULL, NULL, 'ongoing', 'race', 348, 'laps'),
  (3, NULL, NULL, 'paused', 'free-practice', 0, 'laps');

INSERT INTO `competitions_settings`(`competition_id`, `length`, `length_unit`, `pit_time`, `min_number_pits`) VALUES
  (1, 350, 'laps', 120000, 5),
  (2, 320, 'laps', 120000, 4),
  (3, 3600000, 'millis', 10000, 4);

INSERT INTO `participants_teams`(`competition_id`, `participant_code`, `name`, `number`, `reference_time_offset`) VALUES
  (1, 'team-1', 'CKM 1', 41, NULL),
  (1, 'team-2', 'CKM 2', 42, NULL),
  (1, 'team-3', 'CKM 3', 43, NULL),
  (2, 'team-1', 'CKM 1', 41, NULL),
  (2, 'team-2', 'CKM 2', 42, NULL),
  (3, 'team-1', 'CKM 1', 41, NULL);

INSERT INTO `participants_drivers`(`competition_id`, `team_id`, `participant_code`, `name`, `number`, `total_driving_time`, `partial_driving_time`, `reference_time_offset`) VALUES
  (1, 1, 'team-1', 'CKM 1 Driver 1', 41, 0, 0, NULL),
  (1, 1, 'team-1', 'CKM 1 Driver 2', 41, 0, 0, NULL),
  (1, 2, 'team-2', 'CKM 2 Driver 1', 42, 0, 0, NULL),
  (1, 2, 'team-2', 'CKM 2 Driver 2', 42, 0, 0, NULL),
  -- Note that the team 3 does not have any driver yet
  (2, 4, 'team-1', 'CKM 1 Driver 1', 41, 0, 0, NULL),
  (2, 4, 'team-1', 'CKM 1 Driver 2', 41, 0, 0, NULL),
  (2, 5, 'team-2', 'CKM 2 Driver 1', 42, 0, 0, NULL),
  (2, 5, 'team-2', 'CKM 2 Driver 2', 42, 0, 0, NULL),
  (3, 6, 'team-1', 'CKM 1 Driver 1', 41, 0, 0, NULL),
  (3, 6, 'team-1', 'CKM 1 Driver 2', 41, 0, 0, NULL);

INSERT INTO `timing_current`(`competition_id`, `team_id`, `driver_id`, `position`, `last_time`, `best_time`, `lap`, `gap`, `gap_unit`, `interval`, `interval_unit`, `stage`, `pit_time`, `kart_status`, `fixed_kart_status`, `number_pits`) VALUES
  (1, 1, 1, 1, 60000, 59000, 1, 0, 'laps', 0, 'laps', 'race', 35000, 'unknown', NULL, 0),
  (1, 2, 3, 2, 60000, 59000, 1, 0, 'laps', 0, 'laps', 'race', 35000, 'unknown', NULL, 0),
  (1, 3, NULL, 3, 60000, 59000, 1, 0, 'laps', 0, 'laps', 'race', 35000, 'unknown', NULL, 0),
  (2, 4, 5, 1, 58800, 58800, 2, 0, 'millis', 0, 'millis', 'race', NULL, 'good', NULL, 0),
  (2, 5, 7, 2, 59700, 59500, 2, 1400, 'millis', 1400, 'millis', 'race', NULL, 'bad', NULL, 0),
  (3, 3, 9, 1, 60000, 59000, 1, NULL, NULL, NULL, NULL, 'free-practice', NULL, 'unknown', NULL, 0);

INSERT INTO `timing_history`(`competition_id`, `team_id`, `driver_id`, `position`, `last_time`, `best_time`, `lap`, `gap`, `gap_unit`, `interval`, `interval_unit`, `stage`, `pit_time`, `kart_status`, `fixed_kart_status`, `number_pits`) VALUES
  (1, 1, 1, 1, 60000, 59000, 1, 0, 'laps', 0, 'laps', 'race', 35000, 'unknown', NULL, 0),
  (1, 2, 3, 2, 60000, 59000, 1, 0, 'laps', 0, 'laps', 'race', 35000, 'unknown', NULL, 0),
  (1, 3, NULL, 3, 60000, 59000, 1, 0, 'laps', 0, 'laps', 'race', 35000, 'unknown', NULL, 0),
  (2, 4, 5, 1, 0, 0, 0, 0, 'millis', 0, 'millis', 'race', NULL, 'unknown', NULL, 0),
  (2, 5, 7, 2, 0, 0, 0, 0, 'millis', 0, 'millis', 'race', NULL, 'unknown', NULL, 0),
  (2, 4, 5, 1, 59000, 59000, 1, 0, 'millis', 0, 'millis', 'race', NULL, 'unknown', NULL, 0),
  (2, 5, 7, 2, 59500, 59500, 1, 500, 'millis', 500, 'millis', 'race', NULL, 'unknown', NULL, 0),
  (2, 4, 5, 1, 58800, 58800, 2, 0, 'millis', 0, 'millis', 'race', NULL, 'good', NULL, 0),
  (2, 5, 7, 2, 59700, 59500, 2, 1400, 'millis', 1400, 'millis', 'race', NULL, 'bad', NULL, 0),
  (3, 3, 9, 1, 60000, 59000, 1, NULL, NULL, NULL, NULL, 'free-practice', NULL, 'unknown', NULL, 0);

INSERT INTO `timing_pits`(`competition_id`, `team_id`, `driver_id`, `action`, `lap`, `kart_status`, `fixed_kart_status`) VALUES
  (2, 5, 7, 'in', 1, 'unknown', NULL),
  (2, 5, 7, 'out', 1, 'unknown', NULL);

INSERT INTO `parsers_settings`(`competition_id`, `name`, `value`) VALUES
  (1, 'timing-best-time', 'timing-best-time-value'),
  (1, 'timing-gap', 'timing-gap-value'),
  (1, 'timing-interval', 'timing-interval-value'),
  (2, 'timing-best-time', 'timing-best-time-value'),
  (2, 'timing-gap', 'timing-gap-value'),
  (3, 'timing-best-time', 'timing-best-time-value');
