-- All nested leaf values exposed by an evaluation page's embedded model objects.
-- The page URL identifies the source only: other benchmarks may appear in the same object.
CREATE VIEW IF NOT EXISTS evaluation_page_leaf_facts AS
SELECT e.source_url,e.page_sha256,e.model_id,e.model_slug,e.model_name,e.effort,
j.fullkey AS json_path,j.type AS value_type,j.atom AS value
FROM evaluation_page_models e,json_tree(e.model_json) j
WHERE j.type IN ('integer','real','text','true','false','null');

-- Preserve all nested benchmark-run results and published audit fields for coding agents.
CREATE VIEW IF NOT EXISTS coding_agent_evaluation_leaf_facts AS
SELECT a.source_url,a.page_sha256,a.retrieved_at_utc,a.run_id,a.agent_name,a.model_name,a.effort,
json_extract(e.value,'$.datasetIndexName') AS dataset_id,j.fullkey AS json_path,j.type AS value_type,j.atom AS value
FROM coding_agent_latest_runs a,json_each(a.run_json,'$.evals') e,json_tree(e.value) j
WHERE j.type IN ('integer','real','text','true','false','null');
-- Streaming STT raw ratios and latency aggregates by dataset, with source field paths retained.
CREATE VIEW IF NOT EXISTS streaming_speech_benchmark_results AS
WITH metric_map(dataset,wer_field,partial_wer_field,final_field,partial_time_field) AS (VALUES
('AA-WER Streaming','aaWerStreamingIndex','aaWerStreamingFirstPartialAfterSpeechEnd','timeToFinalTranscriptSeconds','timeToFirstPartialTranscriptSeconds'),
('AA-AgentTalk','aaAgenttalkStreamingWer','aaAgenttalkStreamingFirstPartialAfterSpeechEndWer','aaAgenttalkTimeToFinalTranscriptSeconds','aaAgenttalkTimeToFirstPartialTranscriptSeconds'),
('VoxPopuli','voxpopuliStreamingWer','voxpopuliStreamingFirstPartialAfterSpeechEndWer','voxpopuliTimeToFinalTranscriptSeconds','voxpopuliTimeToFirstPartialTranscriptSeconds'),
('Earnings22','earnings22StreamingWer','earnings22StreamingFirstPartialAfterSpeechEndWer','earnings22TimeToFinalTranscriptSeconds','earnings22TimeToFirstPartialTranscriptSeconds')
)
SELECT s.source_url,s.source_sha256,s.host_model_id,s.name,s.host_id,s.host_name,s.model_id,s.model_name,
m.dataset,m.wer_field,json_extract(s.raw_json,'$.'||m.wer_field) AS final_wer_raw,
m.partial_wer_field,json_extract(s.raw_json,'$.'||m.partial_wer_field) AS first_partial_wer_raw,
json_extract(s.raw_json,'$.'||m.final_field) AS time_to_final_seconds,
json_extract(s.raw_json,'$.'||m.partial_time_field) AS time_to_first_partial_seconds,
s.price_per_1000_minutes AS estimated_usd_per_1000_audio_minutes
FROM streaming_speech_observations s CROSS JOIN metric_map m;
CREATE VIEW IF NOT EXISTS image_host_model_latest_observations AS
SELECT * FROM (
 SELECT o.*,q.retrieved_at_utc,ROW_NUMBER() OVER (PARTITION BY o.host_model_id ORDER BY q.retrieved_at_utc DESC,o.source_url) AS source_rank
 FROM image_host_model_observations o JOIN crawl_queue q ON q.url=o.source_url
) WHERE source_rank=1;
CREATE VIEW IF NOT EXISTS video_host_model_latest_observations AS
SELECT * FROM (
 SELECT o.*,q.retrieved_at_utc,ROW_NUMBER() OVER (PARTITION BY o.host_model_id ORDER BY q.retrieved_at_utc DESC,o.source_url) AS source_rank
 FROM video_host_model_observations o JOIN crawl_queue q ON q.url=o.source_url
) WHERE source_rank=1;
CREATE VIEW IF NOT EXISTS search_agent_benchmark_scores AS
SELECT source_url,source_sha256,configuration_id,provider_name,provider_variant,answer_model_slug,answer_model_name,
'DeepSearchQA' AS benchmark,deepsearchqa_f1_raw AS score_raw,900 AS documented_task_count,latest_measured_at
FROM search_agent_details WHERE deepsearchqa_f1_raw IS NOT NULL
UNION ALL
SELECT source_url,source_sha256,configuration_id,provider_name,provider_variant,answer_model_slug,answer_model_name,
'BrowseComp' AS benchmark,browsecomp_accuracy_raw AS score_raw,200 AS documented_task_count,latest_measured_at
FROM search_agent_details WHERE browsecomp_accuracy_raw IS NOT NULL
UNION ALL
SELECT source_url,source_sha256,configuration_id,provider_name,provider_variant,answer_model_slug,answer_model_name,
'AA-Omniscience' AS benchmark,omniscience_accuracy_raw AS score_raw,600 AS documented_task_count,latest_measured_at
FROM search_agent_details WHERE omniscience_accuracy_raw IS NOT NULL;
-- Source-specific, explicitly named benchmark breakdowns; raw keys and types remain intact.
CREATE VIEW IF NOT EXISTS benchmark_named_breakdown_facts AS
WITH mapping(slug,json_path) AS (VALUES
 ('aa-briefcase','$.briefcaseBreakdown'),('automationbench-aa','$.automationBenchBreakdown'),
 ('gdp-pdf','$.gdpPdfBreakdown'),('gdpval-aa','$.gdpvalBreakdown'),('harvey-lab-aa','$.harveyLabBreakdown'),
 ('aa-3d','$.aa3dBreakdown'),('vials-aa','$.vialsBreakdown'),('mka','$.mkaBreakdown'),
 ('omniscience','$.omniscienceBreakdown'),('terminal-bench-science','$.terminalBenchSciencePassRateByDomain'),
 ('hle-diamond','$.hleDiamondScoreByPartition'),('code2video-aa','$.code2videoBreakdown')
)
SELECT e.source_url,e.page_sha256,e.model_id,e.model_slug,e.model_name,coalesce(e.effort,(SELECT md.effort FROM model_details md WHERE md.model_id=e.model_id AND md.effort IS NOT NULL LIMIT 1)) AS effort,
m.slug AS benchmark_slug,m.json_path AS source_breakdown_path,j.fullkey AS detail_path,j.type AS value_type,j.atom AS value
FROM evaluation_page_models e JOIN mapping m ON e.source_url='https://artificialanalysis.ai/evaluations/'||m.slug
,
json_tree(e.model_json,m.json_path) j
WHERE j.type IN ('integer','real','text','true','false','null');
CREATE VIEW IF NOT EXISTS speech_agent_benchmark_observations AS
SELECT source_url,source_sha256,host_model_id,host_name,model_id,model_name,
'Big Bench Audio' AS benchmark,NULL AS subcategory,big_bench_audio_score_raw AS score_raw,
big_bench_audio_average_cost_per_task_usd AS average_cost_usd_per_task,
first_audio_seconds AS time_to_first_audio_seconds,NULL AS mean_conversation_audio_seconds
FROM speech_agent_host_details WHERE big_bench_audio_score_raw IS NOT NULL OR big_bench_audio_average_cost_per_task_usd IS NOT NULL OR first_audio_seconds IS NOT NULL
UNION ALL
SELECT source_url,source_sha256,host_model_id,host_name,model_id,model_name,
'Tau3 Voice' AS benchmark,NULL AS subcategory,tau3_voice_score_raw AS score_raw,
NULL,NULL,tau3_voice_mean_audio_duration_seconds
FROM speech_agent_host_details WHERE tau3_voice_score_raw IS NOT NULL
UNION ALL
SELECT d.source_url,d.source_sha256,d.host_model_id,d.host_name,d.model_id,d.model_name,
'Tau3 Voice' AS benchmark,j.key AS subcategory,json_extract(j.value,'$.avgReward') AS score_raw,
NULL,NULL,NULL
FROM speech_agent_host_details d,json_each(d.raw_json,'$.tauVoiceScoresByCategory') j
WHERE json_extract(j.value,'$.avgReward') IS NOT NULL;
-- Field-to-dataset mappings are explicitly named by the Decision Index page chart definitions.
CREATE VIEW IF NOT EXISTS decision_dataset_benchmark_results AS
SELECT d.source_url,d.source_sha256,d.contestant_slug,d.contestant_name,d.contestant_kind,d.host_name,d.creator_name,
d.dataset_slug,
CASE d.dataset_slug
 WHEN 'aa-paperclip' THEN json_extract(c.raw_json,'$.scores.documentDecisionDecisionScore')
 WHEN 'evalsafe-onet-aa' THEN json_extract(c.raw_json,'$.scores.evalsafeOnetDecisionScore')
 WHEN 'when2call' THEN json_extract(c.raw_json,'$.scores.when2callDecisionScore')
 WHEN 'aa-omniscience-decision' THEN json_extract(c.raw_json,'$.scores.omniscienceDecisionScore')
 WHEN 'hle-multichoice' THEN json_extract(c.raw_json,'$.scores.hleDecisionScore')
 WHEN 'aa-symmetry' THEN json_extract(c.raw_json,'$.scores.invarianceSymmetry')
 END AS decision_or_symmetry_score_0_to_100,
