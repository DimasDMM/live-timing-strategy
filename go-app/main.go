package main

import (
	"os"

	"live-timing/src/runners"

	log "github.com/sirupsen/logrus"
	easyFormatter "github.com/t-tomalak/logrus-easy-formatter"
)

var (
	logger *log.Logger
)

func init() {
	logger = log.New()

	// Output to stdout instead of the default stderr
	// Can be any io.Writer, see below for File example
	logger.SetOutput(os.Stdout)

	// Only log the warning severity or above.
	logger.SetLevel(log.DebugLevel)

	// Set message formatter
	logger.SetFormatter(&easyFormatter.Formatter{
		TimestampFormat: "2006-01-02 15:04:05",
		LogFormat: "[%lvl%] %time% - %msg%\n",
	})
}

func main() {
	logger.Info("Hello World!")
	runners.FilesystemStorage(logger)
}
