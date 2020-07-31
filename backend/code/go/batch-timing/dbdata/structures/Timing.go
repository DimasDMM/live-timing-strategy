package structures

import (
	"database/sql"
	_ "github.com/go-sql-driver/mysql"
)

type Timing struct {
	ID int
	TeamID int
	TeamName string
	Position int
	Time int
	BestTime int
	Lap int
	Interval int
	IntervalUnit string
	Stage string
	KartStatus sql.NullString
	KartStatusGuess sql.NullString
	ForcedKartStatus sql.NullString
	NumberStops int
}
