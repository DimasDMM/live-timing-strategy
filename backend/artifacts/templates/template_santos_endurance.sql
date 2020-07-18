CREATE TABLE `{tables_prefix}_teams` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(191) NOT NULL,
  `number` INT UNSIGNED NULL,
  `reference_time_offset` INT DEFAULT 0 COMMENT 'Respect track reference',
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `team_name` (`name`)
) ENGINE=InnoDB CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `{tables_prefix}_drivers` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `team_id` INT UNSIGNED NULL,
  `name` VARCHAR(191) NOT NULL,
  `time_driving` INT UNSIGNED DEFAULT 0,
  `reference_time_offset` INT DEFAULT 0 COMMENT 'Respect team reference',
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `team_driver` (`name`, `team_id`),
  CONSTRAINT `{tables_prefix}_drivers__team_id` FOREIGN KEY (`team_id`) REFERENCES `{tables_prefix}_teams` (`id`)
) ENGINE=InnoDB CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `{tables_prefix}_timing_historic` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `team_id` INT UNSIGNED NULL,
  `driver_id` INT UNSIGNED NULL,
  `position` INT UNSIGNED NOT NULL,
  `time` INT UNSIGNED NOT NULL,
  `lap` INT UNSIGNED NOT NULL,
  `gap` INT UNSIGNED NOT NULL,
  `stage` ENUM('classification', 'race') NOT NULL,
  `kart_status` ENUM('unknown', 'good', 'medium', 'bad') NOT NULL DEFAULT 'unknown',
  `kart_status_guess` ENUM('good', 'medium', 'bad') NULL,
  `forced_kart_status` ENUM('good', 'medium', 'bad') NULL,
  `number_stops` INT UNSIGNED NOT NULL DEFAULT 0,
  `is_stop` TINYINT(1) NOT NULL DEFAULT 0,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `timing_team_lap` (`team_id`, `lap`),
  CONSTRAINT `{tables_prefix}_timing__team_id` FOREIGN KEY (`team_id`) REFERENCES `{tables_prefix}_teams` (`id`),
  CONSTRAINT `{tables_prefix}_timing__driver_id` FOREIGN KEY (`driver_id`) REFERENCES `{tables_prefix}_drivers` (`id`)
) ENGINE=InnoDB CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `{tables_prefix}_karts_in` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `team_id` INT UNSIGNED NULL,
  `kart_status` ENUM('unknown', 'good', 'medium', 'bad') NOT NULL DEFAULT 'unknown',
  `forced_kart_status` ENUM('good', 'medium', 'bad') NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `{tables_prefix}_karts_in__team_id` FOREIGN KEY (`team_id`) REFERENCES `{tables_prefix}_teams` (`id`)
) ENGINE=InnoDB CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `{tables_prefix}_karts_out` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `team_id` INT UNSIGNED NULL,
  `kart_status` ENUM('unknown', 'good', 'medium', 'bad') NOT NULL DEFAULT 'unknown',
  `forced_kart_status` ENUM('good', 'medium', 'bad') NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `{tables_prefix}_karts_out__team_id` FOREIGN KEY (`team_id`) REFERENCES `{tables_prefix}_teams` (`id`)
) ENGINE=InnoDB CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `{tables_prefix}_karts_probs` (
  `step` INT UNSIGNED NOT NULL,
  `kart_status` ENUM('unknown', 'good', 'medium', 'bad') NOT NULL DEFAULT 'unknown',
  `probability` FLOAT NOT NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`step`, `kart_status`)
) ENGINE=InnoDB CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `{tables_prefix}_event_config` (
  `name` VARCHAR(191) NOT NULL PRIMARY KEY,
  `value` VARCHAR(255) NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `{tables_prefix}_event_stats` (
  `name` VARCHAR(191) NOT NULL PRIMARY KEY,
  `value` VARCHAR(255) NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `{tables_prefix}_event_health` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `category` VARCHAR(191) NOT NULL,
  `name` VARCHAR(191) NOT NULL,
  `status` ENUM('ok', 'warning', 'error', 'offline') NOT NULL,
  `message` VARCHAR(1000) NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `category_name` (`category`, `name`)
) ENGINE=InnoDB CHARSET=utf8 COLLATE=utf8_unicode_ci;

INSERT INTO `{tables_prefix}_event_config` (`name`, `value`) VALUES
  ('race_length', NULL),
  ('race_length_unit', NULL),
  ('reference_time_top_teams', NULL),
  ('stop_time', NULL),
  ('min_number_stops', NULL);

INSERT INTO `{tables_prefix}_event_stats` (`name`, `value`) VALUES
  ('reference_time', 0),
  ('reference_current_offset', 0),
  ('status', 'offline'),
  ('stage', 'unknown'),
  ('remaining_event', 'unknown');

INSERT INTO `{tables_prefix}_event_health` (`category`, `name`, `status`) VALUES
  ('database', 'connection', 'offline'),
  ('crawler', 'internet', 'offline'),
  ('crawler', 'live_timing', 'offline'),
  ('crawler', 'parse_teams', 'offline'),
  ('crawler', 'parse_timing', 'offline'),
  ('batch', 'karts_box_probs', 'offline'),
  ('batch', 'karts_status', 'offline'),
  ('batch', 'time_references', 'offline');
