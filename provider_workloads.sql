CREATE VIEW IF NOT EXISTS provider_endpoint_workloads AS
SELECT e.source_url,e.page_sha256,e.retrieved_at_utc,e.endpoint_id,e.endpoint_slug,e.host_id,e.host_slug,e.host_name,e.model_id,e.model_slug,e.model_name,
w.key AS workload_key,json_extract(w.value,'$.outputSpeed') AS output_tokens_per_second,
json_extract(w.value,'$.timeToFirstToken') AS time_to_first_token_seconds,w.value AS raw_workload_json
FROM latest_provider_endpoints e,json_each(e.raw_json,'$.workloads') w WHERE e.array_kind='hostModels';
CREATE VIEW IF NOT EXISTS provider_endpoint_multiturn AS
SELECT e.source_url,e.page_sha256,e.retrieved_at_utc,e.endpoint_id,e.endpoint_slug,e.host_id,e.host_slug,e.host_name,e.model_id,e.model_slug,e.model_name,
json_extract(e.raw_json,'$.multiTurn.outputSpeed') AS output_tokens_per_second,
json_extract(e.raw_json,'$.multiTurn.timeToFirstToken') AS time_to_first_token_seconds,
json_extract(e.raw_json,'$.multiTurn') AS raw_multiturn_json
FROM latest_provider_endpoints e WHERE e.array_kind='hostModels' AND json_type(e.raw_json,'$.multiTurn')='object';
CREATE VIEW IF NOT EXISTS provider_endpoint_cost_components AS
SELECT e.source_url,e.page_sha256,e.retrieved_at_utc,e.endpoint_id,e.endpoint_slug,e.host_id,e.host_slug,e.host_name,e.model_id,e.model_slug,e.model_name,
c.key AS component,c.value AS amount_usd_per_index_task
FROM latest_provider_endpoints e,json_each(e.raw_json,'$.intelligenceIndexCostPerTask') c
WHERE e.array_kind='hostModels' AND c.type IN ('real','integer','null');
