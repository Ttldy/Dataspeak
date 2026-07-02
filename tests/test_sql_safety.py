from dataspeak.sql_agent.sql_safety import ensure_limit, validate_select_sql


def test_validate_select_allows_readonly_join_query():
    sql = "SELECT c.city, SUM(o.total_amount) AS revenue FROM orders o JOIN customers c ON o.customer_id = c.customer_id GROUP BY c.city"

    result = validate_select_sql(sql, allowed_tables={"orders", "customers"})

    assert result.safety_passed is True
    assert result.error_message is None


def test_validate_select_blocks_mutation():
    result = validate_select_sql("DELETE FROM orders", allowed_tables={"orders"})

    assert result.safety_passed is False
    assert "Only SELECT" in result.error_message


def test_ensure_limit_adds_limit_to_query_without_limit():
    sql = ensure_limit("SELECT * FROM customers", default_limit=50)

    assert sql.lower().endswith("limit 50")