d.cost_usd_per_task,d.median_time_ms_per_task,d.median_time_ms_per_task/1000.0 AS median_time_seconds_per_task,
d.brier,d.raw_json AS dataset_raw_json
FROM decision_dataset_results d JOIN decision_index_contestants c ON c.source_url=d.source_url AND c.contestant_slug=d.contestant_slug;
-- VIALS-AA chart formula transcribed from archived source bundle 38436-bcd8435db2f5b0fb.js.
CREATE VIEW IF NOT EXISTS vials_estimated_time_per_task AS
WITH components AS (
 SELECT e.source_url,e.page_sha256,e.model_id,e.model_slug,e.model_name,coalesce(e.effort,(SELECT md.effort FROM model_details md WHERE md.model_id=e.model_id AND md.effort IS NOT NULL LIMIT 1)) AS effort,
 json_extract(e.model_json,'$.vialsScore') AS score_raw,
 json_extract(e.model_json,'$.canonicalEvalTokenCounts.vials.answer') AS answer_tokens,
 json_extract(e.model_json,'$.canonicalEvalTokenCounts.vials.reasoning') AS reasoning_tokens,
 json_extract(e.model_json,'$.outputSpeed') AS output_speed_tokens_per_second,
 json_extract(e.model_json,'$.vialsBreakdown.telemetry.tools.meanMsPerAttempt') AS mean_tool_ms_per_attempt,
 r.task_count AS benchmark_task_count
 FROM evaluation_page_models e
 LEFT JOIN benchmark_registry_metadata r ON r.evaluation_slug='vials-aa'
 WHERE e.source_url='https://artificialanalysis.ai/evaluations/vials-aa'
)
SELECT *,
 (answer_tokens+reasoning_tokens)/benchmark_task_count/output_speed_tokens_per_second AS estimated_generation_seconds_per_task,
 CASE WHEN mean_tool_ms_per_attempt IS NOT NULL THEN 1 ELSE 0 END AS tool_time_available,
 (answer_tokens+reasoning_tokens)/benchmark_task_count/output_speed_tokens_per_second+coalesce(mean_tool_ms_per_attempt/1000.0,0) AS estimated_seconds_per_task,
 '1e955781826f7a5d8fcca0778c4fe506f1d7cee87b2618b358a277b6b6c97052' AS calculation_source_sha256
