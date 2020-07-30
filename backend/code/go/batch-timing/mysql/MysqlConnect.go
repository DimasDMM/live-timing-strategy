package mysql

import (
	"fmt"
	"database/sql"
	_ "github.com/go-sql-driver/mysql"
)

func MysqlConnect(db_host string, db_port string, db_user string, db_pass string, db_database string) *sql.DB {
	str_connection := db_user + ":@tcp(" + db_host + ":" + db_port + ")/" + db_database
	db, err := sql.Open("mysql", str_connection)
	if err != nil {
		fmt.Println("MySQL db is not connected (1)")
		fmt.Println(err.Error())
	} else {
		// Make sure connection is available
		err = db.Ping()
		if err != nil {
			fmt.Println("MySQL db is not connected (2)")
			fmt.Println(err.Error())
		}
	}
	return db
}
