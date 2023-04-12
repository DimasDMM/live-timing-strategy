-- Optionally, we may run these two commands to create the database:
-- > CREATE DATABASE	IF NOT EXISTS `live-timing`;
-- > USE `live-timing`;

SET GLOBAL time_zone = 'Europe/Madrid';

CREATE TABLE `api_tokens` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `token` VARCHAR(255) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `role` ENUM('admin', 'batch', 'user') NOT NULL DEFAULT 'user',
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `token` (`token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `tracks` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(255) NOT NULL,
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `competitions_index` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `track_id` INT UNSIGNED NOT NULL,
  `competition_code` VARCHAR(255) NOT NULL COMMENT 'Verbose ID to identify a competition',
  `name` VARCHAR(255) NOT NULL,
  `description` VARCHAR(2000) NOT NULL,
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `competitions_index__track_id` FOREIGN KEY (`track_id`) REFERENCES `tracks` (`id`),
  UNIQUE KEY `competition_code` (`competition_code`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `competitions_settings` (
  `competition_id` INT UNSIGNED NOT NULL PRIMARY KEY,
  `length` INT UNSIGNED NOT NULL,
  `length_unit` ENUM('millis', 'laps') NOT NULL,
  `pit_time` INT UNSIGNED NULL,
  `min_number_pits` INT UNSIGNED NOT NULL DEFAULT 0,
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `competitions_settings__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `competitions_metadata_current` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL UNIQUE KEY,
  `reference_time` INT NOT NULL DEFAULT 0 COMMENT 'Reference time (usually, the median) of the track during practice or early stages',
  `reference_current_offset` INT NOT NULL DEFAULT 0 COMMENT 'Time offset with respect to the track reference',
  `status` ENUM('paused', 'ongoing', 'finished') NOT NULL,
  `stage` ENUM('free-practice', 'classification', 'race') NOT NULL,
  `remaining_length` INT UNSIGNED NOT NULL,
  `remaining_length_unit` ENUM('millis', 'laps') NOT NULL,
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `competitions_metadata__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `competitions_metadata_history` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `reference_time` INT NOT NULL DEFAULT 0 COMMENT 'Reference time (usually, the median) of the track during practice or early stages',
  `reference_current_offset` INT NOT NULL DEFAULT 0 COMMENT 'Time offset with respect to the track reference',
  `status` ENUM('paused', 'ongoing', 'finished') NOT NULL,
  `stage` ENUM('free-practice', 'classification', 'race') NOT NULL,
  `remaining_length` INT UNSIGNED NOT NULL,
  `remaining_length_unit` ENUM('millis', 'laps') NOT NULL,
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `competitions_metadata_history__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `teams` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `participant_code` VARCHAR(255) NOT NULL COMMENT 'Unique code given by the live timing (or auto-generated) to the team or the driver',
  `name` VARCHAR(255) NOT NULL,
  `number` INT UNSIGNED NULL,
  `reference_time_offset` INT NOT NULL DEFAULT 0 COMMENT 'Time offset with respect to the track reference',
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `name` (`competition_id`, `name`),
  UNIQUE KEY `participant_code` (`competition_id`, `participant_code`),
  CONSTRAINT `teams__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `drivers` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `team_id` INT UNSIGNED NULL,
  `participant_code` VARCHAR(255) NOT NULL COMMENT 'Unique code given by the live timing (or auto-generated) to the team or the driver',
  `name` VARCHAR(255) NOT NULL,
  `number` INT UNSIGNED NULL,
  `total_driving_time` INT UNSIGNED NOT NULL DEFAULT 0,
  `partial_driving_time` INT UNSIGNED NOT NULL DEFAULT 0,
  `reference_time_offset` INT NOT NULL DEFAULT 0 COMMENT 'Time offset with respect to the track reference',
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `team_driver` (`team_id`, `name`),
  CONSTRAINT `drivers__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`),
  CONSTRAINT `drivers__team_id` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `timing_current` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `team_id` INT UNSIGNED NULL,
  `driver_id` INT UNSIGNED NULL,
  `position` INT UNSIGNED NOT NULL,
  `time` INT UNSIGNED NOT NULL,
  `best_time` INT UNSIGNED NOT NULL,
  `lap` INT UNSIGNED NOT NULL,
  `interval` INT UNSIGNED NOT NULL,
  `interval_unit` ENUM('millis', 'laps') NOT NULL,
  `stage` ENUM('free-practice', 'classification', 'race') NOT NULL,
  `pits` INT UNSIGNED NULL,
  `kart_status` ENUM('unknown', 'good', 'medium', 'bad') NOT NULL DEFAULT 'unknown',
  `fixed_kart_status` ENUM('good', 'medium', 'bad') NULL,
  `number_pits` INT UNSIGNED NOT NULL DEFAULT 0,
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY (`competition_id`, `team_id`, `driver_id`),
  CONSTRAINT `timing_current__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`),
  CONSTRAINT `timing_current__team_id` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`),
  CONSTRAINT `timing_current__driver_id` FOREIGN KEY (`driver_id`) REFERENCES `drivers` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `timing_history` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `team_id` INT UNSIGNED NULL,
  `driver_id` INT UNSIGNED NULL,
  `position` INT UNSIGNED NOT NULL,
  `time` INT UNSIGNED NOT NULL,
  `best_time` INT UNSIGNED NOT NULL,
  `lap` INT UNSIGNED NOT NULL,
  `interval` INT UNSIGNED NOT NULL,
  `interval_unit` ENUM('millis', 'laps') NOT NULL,
  `stage` ENUM('free-practice', 'classification', 'race') NOT NULL,
  `pits` INT UNSIGNED NULL,
  `number_pits` INT UNSIGNED NOT NULL DEFAULT 0,
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `timing_history__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`),
  CONSTRAINT `timing_history__team_id` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`),
  CONSTRAINT `timing_history__driver_id` FOREIGN KEY (`driver_id`) REFERENCES `drivers` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `timing_karts_pits` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `team_id` INT UNSIGNED NULL,
  `action` ENUM('in', 'out') NOT NULL,
  `kart_status` ENUM('unknown', 'good', 'medium', 'bad') NOT NULL DEFAULT 'unknown',
  `fixed_kart_status` ENUM('good', 'medium', 'bad') NULL,
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `timing_karts_pits__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`),
  CONSTRAINT `timing_karts_pits__team_id` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `strategy_karts_probs` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `step` INT UNSIGNED NOT NULL,
  `kart_status` ENUM('unknown', 'good', 'medium', 'bad') NOT NULL DEFAULT 'unknown',
  `probability` FLOAT NOT NULL,
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `strategy_karts_probs__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`),
  UNIQUE KEY (`competition_id`, `step`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `stats_health` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `name` ENUM(
    'timing_connection',
    'api_connection',
    'script_ddbb_storage',
    'script_listener',
    'script_parser',
    'script_raw_storage',
    'script_analysis') NOT NULL,
  `label` VARCHAR(255) NULL,
  `status` ENUM('ok', 'warning', 'error', 'offline') NOT NULL DEFAULT 'offline',
  `message` VARCHAR(1000) NULL,
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `label_name` (`name`, `label`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
