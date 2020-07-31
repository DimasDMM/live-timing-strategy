package analyzers

import (
	"sort"
	"batch-timing/dbdata/structures"
	"github.com/jinzhu/copier"
)

func GetTimeAverage(
	timing_list []structures.Timing,
	event_data *structures.EventData,
	event_stats *structures.EventStats,
	min_required int,
	only_last_pit bool,
	only_min_required bool,
) int {
	if only_last_pit {
		// Filter times of last pit
		timing_list = GetLastPitTimes(timing_list)
	}

	// Only use the best X percentage of times
	const CUT_RATIO = 0.8

	// Only cut if there are at least X times
	const MIN_TIMES_TO_CUT = 10

	// Sort times
	sort.SliceStable(timing_list, func(i, j int) bool {
		return timing_list[i].Time < timing_list[j].Time
	})

	if len(timing_list) < min_required {
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

func GetLastPitTimes(timing_list []structures.Timing) []structures.Timing {
	// Find last pit
	last_pit := 0
	for _, timing := range timing_list {
		if timing.NumberStops > last_pit {
			last_pit = timing.NumberStops
		}
	}

	// Copy of slice to filter times
	parsed_timing_list := []structures.Timing{}
	copier.Copy(&parsed_timing_list, &timing_list)

	// Apply filtering
	for i := len(timing_list) - 1; i >= 0; i-- {
		if parsed_timing_list[i].NumberStops != last_pit {
			if len(parsed_timing_list) == i + 1 {
				// Truncate slice
				parsed_timing_list = parsed_timing_list[:len(parsed_timing_list)-1]
			} else {
				// Copy last item to the index to be removed
				parsed_timing_list[i] = parsed_timing_list[len(parsed_timing_list)-1]
			}
		}
	}

	return parsed_timing_list
}
