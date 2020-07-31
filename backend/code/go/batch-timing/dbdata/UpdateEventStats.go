package dbdata

import (
	"fmt"
	"strconv"
	"github.com/Knetic/go-namedParameterQuery"
	"batch-timing/dbdata/structures"
	"database/sql"
	_ "github.com/go-sql-driver/mysql"
	"github.com/jinzhu/copier"
)

var last_event_stats *structures.EventStats
var initialized bool

func UpdateEventStats(
	connection *sql.DB,
	event_data *structures.EventData,
	event_stats *structures.EventStats,
) (int) {
	first_run := false
	if !initialized {
		// Initialize
		copier.Copy(&last_event_stats, &event_stats)
		initialized = true
		first_run = true
	}
	
	// Depending on the stage, it updates different stats
	if event_stats.Stage == "classification" {
		if first_run || last_event_stats.ReferenceTime != event_stats.ReferenceTime {
			err := UpdateEventStatByName(
				connection,
				event_data.TablesPrefix,
				"reference_time",
				strconv.Itoa(event_stats.ReferenceTime),
			)
			if err != 0 {
				return err
			}
		}
	} else if event_stats.Stage == "race" {
		if first_run || last_event_stats.ReferenceCurrentOffset != event_stats.ReferenceCurrentOffset {
			err := UpdateEventStatByName(
				connection,
				event_data.TablesPrefix,
				"reference_current_offset",
				strconv.Itoa(event_stats.ReferenceCurrentOffset),
			)
			if err != 0 {
				return err
			}
		}
	}
	
	// Save last state
	copier.Copy(&last_event_stats, &event_stats)

	return 0
}

func UpdateEventStatByName(connection *sql.DB, tables_prefix string, name string, value string) int {
	table_name := tables_prefix + "_event_stats"
	query := namedParameterQuery.NewNamedParameterQuery(
		"UPDATE " + table_name + " " +
		"SET `value` = :value " +
		"WHERE `name` = :name ",
	)
	query.SetValue("name", name)
	query.SetValue("value", value)
	
	_, err := connection.Exec(query.GetParsedQuery(), (query.GetParsedParameters())...)
	if err != nil {
		fmt.Println(err.Error())
		return 1
	}

	return 0
}