FROM components WHERE benchmark_task_count>0 AND output_speed_tokens_per_second>0 AND answer_tokens IS NOT NULL AND reasoning_tokens IS NOT NULL;
CREATE VIEW IF NOT EXISTS agentic_benchmark_estimated_times AS
WITH mapping(slug,token_path,tool_path,tool_divisor) AS (VALUES
 ('aa-briefcase','$.canonicalEvalTokenCounts.briefcase','$.briefcaseBreakdown.totalToolMs',91.0),
 ('mka','$.canonicalEvalTokenCounts.mka','$.mkaBreakdown.avgToolMsPerTask',1.0),
 ('vials-aa','$.canonicalEvalTokenCounts.vials','$.vialsBreakdown.telemetry.tools.meanMsPerAttempt',1.0)
), components AS (
 SELECT e.source_url,e.page_sha256,e.model_id,e.model_slug,e.model_name,
 coalesce(e.effort,(SELECT md.effort FROM model_details md WHERE md.model_id=e.model_id AND md.effort IS NOT NULL LIMIT 1)) AS effort,
 m.slug AS benchmark_slug,r.task_count AS benchmark_task_count,json_extract(e.model_json,m.token_path||'.answer') AS answer_tokens,
 json_extract(e.model_json,m.token_path||'.reasoning') AS reasoning_tokens,json_extract(e.model_json,'$.outputSpeed') AS output_speed_tokens_per_second,
 json_extract(e.model_json,m.tool_path)/m.tool_divisor AS mean_tool_ms_per_task
 FROM evaluation_page_models e JOIN mapping m ON e.source_url='https://artificialanalysis.ai/evaluations/'||m.slug
 JOIN benchmark_registry_metadata r ON r.evaluation_slug=m.slug
)
SELECT *,CASE WHEN benchmark_task_count>0 AND output_speed_tokens_per_second>0 AND answer_tokens IS NOT NULL AND reasoning_tokens IS NOT NULL
 THEN (answer_tokens+reasoning_tokens)/benchmark_task_count/output_speed_tokens_per_second END AS estimated_generation_seconds_per_task,
 CASE WHEN mean_tool_ms_per_task IS NOT NULL THEN 1 ELSE 0 END AS tool_time_available,
 CASE WHEN benchmark_task_count>0 AND output_speed_tokens_per_second>0 AND answer_tokens IS NOT NULL AND reasoning_tokens IS NOT NULL
 THEN (answer_tokens+reasoning_tokens)/benchmark_task_count/output_speed_tokens_per_second+coalesce(mean_tool_ms_per_task/1000.0,0) END AS estimated_total_seconds_per_task,
 '1e955781826f7a5d8fcca0778c4fe506f1d7cee87b2618b358a277b6b6c97052' AS calculation_source_sha256
