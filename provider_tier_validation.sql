CREATE VIEW IF NOT EXISTS provider_tier_validation AS
SELECT t.source_url,t.page_sha256,t.endpoint_id,t.host_slug,t.model_slug,
t.input_price_per_million AS footnote_base_input,t.output_price_per_million AS footnote_base_output,
e.price_1m_input_usd AS endpoint_input,e.price_1m_output_usd AS endpoint_output,
CASE WHEN t.input_price_per_million IS NULL OR t.output_price_per_million IS NULL OR e.price_1m_input_usd IS NULL OR e.price_1m_output_usd IS NULL THEN NULL
WHEN abs(t.input_price_per_million-e.price_1m_input_usd)<0.000001 AND abs(t.output_price_per_million-e.price_1m_output_usd)<0.000001 THEN 1 ELSE 0 END AS base_price_matches
FROM provider_tiered_pricing t JOIN latest_provider_endpoints e ON e.endpoint_id=t.endpoint_id AND e.source_url=t.source_url AND e.array_kind='rows'
WHERE t.tier_number=1;
