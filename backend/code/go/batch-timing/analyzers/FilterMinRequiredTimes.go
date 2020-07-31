package analyzers

import (
	"sort"
	"batch-timing/dbdata/structures"
	"github.com/jinzhu/copier"
)

func FilterMinRequiredTimes(
	timing_list []structures.Timing,
	min_required int,
	only_last_pit bool,
	cut_ratio float64,
) []structures.Timing {
	if only_last_pit {
		// Filter times of last pit
		timing_list = GetLastPitTimes(timing_list)
	}

	// Sort times
	sort.SliceStable(timing_list, func(i, j int) bool {
		return timing_list[i].Time < timing_list[j].Time
	})

	if len(timing_list) < min_required {
		// Not enough times in the list
		return []structures.Timing{}
	}

	sublist_index := int(float64(len(timing_list)) * cut_ratio)
	sublist := timing_list[:sublist_index]

	return sublist
}

func GetLastPitTimes(timing_list []structures.Timing) []structures.Timing {
	// Copy of slice to filter times
	parsed_timing_list := []structures.Timing{}
	copier.Copy(&parsed_timing_list, &timing_list)

	if len(timing_list) == 1 {
		return parsed_timing_list
	}

	// Find last pit
	last_pit := 0
	for _, timing := range timing_list {
		if timing.NumberStops > last_pit {
			last_pit = timing.NumberStops
		}
	}
	
	// Apply filtering
	for i := len(timing_list) - 1; i >= 0; i-- {
		if parsed_timing_list[i].NumberStops != last_pit {
			if len(parsed_timing_list) == i + 1 {
				// Truncate slice
				parsed_timing_list = parsed_timing_list[:i]
			} else {
				// Copy last item to the index to be removed
				parsed_timing_list[i] = parsed_timing_list[len(parsed_timing_list)-1]
			}
		}
	}

	return parsed_timing_list
}