FROM components;
-- Mirrors the source's per-evaluation token-speed calculation. Tool-time fields are added only when the source registry supplies them.
CREATE VIEW IF NOT EXISTS benchmark_generation_time_estimates AS
WITH components AS (
 SELECT e.source_url,e.page_sha256,e.model_id,e.model_slug,e.model_name,
 coalesce(e.effort,(SELECT md.effort FROM model_details md WHERE md.model_id=e.model_id AND md.effort IS NOT NULL LIMIT 1)) AS effort,
 t.benchmark_slug,t.token_field,t.task_count,t.has_tool_time,t.registry_source_sha256,
 json_extract(e.model_json,'$.canonicalEvalTokenCounts.'||t.token_field||'.answer') AS answer_tokens,
 json_extract(e.model_json,'$.canonicalEvalTokenCounts.'||t.token_field||'.reasoning') AS reasoning_tokens,
 json_extract(e.model_json,'$.outputSpeed') AS output_speed_tokens_per_second,
 CASE t.benchmark_slug WHEN 'aa-briefcase' THEN json_extract(e.model_json,'$.briefcaseBreakdown.totalToolMs')/91.0
 WHEN 'mka' THEN json_extract(e.model_json,'$.mkaBreakdown.avgToolMsPerTask')
 WHEN 'vials-aa' THEN json_extract(e.model_json,'$.vialsBreakdown.telemetry.tools.meanMsPerAttempt') END AS mean_tool_ms_per_task
 FROM evaluation_page_models e JOIN benchmark_time_config t ON e.source_url='https://artificialanalysis.ai/evaluations/'||t.benchmark_slug
)
SELECT *,
 CASE WHEN output_speed_tokens_per_second>0 AND answer_tokens IS NOT NULL AND reasoning_tokens IS NOT NULL
 THEN (answer_tokens+reasoning_tokens)/task_count/output_speed_tokens_per_second END AS estimated_generation_seconds_per_task,
 CASE WHEN has_tool_time=0 OR mean_tool_ms_per_task IS NOT NULL THEN 1 ELSE 0 END AS source_tool_component_complete,
 CASE WHEN output_speed_tokens_per_second>0 AND answer_tokens IS NOT NULL AND reasoning_tokens IS NOT NULL
 THEN (answer_tokens+reasoning_tokens)/task_count/output_speed_tokens_per_second+coalesce(mean_tool_ms_per_task/1000.0,0) END AS estimated_seconds_per_task,
 '1e955781826f7a5d8fcca0778c4fe506f1d7cee87b2618b358a277b6b6c97052' AS calculation_source_sha256
