SET FOREIGN_KEY_CHECKS=0;

truncate table resistencialossantos_1ae66e9a_drivers;
truncate table resistencialossantos_1ae66e9a_event_config;
truncate table resistencialossantos_1ae66e9a_event_health;
truncate table resistencialossantos_1ae66e9a_event_stats;
truncate table resistencialossantos_1ae66e9a_karts_in;
truncate table resistencialossantos_1ae66e9a_karts_out;
truncate table resistencialossantos_1ae66e9a_karts_probs;
truncate table resistencialossantos_1ae66e9a_teams;
truncate table resistencialossantos_1ae66e9a_timing_historic;

INSERT INTO timing.resistencialossantos_1ae66e9a_event_health (category,name,status) VALUES 
('database','connection','offline')
,('crawler','api_connection','offline')
,('crawler','parse_timing','offline')
,('batch','karts_box_probs','offline')
,('batch','karts_status','offline')
,('batch','time_references','offline');

INSERT INTO timing.resistencialossantos_1ae66e9a_event_stats (name,value) VALUES 
('reference_current_offset','0')
,('reference_time','0')
,('remaining_event','unknown')
,('remaining_event_unit','milli')
,('stage','unknown')
,('status','offline');

INSERT INTO timing.resistencialossantos_1ae66e9a_event_config (name,value) VALUES 
('min_number_stops','4')
,('race_length','10800000')
,('race_length_unit','milli')
,('reference_time_top_teams','10')
,('stop_time','150000');

UPDATE resistencialossantos_1ae66e9a_event_stats s set s.value = 'online' where s.name = 'status';

SET FOREIGN_KEY_CHECKS=1;
