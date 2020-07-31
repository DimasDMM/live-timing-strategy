package main

import (
	"fmt"
	"os"
	"time"
	"batch-timing/mysql"
	"batch-timing/analyzers"
	"batch-timing/dbdata"
	"batch-timing/filedata"
)

func main() {
	fmt.Println("### BATCH TIMING ###")

	settings := filedata.GetSettings("/data/settings.json")
	fmt.Println("Settings:")
	fmt.Println("- Event name: " + settings.EventName)

	db_host := os.Getenv("DB_HOST")
	db_port := os.Getenv("DB_INTERNAL_PORT")
	db_user := os.Getenv("DB_USER")
	db_pass := os.Getenv("DB_PASS")
	db_database := os.Getenv("DB_DATABASE")
	connection := mysql.MysqlConnect(db_host, db_port, db_user, db_pass, db_database)

	fmt.Println("Loading event data...")
	event_data, err_code := dbdata.GetEventData(connection, settings.EventName)
	if err_code != 0 {
		fmt.Println("- Event not found")
		os.Exit(1)
	}
	fmt.Println("- Table prefix: " + event_data.TablesPrefix)

	fmt.Println("Main loop run:")
	for i := 0; true; i++ {
		fmt.Println("------------")
		fmt.Println("Retrieving stats...")
		event_stats, err_code := dbdata.GetEventStats(connection, event_data)
		if err_code != 0 {
			os.Exit(1)
		}

		fmt.Printf("Status: %s - Stage: %s\n", event_stats.Status, event_stats.Stage)

		if event_stats.Status == "offline" {
			// If event is offline, wait and start again
			fmt.Println("Waiting 20 seconds to check stats again...")
			time.Sleep(20 * time.Second)
			continue
        }
        
        // Compute reference time or offset depending on the stage of the race
		fmt.Println("Computing reference time...")
		limit := event_data.NumberTeams * 5
        timing_list, err_code := dbdata.GetLastTiming(connection, event_data, event_stats, limit)
        if event_stats.Stage == "classification" {
			// Reference time
			min_required := event_data.NumberTeams * 5
			timing_list = analyzers.FilterMinRequiredTimes(timing_list, min_required, false, 0.66)
            ref_time := analyzers.GetTimeAverage(timing_list)
            fmt.Printf("- Reference time: %d\n", ref_time)
            event_stats.ReferenceTime = ref_time
        } else {
            // Time offset respect the reference time
			min_required := event_data.NumberTeams * 5
			timing_list = analyzers.FilterMinRequiredTimes(timing_list, min_required, false, 0.66)
            ref_time := analyzers.GetTimeAverage(timing_list)
            time_offset := ref_time - event_stats.ReferenceTime
            fmt.Printf("- Reference time: %d\n", ref_time)
            fmt.Printf("- Time offset: %d\n", time_offset)
            event_stats.ReferenceTime = ref_time
            event_stats.ReferenceCurrentOffset = time_offset
        }

		// Update event stats
		fmt.Println("- Updating stats (if necessary)...")
		dbdata.UpdateEventStats(connection, event_data, event_stats)

		if event_stats.ReferenceTime == 0 {
			fmt.Println("No time reference to make computations...")
		} else {
			teams, err_code := dbdata.GetTeams(connection, event_data, event_stats)
			if err_code != 0 {
				os.Exit(1)
			}

			if event_stats.Stage == "classification" {
				// Compute offset time (only in classification)
				fmt.Println("Computing offset time of each team...")
				for _, team := range teams {
					fmt.Printf("- Team: %s\n", team.Name)
					timing_list, err_code = dbdata.GetLastTimingByTeam(connection, event_data, event_stats, team.ID, -1)
					if err_code != 0 {
						os.Exit(1)
					}

					// Compute offset time of each team
					filtered_timing_list := analyzers.FilterMinRequiredTimes(timing_list, 10, true, 0.8)
					ref_time := analyzers.GetTimeAverage(filtered_timing_list)
					time_offset := ref_time - event_stats.ReferenceTime
					dbdata.UpdateTeamTimeOffset(connection, event_data, team.ID, time_offset)
					fmt.Printf("-- Reference time: %d\n", ref_time)
					fmt.Printf("-- Time offset: %d\n", time_offset)
					team.ReferenceTimeOffset = time_offset
				}
			}

			// Compute kart status
			fmt.Println("Computing kart status...")
			for _, team := range teams {
				fmt.Printf("- Team: %s\n", team.Name)
				timing_list, err_code = dbdata.GetLastTimingByTeam(connection, event_data, event_stats, team.ID, 15)
				if err_code != 0 {
					os.Exit(1)
				}

				// Compute offset time of each team
				filtered_timing_list := analyzers.FilterMinRequiredTimes(timing_list, 8, true, 0.66)
				ref_time := analyzers.GetTimeAverage(filtered_timing_list)

				if ref_time == 0 {
					fmt.Println("-- Not enough times")
				} else {
					time_diff := ref_time - event_stats.ReferenceTime - team.ReferenceTimeOffset + event_stats.ReferenceCurrentOffset
					var (kart_status string)
					if time_diff < 0 {
						kart_status = "good"
					} else {
						kart_status = "bad"
					}
					dbdata.UpdateTeamLastKartStatus(connection, event_data, event_stats, team.ID, kart_status)
					fmt.Printf("-- Kart status: %s (diff: %d)\n", kart_status, time_diff)
				}
			}
		}

		fmt.Println("Finishing...")
		break
	}

	mysql.MysqlClose(connection)
	os.Exit(0)
}
