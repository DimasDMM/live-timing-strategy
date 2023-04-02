START TRANSACTION;

SET autocommit=0;

CREATE DATABASE	IF NOT EXISTS `live-timing`;
USE `live-timing`;

CREATE TABLE `api_tokens` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `token` VARCHAR(255) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `role` ENUM('admin', 'batch', 'user') NOT NULL DEFAULT 'user',
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `token` (`token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `tracks` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(255) NOT NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `token` (`token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `competitions_index` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `track_id` INT UNSIGNED NOT NULL,
  `code` VARCHAR(255) NOT NULL COMMENT 'Verbose ID to identify a competition',
  `name` VARCHAR(255) NOT NULL,
  `description` VARCHAR(2000) NOT NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `competitions_index__track_id` FOREIGN KEY (`track_id`) REFERENCES `tracks` (`id`),
  UNIQUE KEY `code` (`code`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `competitions_teams` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `code` VARCHAR(255) NULL COMMENT 'Optional unique code given by the live timing',
  `name` VARCHAR(255) NOT NULL,
  `number` INT UNSIGNED NULL,
  `reference_time_offset` INT DEFAULT 0 COMMENT 'Respect track reference',
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `code` (`code`),
  CONSTRAINT `competitions_teams__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `competitions_drivers` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `team_id` INT UNSIGNED NULL,
  `name` VARCHAR(255) NOT NULL,
  `total_driving_time` INT UNSIGNED DEFAULT 0,
  `partial_driving_time` INT UNSIGNED DEFAULT 0,
  `reference_time_offset` INT DEFAULT 0 COMMENT 'Respect track reference',
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `team_driver` (`team_id`, `name`),
  CONSTRAINT `competitions_drivers__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`),
  CONSTRAINT `competitions_drivers__team_id` FOREIGN KEY (`team_id`) REFERENCES `competitions_teams` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `competitions_timing_history` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `team_id` INT UNSIGNED NULL,
  `driver_id` INT UNSIGNED NULL,
  `position` INT UNSIGNED NOT NULL,
  `time` INT UNSIGNED NOT NULL,
  `best_time` INT UNSIGNED NOT NULL,
  `lap` INT UNSIGNED NOT NULL,
  `interval` INT UNSIGNED NOT NULL,
  `interval_unit` ENUM('milli', 'laps') NOT NULL,
  `stage` ENUM('free-practice', 'classification', 'race') NOT NULL,
  `pits` INT UNSIGNED NULL,
  `kart_status` ENUM('unknown', 'good', 'medium', 'bad') NOT NULL DEFAULT 'unknown',
  `fixed_kart_status` ENUM('good', 'medium', 'bad') NULL,
  `number_pits` INT UNSIGNED NOT NULL DEFAULT 0,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `competitions_timing__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`),
  CONSTRAINT `competitions_timing__team_id` FOREIGN KEY (`team_id`) REFERENCES `competitions_teams` (`id`),
  CONSTRAINT `competitions_timing__driver_id` FOREIGN KEY (`driver_id`) REFERENCES `competitions_drivers` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `competitions_karts_in` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `team_id` INT UNSIGNED NULL,
  `kart_status` ENUM('unknown', 'good', 'medium', 'bad') NOT NULL DEFAULT 'unknown',
  `fixed_kart_status` ENUM('good', 'medium', 'bad') NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `competitions_karts_in__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`),
  CONSTRAINT `competitions_karts_in__team_id` FOREIGN KEY (`team_id`) REFERENCES `competitions_teams` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `competitions_karts_out` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `team_id` INT UNSIGNED NULL,
  `kart_status` ENUM('unknown', 'good', 'medium', 'bad') NOT NULL DEFAULT 'unknown',
  `fixed_kart_status` ENUM('good', 'medium', 'bad') NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `competitions_karts_out__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`),
  CONSTRAINT `competitions_karts_out__team_id` FOREIGN KEY (`team_id`) REFERENCES `competitions_teams` (`id`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `competitions_settings` (
  `competition_id` INT UNSIGNED NOT NULL,
  `name` ENUM (
    'race_length',
    'race_length_unit',
    'karts_in_box',
    'pit_time',
    'min_number_pits') NOT NULL,
  `value` VARCHAR(255) NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `competitions_settings__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`),
  PRIMARY KEY(`competition_id`, `name`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `competitions_metadata` (
  `competition_id` INT UNSIGNED NOT NULL,
  `name` ENUM(
    'reference_time',
    'reference_current_offset',
    'status',
    'stage',
    'remaining_competition',
    'remaining_competition_unit') NOT NULL,
  `value` VARCHAR(255) NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `competitions_metadata__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`),
  PRIMARY KEY(`competition_id`, `name`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `competitions_metadata_history` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `competition_id` INT UNSIGNED NOT NULL,
  `name` ENUM(
    'reference_time',
    'reference_current_offset',
    'status',
    'stage',
    'remaining_competition',
    'remaining_competition_unit') NOT NULL,
  `value` VARCHAR(255) NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `competitions_metadata__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`)
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
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `label_name` (`name`, `label`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `strategy_karts_probs` (
  `competition_id` INT UNSIGNED NOT NULL,
  `step` INT UNSIGNED NOT NULL,
  `kart_status` ENUM('unknown', 'good', 'medium', 'bad') NOT NULL DEFAULT 'unknown',
  `probability` FLOAT NOT NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `strategy_karts_probs__competition_id` FOREIGN KEY (`competition_id`) REFERENCES `competitions_index` (`id`),
  PRIMARY KEY (`competition_id`, `step`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `parsers_config` (
  `competition_id` INT UNSIGNED NOT NULL,
  `key` VARCHAR(255) NOT NULL,
  `value` VARCHAR(255) NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


INSERT INTO `api_tokens` (`token`, `name`, `role`) VALUES
  ('d265aed699f7409ac0ec6fe07ee9cb11', 'Batch', 'batch'),
  ('f9a23e776e199b52f12f60cd1ea0dfc3', 'Dimas', 'admin');

INSERT INTO `tracks` (`name`) VALUES
  ('Karting Los Santos');

COMMIT;
