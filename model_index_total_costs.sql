-- Evaluation-run costs as reported by the source; not an invoice or guaranteed provider quote.
CREATE VIEW IF NOT EXISTS model_index_total_costs AS
SELECT source_url,page_sha256,retrieved_at_utc,model_id,model_slug,model_name,effort,
json_extract(model_json,'$.creator.name') model_creator_name,
json_extract(model_json,'$.priceDataSource.providerName') pricing_provider_name,
json_extract(model_json,'$.intelligenceIndexCost.total') index_total_cost_usd,
json_extract(model_json,'$.intelligenceIndexCostPerTask.cost.total') index_cost_per_task_usd,
json_extract(model_json,'$.intelligenceIndexCost') source_cost_json
FROM embedded_latest_models WHERE json_type(model_json,'$.intelligenceIndexCost.total') IN ('integer','real');
CREATE VIEW IF NOT EXISTS model_index_total_cost_components AS
SELECT m.source_url,m.page_sha256,m.retrieved_at_utc,m.model_id,m.model_slug,m.model_name,m.effort,
m.pricing_provider_name,j.key AS cost_component,j.value AS amount_usd
FROM model_index_total_costs m,json_each(m.source_cost_json) j WHERE j.type IN ('integer','real','null');
