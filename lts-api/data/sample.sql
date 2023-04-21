-- This data should be used only for testing purposes

INSERT INTO `competitions_index`(`track_id`, `competition_code`, `name`, `description`) VALUES
  (1, 'north-endurance-2023-02-26', 'Endurance North 26-02-2023', 'Endurance in Karting North'),
  (1, 'north-endurance-2023-03-25', 'Endurance North 25-03-2023', 'Endurance in Karting North'),
  (2, 'south-endurance-2023-03-26', 'Endurance South 26-03-2023', 'Endurance in Karting South');

INSERT INTO `competitions_metadata_current`(`competition_id`, `reference_time`, `reference_current_offset`, `status`, `stage`, `remaining_length`, `remaining_length_unit`) VALUES
  (1, 0, 0, 'finished', 'race', 0, 'laps'),
  (2, 0, 0, 'ongoing', 'race', 348, 'laps'),
  (3, 0, 0, 'paused', 'free-practice', 0, 'laps');

INSERT INTO `competitions_metadata_history`(`competition_id`, `reference_time`, `reference_current_offset`, `status`, `stage`, `remaining_length`, `remaining_length_unit`) VALUES
  (1, 0, 0, 'paused', 'free-practice', 0, 'laps'),
  (1, 0, 0, 'ongoing', 'race', 350, 'laps'),
  (1, 0, 0, 'finished', 'race', 0, 'laps'),
  (2, 0, 0, 'paused', 'free-practice', 0, 'laps'),
  (2, 0, 0, 'ongoing', 'race', 350, 'laps'),
  (2, 0, 0, 'ongoing', 'race', 348, 'laps'),
  (3, 0, 0, 'paused', 'free-practice', 0, 'laps');

INSERT INTO `competitions_settings`(`competition_id`, `length`, `length_unit`, `pit_time`, `min_number_pits`) VALUES
  (1, 350, 'laps', 120000, 5),
  (2, 320, 'laps', 120000, 4),
  (3, 3600000, 'millis', 10000, 4);

INSERT INTO `participants_teams`(`competition_id`, `participant_code`, `name`, `number`, `reference_time_offset`) VALUES
  (1, 'team-1', 'CKM 1', 41, 0),
  (1, 'team-2', 'CKM 2', 42, 0),
  (1, 'team-3', 'CKM 3', 43, 0),
  (2, 'team-1', 'CKM 1', 41, 0),
  (2, 'team-2', 'CKM 2', 42, 0),
  (3, 'team-1', 'CKM 1', 41, 0);

INSERT INTO `participants_drivers`(`competition_id`, `team_id`, `participant_code`, `name`, `number`, `total_driving_time`, `partial_driving_time`, `reference_time_offset`) VALUES
  (1, 1, 'team-1', 'CKM 1 Driver 1', 41, 0, 0, 0),
  (1, 1, 'team-1', 'CKM 1 Driver 2', 41, 0, 0, 0),
  (1, 2, 'team-2', 'CKM 2 Driver 1', 42, 0, 0, 0),
  (1, 2, 'team-2', 'CKM 2 Driver 2', 42, 0, 0, 0),
  -- Note that the team 3 does not have any driver yet
  (2, 4, 'team-1', 'CKM 1 Driver 1', 41, 0, 0, 0),
  (2, 4, 'team-1', 'CKM 1 Driver 2', 41, 0, 0, 0),
  (2, 5, 'team-2', 'CKM 2 Driver 1', 42, 0, 0, 0),
  (2, 5, 'team-2', 'CKM 2 Driver 2', 42, 0, 0, 0),
  (3, 6, 'team-1', 'CKM 1 Driver 1', 41, 0, 0, 0),
  (3, 6, 'team-1', 'CKM 1 Driver 2', 41, 0, 0, 0);

INSERT INTO `timing_current`(`competition_id`, `team_id`, `driver_id`, `position`, `time`, `best_time`, `lap`, `interval`, `interval_unit`, `stage`, `pit_time`, `kart_status`, `fixed_kart_status`, `number_pits`) VALUES
  (1, 1, 1, 1, 60000, 59000, 1, 0, 'laps', 'race', 350, 'unknown', NULL, 0),
  (1, 2, 3, 1, 60000, 59000, 1, 0, 'laps', 'race', 350, 'unknown', NULL, 0),
  (1, 3, NULL, 1, 60000, 59000, 1, 0, 'laps', 'race', 350, 'unknown', NULL, 0),
  (2, 4, 5, 1, 58800, 58800, 2, 0, 'millis', 'race', 0, 'good', NULL, 0),
  (2, 5, 7, 2, 59700, 59500, 2, 1400, 'millis', 'race', 0, 'bad', NULL, 0),
  (3, 3, 9, 1, 60000, 59000, 1, 0, 'laps', 'free-practice', 0, 'unknown', NULL, 0);

INSERT INTO `timing_history`(`competition_id`, `team_id`, `driver_id`, `position`, `time`, `best_time`, `lap`, `interval`, `interval_unit`, `stage`, `pit_time`, `kart_status`, `fixed_kart_status`, `number_pits`) VALUES
  (1, 1, 1, 1, 60000, 59000, 1, 0, 'laps', 'race', 350, 'unknown', NULL, 0),
  (1, 2, 3, 1, 60000, 59000, 1, 0, 'laps', 'race', 350, 'unknown', NULL, 0),
  (1, 3, NULL, 1, 60000, 59000, 1, 0, 'laps', 'race', 350, 'unknown', NULL, 0),
  (2, 4, 5, 1, 0, 0, 0, 0, 'millis', 'race', 0, 'unknown', NULL, 0),
  (2, 5, 7, 2, 0, 0, 0, 0, 'millis', 'race', 0, 'unknown', NULL, 0),
  (2, 4, 5, 1, 59000, 59000, 1, 0, 'millis', 'race', 0, 'unknown', NULL, 0),
  (2, 5, 7, 2, 59500, 59500, 1, 500, 'millis', 'race', 0, 'unknown', NULL, 0),
  (2, 4, 5, 1, 58800, 58800, 2, 0, 'millis', 'race', 0, 'good', NULL, 0),
  (2, 5, 7, 2, 59700, 59500, 2, 1400, 'millis', 'race', 0, 'bad', NULL, 0),
  (3, 3, 9, 1, 60000, 59000, 1, 0, 'millis', 'free-practice', 0, 'unknown', NULL, 0);

INSERT INTO `parsers_settings`(`competition_id`, `name`, `value`) VALUES
  (1, 'timing-best-time', 'timing-best-time-value'),
  (1, 'timing-gap', 'timing-gap-value'),
  (1, 'timing-interval', 'timing-interval-value'),
  (2, 'timing-best-time', 'timing-best-time-value'),
  (2, 'timing-gap', 'timing-gap-value'),
  (3, 'timing-best-time', 'timing-best-time-value');
