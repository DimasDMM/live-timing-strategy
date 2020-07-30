package dbdata

import (
	"github.com/Knetic/go-namedParameterQuery"
	"batch-timing/dbdata/structures"
	"fmt"
	"database/sql"
	_ "github.com/go-sql-driver/mysql"
)

func GetEventData(connection *sql.DB, event_name string) (*structures.EventData, int) {
	var (tables_prefix string)

	query := namedParameterQuery.NewNamedParameterQuery("SELECT tables_prefix FROM events_index WHERE name = :eventName")
	query.SetValue("eventName", event_name)
	err := connection.QueryRow(query.GetParsedQuery(), (query.GetParsedParameters())...).Scan(&tables_prefix)
	if err != nil {
		fmt.Println(err.Error())
		return nil, 1
	}

	event_data := structures.EventData{
		TablesPrefix: tables_prefix,
		NumberTeams: GetNumberTeams(connection, tables_prefix),
	}
	return &event_data, 0
}

func GetNumberTeams(connection *sql.DB, tables_prefix string) int {
	var (total int)

	table_name := tables_prefix + "_teams"
	query := namedParameterQuery.NewNamedParameterQuery("SELECT count(*) total FROM " + table_name)
	err := connection.QueryRow(query.GetParsedQuery(), (query.GetParsedParameters())...).Scan(&total)
	if err != nil {
		fmt.Println(err.Error())
		return 0
	} else {
		return total
	}
}
