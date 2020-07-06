CREATE TABLE `events_index` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(255) NOT NULL,
  `table_prefix` VARCHAR(255) NOT NULL,
  `track_name` VARCHAR(255) NOT NULL,
  `event_type` VARCHAR(255) NOT NULL,
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `api_tokens` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `token` VARCHAR(255) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `role` ENUM('admin', 'batch', 'user') NOT NULL DEFAULT 'user',
  `insert_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_date` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `token` (`token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

INSERT INTO `api_tokens` (`token`, `name`, `role`) VALUES
  ('d265aed699f7409ac0ec6fe07ee9cb11', 'Batch', 'batch'),
  ('f9a23e776e199b52f12f60cd1ea0dfc3', 'Dimas', 'admin');
