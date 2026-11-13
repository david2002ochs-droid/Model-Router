CREATE VIEW IF NOT EXISTS model_metrics AS
SELECT d.source_url,d.page_sha256,d.model_id,d.slug,d.name,d.effort,j.key AS metric_key,j.value AS value,j.type AS value_type
FROM model_details d, json_each(d.model_json) j
WHERE j.type IN ('integer','real','null');
CREATE VIEW IF NOT EXISTS benchmark_task_costs AS
SELECT d.source_url,d.model_id,d.slug,d.name,d.effort,
json_extract(e.value,'$.slug') AS evaluation_slug,
json_extract(e.value,'$.weightedCostPerTask') AS weighted_cost_per_task
FROM model_details d, json_each(d.model_json,'$.intelligenceIndexCostPerTask.evaluations') e;
CREATE VIEW IF NOT EXISTS benchmark_results AS
SELECT d.source_url,d.page_sha256,d.model_id,d.slug AS model_slug,d.name AS model_name,d.effort,
json_extract(d.model_json,'$.creator.id') AS creator_id,
json_extract(d.model_json,'$.creator.name') AS creator_name,
json_extract(e.value,'$.slug') AS evaluation_slug,
json_extract(e.value,'$.score') AS score,
json_extract(e.value,'$.costPerTask') AS cost_per_task,
json_extract(e.value,'$.timePerTask') AS time_per_task,
json_extract(e.value,'$.outputTokensPerTask') AS output_tokens_per_task,
e.value AS source_result_json
FROM model_details d, json_each(d.model_json,'$.intelligenceIndexEvaluations') e;
CREATE VIEW IF NOT EXISTS evaluation_page_metrics AS
SELECT e.source_url,e.page_sha256,e.model_id,e.model_slug,e.model_name,e.effort,j.key AS metric_key,j.value AS value,j.type AS value_type
FROM evaluation_page_models e, json_each(e.model_json) j WHERE j.type IN ('integer','real','null');
CREATE VIEW IF NOT EXISTS evaluation_page_scores AS
WITH mapping(evaluation_slug,metric_key) AS (VALUES
('aa-briefcase','briefcaseElo'),('automationbench-aa','automationBenchPartialScore'),
('frontiercode-2-0','frontierCode20'),('gdp-pdf','gdpPdfAllPass'),('hle-diamond','hleDiamond'),
('omniscience','omniscience'),('terminal-bench-science','terminalBenchScience'),('terminalbench-4-0','terminalBench40'))
SELECT e.source_url,e.page_sha256,e.model_id,e.model_slug,e.model_name,coalesce(e.effort,d.effort) effort,
m.evaluation_slug,m.metric_key,json_extract(e.model_json,'$.'||m.metric_key) score
FROM evaluation_page_models e JOIN mapping m ON e.source_url='https://artificialanalysis.ai/evaluations/'||m.evaluation_slug
LEFT JOIN model_details d ON d.model_id=e.model_id
WHERE json_extract(e.model_json,'$.'||m.metric_key) IS NOT NULL;
CREATE VIEW IF NOT EXISTS embedded_benchmark_results AS
SELECT d.source_url,d.page_sha256,d.model_id,d.model_slug,d.model_name,d.effort,
json_extract(d.model_json,'$.creator.id') creator_id,json_extract(d.model_json,'$.creator.name') creator_name,
json_extract(e.value,'$.slug') evaluation_slug,json_extract(e.value,'$.score') score,
json_extract(e.value,'$.costPerTask') cost_per_task,json_extract(e.value,'$.timePerTask') time_per_task,
json_extract(e.value,'$.outputTokensPerTask') output_tokens_per_task,e.value source_result_json
FROM embedded_model_snapshots d,json_each(d.model_json,'$.intelligenceIndexEvaluations') e;
CREATE VIEW IF NOT EXISTS embedded_model_metrics AS
SELECT d.source_url,d.page_sha256,d.model_id,d.model_slug,d.model_name,d.effort,j.key AS metric_key,j.value AS value,j.type AS value_type
FROM embedded_model_snapshots d,json_each(d.model_json) j
WHERE j.type IN ('integer','real','null');
CREATE VIEW IF NOT EXISTS embedded_model_leaves AS
SELECT d.source_url,d.page_sha256,d.model_id,d.model_slug,d.model_name,d.effort,
j.fullkey AS json_path,j.type AS value_type,j.atom AS value
FROM embedded_model_snapshots d,json_tree(d.model_json) j
WHERE j.type IN ('integer','real','text','true','false','null');
CREATE VIEW IF NOT EXISTS embedded_benchmark_results_readable AS
SELECT source_url,page_sha256,model_id,model_slug,model_name,effort,creator_id,creator_name,evaluation_slug,score,
cost_per_task AS cost_per_task_usd_inferred,time_per_task AS time_per_task_seconds_inferred,
time_per_task/60.0 AS time_per_task_minutes_inferred,output_tokens_per_task,source_result_json
FROM embedded_benchmark_results;
CREATE VIEW IF NOT EXISTS embedded_verified_scores AS
WITH mapping(evaluation_slug,json_path) AS (VALUES
('aa-briefcase','$.briefcaseBreakdown.overall.elo'),
('automationbench-aa','$.automationBenchPartialScore'),
('critpt-v2-hard','$.critptAgenticHard'),
('frontiercode-2-0','$.frontierCode20'),
('gdp-pdf','$.gdpPdfAllPass'),
('hle-diamond','$.hleDiamond'),
('omniscience','$.omniscience'),
('terminal-bench-science','$.terminalBenchScience'),
('terminalbench-4-0','$.terminalBench40'))
SELECT d.source_url,d.page_sha256,d.model_id,d.model_slug,d.model_name,d.effort,
m.evaluation_slug,m.json_path,json_extract(d.model_json,m.json_path) AS score
FROM embedded_model_snapshots d CROSS JOIN mapping m
WHERE json_extract(d.model_json,m.json_path) IS NOT NULL;
CREATE VIEW IF NOT EXISTS benchmark_catalog AS
SELECT s.source_url,s.page_sha256,s.model_id,s.model_slug,s.model_name,s.effort,s.evaluation_slug,s.score,
r.cost_per_task_usd_inferred,r.time_per_task_seconds_inferred,r.time_per_task_minutes_inferred,r.output_tokens_per_task
FROM embedded_verified_scores s LEFT JOIN embedded_benchmark_results_readable r
ON r.source_url=s.source_url AND r.page_sha256=s.page_sha256 AND r.model_id=s.model_id AND r.evaluation_slug=s.evaluation_slug;
CREATE VIEW IF NOT EXISTS registry_benchmark_scores AS
SELECT e.source_url,e.page_sha256,e.model_id,e.model_slug,e.model_name,coalesce(e.effort,d.effort) effort,
r.evaluation_slug,r.score_field,r.source_sha256 AS registry_sha256,
json_extract(e.model_json,'$.'||r.score_field) score
FROM evaluation_page_models e JOIN benchmark_registry r
ON e.source_url='https://artificialanalysis.ai/evaluations/'||r.evaluation_slug
LEFT JOIN model_details d ON d.model_id=e.model_id
WHERE json_extract(e.model_json,'$.'||r.score_field) IS NOT NULL;
CREATE VIEW IF NOT EXISTS embedded_registry_scores AS
SELECT e.source_url,e.page_sha256,e.model_id,e.model_slug,e.model_name,e.effort,
r.evaluation_slug,r.score_field,r.source_sha256 AS registry_sha256,
json_extract(e.model_json,'$.'||r.score_field) score
FROM embedded_model_snapshots e CROSS JOIN benchmark_registry r
WHERE json_extract(e.model_json,'$.'||r.score_field) IS NOT NULL;
CREATE VIEW IF NOT EXISTS coding_agent_benchmark_results AS
SELECT a.source_url,a.page_sha256,a.run_id,a.agent_name,a.agent_slug,a.model_name,a.effort,
json_extract(e.value,'$.datasetIndexName') dataset_id,json_extract(e.value,'$.evaluationDatasetSlug') benchmark_name,
json_extract(e.value,'$.refDatasetName') dataset_reference,json_extract(e.value,'$.weight') weight,
json_extract(e.value,'$.mean.reward') mean_reward,json_extract(e.value,'$.mean.inputTokens') mean_input_tokens,
json_extract(e.value,'$.mean.outputTokens') mean_output_tokens,e.value result_json
FROM coding_agent_runs a,json_each(a.run_json,'$.evals') e;
CREATE VIEW IF NOT EXISTS coding_agent_run_summary AS
SELECT source_url,page_sha256,run_id,agent_name,agent_slug,model_name,effort,
json_extract(run_json,'$.indexScore') index_score,json_extract(run_json,'$.mean.costUsd') mean_cost_usd,
json_extract(run_json,'$.mean.agentWallTimeSec') mean_agent_wall_time_seconds,
json_extract(run_json,'$.mean.inputTokens') mean_input_tokens,json_extract(run_json,'$.mean.outputTokens') mean_output_tokens,
json_extract(run_json,'$.mean.cacheTokens') mean_cache_tokens,json_extract(run_json,'$.mean.steps') mean_steps
FROM coding_agent_runs;
CREATE VIEW IF NOT EXISTS coding_agent_latest_runs AS
SELECT * FROM (
 SELECT a.*,q.retrieved_at_utc,ROW_NUMBER() OVER (PARTITION BY a.run_id ORDER BY q.retrieved_at_utc DESC,a.source_url) AS source_rank
 FROM coding_agent_runs a JOIN crawl_queue q ON q.url=a.source_url
) WHERE source_rank=1;
CREATE VIEW IF NOT EXISTS coding_agent_latest_benchmarks AS
SELECT a.source_url,a.page_sha256,a.retrieved_at_utc,a.run_id,a.agent_name,a.agent_slug,a.model_name,a.effort,
json_extract(e.value,'$.datasetIndexName') dataset_id,json_extract(e.value,'$.evaluationDatasetSlug') benchmark_name,
json_extract(e.value,'$.refDatasetName') dataset_reference,json_extract(e.value,'$.weight') weight,
json_extract(e.value,'$.mean.reward') mean_reward,json_extract(e.value,'$.mean.inputTokens') mean_input_tokens,
json_extract(e.value,'$.mean.outputTokens') mean_output_tokens,e.value result_json
FROM coding_agent_latest_runs a,json_each(a.run_json,'$.evals') e;
CREATE VIEW IF NOT EXISTS embedded_latest_models AS
SELECT * FROM (
 SELECT e.*,q.retrieved_at_utc,ROW_NUMBER() OVER (PARTITION BY e.model_id ORDER BY q.retrieved_at_utc DESC,e.source_url) source_rank
 FROM embedded_model_snapshots e JOIN crawl_queue q ON q.url=e.source_url
) WHERE source_rank=1;
CREATE VIEW IF NOT EXISTS latest_registry_benchmark_scores AS
SELECT e.source_url,e.page_sha256,e.retrieved_at_utc,e.model_id,e.model_slug,e.model_name,e.effort,
r.evaluation_slug,r.score_field,r.source_sha256 registry_sha256,json_extract(e.model_json,'$.'||r.score_field) score
FROM embedded_latest_models e CROSS JOIN benchmark_registry r
WHERE json_extract(e.model_json,'$.'||r.score_field) IS NOT NULL;
CREATE VIEW IF NOT EXISTS latest_index_benchmark_results AS
SELECT e.source_url,e.page_sha256,e.retrieved_at_utc,e.model_id,e.model_slug,e.model_name,e.effort,
json_extract(x.value,'$.slug') evaluation_slug,json_extract(x.value,'$.score') score,
json_extract(x.value,'$.costPerTask') cost_per_task_usd_inferred,
json_extract(x.value,'$.timePerTask') time_per_task_seconds_inferred,
json_extract(x.value,'$.timePerTask')/60.0 time_per_task_minutes_inferred,
json_extract(x.value,'$.outputTokensPerTask') output_tokens_per_task,x.value result_json
FROM embedded_latest_models e,json_each(e.model_json,'$.intelligenceIndexEvaluations') x;
CREATE VIEW IF NOT EXISTS latest_search_api_observations AS
SELECT * FROM (
 SELECT s.*,q.retrieved_at_utc,ROW_NUMBER() OVER (PARTITION BY s.provider_variant ORDER BY q.retrieved_at_utc DESC,s.source_url) source_rank
 FROM search_api_observations s JOIN crawl_queue q ON q.url=s.source_url
) WHERE source_rank=1;
CREATE VIEW IF NOT EXISTS benchmark_scores_with_metadata AS
SELECT s.source_url,s.page_sha256,s.retrieved_at_utc,s.model_id,s.model_slug,s.model_name,s.effort,
s.evaluation_slug,s.score_field,s.score AS score_raw,m.score_format,
CASE WHEN instr(coalesce(m.score_format,''),'%')>0 THEN s.score*100 ELSE s.score END AS score_display_value,
m.task_count,m.task_weight,m.source_sha256 AS metadata_source_sha256
FROM latest_registry_benchmark_scores s LEFT JOIN benchmark_registry_metadata m ON m.evaluation_slug=s.evaluation_slug;
CREATE VIEW IF NOT EXISTS latest_verified_field_aliases AS
WITH aliases(evaluation_slug,json_path) AS (VALUES
('itbench-aa','$.itBenchSre'),('aa-briefcase','$.briefcaseBreakdown.overall.elo'))
SELECT e.source_url,e.page_sha256,e.retrieved_at_utc,e.model_id,e.model_slug,e.model_name,e.effort,
a.evaluation_slug,a.json_path AS score_field,r.source_sha256 AS registry_sha256,
json_extract(e.model_json,a.json_path) AS score
FROM embedded_latest_models e CROSS JOIN aliases a
JOIN benchmark_registry r ON r.evaluation_slug=a.evaluation_slug
WHERE json_extract(e.model_json,a.json_path) IS NOT NULL
AND NOT EXISTS (SELECT 1 FROM latest_registry_benchmark_scores x WHERE x.model_id=e.model_id AND x.evaluation_slug=a.evaluation_slug);
CREATE VIEW IF NOT EXISTS combined_latest_benchmark_scores AS
SELECT * FROM latest_registry_benchmark_scores
UNION ALL SELECT * FROM latest_verified_field_aliases;
DROP VIEW IF EXISTS benchmark_scores_with_metadata;
CREATE VIEW benchmark_scores_with_metadata AS
SELECT s.source_url,s.page_sha256,s.retrieved_at_utc,s.model_id,s.model_slug,s.model_name,s.effort,
s.evaluation_slug,s.score_field,s.score AS score_raw,m.score_format,
CASE WHEN instr(coalesce(m.score_format,''),'%')>0 THEN s.score*100 ELSE s.score END AS score_display_value,
m.task_count,m.task_weight,m.source_sha256 AS metadata_source_sha256
FROM combined_latest_benchmark_scores s LEFT JOIN benchmark_registry_metadata m ON m.evaluation_slug=s.evaluation_slug;
CREATE VIEW IF NOT EXISTS latest_combined_benchmark_scores AS
SELECT source_url,page_sha256,retrieved_at_utc,model_id,model_slug,model_name,effort,evaluation_slug,score_field,registry_sha256,score FROM (
 SELECT v.*,ROW_NUMBER() OVER (PARTITION BY model_id,evaluation_slug ORDER BY retrieved_at_utc DESC,source_url) AS source_rank FROM (
  SELECT source_url,page_sha256,retrieved_at_utc,model_id,model_slug,model_name,effort,evaluation_slug,score_field,registry_sha256,score FROM combined_latest_benchmark_scores
  UNION ALL
  SELECT p.source_url,p.page_sha256,q.retrieved_at_utc,p.model_id,p.model_slug,p.model_name,p.effort,p.evaluation_slug,p.score_field,p.registry_sha256,p.score
  FROM registry_benchmark_scores p JOIN crawl_queue q ON q.url=p.source_url
 ) v
) WHERE source_rank=1;
DROP VIEW IF EXISTS benchmark_scores_with_metadata;
CREATE VIEW benchmark_scores_with_metadata AS
SELECT s.source_url,s.page_sha256,s.retrieved_at_utc,s.model_id,s.model_slug,s.model_name,s.effort,
s.evaluation_slug,s.score_field,s.score AS score_raw,m.score_format,
CASE WHEN instr(coalesce(m.score_format,''),'%')>0 THEN s.score*100 ELSE s.score END AS score_display_value,
m.task_count,m.task_weight,m.source_sha256 AS metadata_source_sha256
FROM latest_combined_benchmark_scores s LEFT JOIN benchmark_registry_metadata m ON m.evaluation_slug=s.evaluation_slug;
CREATE VIEW IF NOT EXISTS latest_model_facts AS
SELECT source_url,page_sha256,retrieved_at_utc,model_id,model_slug,model_name,effort,
json_extract(model_json,'$.creator.name') AS creator_name,
json_extract(model_json,'$.contextWindowTokens') AS context_window_tokens,
json_extract(model_json,'$.intelligenceIndex') AS intelligence_index,
json_extract(model_json,'$.price1mInputTokens') AS input_price_per_million,
json_extract(model_json,'$.price1mOutputTokens') AS output_price_per_million,
json_extract(model_json,'$.cacheHitPrice') AS cache_hit_price,
json_extract(model_json,'$.cacheWritePrice') AS cache_write_price,
json_extract(model_json,'$.headline.outputSpeed') AS output_speed_tokens_per_second,
json_extract(model_json,'$.headline.timeToFirstAnswerToken') AS first_answer_token_seconds,
json_extract(model_json,'$.intelligenceIndexTimePerTask') AS index_time_per_task_seconds_inferred,
json_extract(model_json,'$.intelligenceIndexCostPerTask.cost.total') AS index_cost_per_task_usd_inferred,
json_extract(model_json,'$.priceDataSource.providerName') AS price_data_provider,
json_extract(model_json,'$.performanceDataSource.providerName') AS performance_data_provider
FROM embedded_latest_models;
DROP VIEW IF EXISTS embedded_latest_models;
CREATE VIEW embedded_latest_models AS
SELECT * FROM (
 SELECT e.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=e.page_sha256 THEN q.retrieved_at_utc END) AS retrieved_at_utc,
 ROW_NUMBER() OVER (PARTITION BY e.model_id ORDER BY coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=e.page_sha256 THEN q.retrieved_at_utc END) DESC,e.source_url,e.page_sha256) AS source_rank
 FROM embedded_model_snapshots e
 LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=e.source_url AND t.page_sha256=e.page_sha256
 LEFT JOIN crawl_queue q ON q.url=e.source_url
 LEFT JOIN page_archive p ON p.url=e.source_url
) WHERE source_rank=1;
DROP VIEW IF EXISTS latest_combined_benchmark_scores;
CREATE VIEW latest_combined_benchmark_scores AS
SELECT source_url,page_sha256,retrieved_at_utc,model_id,model_slug,model_name,effort,evaluation_slug,score_field,registry_sha256,score FROM (
 SELECT v.*,ROW_NUMBER() OVER (PARTITION BY model_id,evaluation_slug ORDER BY retrieved_at_utc DESC,source_url) AS source_rank FROM (
  SELECT source_url,page_sha256,retrieved_at_utc,model_id,model_slug,model_name,effort,evaluation_slug,score_field,registry_sha256,score FROM combined_latest_benchmark_scores
  UNION ALL
  SELECT p.source_url,p.page_sha256,coalesce(t.retrieved_at_utc,CASE WHEN a.sha256=p.page_sha256 THEN q.retrieved_at_utc END),p.model_id,p.model_slug,p.model_name,p.effort,p.evaluation_slug,p.score_field,p.registry_sha256,p.score
  FROM registry_benchmark_scores p LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=p.source_url AND t.page_sha256=p.page_sha256 LEFT JOIN crawl_queue q ON q.url=p.source_url LEFT JOIN page_archive a ON a.url=p.source_url
 ) v
) WHERE source_rank=1;
DROP VIEW IF EXISTS coding_agent_latest_runs;
CREATE VIEW coding_agent_latest_runs AS
SELECT * FROM (
 SELECT a.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=a.page_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc,
 ROW_NUMBER() OVER (PARTITION BY a.run_id ORDER BY coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=a.page_sha256 THEN q.retrieved_at_utc END) DESC,a.source_url) source_rank
 FROM coding_agent_runs a LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=a.source_url AND t.page_sha256=a.page_sha256 LEFT JOIN crawl_queue q ON q.url=a.source_url LEFT JOIN page_archive p ON p.url=a.source_url
) WHERE source_rank=1;
DROP VIEW IF EXISTS latest_search_api_observations;
CREATE VIEW latest_search_api_observations AS
SELECT * FROM (
 SELECT s.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=s.page_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc,
 ROW_NUMBER() OVER (PARTITION BY s.provider_variant ORDER BY coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=s.page_sha256 THEN q.retrieved_at_utc END) DESC,s.source_url) source_rank
 FROM search_api_observations s LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=s.source_url AND t.page_sha256=s.page_sha256 LEFT JOIN crawl_queue q ON q.url=s.source_url LEFT JOIN page_archive p ON p.url=s.source_url
) WHERE source_rank=1;
DROP VIEW IF EXISTS latest_media_endpoints;
CREATE VIEW latest_media_endpoints AS SELECT * FROM (
 SELECT e.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=e.page_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc,
 ROW_NUMBER() OVER (PARTITION BY e.modality,e.endpoint_id ORDER BY coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=e.page_sha256 THEN q.retrieved_at_utc END) DESC,e.source_url) source_rank
 FROM media_endpoint_records e LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=e.source_url AND t.page_sha256=e.page_sha256 LEFT JOIN crawl_queue q ON q.url=e.source_url LEFT JOIN page_archive p ON p.url=e.source_url
) WHERE source_rank=1;
DROP VIEW IF EXISTS image_host_model_latest_observations;
CREATE VIEW image_host_model_latest_observations AS SELECT * FROM (
 SELECT o.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.source_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc,
 ROW_NUMBER() OVER (PARTITION BY o.host_model_id ORDER BY coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.source_sha256 THEN q.retrieved_at_utc END) DESC,o.source_url) source_rank
 FROM image_host_model_observations o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.source_sha256 LEFT JOIN crawl_queue q ON q.url=o.source_url LEFT JOIN page_archive p ON p.url=o.source_url
) WHERE source_rank=1;
DROP VIEW IF EXISTS video_host_model_latest_observations;
CREATE VIEW video_host_model_latest_observations AS SELECT * FROM (
 SELECT o.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.source_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc,
 ROW_NUMBER() OVER (PARTITION BY o.host_model_id ORDER BY coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.source_sha256 THEN q.retrieved_at_utc END) DESC,o.source_url) source_rank
 FROM video_host_model_observations o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.source_sha256 LEFT JOIN crawl_queue q ON q.url=o.source_url LEFT JOIN page_archive p ON p.url=o.source_url
) WHERE source_rank=1;
CREATE VIEW IF NOT EXISTS model_efforts AS
SELECT model_id,CASE WHEN count(DISTINCT effort)=1 THEN min(effort) ELSE NULL END AS effort
FROM model_details GROUP BY model_id;
DROP VIEW IF EXISTS registry_benchmark_scores;
CREATE VIEW registry_benchmark_scores AS
SELECT e.source_url,e.page_sha256,e.model_id,e.model_slug,e.model_name,coalesce(e.effort,d.effort) effort,
r.evaluation_slug,r.score_field,r.source_sha256 registry_sha256,json_extract(e.model_json,'$.'||r.score_field) score
FROM evaluation_page_models e JOIN benchmark_registry r ON e.source_url='https://artificialanalysis.ai/evaluations/'||r.evaluation_slug
LEFT JOIN model_efforts d ON d.model_id=e.model_id
WHERE json_extract(e.model_json,'$.'||r.score_field) IS NOT NULL;
DROP VIEW IF EXISTS evaluation_page_scores;
CREATE VIEW evaluation_page_scores AS
WITH mapping(evaluation_slug,metric_key) AS (VALUES
('aa-briefcase','briefcaseElo'),('automationbench-aa','automationBenchPartialScore'),
('frontiercode-2-0','frontierCode20'),('gdp-pdf','gdpPdfAllPass'),('hle-diamond','hleDiamond'),
('omniscience','omniscience'),('terminal-bench-science','terminalBenchScience'),('terminalbench-4-0','terminalBench40'))
SELECT e.source_url,e.page_sha256,e.model_id,e.model_slug,e.model_name,coalesce(e.effort,d.effort) effort,
m.evaluation_slug,m.metric_key,json_extract(e.model_json,'$.'||m.metric_key) score
FROM evaluation_page_models e JOIN mapping m ON e.source_url='https://artificialanalysis.ai/evaluations/'||m.evaluation_slug
LEFT JOIN model_efforts d ON d.model_id=e.model_id
WHERE json_extract(e.model_json,'$.'||m.metric_key) IS NOT NULL;
CREATE VIEW IF NOT EXISTS model_benchmark_availability AS
WITH scores AS (SELECT model_id,evaluation_slug FROM latest_combined_benchmark_scores),
index_data AS (SELECT DISTINCT model_id,evaluation_slug,CASE WHEN cost_per_task_usd_inferred IS NOT NULL THEN 1 ELSE 0 END has_cost,CASE WHEN time_per_task_seconds_inferred IS NOT NULL THEN 1 ELSE 0 END has_time FROM latest_index_benchmark_results),
estimated_cost AS (SELECT DISTINCT model_id,benchmark_slug FROM benchmark_cost_estimates WHERE cost_usd_per_task IS NOT NULL),
estimated_time AS (SELECT DISTINCT model_id,benchmark_slug FROM benchmark_generation_time_estimates WHERE estimated_seconds_per_task IS NOT NULL)
SELECT s.evaluation_slug,count(*) model_score_count,
sum(CASE WHEN i.has_cost=1 THEN 1 ELSE 0 END) models_with_index_component_cost,
sum(CASE WHEN i.has_time=1 THEN 1 ELSE 0 END) models_with_index_component_time,
sum(CASE WHEN ec.model_id IS NOT NULL THEN 1 ELSE 0 END) models_with_cost_estimate,
sum(CASE WHEN et.model_id IS NOT NULL THEN 1 ELSE 0 END) models_with_time_estimate
FROM scores s LEFT JOIN index_data i ON i.model_id=s.model_id AND i.evaluation_slug=s.evaluation_slug
LEFT JOIN estimated_cost ec ON ec.model_id=s.model_id AND ec.benchmark_slug=s.evaluation_slug
LEFT JOIN estimated_time et ON et.model_id=s.model_id AND et.benchmark_slug=s.evaluation_slug
GROUP BY s.evaluation_slug;
CREATE VIEW IF NOT EXISTS benchmark_cost_estimate_gaps AS
SELECT g.source_url,g.page_sha256,g.model_id,g.model_name,g.effort,g.benchmark_slug,g.token_field,
CASE WHEN json_type(e.model_json,'$.price1mInputTokens') NOT IN ('integer','real') OR json_type(e.model_json,'$.price1mOutputTokens') NOT IN ('integer','real') OR json_type(e.model_json,'$.price1mInputTokens') IS NULL OR json_type(e.model_json,'$.price1mOutputTokens') IS NULL THEN 1 ELSE 0 END AS input_or_output_price_missing,
CASE WHEN json_type(e.model_json,'$.canonicalEvalTokenCounts."'||g.token_field||'".cacheableInput') IN ('integer','real') AND (json_type(e.model_json,'$.cacheHitRate') IS NULL OR json_type(e.model_json,'$.cacheHitRate') NOT IN ('integer','real')) THEN 1 ELSE 0 END AS cache_hit_rate_missing,
CASE WHEN coalesce(json_type(e.model_json,'$.canonicalEvalTokenCounts."'||g.token_field||'".input'),'missing') NOT IN ('integer','real') OR coalesce(json_type(e.model_json,'$.canonicalEvalTokenCounts."'||g.token_field||'".answer'),'missing') NOT IN ('integer','real') OR coalesce(json_type(e.model_json,'$.canonicalEvalTokenCounts."'||g.token_field||'".reasoning'),'missing') NOT IN ('integer','real') THEN 1 ELSE 0 END AS required_tokens_missing
FROM benchmark_generation_time_estimates g JOIN evaluation_page_models e ON e.source_url=g.source_url AND e.model_id=g.model_id
LEFT JOIN benchmark_cost_estimates b ON b.source_url=g.source_url AND b.model_id=g.model_id AND b.benchmark_slug=g.benchmark_slug
WHERE b.model_id IS NULL;
