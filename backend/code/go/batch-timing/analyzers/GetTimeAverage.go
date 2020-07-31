package analyzers

import (
	"batch-timing/dbdata/structures"
)

func GetTimeAverage(timing_list []structures.Timing) int {
	if len(timing_list) == 0 {
		return 0
	}

	average := 0
	for _, timing := range timing_list {
		average = average + timing.Time
	}
	average = average / len(timing_list)

	return average
}
