package mysql

import (
	"database/sql"
	_ "github.com/go-sql-driver/mysql"
)

func MysqlClose(connection *sql.DB) {
	defer connection.Close()
}
