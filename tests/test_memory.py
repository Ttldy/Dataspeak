from dataspeak.memory.long_term import LongTermMemory
from dataspeak.memory.short_term import ShortTermMemory


def test_short_term_memory_keeps_sliding_window_and_summary():
    memory = ShortTermMemory(window_size=2)
    memory.add_turn("u1", "q1", "a1")
    memory.add_turn("u1", "q2", "a2")
    memory.add_turn("u1", "q3", "a3")

    context = memory.get_context("u1")

    assert "q3" in context["window_text"]
    assert "q1" not in context["window_text"]
    assert "q1" in context["summary"]


def test_long_term_memory_retrieves_saved_preference_without_raw_rows():
    memory = LongTermMemory()
    memory.save("u1", "以后收入统计默认排除已退款订单", {"kind": "preference", "raw_rows": [{"secret": 1}]})

    results = memory.search("u1", "收入统计口径", top_k=1)

    assert results
    assert "排除已退款订单" in results[0]["text"]
    assert "raw_rows" not in results[0]["metadata"]
