package dbdata

import (
	"github.com/Knetic/go-namedParameterQuery"
	"batch-timing/dbdata/structures"
	"fmt"
	"database/sql"
	_ "github.com/go-sql-driver/mysql"
)

func GetLastTimingByTeam(
	connection *sql.DB,
	event_data *structures.EventData,
	event_stats *structures.EventStats,
	team_id int,
	limit int,
) ([]structures.Timing, int) {
	if event_data.NumberTeams == 0 {
		return nil, 0
	}

	// Definition
	var (
		id int
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

	clause_limit := ""
	if limit > 0 {
		clause_limit = "LIMIT :limit"
	}
	
	table_timing := event_data.TablesPrefix + "_timing_historic"
	table_teams := event_data.TablesPrefix + "_teams"
	query := namedParameterQuery.NewNamedParameterQuery(
		"SELECT " +
		"   th.`id`, " +
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
		"WHERE " +
		"	th.stage = :stage AND " +
		"	th.team_id = :teamId " +
		"ORDER BY th.insert_date DESC " +
		clause_limit,
	)
	query.SetValue("stage", event_stats.Stage)
	query.SetValue("teamId", team_id)
	if limit > 0 {
		query.SetValue("limit", limit)
	}

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
