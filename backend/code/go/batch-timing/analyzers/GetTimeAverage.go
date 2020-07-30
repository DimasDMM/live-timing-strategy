package analyzers

import (
	"sort"
	"batch-timing/dbdata/structures"
)

const MIN_LAPS = 5

// Only use the best X percentage of times
const CUT_RATIO = 0.9

// Only cut if there are at least X times
const MIN_TIMES_TO_CUT = 20

func GetTimeAverage(
	timing_list []structures.Timing,
	event_data *structures.EventData,
	event_stats *structures.EventStats,
) int {
	// Sort times
	sort.SliceStable(timing_list, func(i, j int) bool {
		return timing_list[i].Time < timing_list[j].Time
	})

	requiredTimes := event_data.NumberTeams * MIN_LAPS
	if len(timing_list) < requiredTimes {
		// Not enough times in the list
		return 0
	}

	var sublist []structures.Timing
	if len(timing_list) < MIN_TIMES_TO_CUT {
		sublist = timing_list
	} else {
		sublist_index := int(float64(len(timing_list)) * CUT_RATIO)
		sublist = timing_list[:sublist_index]
	}

	// Compute average
	average := 0
	for _, timing := range sublist {
		average = average + timing.Time
	}
	average = average / len(sublist)

	return average
}
