-- Stable endpoint UUID linkage only. No name-based or slug-based identity fusion.
CREATE VIEW IF NOT EXISTS provider_endpoint_id_conflicts AS
SELECT endpoint_id,COUNT(DISTINCT host_id) host_id_count,COUNT(DISTINCT model_id) model_id_count,
GROUP_CONCAT(DISTINCT host_id) observed_host_ids,GROUP_CONCAT(DISTINCT model_id) observed_model_ids
FROM provider_endpoint_records GROUP BY endpoint_id HAVING COUNT(DISTINCT host_id)>1 OR COUNT(DISTINCT model_id)>1;
CREATE VIEW IF NOT EXISTS provider_endpoint_id_evidence AS
SELECT endpoint_id,
CASE WHEN COUNT(DISTINCT host_id)=1 THEN MIN(host_id) END AS evidence_host_id,
CASE WHEN COUNT(DISTINCT model_id)=1 THEN MIN(model_id) END AS evidence_model_id,
COUNT(DISTINCT host_id) AS host_id_count,COUNT(DISTINCT model_id) AS model_id_count,
COUNT(DISTINCT CASE WHEN host_id IS NOT NULL THEN source_url END) AS host_evidence_source_count,
COUNT(DISTINCT CASE WHEN model_id IS NOT NULL THEN source_url END) AS model_evidence_source_count
FROM provider_endpoint_records GROUP BY endpoint_id;
CREATE VIEW IF NOT EXISTS provider_endpoint_id_linked AS
SELECT e.*,ev.evidence_host_id AS linked_provider_id,ev.evidence_model_id AS linked_model_id,
ev.host_id_count,ev.model_id_count,ev.host_evidence_source_count,ev.model_evidence_source_count
FROM latest_provider_endpoints e LEFT JOIN provider_endpoint_id_evidence ev ON ev.endpoint_id=e.endpoint_id;
