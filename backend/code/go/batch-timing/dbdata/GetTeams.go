package dbdata

import (
	"github.com/Knetic/go-namedParameterQuery"
	"batch-timing/dbdata/structures"
	"fmt"
	"database/sql"
	_ "github.com/go-sql-driver/mysql"
)

func GetTeams(
	connection *sql.DB,
	event_data *structures.EventData,
	event_stats *structures.EventStats,
) ([]structures.Team, int) {
	if event_data.NumberTeams == 0 {
		return nil, 0
	}
	
	const MIN_LAPS = 5

	// Definition
	var (
		id int
		name string
		number int
		reference_time_offset int
	)
	
	table_name := event_data.TablesPrefix + "_teams"
	query := namedParameterQuery.NewNamedParameterQuery(
		"SELECT " +
		"   teams.`id`, " +
		"   teams.`name`, " +
		"   teams.`number`, " +
		"   teams.`reference_time_offset` " +
		"FROM " + table_name + " teams ",
	)

	rows, err := connection.Query(query.GetParsedQuery())
	if err != nil {
		fmt.Println(err.Error())
		return nil, 1
	}
	defer rows.Close()
	
	team_list := []structures.Team{}
	for rows.Next() {
		err := rows.Scan(
			&id,
			&name,
			&number,
			&reference_time_offset,
		)
		if err != nil {
			fmt.Println(err)
			return nil, 1
		}

		team := structures.Team{
			ID: id,
			Name: name,
			Number: number,
			ReferenceTimeOffset: reference_time_offset,
		}

		team_list = append(team_list, team)
	}
	err = rows.Err()
	
	if err != nil {
		fmt.Println(err.Error())
		return nil, 1
	}

	return team_list, 0
}
