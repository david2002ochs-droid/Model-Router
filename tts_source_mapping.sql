-- The archived application bundle in media_mapping_sources labels the following
-- TTS fields as throughput (characters per second), despite their field names.
CREATE VIEW IF NOT EXISTS tts_throughput_percentiles AS
SELECT e.source_url,e.page_sha256,e.endpoint_id,e.endpoint_name,e.provider_name,e.model_name,
e.median_chars_per_second,e.p05_generation_seconds AS p05_characters_per_second,
e.p25_generation_seconds AS p25_characters_per_second,e.p75_generation_seconds AS p75_characters_per_second,
e.p95_generation_seconds AS p95_characters_per_second,e.median_generation_seconds,e.time_percentiles_consistent
FROM latest_media_endpoints e WHERE e.modality='text-to-speech';
