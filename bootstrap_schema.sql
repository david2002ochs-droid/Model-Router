-- Leeres, kompatibles Datenbankschema; enthält keine Daten.
BEGIN;
CREATE TABLE IF NOT EXISTS archive_integrity_checks(source_url TEXT PRIMARY KEY,page_sha256 TEXT NOT NULL,checked_at_utc TEXT NOT NULL,status TEXT NOT NULL,error TEXT);
CREATE TABLE IF NOT EXISTS benchmark_calculation_sources(sha256 TEXT PRIMARY KEY,source_url TEXT NOT NULL,retrieved_at_utc TEXT NOT NULL,body BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS benchmark_cost_estimates(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,model_id TEXT NOT NULL,model_slug TEXT,model_name TEXT,effort TEXT,
 benchmark_slug TEXT NOT NULL,token_field TEXT NOT NULL,task_count REAL NOT NULL,cost_usd_per_task REAL,
 noncache_input_cost_usd_per_task REAL,cache_read_cost_usd_per_task REAL,cache_write_cost_usd_per_task REAL,
 reasoning_cost_usd_per_task REAL,answer_cost_usd_per_task REAL,fallback_applied INTEGER NOT NULL,
 registry_source_sha256 TEXT NOT NULL,formula_source_sha256 TEXT NOT NULL,formula_helper_sha256 TEXT NOT NULL,
 PRIMARY KEY(source_url,model_id,benchmark_slug));
CREATE TABLE IF NOT EXISTS benchmark_registry(evaluation_slug TEXT PRIMARY KEY,score_field TEXT NOT NULL,source_sha256 TEXT NOT NULL,expression TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS benchmark_registry_metadata(evaluation_slug TEXT PRIMARY KEY,source_sha256 TEXT NOT NULL,task_count REAL,task_weight REAL,score_format TEXT,config_raw TEXT,definition_raw TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS benchmark_time_config(
 benchmark_slug TEXT PRIMARY KEY,token_field TEXT NOT NULL,task_count REAL NOT NULL,has_tool_time INTEGER NOT NULL,
 registry_source_sha256 TEXT NOT NULL,source_definition TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS cache_pricing_source_rows(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,provider_group_raw TEXT NOT NULL,provider_links_json TEXT NOT NULL,model_name TEXT NOT NULL,input_usd_per_million REAL,cache_write_usd_per_million REAL,cache_hit_usd_per_million REAL,cache_storage_raw TEXT,output_usd_per_million REAL,auto_enabled_raw TEXT,min_tokens_raw TEXT,cache_ttl_raw TEXT,notes_raw TEXT,raw_cells_json TEXT NOT NULL,PRIMARY KEY(source_url,table_number,row_number));
CREATE TABLE IF NOT EXISTS captures(id INTEGER PRIMARY KEY, retrieved_at_utc TEXT NOT NULL, source_url TEXT NOT NULL, sha256 TEXT NOT NULL, headers_json TEXT NOT NULL, row_count INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS chatbot_plan_observations(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,plan_id TEXT NOT NULL,plan_name TEXT NOT NULL,creator_name TEXT,product_slug TEXT,tier TEXT,monthly_price_usd REAL,monthly_price_notes TEXT,model_slug TEXT,model_name TEXT,model_notes TEXT,intelligence_index REAL,feature_score REAL,raw_json TEXT NOT NULL,PRIMARY KEY(source_url,plan_id));
CREATE TABLE IF NOT EXISTS coding_agent_extraction_log(source_url TEXT PRIMARY KEY,page_sha256 TEXT NOT NULL,run_count INTEGER NOT NULL,error TEXT);
CREATE TABLE IF NOT EXISTS coding_agent_runs(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,run_id TEXT NOT NULL,agent_name TEXT,agent_slug TEXT,model_name TEXT,effort TEXT,run_json TEXT NOT NULL,PRIMARY KEY(source_url,run_id));
CREATE TABLE IF NOT EXISTS crawl_queue(url TEXT PRIMARY KEY, status TEXT NOT NULL DEFAULT 'pending', http_status INTEGER, retrieved_at_utc TEXT, error TEXT);
CREATE TABLE IF NOT EXISTS decision_dataset_results(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,contestant_slug TEXT NOT NULL,contestant_name TEXT,
 contestant_kind TEXT,host_name TEXT,creator_name TEXT,dataset_slug TEXT NOT NULL,cost_usd_per_task REAL,
 median_time_ms_per_task REAL,brier REAL,raw_json TEXT NOT NULL,PRIMARY KEY(source_url,contestant_slug,dataset_slug));
CREATE TABLE IF NOT EXISTS decision_index_contestants(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,contestant_slug TEXT NOT NULL,contestant_name TEXT,contestant_kind TEXT,
 host_name TEXT,creator_name TEXT,index_score REAL,accuracy_index_score REAL,cost_usd_per_task REAL,median_time_ms_per_task REAL,
 brier REAL,raw_json TEXT NOT NULL,PRIMARY KEY(source_url,contestant_slug));
CREATE TABLE IF NOT EXISTS discovered_links(url TEXT NOT NULL,source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,PRIMARY KEY(url,source_url));
CREATE TABLE IF NOT EXISTS embedded_model_snapshots(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,model_id TEXT NOT NULL,model_slug TEXT,model_name TEXT,effort TEXT,model_json TEXT NOT NULL,PRIMARY KEY(source_url,page_sha256,model_id));
CREATE TABLE IF NOT EXISTS evaluation_extraction_log(source_url TEXT PRIMARY KEY,page_sha256 TEXT NOT NULL,model_count INTEGER NOT NULL,error TEXT);
CREATE TABLE IF NOT EXISTS evaluation_page_models(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,model_id TEXT NOT NULL,model_slug TEXT,model_name TEXT,effort TEXT,model_json TEXT NOT NULL,PRIMARY KEY(source_url,model_id));
CREATE TABLE IF NOT EXISTS evaluation_price_fallbacks(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,model_id TEXT NOT NULL,raw_json TEXT NOT NULL,PRIMARY KEY(source_url,model_id));
CREATE TABLE IF NOT EXISTS extracted_tables(url TEXT NOT NULL, page_sha256 TEXT NOT NULL, table_number INTEGER NOT NULL, rows_json TEXT NOT NULL, PRIMARY KEY(url,table_number));
CREATE TABLE IF NOT EXISTS harvey_exact_task_costs(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,model_id TEXT NOT NULL,model_name TEXT,creator_name TEXT,gated_all_pass_fraction REAL,criterion_pass_fraction REAL,material_hallucinations_per_task REAL,cost_per_task_usd REAL,release_date TEXT,raw_json TEXT NOT NULL,PRIMARY KEY(source_url,model_id));
CREATE TABLE IF NOT EXISTS harvey_lab_table_observations(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,
 display_rank INTEGER,creator_name TEXT,model_name TEXT NOT NULL,hallucination_gated_all_pass_pct REAL,
 criterion_pass_pct REAL,material_hallucinations_per_task REAL,displayed_cost_usd_per_task REAL,release_date_text TEXT,
 raw_cells_json TEXT NOT NULL,PRIMARY KEY(source_url,table_number,row_number));
CREATE TABLE IF NOT EXISTS image_host_model_observations(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,host_model_id TEXT NOT NULL,host_model_name TEXT,host_model_slug TEXT,
 host_id TEXT,host_name TEXT,host_slug TEXT,model_id TEXT,model_name TEXT,model_slug TEXT,creator_id TEXT,creator_name TEXT,
 price_usd_per_1000_images REAL,endpoint_classification TEXT,quality_elo REAL,quality_elo_ci_low REAL,quality_elo_ci_high REAL,
 median_generation_seconds REAL,p05_generation_seconds REAL,p25_generation_seconds REAL,p75_generation_seconds REAL,p95_generation_seconds REAL,
 raw_json TEXT NOT NULL,PRIMARY KEY(source_url,host_model_id));
CREATE TABLE IF NOT EXISTS media_arena_observations(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,media_type TEXT NOT NULL,arena_task TEXT NOT NULL,
 category_slug TEXT NOT NULL,model_id TEXT NOT NULL,model_name TEXT NOT NULL,creator_id TEXT,creator_name TEXT,
 elo REAL,confidence_lower REAL,confidence_upper REAL,sample_count INTEGER,release_date TEXT,
 price_usd_per_1000_images REAL,price_usd_per_video_minute REAL,open_weights_url TEXT,raw_json TEXT NOT NULL,
 PRIMARY KEY(source_url,category_slug,model_id));
CREATE TABLE IF NOT EXISTS media_arena_openweights_observations(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,
 media_type TEXT NOT NULL,arena_task TEXT NOT NULL,rank INTEGER,rank_range TEXT,model_name TEXT NOT NULL,
 elo_displayed REAL,ci_lower_displayed REAL,ci_upper_displayed REAL,sample_count INTEGER,released TEXT,
 price_text TEXT,price_usd_per_1000_images REAL,price_usd_per_video_minute REAL,raw_cells_json TEXT NOT NULL,
 PRIMARY KEY(source_url,table_number,row_number));
CREATE TABLE IF NOT EXISTS media_endpoint_extraction_log(source_url TEXT PRIMARY KEY,page_sha256 TEXT NOT NULL,record_count INTEGER NOT NULL,extracted_at_utc TEXT NOT NULL,error TEXT);
CREATE TABLE IF NOT EXISTS media_endpoint_records(
 source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,modality TEXT NOT NULL,endpoint_id TEXT NOT NULL,endpoint_slug TEXT,endpoint_name TEXT,endpoint_classification TEXT,
 provider_id TEXT,provider_slug TEXT,provider_name TEXT,model_id TEXT,model_slug TEXT,model_name TEXT,
 price_per_1000_images_usd REAL,model_quality_elo REAL,model_quality_ci95_low REAL,model_quality_ci95_high REAL,
 median_generation_seconds REAL,p05_generation_seconds REAL,p25_generation_seconds REAL,p75_generation_seconds REAL,p95_generation_seconds REAL,
 is_representative INTEGER,raw_json TEXT NOT NULL, video_price_usd_per_minute REAL, tts_price_usd_per_million_chars REAL, median_chars_per_second REAL, latency_json TEXT, time_percentiles_consistent INTEGER, text_to_video_elo REAL, image_to_video_elo REAL,PRIMARY KEY(source_url,endpoint_id));
CREATE TABLE IF NOT EXISTS media_leaderboard_observations(
 source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,
 modality TEXT NOT NULL,benchmark_slug TEXT NOT NULL,open_weights_filter INTEGER NOT NULL,rank INTEGER,rank_range TEXT,
 model_name TEXT NOT NULL,model_links_json TEXT NOT NULL,elo REAL,elo_ci95_low REAL,elo_ci95_high REAL,elo_raw TEXT,
 samples INTEGER,arena_voices TEXT,released TEXT,price_usd REAL,price_unit TEXT,price_raw TEXT,raw_cells_json TEXT NOT NULL,
 PRIMARY KEY(source_url,table_number,row_number));
CREATE TABLE IF NOT EXISTS media_mapping_sources(source_url TEXT PRIMARY KEY,sha256 TEXT NOT NULL,retrieved_at_utc TEXT NOT NULL,body BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS model_details(source_url TEXT PRIMARY KEY, page_sha256 TEXT NOT NULL, model_id TEXT, slug TEXT, name TEXT, effort TEXT, model_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS model_extraction_log(source_url TEXT PRIMARY KEY, page_sha256 TEXT NOT NULL, object_count INTEGER NOT NULL, error TEXT);
CREATE TABLE IF NOT EXISTS model_observations(capture_id INTEGER NOT NULL REFERENCES captures(id), row_number INTEGER NOT NULL, model_name TEXT NOT NULL, context_window TEXT, creator TEXT, intelligence_index REAL, cost_per_task_usd REAL, time_per_task_minutes REAL, first_answer_token_seconds REAL, raw_cells_json TEXT NOT NULL, links_json TEXT NOT NULL, PRIMARY KEY(capture_id,row_number));
CREATE TABLE IF NOT EXISTS page_archive(url TEXT PRIMARY KEY REFERENCES crawl_queue(url), sha256 TEXT NOT NULL, content_type TEXT, body_gzip BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS page_capture_events(id INTEGER PRIMARY KEY,source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,retrieved_at_utc TEXT NOT NULL,final_url TEXT,content_type TEXT);
CREATE TABLE IF NOT EXISTS pipeline_step_runs(id INTEGER PRIMARY KEY,started_at_utc TEXT NOT NULL,script TEXT NOT NULL,exit_code INTEGER,status TEXT NOT NULL,summary TEXT);
CREATE TABLE IF NOT EXISTS provider_accuracy_observations(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,model_slug TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,provider TEXT,cost_per_task_usd REAL,time_per_task_minutes REAL,endpoint_accuracy_index_percent REAL,first_answer_token_seconds REAL,error_rate_percent REAL,context_window TEXT,function_calling TEXT,json_mode TEXT,license TEXT,raw_cells_json TEXT NOT NULL,PRIMARY KEY(source_url,table_number,row_number));
CREATE TABLE IF NOT EXISTS provider_endpoint_extraction_log (
 source_url TEXT PRIMARY KEY,page_sha256 TEXT NOT NULL,record_count INTEGER NOT NULL,extracted_at_utc TEXT NOT NULL,error TEXT);
CREATE TABLE IF NOT EXISTS provider_endpoint_records (
 source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,array_kind TEXT NOT NULL,endpoint_id TEXT NOT NULL,
 endpoint_slug TEXT,host_id TEXT,host_slug TEXT,host_name TEXT,model_id TEXT,model_slug TEXT,model_name TEXT,
 price_1m_input_usd REAL,price_1m_output_usd REAL,cache_hit_usd_per_1m REAL,cache_write_usd_per_1m REAL,
 cost_per_task_usd REAL,index_time_per_task_seconds REAL,output_tokens_per_second REAL,
 first_answer_token_seconds REAL,first_token_seconds REAL,error_rate_fraction REAL,context_window_tokens INTEGER,
 function_calling INTEGER,json_mode INTEGER,raw_json TEXT NOT NULL,
 PRIMARY KEY(source_url,array_kind,endpoint_id));
CREATE TABLE IF NOT EXISTS provider_leaderboard_observations(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,provider TEXT,model_name TEXT,intelligence_index REAL,cost_per_task_usd REAL,time_per_task_minutes REAL,first_answer_token_seconds REAL,error_rate_percent REAL,context_window TEXT,license TEXT,raw_cells_json TEXT NOT NULL,PRIMARY KEY(source_url,table_number,row_number));
CREATE TABLE IF NOT EXISTS provider_observations(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,model_slug TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,provider TEXT,cost_per_task_usd REAL,time_per_task_minutes REAL,first_answer_token_seconds REAL,error_rate_percent REAL,context_window TEXT,function_calling TEXT,json_mode TEXT,license TEXT,raw_cells_json TEXT NOT NULL,PRIMARY KEY(source_url,table_number,row_number));
CREATE TABLE IF NOT EXISTS provider_page_models(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,provider_slug TEXT NOT NULL,model_name TEXT NOT NULL,intelligence_index REAL,cost_per_task_usd REAL,time_per_task_minutes REAL,first_answer_token_seconds REAL,error_rate_percent REAL,context_window TEXT,function_calling TEXT,json_mode TEXT,license TEXT,raw_cells_json TEXT NOT NULL,PRIMARY KEY(source_url,table_number,row_number));
CREATE TABLE IF NOT EXISTS provider_pricing_footnotes(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,endpoint_id TEXT NOT NULL,host_slug TEXT,host_name TEXT,model_slug TEXT,model_name TEXT,footnote_text TEXT NOT NULL,PRIMARY KEY(source_url,endpoint_id));
CREATE TABLE IF NOT EXISTS provider_pricing_mapping_sources(source_url text primary key,sha256 text not null,recorded_at_utc text not null,body blob not null);
CREATE TABLE IF NOT EXISTS provider_tiered_pricing(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,endpoint_id TEXT NOT NULL,host_slug TEXT,model_slug TEXT,tier_number INTEGER NOT NULL,threshold_raw TEXT NOT NULL,input_price_raw TEXT NOT NULL,output_price_raw TEXT NOT NULL,input_price_per_million REAL,output_price_per_million REAL,amount_parse_warning TEXT,footnote_text TEXT NOT NULL,PRIMARY KEY(source_url,endpoint_id,tier_number));
CREATE TABLE IF NOT EXISTS registry_sources(sha256 TEXT PRIMARY KEY,source_url TEXT NOT NULL,retrieved_at_utc TEXT NOT NULL,body BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS retry_attempts(url text primary key, retry_count integer not null default 0, last_error text);
CREATE TABLE IF NOT EXISTS search_agent_details(
 source_url TEXT NOT NULL, source_sha256 TEXT NOT NULL, configuration_id TEXT NOT NULL,
 provider_key TEXT, provider_name TEXT,provider_family_slug TEXT, provider_variant TEXT,
 answer_model_slug TEXT, answer_model_name TEXT,
 quality_index_raw REAL, browsecomp_accuracy_raw REAL, deepsearchqa_f1_raw REAL, omniscience_accuracy_raw REAL, baseline_lift_raw REAL,
 average_task_seconds REAL, search_time_per_task_seconds REAL, candidate_model_time_seconds_derived REAL,search_query_latency_seconds REAL,
 candidate_model_cost_usd_per_task REAL, search_api_cost_usd_per_task REAL, cost_usd_per_search_query REAL,
 search_queries_per_task REAL,input_tokens_per_task REAL, reasoning_tokens_per_task REAL,answer_tokens_per_task REAL,
 benchmark_count INTEGER, latest_measured_at TEXT,raw_json TEXT NOT NULL, PRIMARY KEY(source_url,configuration_id));
CREATE TABLE IF NOT EXISTS search_api_observations(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,provider_variant TEXT NOT NULL,search_index REAL,baseline_lift REAL,deepsearchqa_f1 REAL,browsecomp_accuracy REAL,omniscience_accuracy REAL,search_cost_usd_per_1000 REAL,model_cost_usd_per_1000 REAL,time_per_task_seconds REAL,website TEXT,raw_cells_json TEXT NOT NULL,PRIMARY KEY(source_url,table_number,row_number));
CREATE TABLE IF NOT EXISTS speech_agent_arena_results(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,result_id TEXT NOT NULL,model_key TEXT,host_model_id TEXT,
 model_name TEXT NOT NULL,creator_id TEXT,creator_name TEXT,slice_key TEXT,elo REAL,elo_ci_low REAL,elo_ci_high REAL,
 appearances INTEGER,task_completion_rate REAL,task_completion_success_count INTEGER,task_completion_failure_count INTEGER,
 source_rank INTEGER,speech_quality_index REAL,raw_json TEXT NOT NULL,PRIMARY KEY(source_url,result_id));
CREATE TABLE IF NOT EXISTS speech_agent_host_details(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,host_model_id TEXT NOT NULL,host_model_name TEXT,host_model_slug TEXT,
 host_id TEXT,host_name TEXT,model_id TEXT,model_name TEXT,model_slug TEXT,
 speech_index REAL,big_bench_audio_score_raw REAL,conversational_dynamics_score_raw REAL,tau3_voice_score_raw REAL,
 first_audio_seconds REAL,big_bench_audio_average_cost_per_task_usd REAL,big_bench_audio_cost_per_input_hour_usd REAL,
 input_audio_price_usd_per_hour REAL,output_audio_price_usd_per_hour REAL,tau3_voice_mean_audio_duration_seconds REAL,
 source_series_json TEXT NOT NULL,raw_json TEXT NOT NULL,PRIMARY KEY(source_url,host_model_id));
CREATE TABLE IF NOT EXISTS speech_to_speech_observations(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,
 provider TEXT,model TEXT, speech_to_speech_index REAL,speech_reasoning_pct REAL,conversational_dynamics_pct REAL,
 agentic_performance_pct REAL,arena_preference_elo REAL,task_success_pct REAL,first_audio_seconds REAL,
 cost_per_hour_input_audio_usd REAL,input_audio_price_usd_per_hour REAL,output_audio_price_usd_per_hour REAL,
 raw_cells_json TEXT NOT NULL, PRIMARY KEY(source_url,table_number,row_number));
CREATE TABLE IF NOT EXISTS speech_to_text_observations(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,
 model TEXT,provider TEXT,whisper_version TEXT,word_error_rate_pct REAL,median_speed_factor REAL,
 price_usd_per_1000_minutes REAL,raw_cells_json TEXT NOT NULL, PRIMARY KEY(source_url,table_number,row_number));
CREATE TABLE IF NOT EXISTS streaming_speech_observations(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,host_model_id TEXT NOT NULL,
 name TEXT,host_id TEXT,host_name TEXT,model_id TEXT,model_name TEXT,price_per_1000_minutes REAL,
 aa_wer_streaming_index REAL,aa_agenttalk_streaming_wer REAL,voxpopuli_streaming_wer REAL,
 earnings22_streaming_wer REAL,time_to_final_transcript_seconds REAL,time_to_first_partial_transcript_seconds REAL,
 raw_json TEXT NOT NULL, PRIMARY KEY(source_url,host_model_id));
CREATE TABLE IF NOT EXISTS table_extraction_log(url TEXT PRIMARY KEY, page_sha256 TEXT NOT NULL, table_count INTEGER NOT NULL, error TEXT);
CREATE TABLE IF NOT EXISTS tts_arena_observations(
 source_url TEXT NOT NULL, source_sha256 TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,
 arena_variant TEXT NOT NULL,rank INTEGER,rank_range TEXT,model_name TEXT NOT NULL,elo REAL,elo_interval_low REAL,elo_interval_high REAL,
 sample_count INTEGER,arena_voices TEXT,released TEXT,price_usd_per_million_characters REAL,price_text TEXT,raw_cells_json TEXT NOT NULL,
 PRIMARY KEY(source_url,table_number,row_number));
CREATE TABLE IF NOT EXISTS video_host_model_observations(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,host_model_id TEXT NOT NULL,host_model_name TEXT,host_model_slug TEXT,
 host_id TEXT,host_name TEXT,host_slug TEXT,model_id TEXT,model_name TEXT,model_slug TEXT,creator_id TEXT,creator_name TEXT,
 price_usd_per_video_minute REAL,endpoint_classification TEXT,text_to_video_elo REAL,image_to_video_elo REAL,
 median_generation_seconds REAL,p05_generation_seconds REAL,p25_generation_seconds REAL,p75_generation_seconds REAL,p95_generation_seconds REAL,
 raw_json TEXT NOT NULL,PRIMARY KEY(source_url,host_model_id));
CREATE VIEW agentic_benchmark_estimated_times AS
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
CREATE VIEW agentic_estimates_with_source AS SELECT o.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.page_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc FROM agentic_benchmark_estimated_times o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.page_sha256 LEFT JOIN page_archive p ON p.url=o.source_url LEFT JOIN crawl_queue q ON q.url=o.source_url;
CREATE VIEW all_provider_observations AS
SELECT source_url,page_sha256,model_slug,table_number,row_number,provider,cost_per_task_usd,time_per_task_minutes,
CAST(NULL AS REAL) AS endpoint_accuracy_index_percent,first_answer_token_seconds,error_rate_percent,context_window,function_calling,json_mode,license,raw_cells_json
FROM provider_observations
UNION ALL
SELECT source_url,page_sha256,model_slug,table_number,row_number,provider,cost_per_task_usd,time_per_task_minutes,
endpoint_accuracy_index_percent,first_answer_token_seconds,error_rate_percent,context_window,function_calling,json_mode,license,raw_cells_json
FROM provider_accuracy_observations;
CREATE VIEW benchmark_catalog AS
SELECT s.source_url,s.page_sha256,s.model_id,s.model_slug,s.model_name,s.effort,s.evaluation_slug,s.score,
r.cost_per_task_usd_inferred,r.time_per_task_seconds_inferred,r.time_per_task_minutes_inferred,r.output_tokens_per_task
FROM embedded_verified_scores s LEFT JOIN embedded_benchmark_results_readable r
ON r.source_url=s.source_url AND r.page_sha256=s.page_sha256 AND r.model_id=s.model_id AND r.evaluation_slug=s.evaluation_slug;
CREATE VIEW benchmark_cost_estimate_gaps AS
SELECT g.source_url,g.page_sha256,g.model_id,g.model_name,g.effort,g.benchmark_slug,g.token_field,
CASE WHEN json_type(e.model_json,'$.price1mInputTokens') NOT IN ('integer','real') OR json_type(e.model_json,'$.price1mOutputTokens') NOT IN ('integer','real') OR json_type(e.model_json,'$.price1mInputTokens') IS NULL OR json_type(e.model_json,'$.price1mOutputTokens') IS NULL THEN 1 ELSE 0 END AS input_or_output_price_missing,
CASE WHEN json_type(e.model_json,'$.canonicalEvalTokenCounts."'||g.token_field||'".cacheableInput') IN ('integer','real') AND (json_type(e.model_json,'$.cacheHitRate') IS NULL OR json_type(e.model_json,'$.cacheHitRate') NOT IN ('integer','real')) THEN 1 ELSE 0 END AS cache_hit_rate_missing,
CASE WHEN coalesce(json_type(e.model_json,'$.canonicalEvalTokenCounts."'||g.token_field||'".input'),'missing') NOT IN ('integer','real') OR coalesce(json_type(e.model_json,'$.canonicalEvalTokenCounts."'||g.token_field||'".answer'),'missing') NOT IN ('integer','real') OR coalesce(json_type(e.model_json,'$.canonicalEvalTokenCounts."'||g.token_field||'".reasoning'),'missing') NOT IN ('integer','real') THEN 1 ELSE 0 END AS required_tokens_missing
FROM benchmark_generation_time_estimates g JOIN evaluation_page_models e ON e.source_url=g.source_url AND e.model_id=g.model_id
LEFT JOIN benchmark_cost_estimates b ON b.source_url=g.source_url AND b.model_id=g.model_id AND b.benchmark_slug=g.benchmark_slug
WHERE b.model_id IS NULL;
CREATE VIEW benchmark_cost_estimates_with_source AS SELECT o.*,o.cost_usd_per_task estimated_cost_usd_per_task,f.cache_read_input_price_substituted,f.cache_write_input_price_substituted,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.source_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc FROM benchmark_cost_estimates o LEFT JOIN benchmark_cost_fallback_flags f ON f.source_url=o.source_url AND f.model_id=o.model_id AND f.benchmark_slug=o.benchmark_slug LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.source_sha256 LEFT JOIN page_archive p ON p.url=o.source_url LEFT JOIN crawl_queue q ON q.url=o.source_url;
CREATE VIEW benchmark_cost_fallback_flags AS
SELECT b.source_url,b.model_id,b.benchmark_slug,
CASE WHEN json_extract(e.model_json,'$.canonicalEvalTokenCounts."'||b.token_field||'".cacheableInput') * json_extract(e.model_json,'$.cacheHitRate')>0 AND
 ((json_extract(e.model_json,'$.cacheHitPrice') IS NULL AND coalesce(json_extract(f.raw_json,'$.rateByEval."'||b.benchmark_slug||'".input'),0)<1)
 OR (b.fallback_applied=1 AND coalesce(json_extract(f.raw_json,'$.rateByEval."'||b.benchmark_slug||'".input'),0)>0 AND json_extract(f.raw_json,'$.fallbackPrice.cacheHit') IS NULL)) THEN 1 ELSE 0 END cache_read_input_price_substituted,
CASE WHEN json_extract(e.model_json,'$.canonicalEvalTokenCounts."'||b.token_field||'".input') - json_extract(e.model_json,'$.canonicalEvalTokenCounts."'||b.token_field||'".cacheableInput') * json_extract(e.model_json,'$.cacheHitRate')>0 AND
 ((json_extract(e.model_json,'$.cacheWritePrice') IS NULL AND coalesce(json_extract(f.raw_json,'$.rateByEval."'||b.benchmark_slug||'".input'),0)<1)
 OR (b.fallback_applied=1 AND coalesce(json_extract(f.raw_json,'$.rateByEval."'||b.benchmark_slug||'".input'),0)>0 AND json_extract(f.raw_json,'$.fallbackPrice.cacheWrite') IS NULL)) THEN 1 ELSE 0 END cache_write_input_price_substituted
FROM benchmark_cost_estimates b JOIN evaluation_page_models e ON e.source_url=b.source_url AND e.model_id=b.model_id
LEFT JOIN evaluation_price_fallbacks f ON f.source_url=b.source_url AND f.model_id=b.model_id;
CREATE VIEW benchmark_cost_gaps_with_source AS SELECT o.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.page_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc FROM benchmark_cost_estimate_gaps o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.page_sha256 LEFT JOIN page_archive p ON p.url=o.source_url LEFT JOIN crawl_queue q ON q.url=o.source_url;
CREATE VIEW benchmark_cost_time_with_source AS SELECT o.*,o.cost_usd_per_task estimated_cost_usd_per_task,g.has_tool_time,f.cache_read_input_price_substituted,f.cache_write_input_price_substituted,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.page_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc FROM benchmark_estimated_costs_and_times o LEFT JOIN benchmark_generation_time_estimates g ON g.source_url=o.source_url AND g.page_sha256=o.page_sha256 AND g.model_id=o.model_id AND g.benchmark_slug=o.benchmark_slug LEFT JOIN benchmark_cost_fallback_flags f ON f.source_url=o.source_url AND f.model_id=o.model_id AND f.benchmark_slug=o.benchmark_slug LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.page_sha256 LEFT JOIN page_archive p ON p.url=o.source_url LEFT JOIN crawl_queue q ON q.url=o.source_url;
CREATE VIEW benchmark_estimated_costs_and_times AS
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
CREATE VIEW benchmark_generation_time_estimates AS
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
CREATE VIEW benchmark_named_breakdown_facts AS
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
CREATE VIEW benchmark_named_breakdown_with_source AS SELECT o.*,t.retrieved_at_utc FROM benchmark_named_breakdown_facts o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.page_sha256;
CREATE VIEW benchmark_results AS
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
CREATE VIEW benchmark_scores_with_metadata AS
SELECT s.source_url,s.page_sha256,s.retrieved_at_utc,s.model_id,s.model_slug,s.model_name,s.effort,
s.evaluation_slug,s.score_field,s.score AS score_raw,m.score_format,
CASE WHEN instr(coalesce(m.score_format,''),'%')>0 THEN s.score*100 ELSE s.score END AS score_display_value,
m.task_count,m.task_weight,m.source_sha256 AS metadata_source_sha256
FROM latest_combined_benchmark_scores s LEFT JOIN benchmark_registry_metadata m ON m.evaluation_slug=s.evaluation_slug;
CREATE VIEW benchmark_task_costs AS
SELECT d.source_url,d.model_id,d.slug,d.name,d.effort,
json_extract(e.value,'$.slug') AS evaluation_slug,
json_extract(e.value,'$.weightedCostPerTask') AS weighted_cost_per_task
FROM model_details d, json_each(d.model_json,'$.intelligenceIndexCostPerTask.evaluations') e;
CREATE VIEW benchmark_time_estimates_with_source AS SELECT o.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.page_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc FROM benchmark_generation_time_estimates o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.page_sha256 LEFT JOIN page_archive p ON p.url=o.source_url LEFT JOIN crawl_queue q ON q.url=o.source_url;
CREATE VIEW cache_pricing_rows_with_source AS SELECT o.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.page_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc FROM cache_pricing_source_rows o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.page_sha256 LEFT JOIN page_archive p ON p.url=o.source_url LEFT JOIN crawl_queue q ON q.url=o.source_url;
CREATE VIEW chatbot_plans_with_source AS SELECT o.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.page_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc FROM chatbot_plan_observations o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.page_sha256 LEFT JOIN page_archive p ON p.url=o.source_url LEFT JOIN crawl_queue q ON q.url=o.source_url;
CREATE VIEW coding_agent_benchmark_results AS
SELECT a.source_url,a.page_sha256,a.run_id,a.agent_name,a.agent_slug,a.model_name,a.effort,
json_extract(e.value,'$.datasetIndexName') dataset_id,json_extract(e.value,'$.evaluationDatasetSlug') benchmark_name,
json_extract(e.value,'$.refDatasetName') dataset_reference,json_extract(e.value,'$.weight') weight,
json_extract(e.value,'$.mean.reward') mean_reward,json_extract(e.value,'$.mean.inputTokens') mean_input_tokens,
json_extract(e.value,'$.mean.outputTokens') mean_output_tokens,e.value result_json
FROM coding_agent_runs a,json_each(a.run_json,'$.evals') e;
CREATE VIEW coding_agent_display_benchmark_results AS
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
CREATE VIEW coding_agent_evaluation_leaf_facts AS
SELECT a.source_url,a.page_sha256,a.retrieved_at_utc,a.run_id,a.agent_name,a.model_name,a.effort,
json_extract(e.value,'$.datasetIndexName') AS dataset_id,j.fullkey AS json_path,j.type AS value_type,j.atom AS value
FROM coding_agent_latest_runs a,json_each(a.run_json,'$.evals') e,json_tree(e.value) j
WHERE j.type IN ('integer','real','text','true','false','null');
CREATE VIEW coding_agent_latest_benchmarks AS
SELECT a.source_url,a.page_sha256,a.retrieved_at_utc,a.run_id,a.agent_name,a.agent_slug,a.model_name,a.effort,
json_extract(e.value,'$.datasetIndexName') dataset_id,json_extract(e.value,'$.evaluationDatasetSlug') benchmark_name,
json_extract(e.value,'$.refDatasetName') dataset_reference,json_extract(e.value,'$.weight') weight,
json_extract(e.value,'$.mean.reward') mean_reward,json_extract(e.value,'$.mean.inputTokens') mean_input_tokens,
json_extract(e.value,'$.mean.outputTokens') mean_output_tokens,e.value result_json
FROM coding_agent_latest_runs a,json_each(a.run_json,'$.evals') e;
CREATE VIEW coding_agent_latest_runs AS
SELECT * FROM (
 SELECT a.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=a.page_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc,
 ROW_NUMBER() OVER (PARTITION BY a.run_id ORDER BY coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=a.page_sha256 THEN q.retrieved_at_utc END) DESC,a.source_url) source_rank
 FROM coding_agent_runs a LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=a.source_url AND t.page_sha256=a.page_sha256 LEFT JOIN crawl_queue q ON q.url=a.source_url LEFT JOIN page_archive p ON p.url=a.source_url
) WHERE source_rank=1;
CREATE VIEW coding_agent_run_summary AS
SELECT source_url,page_sha256,run_id,agent_name,agent_slug,model_name,effort,
json_extract(run_json,'$.indexScore') index_score,json_extract(run_json,'$.mean.costUsd') mean_cost_usd,
json_extract(run_json,'$.mean.agentWallTimeSec') mean_agent_wall_time_seconds,
json_extract(run_json,'$.mean.inputTokens') mean_input_tokens,json_extract(run_json,'$.mean.outputTokens') mean_output_tokens,
json_extract(run_json,'$.mean.cacheTokens') mean_cache_tokens,json_extract(run_json,'$.mean.steps') mean_steps
FROM coding_agent_runs;
CREATE VIEW combined_latest_benchmark_scores AS
SELECT * FROM latest_registry_benchmark_scores
UNION ALL SELECT * FROM latest_verified_field_aliases;
CREATE VIEW decision_dataset_benchmark_results AS
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
CREATE VIEW decision_dataset_results_with_source AS SELECT o.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.source_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc FROM decision_dataset_benchmark_results o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.source_sha256 LEFT JOIN page_archive p ON p.url=o.source_url LEFT JOIN crawl_queue q ON q.url=o.source_url;
CREATE VIEW embedded_benchmark_results AS
SELECT d.source_url,d.page_sha256,d.model_id,d.model_slug,d.model_name,d.effort,
json_extract(d.model_json,'$.creator.id') creator_id,json_extract(d.model_json,'$.creator.name') creator_name,
json_extract(e.value,'$.slug') evaluation_slug,json_extract(e.value,'$.score') score,
json_extract(e.value,'$.costPerTask') cost_per_task,json_extract(e.value,'$.timePerTask') time_per_task,
json_extract(e.value,'$.outputTokensPerTask') output_tokens_per_task,e.value source_result_json
FROM embedded_model_snapshots d,json_each(d.model_json,'$.intelligenceIndexEvaluations') e;
CREATE VIEW embedded_benchmark_results_readable AS
SELECT source_url,page_sha256,model_id,model_slug,model_name,effort,creator_id,creator_name,evaluation_slug,score,
cost_per_task AS cost_per_task_usd_inferred,time_per_task AS time_per_task_seconds_inferred,
time_per_task/60.0 AS time_per_task_minutes_inferred,output_tokens_per_task,source_result_json
FROM embedded_benchmark_results;
CREATE VIEW embedded_latest_models AS
SELECT * FROM (
 SELECT e.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=e.page_sha256 THEN q.retrieved_at_utc END) AS retrieved_at_utc,
 ROW_NUMBER() OVER (PARTITION BY e.model_id ORDER BY coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=e.page_sha256 THEN q.retrieved_at_utc END) DESC,e.source_url,e.page_sha256) AS source_rank
 FROM embedded_model_snapshots e
 LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=e.source_url AND t.page_sha256=e.page_sha256
 LEFT JOIN crawl_queue q ON q.url=e.source_url
 LEFT JOIN page_archive p ON p.url=e.source_url
) WHERE source_rank=1;
CREATE VIEW embedded_model_leaves AS
SELECT d.source_url,d.page_sha256,d.model_id,d.model_slug,d.model_name,d.effort,
j.fullkey AS json_path,j.type AS value_type,j.atom AS value
FROM embedded_model_snapshots d,json_tree(d.model_json) j
WHERE j.type IN ('integer','real','text','true','false','null');
CREATE VIEW embedded_model_metrics AS
SELECT d.source_url,d.page_sha256,d.model_id,d.model_slug,d.model_name,d.effort,j.key AS metric_key,j.value AS value,j.type AS value_type
FROM embedded_model_snapshots d,json_each(d.model_json) j
WHERE j.type IN ('integer','real','null');
CREATE VIEW embedded_registry_scores AS
SELECT e.source_url,e.page_sha256,e.model_id,e.model_slug,e.model_name,e.effort,
r.evaluation_slug,r.score_field,r.source_sha256 AS registry_sha256,
json_extract(e.model_json,'$.'||r.score_field) score
FROM embedded_model_snapshots e CROSS JOIN benchmark_registry r
WHERE json_extract(e.model_json,'$.'||r.score_field) IS NOT NULL;
CREATE VIEW embedded_verified_scores AS
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
CREATE VIEW evaluation_page_leaf_facts AS
SELECT e.source_url,e.page_sha256,e.model_id,e.model_slug,e.model_name,e.effort,
j.fullkey AS json_path,j.type AS value_type,j.atom AS value
FROM evaluation_page_models e,json_tree(e.model_json) j
WHERE j.type IN ('integer','real','text','true','false','null');
CREATE VIEW evaluation_page_metrics AS
SELECT e.source_url,e.page_sha256,e.model_id,e.model_slug,e.model_name,e.effort,j.key AS metric_key,j.value AS value,j.type AS value_type
FROM evaluation_page_models e, json_each(e.model_json) j WHERE j.type IN ('integer','real','null');
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
CREATE VIEW harvey_costs_with_source AS SELECT o.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.page_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc FROM harvey_exact_task_costs o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.page_sha256 LEFT JOIN page_archive p ON p.url=o.source_url LEFT JOIN crawl_queue q ON q.url=o.source_url;
CREATE VIEW image_endpoint_records AS SELECT * FROM latest_media_endpoints WHERE modality='image';
CREATE VIEW image_host_model_latest_observations AS SELECT * FROM (
 SELECT o.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.source_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc,
 ROW_NUMBER() OVER (PARTITION BY o.host_model_id ORDER BY coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.source_sha256 THEN q.retrieved_at_utc END) DESC,o.source_url) source_rank
 FROM image_host_model_observations o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.source_sha256 LEFT JOIN crawl_queue q ON q.url=o.source_url LEFT JOIN page_archive p ON p.url=o.source_url
) WHERE source_rank=1;
CREATE VIEW latest_combined_benchmark_scores AS
SELECT source_url,page_sha256,retrieved_at_utc,model_id,model_slug,model_name,effort,evaluation_slug,score_field,registry_sha256,score FROM (
 SELECT v.*,ROW_NUMBER() OVER (PARTITION BY model_id,evaluation_slug ORDER BY retrieved_at_utc DESC,source_url) AS source_rank FROM (
  SELECT source_url,page_sha256,retrieved_at_utc,model_id,model_slug,model_name,effort,evaluation_slug,score_field,registry_sha256,score FROM combined_latest_benchmark_scores
  UNION ALL
  SELECT p.source_url,p.page_sha256,coalesce(t.retrieved_at_utc,CASE WHEN a.sha256=p.page_sha256 THEN q.retrieved_at_utc END),p.model_id,p.model_slug,p.model_name,p.effort,p.evaluation_slug,p.score_field,p.registry_sha256,p.score
  FROM registry_benchmark_scores p LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=p.source_url AND t.page_sha256=p.page_sha256 LEFT JOIN crawl_queue q ON q.url=p.source_url LEFT JOIN page_archive a ON a.url=p.source_url
 ) v
) WHERE source_rank=1;
CREATE VIEW latest_index_benchmark_results AS
SELECT e.source_url,e.page_sha256,e.retrieved_at_utc,e.model_id,e.model_slug,e.model_name,e.effort,
json_extract(x.value,'$.slug') evaluation_slug,json_extract(x.value,'$.score') score,
json_extract(x.value,'$.costPerTask') cost_per_task_usd_inferred,
json_extract(x.value,'$.timePerTask') time_per_task_seconds_inferred,
json_extract(x.value,'$.timePerTask')/60.0 time_per_task_minutes_inferred,
json_extract(x.value,'$.outputTokensPerTask') output_tokens_per_task,x.value result_json
FROM embedded_latest_models e,json_each(e.model_json,'$.intelligenceIndexEvaluations') x;
CREATE VIEW latest_media_endpoints AS SELECT * FROM (
 SELECT e.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=e.page_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc,
 ROW_NUMBER() OVER (PARTITION BY e.modality,e.endpoint_id ORDER BY coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=e.page_sha256 THEN q.retrieved_at_utc END) DESC,e.source_url) source_rank
 FROM media_endpoint_records e LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=e.source_url AND t.page_sha256=e.page_sha256 LEFT JOIN crawl_queue q ON q.url=e.source_url LEFT JOIN page_archive p ON p.url=e.source_url
) WHERE source_rank=1;
CREATE VIEW latest_model_facts AS
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
CREATE VIEW latest_provider_endpoints AS
SELECT * FROM (SELECT p.*,coalesce(t.retrieved_at_utc,CASE WHEN a.sha256=p.page_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc,
ROW_NUMBER() OVER (PARTITION BY p.endpoint_id,p.array_kind ORDER BY coalesce(t.retrieved_at_utc,CASE WHEN a.sha256=p.page_sha256 THEN q.retrieved_at_utc END) DESC,p.source_url) AS source_rank
FROM provider_endpoint_records p LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=p.source_url AND t.page_sha256=p.page_sha256 LEFT JOIN crawl_queue q ON q.url=p.source_url LEFT JOIN page_archive a ON a.url=p.source_url) WHERE source_rank=1;
CREATE VIEW latest_registry_benchmark_scores AS
SELECT e.source_url,e.page_sha256,e.retrieved_at_utc,e.model_id,e.model_slug,e.model_name,e.effort,
r.evaluation_slug,r.score_field,r.source_sha256 registry_sha256,json_extract(e.model_json,'$.'||r.score_field) score
FROM embedded_latest_models e CROSS JOIN benchmark_registry r
WHERE json_extract(e.model_json,'$.'||r.score_field) IS NOT NULL;
CREATE VIEW latest_search_api_observations AS
SELECT * FROM (
 SELECT s.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=s.page_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc,
 ROW_NUMBER() OVER (PARTITION BY s.provider_variant ORDER BY coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=s.page_sha256 THEN q.retrieved_at_utc END) DESC,s.source_url) source_rank
 FROM search_api_observations s LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=s.source_url AND t.page_sha256=s.page_sha256 LEFT JOIN crawl_queue q ON q.url=s.source_url LEFT JOIN page_archive p ON p.url=s.source_url
) WHERE source_rank=1;
CREATE VIEW latest_verified_field_aliases AS
WITH aliases(evaluation_slug,json_path) AS (VALUES
('itbench-aa','$.itBenchSre'),('aa-briefcase','$.briefcaseBreakdown.overall.elo'))
SELECT e.source_url,e.page_sha256,e.retrieved_at_utc,e.model_id,e.model_slug,e.model_name,e.effort,
a.evaluation_slug,a.json_path AS score_field,r.source_sha256 AS registry_sha256,
json_extract(e.model_json,a.json_path) AS score
FROM embedded_latest_models e CROSS JOIN aliases a
JOIN benchmark_registry r ON r.evaluation_slug=a.evaluation_slug
WHERE json_extract(e.model_json,a.json_path) IS NOT NULL
AND NOT EXISTS (SELECT 1 FROM latest_registry_benchmark_scores x WHERE x.model_id=e.model_id AND x.evaluation_slug=a.evaluation_slug);
CREATE VIEW media_arena_observations_with_source AS SELECT o.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.source_sha256 THEN q.retrieved_at_utc END) AS retrieved_at_utc FROM media_arena_observations o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.source_sha256 LEFT JOIN page_archive p ON p.url=o.source_url LEFT JOIN crawl_queue q ON q.url=o.source_url;
CREATE VIEW media_endpoint_leaves AS SELECT e.source_url,e.page_sha256,e.modality,e.endpoint_id,e.provider_slug,e.model_slug,j.fullkey AS json_path,j.type AS value_type,j.atom AS value FROM media_endpoint_records e,json_tree(e.raw_json) j WHERE j.type IN ('integer','real','text','true','false','null');
CREATE VIEW media_endpoint_normalized_prices AS
SELECT source_url,page_sha256,retrieved_at_utc,modality,endpoint_id,endpoint_slug,endpoint_name,
provider_id,provider_slug,provider_name,model_id,model_slug,model_name,
price_per_1000_images_usd,price_per_1000_images_usd/1000.0 AS price_per_generated_image_usd,
video_price_usd_per_minute,video_price_usd_per_minute/60.0 AS price_per_generated_video_second_usd,
tts_price_usd_per_million_chars,tts_price_usd_per_million_chars/1000000.0 AS price_per_text_character_usd,
median_generation_seconds,median_chars_per_second,time_percentiles_consistent
FROM latest_media_endpoints;
CREATE VIEW model_benchmark_availability AS
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
CREATE VIEW model_efforts AS
SELECT model_id,CASE WHEN count(DISTINCT effort)=1 THEN min(effort) ELSE NULL END AS effort
FROM model_details GROUP BY model_id;
CREATE VIEW model_image_input_prices AS
SELECT source_url,page_sha256,retrieved_at_utc,model_id,model_slug,model_name,effort,
json_extract(model_json,'$.creator.name') AS model_creator_name,
json_extract(model_json,'$.priceDataSource.providerName') AS pricing_provider_name,
json_extract(model_json,'$.pricePer1k1mpImages') AS input_price_usd_per_1000_1mp_images,
json_extract(model_json,'$.pricePer1k1mpImages')/1000.0 AS input_price_usd_per_1mp_image_inferred
FROM embedded_latest_models WHERE json_type(model_json,'$.pricePer1k1mpImages') IN ('real','integer');
CREATE VIEW model_index_total_cost_components AS
SELECT m.source_url,m.page_sha256,m.retrieved_at_utc,m.model_id,m.model_slug,m.model_name,m.effort,
m.pricing_provider_name,j.key AS cost_component,j.value AS amount_usd
FROM model_index_total_costs m,json_each(m.source_cost_json) j WHERE j.type IN ('integer','real','null');
CREATE VIEW model_index_total_costs AS
SELECT source_url,page_sha256,retrieved_at_utc,model_id,model_slug,model_name,effort,
json_extract(model_json,'$.creator.name') model_creator_name,
json_extract(model_json,'$.priceDataSource.providerName') pricing_provider_name,
json_extract(model_json,'$.intelligenceIndexCost.total') index_total_cost_usd,
json_extract(model_json,'$.intelligenceIndexCostPerTask.cost.total') index_cost_per_task_usd,
json_extract(model_json,'$.intelligenceIndexCost') source_cost_json
FROM embedded_latest_models WHERE json_type(model_json,'$.intelligenceIndexCost.total') IN ('integer','real');
CREATE VIEW model_metrics AS
SELECT d.source_url,d.page_sha256,d.model_id,d.slug,d.name,d.effort,j.key AS metric_key,j.value AS value,j.type AS value_type
FROM model_details d, json_each(d.model_json) j
WHERE j.type IN ('integer','real','null');
CREATE VIEW provider_cache_metrics AS
SELECT e.source_url,e.page_sha256,e.retrieved_at_utc,e.endpoint_id,e.endpoint_slug,e.host_id,e.host_slug,e.host_name,e.model_id,e.model_slug,e.model_name,
e.cache_hit_usd_per_1m,e.cache_write_usd_per_1m,
json_extract(e.raw_json,'$.pricing.cacheHitRate') AS observed_cache_hit_rate_fraction,
json_extract(e.raw_json,'$.pricing.cacheHitDiscountPercent') AS cache_hit_discount_fraction
FROM latest_provider_endpoints e WHERE e.array_kind='hostModels';
CREATE VIEW provider_endpoint_cost_components AS
SELECT e.source_url,e.page_sha256,e.retrieved_at_utc,e.endpoint_id,e.endpoint_slug,e.host_id,e.host_slug,e.host_name,e.model_id,e.model_slug,e.model_name,
c.key AS component,c.value AS amount_usd_per_index_task
FROM latest_provider_endpoints e,json_each(e.raw_json,'$.intelligenceIndexCostPerTask') c
WHERE e.array_kind='hostModels' AND c.type IN ('real','integer','null');
CREATE VIEW provider_endpoint_id_conflicts AS
SELECT endpoint_id,COUNT(DISTINCT host_id) host_id_count,COUNT(DISTINCT model_id) model_id_count,
GROUP_CONCAT(DISTINCT host_id) observed_host_ids,GROUP_CONCAT(DISTINCT model_id) observed_model_ids
FROM provider_endpoint_records GROUP BY endpoint_id HAVING COUNT(DISTINCT host_id)>1 OR COUNT(DISTINCT model_id)>1;
CREATE VIEW provider_endpoint_id_evidence AS
SELECT endpoint_id,
CASE WHEN COUNT(DISTINCT host_id)=1 THEN MIN(host_id) END AS evidence_host_id,
CASE WHEN COUNT(DISTINCT model_id)=1 THEN MIN(model_id) END AS evidence_model_id,
COUNT(DISTINCT host_id) AS host_id_count,COUNT(DISTINCT model_id) AS model_id_count,
COUNT(DISTINCT CASE WHEN host_id IS NOT NULL THEN source_url END) AS host_evidence_source_count,
COUNT(DISTINCT CASE WHEN model_id IS NOT NULL THEN source_url END) AS model_evidence_source_count
FROM provider_endpoint_records GROUP BY endpoint_id;
CREATE VIEW provider_endpoint_id_linked AS
SELECT e.*,ev.evidence_host_id AS linked_provider_id,ev.evidence_model_id AS linked_model_id,
ev.host_id_count,ev.model_id_count,ev.host_evidence_source_count,ev.model_evidence_source_count
FROM latest_provider_endpoints e LEFT JOIN provider_endpoint_id_evidence ev ON ev.endpoint_id=e.endpoint_id;
CREATE VIEW provider_endpoint_multiturn AS
SELECT e.source_url,e.page_sha256,e.retrieved_at_utc,e.endpoint_id,e.endpoint_slug,e.host_id,e.host_slug,e.host_name,e.model_id,e.model_slug,e.model_name,
json_extract(e.raw_json,'$.multiTurn.outputSpeed') AS output_tokens_per_second,
json_extract(e.raw_json,'$.multiTurn.timeToFirstToken') AS time_to_first_token_seconds,
json_extract(e.raw_json,'$.multiTurn') AS raw_multiturn_json
FROM latest_provider_endpoints e WHERE e.array_kind='hostModels' AND json_type(e.raw_json,'$.multiTurn')='object';
CREATE VIEW provider_endpoint_workloads AS
SELECT e.source_url,e.page_sha256,e.retrieved_at_utc,e.endpoint_id,e.endpoint_slug,e.host_id,e.host_slug,e.host_name,e.model_id,e.model_slug,e.model_name,
w.key AS workload_key,json_extract(w.value,'$.outputSpeed') AS output_tokens_per_second,
json_extract(w.value,'$.timeToFirstToken') AS time_to_first_token_seconds,w.value AS raw_workload_json
FROM latest_provider_endpoints e,json_each(e.raw_json,'$.workloads') w WHERE e.array_kind='hostModels';
CREATE VIEW provider_endpoints_enriched AS SELECT p.*,coalesce(p.model_name,m.model_name) resolved_model_name,x.price_conflict,x.hostmodels_input,x.hostmodels_output,x.rows_input,x.rows_output FROM provider_endpoint_id_linked p LEFT JOIN embedded_latest_models m ON m.model_id=coalesce(p.model_id,p.linked_model_id) LEFT JOIN provider_price_array_conflicts x ON x.source_url=p.source_url AND x.page_sha256=p.page_sha256 AND x.endpoint_id=p.endpoint_id;
CREATE VIEW provider_id_slug_conflicts AS
SELECT provider_id,COUNT(DISTINCT provider_slug) AS slug_count,GROUP_CONCAT(DISTINCT provider_slug) AS observed_slugs
FROM provider_identity_evidence GROUP BY provider_id HAVING COUNT(DISTINCT provider_slug)>1;
CREATE VIEW provider_identities AS
SELECT provider_slug,MIN(provider_id) AS provider_id,GROUP_CONCAT(DISTINCT observed_name) AS observed_names,
GROUP_CONCAT(DISTINCT modality) AS observed_modalities,COUNT(DISTINCT endpoint_id) AS observed_endpoint_count,
COUNT(DISTINCT source_url) AS observed_source_count,MAX(retrieved_at_utc) AS latest_retrieved_at_utc
FROM provider_identity_evidence e WHERE NOT EXISTS (SELECT 1 FROM provider_slug_identity_conflicts c WHERE c.provider_slug=e.provider_slug)
AND NOT EXISTS (SELECT 1 FROM provider_id_slug_conflicts c WHERE c.provider_id=e.provider_id)
GROUP BY provider_slug;
CREATE VIEW provider_identity_evidence AS
SELECT 'language' AS modality,e.host_id AS provider_id,e.host_slug AS provider_slug,e.host_name AS observed_name,
e.source_url,e.page_sha256,e.retrieved_at_utc,e.endpoint_id
FROM latest_provider_endpoints e WHERE e.host_id IS NOT NULL AND e.host_slug IS NOT NULL
UNION ALL
SELECT e.modality,e.provider_id,e.provider_slug,e.provider_name,e.source_url,e.page_sha256,e.retrieved_at_utc,e.endpoint_id
FROM latest_media_endpoints e WHERE e.provider_id IS NOT NULL AND e.provider_slug IS NOT NULL;
CREATE VIEW provider_observations_with_source AS SELECT o.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.page_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc FROM all_provider_observations o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.page_sha256 LEFT JOIN page_archive p ON p.url=o.source_url LEFT JOIN crawl_queue q ON q.url=o.source_url;
CREATE VIEW provider_price_array_conflicts AS
SELECT source_url,page_sha256,endpoint_id,
max(CASE WHEN array_kind='hostModels' THEN price_1m_input_usd END) hostmodels_input,
max(CASE WHEN array_kind='hostModels' THEN price_1m_output_usd END) hostmodels_output,
max(CASE WHEN array_kind='rows' THEN price_1m_input_usd END) rows_input,
max(CASE WHEN array_kind='rows' THEN price_1m_output_usd END) rows_output,
CASE WHEN count(distinct array_kind)=2 AND count(price_1m_input_usd)=2 AND count(price_1m_output_usd)=2
THEN CASE WHEN min(price_1m_input_usd)<>max(price_1m_input_usd) OR min(price_1m_output_usd)<>max(price_1m_output_usd) THEN 1 ELSE 0 END ELSE NULL END price_conflict
FROM provider_endpoint_records GROUP BY source_url,page_sha256,endpoint_id;
CREATE VIEW provider_price_scenarios AS
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
CREATE VIEW provider_slug_identity_conflicts AS
SELECT provider_slug,COUNT(DISTINCT provider_id) AS id_count,GROUP_CONCAT(DISTINCT provider_id) AS observed_ids
FROM provider_identity_evidence GROUP BY provider_slug HAVING COUNT(DISTINCT provider_id)>1;
CREATE VIEW provider_tier_validation AS
SELECT t.source_url,t.page_sha256,t.endpoint_id,t.host_slug,t.model_slug,
t.input_price_per_million AS footnote_base_input,t.output_price_per_million AS footnote_base_output,
e.price_1m_input_usd AS endpoint_input,e.price_1m_output_usd AS endpoint_output,
CASE WHEN t.input_price_per_million IS NULL OR t.output_price_per_million IS NULL OR e.price_1m_input_usd IS NULL OR e.price_1m_output_usd IS NULL THEN NULL
WHEN abs(t.input_price_per_million-e.price_1m_input_usd)<0.000001 AND abs(t.output_price_per_million-e.price_1m_output_usd)<0.000001 THEN 1 ELSE 0 END AS base_price_matches
FROM provider_tiered_pricing t JOIN latest_provider_endpoints e ON e.endpoint_id=t.endpoint_id AND e.source_url=t.source_url AND e.array_kind='rows'
WHERE t.tier_number=1;
CREATE VIEW provider_tiered_pricing_with_source AS SELECT o.*,v.endpoint_input standard_input_usd_per_million,v.endpoint_output standard_output_usd_per_million,v.base_price_matches,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.page_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc FROM provider_tiered_pricing o LEFT JOIN provider_tier_validation v ON v.source_url=o.source_url AND v.page_sha256=o.page_sha256 AND v.endpoint_id=o.endpoint_id LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.page_sha256 LEFT JOIN page_archive p ON p.url=o.source_url LEFT JOIN crawl_queue q ON q.url=o.source_url;
CREATE VIEW registry_benchmark_scores AS
SELECT e.source_url,e.page_sha256,e.model_id,e.model_slug,e.model_name,coalesce(e.effort,d.effort) effort,
r.evaluation_slug,r.score_field,r.source_sha256 registry_sha256,json_extract(e.model_json,'$.'||r.score_field) score
FROM evaluation_page_models e JOIN benchmark_registry r ON e.source_url='https://artificialanalysis.ai/evaluations/'||r.evaluation_slug
LEFT JOIN model_efforts d ON d.model_id=e.model_id
WHERE json_extract(e.model_json,'$.'||r.score_field) IS NOT NULL;
CREATE VIEW search_agent_benchmark_scores AS
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
CREATE VIEW search_agent_details_with_source AS SELECT o.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.source_sha256 THEN q.retrieved_at_utc END) AS retrieved_at_utc FROM search_agent_details o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.source_sha256 LEFT JOIN page_archive p ON p.url=o.source_url LEFT JOIN crawl_queue q ON q.url=o.source_url;
CREATE VIEW speech_agent_arena_results_with_source AS SELECT o.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.source_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc FROM speech_agent_arena_results o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.source_sha256 LEFT JOIN page_archive p ON p.url=o.source_url LEFT JOIN crawl_queue q ON q.url=o.source_url;
CREATE VIEW speech_agent_benchmark_observations AS
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
CREATE VIEW speech_agent_benchmark_observations_with_source AS SELECT o.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.source_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc FROM speech_agent_benchmark_observations o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.source_sha256 LEFT JOIN page_archive p ON p.url=o.source_url LEFT JOIN crawl_queue q ON q.url=o.source_url;
CREATE VIEW speech_to_speech_observations_with_source AS SELECT o.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.source_sha256 THEN q.retrieved_at_utc END) AS retrieved_at_utc FROM speech_to_speech_observations o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.source_sha256 LEFT JOIN page_archive p ON p.url=o.source_url LEFT JOIN crawl_queue q ON q.url=o.source_url;
CREATE VIEW speech_to_text_observations_with_source AS SELECT o.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.source_sha256 THEN q.retrieved_at_utc END) AS retrieved_at_utc FROM speech_to_text_observations o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.source_sha256 LEFT JOIN page_archive p ON p.url=o.source_url LEFT JOIN crawl_queue q ON q.url=o.source_url;
CREATE VIEW streaming_speech_benchmark_results AS
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
CREATE VIEW streaming_speech_observations_with_source AS SELECT o.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.source_sha256 THEN q.retrieved_at_utc END) AS retrieved_at_utc FROM streaming_speech_observations o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.source_sha256 LEFT JOIN page_archive p ON p.url=o.source_url LEFT JOIN crawl_queue q ON q.url=o.source_url;
CREATE VIEW tts_arena_observations_with_source AS SELECT o.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.source_sha256 THEN q.retrieved_at_utc END) AS retrieved_at_utc FROM tts_arena_observations o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.source_sha256 LEFT JOIN page_archive p ON p.url=o.source_url LEFT JOIN crawl_queue q ON q.url=o.source_url;
CREATE VIEW tts_endpoint_display AS SELECT e.*,t.median_chars_per_second AS throughput_median_characters_per_second,t.p05_characters_per_second AS throughput_p05_characters_per_second,t.p95_characters_per_second AS throughput_p95_characters_per_second FROM tts_endpoint_records e LEFT JOIN tts_throughput_percentiles t ON t.endpoint_id=e.endpoint_id AND t.source_url=e.source_url AND t.page_sha256=e.page_sha256;
CREATE VIEW tts_endpoint_records AS SELECT * FROM latest_media_endpoints WHERE modality='text-to-speech';
CREATE VIEW tts_throughput_percentiles AS SELECT e.source_url,e.page_sha256,e.endpoint_id,e.endpoint_name,e.provider_name,e.model_name,e.median_chars_per_second,e.p05_generation_seconds AS p05_characters_per_second,e.p25_generation_seconds AS p25_characters_per_second,e.p75_generation_seconds AS p75_characters_per_second,e.p95_generation_seconds AS p95_characters_per_second,e.median_generation_seconds,e.time_percentiles_consistent FROM latest_media_endpoints e WHERE e.modality='text-to-speech';
CREATE VIEW vials_estimated_time_per_task AS
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
CREATE VIEW vials_estimated_time_with_source AS SELECT o.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.page_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc FROM vials_estimated_time_per_task o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.page_sha256 LEFT JOIN page_archive p ON p.url=o.source_url LEFT JOIN crawl_queue q ON q.url=o.source_url;
CREATE VIEW video_endpoint_records AS SELECT * FROM latest_media_endpoints WHERE modality='video';
CREATE VIEW video_host_model_latest_observations AS SELECT * FROM (
 SELECT o.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.source_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc,
 ROW_NUMBER() OVER (PARTITION BY o.host_model_id ORDER BY coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=o.source_sha256 THEN q.retrieved_at_utc END) DESC,o.source_url) source_rank
 FROM video_host_model_observations o LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=o.source_url AND t.page_sha256=o.source_sha256 LEFT JOIN crawl_queue q ON q.url=o.source_url LEFT JOIN page_archive p ON p.url=o.source_url
) WHERE source_rank=1;
COMMIT;
