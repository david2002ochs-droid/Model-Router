-- Provider identifiers remain tied to the originating endpoints and source snapshots.
CREATE VIEW IF NOT EXISTS provider_identity_evidence AS
SELECT 'language' AS modality,e.host_id AS provider_id,e.host_slug AS provider_slug,e.host_name AS observed_name,
e.source_url,e.page_sha256,e.retrieved_at_utc,e.endpoint_id
FROM latest_provider_endpoints e WHERE e.host_id IS NOT NULL AND e.host_slug IS NOT NULL
UNION ALL
SELECT e.modality,e.provider_id,e.provider_slug,e.provider_name,e.source_url,e.page_sha256,e.retrieved_at_utc,e.endpoint_id
FROM latest_media_endpoints e WHERE e.provider_id IS NOT NULL AND e.provider_slug IS NOT NULL;
CREATE VIEW IF NOT EXISTS provider_slug_identity_conflicts AS
SELECT provider_slug,COUNT(DISTINCT provider_id) AS id_count,GROUP_CONCAT(DISTINCT provider_id) AS observed_ids
FROM provider_identity_evidence GROUP BY provider_slug HAVING COUNT(DISTINCT provider_id)>1;
CREATE VIEW IF NOT EXISTS provider_id_slug_conflicts AS
SELECT provider_id,COUNT(DISTINCT provider_slug) AS slug_count,GROUP_CONCAT(DISTINCT provider_slug) AS observed_slugs
FROM provider_identity_evidence GROUP BY provider_id HAVING COUNT(DISTINCT provider_slug)>1;
CREATE VIEW IF NOT EXISTS provider_identities AS
SELECT provider_slug,MIN(provider_id) AS provider_id,GROUP_CONCAT(DISTINCT observed_name) AS observed_names,
GROUP_CONCAT(DISTINCT modality) AS observed_modalities,COUNT(DISTINCT endpoint_id) AS observed_endpoint_count,
COUNT(DISTINCT source_url) AS observed_source_count,MAX(retrieved_at_utc) AS latest_retrieved_at_utc
FROM provider_identity_evidence e WHERE NOT EXISTS (SELECT 1 FROM provider_slug_identity_conflicts c WHERE c.provider_slug=e.provider_slug)
AND NOT EXISTS (SELECT 1 FROM provider_id_slug_conflicts c WHERE c.provider_id=e.provider_id)
GROUP BY provider_slug;