FROM components;
CREATE VIEW IF NOT EXISTS benchmark_estimated_costs_and_times AS
SELECT t.source_url,t.page_sha256,t.model_id,t.model_slug,t.model_name,t.effort,t.benchmark_slug,t.task_count,
r.score_field,json_extract(e.model_json,'$.'||r.score_field) AS score_raw,
c.cost_usd_per_task,c.noncache_input_cost_usd_per_task,c.cache_read_cost_usd_per_task,c.cache_write_cost_usd_per_task,
c.reasoning_cost_usd_per_task,c.answer_cost_usd_per_task,c.fallback_applied,
t.estimated_generation_seconds_per_task,t.mean_tool_ms_per_task,t.source_tool_component_complete,t.estimated_seconds_per_task,
t.output_speed_tokens_per_second,t.answer_tokens,t.reasoning_tokens,t.registry_source_sha256,t.calculation_source_sha256,
c.formula_helper_sha256
FROM benchmark_generation_time_estimates t JOIN evaluation_page_models e ON e.source_url=t.source_url AND e.model_id=t.model_id
LEFT JOIN benchmark_cost_estimates c ON c.source_url=t.source_url AND c.model_id=t.model_id AND c.benchmark_slug=t.benchmark_slug
LEFT JOIN benchmark_registry r ON r.evaluation_slug=t.benchmark_slug;
-- Display labels capture router/model combinations whose structured `model` is null.
CREATE VIEW IF NOT EXISTS coding_agent_display_benchmark_results AS
SELECT a.source_url,a.page_sha256,a.retrieved_at_utc,a.run_id,a.agent_slug,
a.agent_name AS source_agent_name,coalesce(json_extract(a.run_json,'$.display.agent'),a.agent_name) AS display_agent_name,
a.model_name AS structured_model_name,coalesce(a.model_name,json_extract(a.run_json,'$.display.model')) AS display_model_name,
a.effort,json_extract(e.value,'$.datasetIndexName') AS dataset_id,
json_extract(e.value,'$.evaluationDatasetSlug') AS benchmark_name,json_extract(e.value,'$.mean.reward') AS mean_reward,
json_extract(e.value,'$.mean.inputTokens') AS mean_input_tokens,json_extract(e.value,'$.mean.outputTokens') AS mean_output_tokens,
json_extract(a.run_json,'$.mean.costUsd') AS index_mix_mean_cost_usd_per_task,
json_extract(a.run_json,'$.mean.agentWallTimeSec') AS index_mix_mean_wall_time_seconds,
e.value AS benchmark_raw_json
FROM coding_agent_latest_runs a,json_each(a.run_json,'$.evals') e;
