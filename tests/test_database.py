"""Tests for examples/database/server.py — DatabaseConnection class (SQLite)."""

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_db(database_mod, db_path, read_only=True):
    return database_mod.DatabaseConnection(
        db_type="sqlite",
        connection_string=str(db_path),
        read_only=read_only,
        max_rows=100,
    )


# ---------------------------------------------------------------------------
# execute_query (SELECT)
# ---------------------------------------------------------------------------


async def test_execute_query_returns_rows(database_mod, sqlite_db_path):
    db = make_db(database_mod, sqlite_db_path)
    rows = await db.execute_query("SELECT * FROM products")
    assert len(rows) == 3
    assert rows[0]["name"] == "Widget"


async def test_execute_query_with_filter(database_mod, sqlite_db_path):
    db = make_db(database_mod, sqlite_db_path)
    rows = await db.execute_query("SELECT * FROM products WHERE stock > 0")
    assert len(rows) == 2
    names = {r["name"] for r in rows}
    assert "Gadget" not in names


async def test_execute_query_blocked_when_not_select(database_mod, sqlite_db_path):
    db = make_db(database_mod, sqlite_db_path, read_only=True)
    with pytest.raises(ValueError, match="Only SELECT"):
        await db.execute_query("INSERT INTO products VALUES (4, 'X', 1.0, 1)")


async def test_execute_query_respects_max_rows(database_mod, sqlite_db_path):
    db = database_mod.DatabaseConnection(
        db_type="sqlite",
        connection_string=str(sqlite_db_path),
        read_only=True,
        max_rows=2,
    )
    rows = await db.execute_query("SELECT * FROM products")
    assert len(rows) == 2


# ---------------------------------------------------------------------------
# execute_write (INSERT / UPDATE / DELETE)
# ---------------------------------------------------------------------------


async def test_execute_write_insert(database_mod, sqlite_db_path):
    db = make_db(database_mod, sqlite_db_path, read_only=False)
    result = await db.execute_write(
        "INSERT INTO products VALUES (4, 'NewThing', 1.99, 10)"
    )
    assert result["rows_affected"] == 1
    rows = await db.execute_query("SELECT * FROM products WHERE id = 4")
    assert rows[0]["name"] == "NewThing"


async def test_execute_write_blocked_in_read_only(database_mod, sqlite_db_path):
    db = make_db(database_mod, sqlite_db_path, read_only=True)
    with pytest.raises(ValueError, match="read-only"):
        await db.execute_write("INSERT INTO products VALUES (5, 'X', 1.0, 1)")


async def test_execute_write_rejects_select(database_mod, sqlite_db_path):
    db = make_db(database_mod, sqlite_db_path, read_only=False)
    with pytest.raises(ValueError, match="execute_query"):
        await db.execute_write("SELECT * FROM products")


# ---------------------------------------------------------------------------
# list_tables
# ---------------------------------------------------------------------------


async def test_list_tables(database_mod, sqlite_db_path):
    db = make_db(database_mod, sqlite_db_path)
    tables = await db.list_tables()
    names = [t["name"] for t in tables]
    assert "products" in names


# ---------------------------------------------------------------------------
# describe_table
# ---------------------------------------------------------------------------


async def test_describe_table_columns(database_mod, sqlite_db_path):
    # describe_table uses PRAGMA internally which doesn't start with SELECT,
    # so it requires read_only=False even though it's a schema inspection query.
    db = make_db(database_mod, sqlite_db_path, read_only=False)
    info = await db.describe_table("products")
    col_names = [c["name"] for c in info["columns"]]
    assert "id" in col_names
    assert "name" in col_names
    assert "price" in col_names


async def test_describe_table_row_count(database_mod, sqlite_db_path):
    db = make_db(database_mod, sqlite_db_path, read_only=False)
    info = await db.describe_table("products")
    assert info["row_count"] == 3


async def test_describe_table_primary_key(database_mod, sqlite_db_path):
    db = make_db(database_mod, sqlite_db_path, read_only=False)
    info = await db.describe_table("products")
    pk_cols = [c["name"] for c in info["columns"] if c["primary_key"]]
    assert "id" in pk_cols


# ---------------------------------------------------------------------------
# get_sample_data
# ---------------------------------------------------------------------------


async def test_get_sample_data(database_mod, sqlite_db_path):
    db = make_db(database_mod, sqlite_db_path)
    rows = await db.get_sample_data("products", limit=2)
    assert len(rows) == 2


async def test_get_sample_data_limit_capped_by_max_rows(database_mod, sqlite_db_path):
    db = database_mod.DatabaseConnection(
        db_type="sqlite",
        connection_string=str(sqlite_db_path),
        read_only=True,
        max_rows=1,
    )
    rows = await db.get_sample_data("products", limit=100)
    assert len(rows) == 1
