package structures

type Settings struct {
	EventName string `json:"event_name"`
	TimeWaitClassification string `json:"time_wait_classification"`
	TimeWaitRace string `json:"time_wait_race"`
}
