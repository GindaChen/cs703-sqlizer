from database.table import Database, DatabaseTable


def test_infer_table():
    db = Database("test_inferTable_db")
    table = DatabaseTable("test_table")
    table.add_column("test_col1")
    db.tables["test_table"] = table
