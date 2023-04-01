package runners

import (
	"flag"
	"os"

	"github.com/confluentinc/confluent-kafka-go/v2/kafka"
	log "github.com/sirupsen/logrus"
)

const KafkaGroup = "RawStorage"

var (
	bootstrapServers string
    outputPath string
)

func FilesystemStorage(logger *log.Logger) {
	parseArguments(logger)
	
	logger.Debug(outputPath)
	consumer, err := kafka.NewConsumer(&kafka.ConfigMap{
		"bootstrap.servers": bootstrapServers,
		"group.id": KafkaGroup,
		"auto.offset.reset": "smallest",
	})
}

func parseArguments(logger *log.Logger) {
	flag.StringVar(&bootstrapServers, "bootstrap_servers", "", "Kafka bootstrap servers")
	flag.StringVar(&outputPath, "output_path", "", "Output path")
	flag.Parse()

	if len(outputPath) == 0 {
        logger.Error("The output path cannot be empty")
        flag.PrintDefaults()
        os.Exit(1)
    } else if len(bootstrapServers) == 0 {
		logger.Error("The bootstrap servers cannot be empty")
        flag.PrintDefaults()
        os.Exit(1)
	}

	err := os.MkdirAll(outputPath, os.ModePerm)
	if err != nil {
		logger.Error("Could not create output path: " + err.Error())
		os.Exit(1)
	}
}
