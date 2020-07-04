CREATE TABLE `{event_name}_teams` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(255) NOT NULL,
  `team_number` INT UNSIGNED NULL,
  `number_drivers` INT UNSIGNED NULL DEFAULT 1,
  `reference_time_offset` INT DEFAULT 0,
  `kart_status` ENUM('unknown', 'good', 'medium', 'bad') NOT NULL DEFAULT 'unknown',
  `kart_status_guess` ENUM('good', 'medium', 'bad') NULL,
  `forced_kart_status` TINYINT(1) NOT NULL DEFAULT 0,
  `number_stops` INT UNSIGNED NOT NULL DEFAULT 0,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `{event_name}_drivers` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `team_id` INT UNSIGNED NULL,
  `name` VARCHAR(255) NOT NULL,
  `time_driving` INT UNSIGNED DEFAULT 0,
  `reference_time_offset` INT DEFAULT 0,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `team_driver` (`name`, `team_id`),
  CONSTRAINT `{event_name}_drivers__team_id` FOREIGN KEY (`team_id`) REFERENCES `{event_name}_teams` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `{event_name}_timing_onlap` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `team_id` INT UNSIGNED NULL,
  `driver_id` INT UNSIGNED NULL,
  `position` INT UNSIGNED NOT NULL,
  `best_time` INT UNSIGNED NOT NULL,
  `time` INT NOT NULL,
  `lap` INT NOT NULL,
  `gap` INT NOT NULL,
  `stage` ENUM('classification', 'race') NOT NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `{event_name}_timing__team_id` FOREIGN KEY (`team_id`) REFERENCES `{event_name}_teams` (`id`)
  CONSTRAINT `{event_name}_timing__driver_id` FOREIGN KEY (`driver_id`) REFERENCES `{event_name}_drivers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `{event_name}_timing_historic` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `team_id` INT UNSIGNED NULL,
  `driver_id` INT UNSIGNED NULL,
  `position` INT UNSIGNED NOT NULL,
  `time` INT NOT NULL,
  `lap` INT NOT NULL,
  `stage` ENUM('classification', 'race') NOT NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `{event_name}_timing__team_id` FOREIGN KEY (`team_id`) REFERENCES `{event_name}_teams` (`id`)
  CONSTRAINT `{event_name}_timing__driver_id` FOREIGN KEY (`driver_id`) REFERENCES `{event_name}_drivers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `{event_name}_karts_in` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `team_id` INT UNSIGNED NULL,
  `kart_status` ENUM('unknown', 'good', 'medium', 'bad') NOT NULL DEFAULT 'unknown',
  `forced_kart_status` TINYINT(1) NOT NULL DEFAULT 0,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `{event_name}_karts_in__team_id` FOREIGN KEY (`team_id`) REFERENCES `{event_name}_teams` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `{event_name}_karts_out` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `team_id` INT UNSIGNED NULL,
  `kart_status` ENUM('unknown', 'good', 'medium', 'bad') NOT NULL DEFAULT 'unknown',
  `forced_kart_status` TINYINT(1) NOT NULL DEFAULT 0,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `{event_name}_karts_out__team_id` FOREIGN KEY (`team_id`) REFERENCES `{event_name}_teams` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `{event_name}_event_config` (
  `name` VARCHAR(191) NOT NULL PRIMARY KEY,
  `value` VARCHAR(255) NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `{event_name}_event_stats` (
  `name` VARCHAR(191) NOT NULL PRIMARY KEY,
  `value` VARCHAR(255) NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `{event_name}_event_health` (
  `category` VARCHAR(191) NOT NULL,
  `name` VARCHAR(191) NOT NULL,
  `status` ENUM('ok', 'warning', 'error', 'offline') NOT NULL,
  `message` VARCHAR(1000) NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`category`, `name`),
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

INSERT INTO `{event_name}_event_config` (`name`, `value`) VALUES
  ('track_name', 'santos'),
  ('race_type', 'endurance'),
  ('race_length', NULL),
  ('race_length_unit', NULL),
  ('reference_top_teams', NULL);

INSERT INTO `{event_name}_event_stats` (`name`, `value`) VALUES
  ('reference_time', 0),
  ('reference_current_offset', 0),
  ('status', 'Offline'),
  ('stage', NULL),
  ('remaining_event', NULL);

INSERT INTO `{event_name}_event_health` (`name`, `status`) VALUES
  ('database', 'connection', 'offline'),
  ('crawler', 'internet', 'offline'),
  ('crawler', 'live_timing', 'offline'),
  ('crawler', 'parse_teams', 'offline'),
  ('crawler', 'parse_timing', 'offline'),
  ('batch', 'karts_box_probs', 'offline'),
  ('batch', 'karts_status', 'offline'),
  ('batch', 'time_references', 'offline');
