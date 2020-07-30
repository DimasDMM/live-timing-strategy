package structures

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
	KartStatus NullString
	KartStatusGuess NullString
	ForcedKartStatus NullString
	NumberStops int
}
