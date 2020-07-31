package dbdata

import (
	"fmt"
	"github.com/Knetic/go-namedParameterQuery"
	"batch-timing/dbdata/structures"
	"database/sql"
	_ "github.com/go-sql-driver/mysql"
)

func UpdateTeamLastKartStatus(
	connection *sql.DB,
	event_data *structures.EventData,
	event_stats *structures.EventStats,
	team_id int,
	kart_status string,
) (int) {
	table_name := event_data.TablesPrefix + "_timing_historic"
	query := namedParameterQuery.NewNamedParameterQuery(
		"UPDATE " + table_name + " " +
		"SET kart_status = :kartStatus " +
		"WHERE team_id = :teamId AND stage = :stage " +
		"ORDER BY id DESC " +
		"LIMIT 1",
	)
	query.SetValue("kartStatus", kart_status)
	query.SetValue("teamId", team_id)
	query.SetValue("stage", event_stats.Stage)
	
	_, err := connection.Exec(query.GetParsedQuery(), (query.GetParsedParameters())...)
	if err != nil {
		fmt.Println(err.Error())
		return 1
	}

	return 0
}
