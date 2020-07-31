package dbdata

import (
	"fmt"
	"github.com/Knetic/go-namedParameterQuery"
	"batch-timing/dbdata/structures"
	"database/sql"
	_ "github.com/go-sql-driver/mysql"
)

func UpdateTeamTimeOffset(
	connection *sql.DB,
	event_data *structures.EventData,
	team_id int,
	time_offset int,
) (int) {
	table_name := event_data.TablesPrefix + "_teams"
	query := namedParameterQuery.NewNamedParameterQuery(
		"UPDATE " + table_name + " " +
		"SET `reference_time_offset` = :timeOffset " +
		"WHERE `id` = :teamId ",
	)
	query.SetValue("timeOffset", time_offset)
	query.SetValue("teamId", team_id)
	
	_, err := connection.Exec(query.GetParsedQuery(), (query.GetParsedParameters())...)
	if err != nil {
		fmt.Println(err.Error())
		return 1
	}

	return 0
}
