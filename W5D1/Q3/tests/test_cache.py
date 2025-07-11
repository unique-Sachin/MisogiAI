from app.services.cache.client import CacheClient

def test_build_query_key_stable():
    key1 = CacheClient.build_query_key("Q?", ["AAPL"], "Q1-2024")
    key2 = CacheClient.build_query_key("Q?", ["AAPL"], "Q1-2024")
    assert key1 == key2
    assert key1.startswith("query_result:") 