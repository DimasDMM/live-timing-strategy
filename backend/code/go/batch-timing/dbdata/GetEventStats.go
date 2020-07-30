package dbdata

import (
	"github.com/Knetic/go-namedParameterQuery"
	"batch-timing/dbdata/structures"
	"fmt"
	"strconv"
	"database/sql"
	_ "github.com/go-sql-driver/mysql"
)

func GetEventStats(connection *sql.DB, event_data *structures.EventData) (*structures.EventStats, int) {
	var (
		name string
		value string
	)
	event_stats := structures.EventStats{}

	table_name := event_data.TablesPrefix + "_event_stats"
	query := namedParameterQuery.NewNamedParameterQuery("SELECT `name`, `value` FROM " + table_name)

	rows, err := connection.Query(query.GetParsedQuery(), (query.GetParsedParameters())...)
	if err != nil {
		fmt.Println(err.Error())
		return nil, 1
	}
	defer rows.Close()
	
	for rows.Next() {
		err := rows.Scan(&name, &value)
		if err != nil {
			fmt.Println(err)
			return nil, 1
		}

		switch; name {
			case "reference_current_offset":
				event_stats.ReferenceCurrentOffset, _ = strconv.Atoi(value)
			case "reference_time":
				event_stats.ReferenceTime, _ = strconv.Atoi(value)
			case "remaining_event":
				event_stats.RemainingEvent, _ = strconv.Atoi(value)
			case "remaining_event_unit":
				event_stats.RemainingEventUnit = value
			case "stage":
				event_stats.Stage = value
			case "status":
				event_stats.Status = value
			default:
				fmt.Printf("Error: unknown stat \"%s\".\n", name)
				return nil, 1
		}
	}
	err = rows.Err()
	
	if err != nil {
		fmt.Println(err.Error())
		return nil, 1
	}

	return &event_stats, 0
}
