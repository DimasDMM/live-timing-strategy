CREATE TABLE `{event_name}_teams` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(255) COLLATE utf8_unicode_ci NOT NULL,
  `team_number` INT UNSIGNED NULL,
  `number_drivers` INT UNSIGNED DEFAULT 1,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `{event_name}_drivers` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `team_id` INT UNSIGNED NULL,
  `name` VARCHAR(255) COLLATE utf8_unicode_ci NOT NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `team_driver` (`name`, `team_id`),
  CONSTRAINT `{event_name}_drivers__team_id` FOREIGN KEY (`team_id`) REFERENCES `{event_name}_teams` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `{event_name}_timing` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `team_id` INT UNSIGNED NULL,
  `driver_id` INT UNSIGNED NULL,
  `time` TIME NOT NULL,
  `lap` INT NOT NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `{event_name}_timing__team_id` FOREIGN KEY (`team_id`) REFERENCES `{event_name}_teams` (`id`)
  CONSTRAINT `{event_name}_timing__driver_id` FOREIGN KEY (`driver_id`) REFERENCES `{event_name}_drivers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `{event_name}_team_stats` (
  `team_id` INT UNSIGNED NULL,
  `name` VARCHAR(255) COLLATE utf8_unicode_ci NOT NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`team_id`),
  CONSTRAINT `{event_name}_team_stats__team_id` FOREIGN KEY (`team_id`) REFERENCES `{event_name}_teams` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
