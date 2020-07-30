package filedata

import (
	"batch-timing/filedata/structures"
	"encoding/json"
	"io/ioutil"
)

func GetSettings(filepath string) *structures.Settings {
	settings := structures.Settings{}

	file, _ := ioutil.ReadFile(filepath)
	_ = json.Unmarshal([]byte(file), &settings)

	return &settings
}
