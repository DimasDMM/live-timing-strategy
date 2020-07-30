package dbdata

import (
	"github.com/Knetic/go-namedParameterQuery"
	"batch-timing/dbdata/structures"
	"fmt"
	"database/sql"
	_ "github.com/go-sql-driver/mysql"
)

const MIN_LAPS = 5

func GetLastTiming(
	connection *sql.DB,
	event_data *structures.EventData,
	event_stats *structures.EventStats,
) ([]structures.Timing, int) {
	if event_data.NumberTeams == 0 {
		return nil, 0
	}

	// Definition
	var (
		id int
		team_id int
		team_name string
		position int
		time int
		best_time int
		lap int
		interval int
		interval_unit string
		stage string
		kart_status structures.NullString
		kart_status_guess structures.NullString
		forced_kart_status structures.NullString
		number_stops int
	)
	
	// Limit based on the number of teams
	limit := event_data.NumberTeams * MIN_LAPS
	
	table_timing := event_data.TablesPrefix + "_timing_historic"
	table_teams := event_data.TablesPrefix + "_teams"
	query := namedParameterQuery.NewNamedParameterQuery(
		"SELECT " +
		"   th.`id`, " +
		"   th.`team_id`, " +
		"   teams.`name` team_name, " +
		"   th.`position`, " +
		"   th.`time`, " +
		"   th.`best_time`, " +
		"   th.`lap`, " +
		"   th.`interval`, " +
		"   th.`interval_unit`, " +
		"   th.`stage`, " +
		"   th.`kart_status`, " +
		"   th.`kart_status_guess`, " +
		"   th.`forced_kart_status`, " +
		"   th.`number_stops` " +
		"FROM " + table_timing + " th " +
		"JOIN " + table_teams + " teams " +
		"WHERE th.stage = :stage " +
		"ORDER BY th.insert_date DESC " +
		"LIMIT :limit",
	)
	query.SetValue("stage", event_stats.Stage)
	query.SetValue("limit", limit)

	rows, err := connection.Query(query.GetParsedQuery(), (query.GetParsedParameters())...)
	if err != nil {
		fmt.Println(err.Error())
		return nil, 1
	}
	defer rows.Close()
	
	timing_list := []structures.Timing{}
	for rows.Next() {
		err := rows.Scan(
			&id,
			&team_id,
			&team_name,
			&position,
			&time,
			&best_time,
			&lap,
			&interval,
			&interval_unit,
			&stage,
			&kart_status,
			&kart_status_guess,
			&forced_kart_status,
			&number_stops,
		)
		if err != nil {
			fmt.Println(err)
			return nil, 1
		}

		timing := structures.Timing{
			ID: id,
			TeamID: team_id,
			TeamName: team_name,
			Position: position,
			Time: time,
			BestTime: best_time,
			Lap: lap,
			Interval: interval,
			IntervalUnit: interval_unit,
			Stage: stage,
			KartStatus: kart_status,
			KartStatusGuess: kart_status_guess,
			ForcedKartStatus: forced_kart_status,
			NumberStops: number_stops,
		}

		timing_list = append(timing_list, timing)
	}
	err = rows.Err()
	
	if err != nil {
		fmt.Println(err.Error())
		return nil, 1
	}

	return timing_list, 0
}
