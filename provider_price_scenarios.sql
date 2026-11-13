CREATE VIEW IF NOT EXISTS provider_price_scenarios AS
WITH kinds(field_key,cache_ratio,input_ratio,output_ratio) AS (VALUES
('price1mBlended0To3To1',0,3,1),('price1mBlended7To2To1',7,2,1),
('price1mBlended0To1To1',0,1,1),('price1mBlended100To1To1',100,1,1),
('price1mBlended0To100To1',0,100,1))
SELECT e.source_url,e.page_sha256,e.retrieved_at_utc,e.endpoint_id,e.endpoint_slug,e.host_id,e.host_slug,e.host_name,e.model_id,e.model_slug,e.model_name,
k.field_key,k.cache_ratio,k.input_ratio,k.output_ratio,
json_extract(e.raw_json,'$.pricing.'||k.field_key) AS price_usd_per_million_tokens,
CASE WHEN k.cache_ratio>0 AND json_type(e.raw_json,'$.pricing.cacheHitPrice')='null' THEN 1 ELSE 0 END AS cache_price_absent
FROM latest_provider_endpoints e CROSS JOIN kinds k WHERE e.array_kind='hostModels'
AND json_type(e.raw_json,'$.pricing.'||k.field_key) IN ('real','integer');
CREATE VIEW IF NOT EXISTS provider_cache_metrics AS
SELECT e.source_url,e.page_sha256,e.retrieved_at_utc,e.endpoint_id,e.endpoint_slug,e.host_id,e.host_slug,e.host_name,e.model_id,e.model_slug,e.model_name,
e.cache_hit_usd_per_1m,e.cache_write_usd_per_1m,
json_extract(e.raw_json,'$.pricing.cacheHitRate') AS observed_cache_hit_rate_fraction,
json_extract(e.raw_json,'$.pricing.cacheHitDiscountPercent') AS cache_hit_discount_fraction
FROM latest_provider_endpoints e WHERE e.array_kind='hostModels';
