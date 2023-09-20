-- Optionally, we may run this command to re-build the database:
-- DROP DATABASE IF EXISTS `live-timing`;

CREATE DATABASE	IF NOT EXISTS `live-timing`;
USE `live-timing`;

SET GLOBAL time_zone = 'Europe/Madrid';

-- Note: this should be stored in the config file of MySQL
SET sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
-- --


CREATE TABLE `api_auth` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `key` VARCHAR(255) NOT NULL,
  `bearer` VARCHAR(255) NULL,
  `name` VARCHAR(255) NOT NULL,
  `role` ENUM('admin', 'batch', 'viewer') NOT NULL DEFAULT 'viewer',
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `key` (`key`)
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
  `competition_id` INT UNSIGNED NOT NULL PRIMARY KEY,
  `reference_time` INT NULL COMMENT 'Reference time (usually, the median) of the track during practice or early stages',
  `reference_current_offset` INT NULL COMMENT 'Time offset with respect to the track reference',
  `status` ENUM('paused', 'ongoing', 'finished') NOT NULL,
  `stage` ENUM('free-practice', 'qualifying', 'race') NOT NULL,
  `remaining_length` INT UNSIGNED NOT NULL,
  `remaining_length_unit` ENUM('millis', 'laps') NOT NULL,
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `competitions_metadata__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `competitions_metadata_history` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `reference_time` INT NULL COMMENT 'Reference time (usually, the median) of the track during practice or early stages',
  `reference_current_offset` INT NULL COMMENT 'Time offset with respect to the track reference',
  `status` ENUM('paused', 'ongoing', 'finished') NOT NULL,
  `stage` ENUM('free-practice', 'qualifying', 'race') NOT NULL,
  `remaining_length` INT UNSIGNED NOT NULL,
  `remaining_length_unit` ENUM('millis', 'laps') NOT NULL,
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `competitions_metadata_history__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `participants_teams` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `participant_code` VARCHAR(255) NOT NULL COMMENT 'Unique code given by the live timing (or auto-generated) to the team or the driver',
  `name` VARCHAR(255) NOT NULL,
  `number` INT UNSIGNED NULL,
  `reference_time_offset` INT NULL COMMENT 'Time offset with respect to the track reference',
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `name` (`competition_id`, `name`),
  UNIQUE KEY `participant_code` (`competition_id`, `participant_code`),
  CONSTRAINT `participants_teams__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `participants_drivers` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `team_id` INT UNSIGNED NULL,
  `participant_code` VARCHAR(255) NOT NULL COMMENT 'Unique code given by the live timing (or auto-generated) to the team or the driver',
  `name` VARCHAR(255) NOT NULL,
  `number` INT UNSIGNED NULL,
  `total_driving_time` INT UNSIGNED NOT NULL DEFAULT 0,
  `partial_driving_time` INT UNSIGNED NOT NULL DEFAULT 0,
  `reference_time_offset` INT NULL COMMENT 'Time offset with respect to the track reference',
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `team_driver_name` (`team_id`, `name`),
  CONSTRAINT `participants_drivers__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`),
  CONSTRAINT `participants_drivers__team_id` FOREIGN KEY (`team_id`) REFERENCES `participants_teams` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `timing_current` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `team_id` INT UNSIGNED NULL,
  `driver_id` INT UNSIGNED NULL,
  `position` INT UNSIGNED NOT NULL,
  `last_time` INT UNSIGNED NOT NULL,
  `best_time` INT UNSIGNED NOT NULL,
  `lap` INT UNSIGNED NOT NULL,
  `gap` INT UNSIGNED NULL,
  `gap_unit` ENUM('millis', 'laps') NULL,
  `interval` INT UNSIGNED NULL,
  `interval_unit` ENUM('millis', 'laps') NULL,
  `stage` ENUM('free-practice', 'qualifying', 'race') NOT NULL,
  `pit_time` INT UNSIGNED NULL,
  `kart_status` ENUM('unknown', 'good', 'medium', 'bad') NOT NULL DEFAULT 'unknown',
  `fixed_kart_status` ENUM('unknown', 'good', 'medium', 'bad') NULL,
  `number_pits` INT UNSIGNED NOT NULL DEFAULT 0,
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY (`competition_id`, `team_id`, `driver_id`),
  CONSTRAINT `timing_current__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`),
  CONSTRAINT `timing_current__team_id` FOREIGN KEY (`team_id`) REFERENCES `participants_teams` (`id`),
  CONSTRAINT `timing_current__driver_id` FOREIGN KEY (`driver_id`) REFERENCES `participants_drivers` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `timing_history` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `team_id` INT UNSIGNED NULL,
  `driver_id` INT UNSIGNED NULL,
  `position` INT UNSIGNED NOT NULL,
  `last_time` INT UNSIGNED NOT NULL,
  `best_time` INT UNSIGNED NOT NULL,
  `lap` INT UNSIGNED NOT NULL,
  `gap` INT UNSIGNED NULL,
  `gap_unit` ENUM('millis', 'laps') NULL,
  `interval` INT UNSIGNED NULL,
  `interval_unit` ENUM('millis', 'laps') NULL,
  `stage` ENUM('free-practice', 'qualifying', 'race') NOT NULL,
  `pit_time` INT UNSIGNED NULL,
  `kart_status` ENUM('unknown', 'good', 'medium', 'bad') NOT NULL DEFAULT 'unknown',
  `fixed_kart_status` ENUM('unknown', 'good', 'medium', 'bad') NULL,
  `number_pits` INT UNSIGNED NOT NULL DEFAULT 0,
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `timing_history__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`),
  CONSTRAINT `timing_history__team_id` FOREIGN KEY (`team_id`) REFERENCES `participants_teams` (`id`),
  CONSTRAINT `timing_history__driver_id` FOREIGN KEY (`driver_id`) REFERENCES `participants_drivers` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `timing_pits_in` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `team_id` INT UNSIGNED NULL,
  `driver_id` INT UNSIGNED NULL,
  `lap` INT UNSIGNED NOT NULL,
  `pit_time` INT UNSIGNED NULL,
  `kart_status` ENUM('unknown', 'good', 'medium', 'bad') NOT NULL DEFAULT 'unknown',
  `fixed_kart_status` ENUM('good', 'medium', 'bad') NULL,
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `timing_pits_in__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`),
  CONSTRAINT `timing_pits_in__team_id` FOREIGN KEY (`team_id`) REFERENCES `participants_teams` (`id`),
  CONSTRAINT `timing_pits_in__driver_id` FOREIGN KEY (`driver_id`) REFERENCES `participants_drivers` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `timing_pits_out` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `team_id` INT UNSIGNED NULL,
  `driver_id` INT UNSIGNED NULL,
  `kart_status` ENUM('unknown', 'good', 'medium', 'bad') NOT NULL DEFAULT 'unknown',
  `fixed_kart_status` ENUM('good', 'medium', 'bad') NULL,
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `timing_pits_out__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`),
  CONSTRAINT `timing_pits_out__team_id` FOREIGN KEY (`team_id`) REFERENCES `participants_teams` (`id`),
  CONSTRAINT `timing_pits_out__driver_id` FOREIGN KEY (`driver_id`) REFERENCES `participants_drivers` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `timing_pits_in_out` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `pit_in_id` INT UNSIGNED NOT NULL,
  `pit_out_id` INT UNSIGNED NOT NULL,
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `timing_pits_in_out__pit_in_id` FOREIGN KEY (`pit_in_id`) REFERENCES `timing_pits_in` (`id`),
  CONSTRAINT `timing_pits_in_out__pit_out_id` FOREIGN KEY (`pit_out_id`) REFERENCES `timing_pits_out` (`id`),
  UNIQUE KEY `pit_in_id`(`pit_in_id`),
  UNIQUE KEY `pit_out_id`(`pit_out_id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `strategy_pits_stats` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `pit_in_id` INT UNSIGNED NOT NULL,
  `best_time` INT UNSIGNED NOT NULL,
  `avg_time` INT UNSIGNED NOT NULL,
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `strategy_pits_stats__pit_in_id` FOREIGN KEY (`pit_in_id`) REFERENCES `timing_pits_in` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `strategy_pits_karts` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `pit_in_id` INT UNSIGNED NOT NULL,
  `step` INT UNSIGNED NOT NULL,
  `kart_status` ENUM('unknown', 'good', 'medium', 'bad') NOT NULL DEFAULT 'unknown',
  `probability` FLOAT NOT NULL,
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `strategy_pits_karts__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`),
  CONSTRAINT `strategy_pits_karts__pit_in_id` FOREIGN KEY (`pit_in_id`) REFERENCES `timing_pits_in` (`id`)
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

CREATE TABLE `parsers_settings` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `value` VARCHAR(255) NOT NULL,
  `insert_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `parsers_settings__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`),
  UNIQUE KEY `competition_name` (`competition_id`, `name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
