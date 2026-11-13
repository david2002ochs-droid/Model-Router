#!/usr/bin/env python3
"""Read-only local browser for the collected SQLite observations."""
import csv,html,io,sqlite3,urllib.parse
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
DB=Path(__file__).with_name('artificial_analysis.sqlite3')
VIEWS={
 'kosten_luecken':('Benchmark-Kosten – Datenlücken','benchmark_cost_gaps_with_source',['model_name','effort','benchmark_slug','input_or_output_price_missing','cache_hit_rate_missing','required_tokens_missing','retrieved_at_utc','page_sha256','source_url']),
 'benchmark_abdeckung':('Benchmark-Datenverfügbarkeit','model_benchmark_availability',['evaluation_slug','model_score_count','models_with_index_component_cost','models_with_index_component_time','models_with_cost_estimate','models_with_time_estimate']),
 'index_gesamtkosten':('Intelligence Index – Gesamtkosten','model_index_total_costs',['model_name','effort','model_creator_name','pricing_provider_name','index_total_cost_usd','index_cost_per_task_usd','retrieved_at_utc','page_sha256','source_url']),
 'chat_plaene':('Chatbot-Abos pro Monat','chatbot_plans_with_source',['creator_name','plan_name','tier','monthly_price_usd','monthly_price_notes','model_name','intelligence_index','feature_score','retrieved_at_utc','page_sha256','source_url']),
 'cache_tabelle':('Cachepreise – Quelltabelle','cache_pricing_rows_with_source',['provider_group_raw','model_name','input_usd_per_million','cache_write_usd_per_million','cache_hit_usd_per_million','cache_storage_raw','output_usd_per_million','min_tokens_raw','cache_ttl_raw','notes_raw','retrieved_at_utc','page_sha256','source_url']),
 'harvey':('Harvey-LAB-AA – Aufgabenkosten','harvey_costs_with_source',['creator_name','model_name','gated_all_pass_fraction','criterion_pass_fraction','material_hallucinations_per_task','cost_per_task_usd','retrieved_at_utc','page_sha256','source_url']),
 'benchmark_kosten_zeit':('Benchmark-Kosten und Zeiten – Schätzungen','benchmark_cost_time_with_source',['model_name','effort','benchmark_slug','task_count','score_raw','estimated_cost_usd_per_task','estimated_seconds_per_task','fallback_applied','cache_read_input_price_substituted','cache_write_input_price_substituted','has_tool_time','source_tool_component_complete','retrieved_at_utc','page_sha256','source_url']),
 'benchmark_kosten_schaetzung':('Benchmark-Kostenschätzungen','benchmark_cost_estimates_with_source',['model_name','effort','benchmark_slug','estimated_cost_usd_per_task','noncache_input_cost_usd_per_task','cache_read_cost_usd_per_task','cache_write_cost_usd_per_task','reasoning_cost_usd_per_task','answer_cost_usd_per_task','fallback_applied','cache_read_input_price_substituted','cache_write_input_price_substituted','retrieved_at_utc','source_sha256','source_url']),
 'benchmark_zeit_schaetzung':('Benchmark-Zeitschätzungen','benchmark_time_estimates_with_source',['model_name','effort','benchmark_slug','task_count','estimated_seconds_per_task','estimated_generation_seconds_per_task','mean_tool_ms_per_task','has_tool_time','source_tool_component_complete','retrieved_at_utc','page_sha256','source_url']),
 'agent_schaetzungen':('Agent-Benchmarks – Zeitschätzungen','agentic_estimates_with_source',['model_name','effort','benchmark_slug','benchmark_task_count','estimated_total_seconds_per_task','estimated_generation_seconds_per_task','mean_tool_ms_per_task','tool_time_available','retrieved_at_utc','page_sha256','source_url']),
 'vials':('VIALS-AA – geschätzte Aufgabenzeit','vials_estimated_time_with_source',['model_name','effort','score_raw','estimated_seconds_per_task','estimated_generation_seconds_per_task','mean_tool_ms_per_attempt','output_speed_tokens_per_second','tool_time_available','retrieved_at_utc','page_sha256','source_url']),
 'preis_staffeln':('Provider-Preisstaffeln','provider_tiered_pricing_with_source',['host_slug','model_slug','endpoint_id','threshold_raw','input_price_raw','output_price_raw','input_price_per_million','output_price_per_million','standard_input_usd_per_million','standard_output_usd_per_million','base_price_matches','amount_parse_warning','footnote_text','retrieved_at_utc','page_sha256','source_url']),
 'decision':('Decision-Benchmarks pro Aufgabe','decision_dataset_results_with_source',['contestant_name','contestant_kind','host_name','dataset_slug','decision_or_symmetry_score_0_to_100','cost_usd_per_task','median_time_seconds_per_task','brier','retrieved_at_utc','source_sha256','source_url']),
 'bild_input':('Bild-Eingabepreise für Sprachmodelle','model_image_input_prices',['model_name','effort','model_creator_name','pricing_provider_name','input_price_usd_per_1000_1mp_images','input_price_usd_per_1mp_image_inferred','retrieved_at_utc','page_sha256','source_url']),
 'preis_szenarien':('Provider-Mischpreise','provider_price_scenarios',['host_name','host_slug','model_slug','endpoint_id','cache_ratio','input_ratio','output_ratio','price_usd_per_million_tokens','cache_price_absent','retrieved_at_utc','page_sha256','source_url']),
 'speech_agent_bench':('Speech-Agent Benchmarks','speech_agent_benchmark_observations_with_source',['host_name','model_name','benchmark','subcategory','score_raw','average_cost_usd_per_task','time_to_first_audio_seconds','mean_conversation_audio_seconds','retrieved_at_utc','source_sha256','source_url']),
 'speech_agent_arena':('Speech-Agent Arena','speech_agent_arena_results_with_source',['creator_name','model_name','slice_key','elo','elo_ci_low','elo_ci_high','appearances','task_completion_rate','task_completion_success_count','task_completion_failure_count','retrieved_at_utc','source_sha256','source_url']),
 'workloads':('Provider-Leistung nach Eingabegröße','provider_endpoint_workloads',['host_name','host_slug','model_slug','endpoint_id','workload_key','output_tokens_per_second','time_to_first_token_seconds','retrieved_at_utc','page_sha256','source_url']),
 'kostenbestandteile':('Index-Kostenbestandteile','provider_endpoint_cost_components',['host_name','host_slug','model_slug','endpoint_id','component','amount_usd_per_index_task','retrieved_at_utc','page_sha256','source_url']),
 'anbieter':('Provider-Verzeichnis','provider_identities',['provider_slug','provider_id','observed_names','observed_modalities','observed_endpoint_count','observed_source_count','latest_retrieved_at_utc']),
 'benchmark_details':('Benchmark-Teilwerte','benchmark_named_breakdown_with_source',['model_name','effort','benchmark_slug','detail_path','value_type','value','retrieved_at_utc','page_sha256','source_url']),
 'such_details':('Such-Agenten – Details','search_agent_details_with_source',['provider_name','provider_variant','answer_model_name','answer_model_slug','quality_index_raw','browsecomp_accuracy_raw','deepsearchqa_f1_raw','omniscience_accuracy_raw','average_task_seconds','search_time_per_task_seconds','candidate_model_time_seconds_derived','search_api_cost_usd_per_task','candidate_model_cost_usd_per_task','retrieved_at_utc','source_sha256','source_url']),
 'video_endpunkte':('Video-Provider-Endpunkte','video_endpoint_records',['provider_name','model_name','endpoint_name','video_price_usd_per_minute','median_generation_seconds','p05_generation_seconds','p95_generation_seconds','retrieved_at_utc','page_sha256','source_url']),
 'tts_endpunkte':('TTS-Provider-Endpunkte','tts_endpoint_display',['provider_name','model_name','endpoint_name','tts_price_usd_per_million_chars','median_generation_seconds','throughput_median_characters_per_second','throughput_p05_characters_per_second','throughput_p95_characters_per_second','retrieved_at_utc','page_sha256','source_url']),
 'bild_endpunkte':('Bild-Provider-Endpunkte','image_endpoint_records',['provider_name','model_name','endpoint_name','price_per_1000_images_usd','model_quality_elo','median_generation_seconds','p05_generation_seconds','p95_generation_seconds','retrieved_at_utc','page_sha256','source_url']),
 'medien':('Bild- und Video-Arena','media_arena_observations_with_source',['media_type','arena_task','category_slug','model_name','creator_name','elo','confidence_lower','confidence_upper','sample_count','price_usd_per_1000_images','price_usd_per_video_minute','retrieved_at_utc','source_sha256','source_url']),
 'tts':('Text-to-Speech Arena','tts_arena_observations_with_source',['arena_variant','rank','model_name','elo','elo_interval_low','elo_interval_high','sample_count','price_usd_per_million_characters','retrieved_at_utc','source_sha256','source_url']),
 'endpunkte':('Provider-Endpunkte','provider_endpoints_enriched',['host_name','host_slug','resolved_model_name','endpoint_id','linked_model_id','linked_provider_id','array_kind','price_conflict','hostmodels_input','hostmodels_output','rows_input','rows_output','price_1m_input_usd','price_1m_output_usd','cache_hit_usd_per_1m','cache_write_usd_per_1m','cost_per_task_usd','index_time_per_task_seconds','output_tokens_per_second','retrieved_at_utc','page_sha256','source_url']),
 'sprache':('Speech-to-Speech','speech_to_speech_observations_with_source',['provider','model','speech_to_speech_index','speech_reasoning_pct','conversational_dynamics_pct','agentic_performance_pct','task_success_pct','first_audio_seconds','cost_per_hour_input_audio_usd','retrieved_at_utc','source_sha256','source_url']),
 'transkription':('Speech-to-Text','speech_to_text_observations_with_source',['provider','model','word_error_rate_pct','median_speed_factor','price_usd_per_1000_minutes','retrieved_at_utc','source_sha256','source_url']),
 'streaming':('Streaming-Transkription','streaming_speech_observations_with_source',['host_name','model_name','aa_wer_streaming_index','aa_agenttalk_streaming_wer','voxpopuli_streaming_wer','earnings22_streaming_wer','price_per_1000_minutes','time_to_final_transcript_seconds','time_to_first_partial_transcript_seconds','retrieved_at_utc','source_sha256','source_url']),
 'modelle':('Modelle und Preise','latest_model_facts',['model_name','effort','creator_name','context_window_tokens','intelligence_index','input_price_per_million','output_price_per_million','cache_hit_price','cache_write_price','output_speed_tokens_per_second','first_answer_token_seconds','index_cost_per_task_usd_inferred','index_time_per_task_seconds_inferred','price_data_provider','retrieved_at_utc','page_sha256','source_url']),
 'benchmarks':('Benchmarks und Modelle','benchmark_scores_with_metadata',['model_name','effort','evaluation_slug','score_raw','score_display_value','score_format','task_count','retrieved_at_utc','page_sha256','source_url']),
 'index':('Benchmarkkosten und Laufzeiten','latest_index_benchmark_results',['model_name','effort','evaluation_slug','score','cost_per_task_usd_inferred','time_per_task_minutes_inferred','output_tokens_per_task','retrieved_at_utc','page_sha256','source_url']),
 'provider':('Modell-Provider','provider_observations_with_source',['model_slug','provider','table_number','row_number','cost_per_task_usd','time_per_task_minutes','endpoint_accuracy_index_percent','first_answer_token_seconds','error_rate_percent','retrieved_at_utc','page_sha256','source_url']),
 'search':('Such-APIs','latest_search_api_observations',['provider_variant','search_index','deepsearchqa_f1','browsecomp_accuracy','omniscience_accuracy','search_cost_usd_per_1000','model_cost_usd_per_1000','time_per_task_seconds','retrieved_at_utc','page_sha256','source_url']),
 'agents':('Coding-Agenten','coding_agent_display_benchmark_results',['display_agent_name','display_model_name','effort','benchmark_name','mean_reward','mean_input_tokens','mean_output_tokens','index_mix_mean_cost_usd_per_task','index_mix_mean_wall_time_seconds','retrieved_at_utc','page_sha256','source_url']),
}
LABELS={
 'input_or_output_price_missing':'Input-/Outputpreis fehlt (1 = ja)',
 'cache_hit_rate_missing':'Cache-Hit-Anteil fehlt (1 = ja)','required_tokens_missing':'Benötigte Tokenzahlen fehlen (1 = ja)',
 'model_score_count':'Modell-IDs mit Score','models_with_index_component_cost':'Davon Index-Teilkosten',
 'models_with_index_component_time':'Davon Index-Teilzeit','models_with_cost_estimate':'Davon Kostenschätzung','models_with_time_estimate':'Davon Zeitschätzung',
 'price_conflict':'Preisabweichung Quellarrays (1 = ja)','hostmodels_input':'HostModels Input (USD / Mio. Token)',
 'hostmodels_output':'HostModels Output (USD / Mio. Token)','rows_input':'Rows Input (USD / Mio. Token)','rows_output':'Rows Output (USD / Mio. Token)',
 'standard_input_usd_per_million':'Endpunkt-Inputpreis (USD / Mio.)','standard_output_usd_per_million':'Endpunkt-Outputpreis (USD / Mio.)',
 'base_price_matches':'Basisstaffel entspricht Endpunktpreis (0 = nein)',
 'host_slug':'Provider-Slug',
 'linked_model_id':'Belegte Modell-ID','linked_provider_id':'Belegte Provider-ID',
 'display_agent_name':'Agent (Quellanzeige)','display_model_name':'Modell (Quellanzeige)',
 'index_mix_mean_cost_usd_per_task':'Indexmix-Kosten (USD / Aufgabe)',
 'index_mix_mean_wall_time_seconds':'Indexmix-Laufzeit (Sek.)',
 'index_total_cost_usd':'Gesamtkosten Intelligence Index (USD)','index_cost_per_task_usd':'Indexkosten (USD / Aufgabe)',
 'plan_name':'Abo-Plan','tier':'Tarifklasse','monthly_price_usd':'Monatspreis (USD)','monthly_price_notes':'Preishinweise',
 'feature_score':'Feature-Score',
 'provider_group_raw':'Providergruppe (Quelltext)','input_usd_per_million':'Input (USD / Mio. Token)',
 'cache_write_usd_per_million':'Cache-Write (USD / Mio. Token)','cache_hit_usd_per_million':'Cache-Hit (USD / Mio. Token)',
 'output_usd_per_million':'Output (USD / Mio. Token)','cache_storage_raw':'Cache-Speicher (Original)',
 'min_tokens_raw':'Min. Token (Original)','cache_ttl_raw':'Cache-TTL (Original)','notes_raw':'Hinweise (Original)',
 'table_number':'Tabelle (Quellseite)','row_number':'Zeile (Quellseite)',
 'endpoint_accuracy_index_percent':'Endpoint Accuracy Index (% des Referenzendpunkts)',
 'gated_all_pass_fraction':'Halluzinationsbereinigtes All-Pass (Anteil)','criterion_pass_fraction':'Kriterienerfüllung (Anteil)',
 'material_hallucinations_per_task':'Materielle Halluzinationen / Aufgabe','cost_per_task_usd':'Kosten (USD / Aufgabe, Quellberechnung)',
 'cache_read_input_price_substituted':'Cache-Lesen: Inputpreis-Ersatz (1 = ja)',
 'cache_write_input_price_substituted':'Cache-Schreiben: Inputpreis-Ersatz (1 = ja)',
 'estimated_cost_usd_per_task':'Geschätzte Kosten (USD / Aufgabe)',
 'noncache_input_cost_usd_per_task':'Nicht-Cache-Input (USD / Aufgabe, geschätzt)',
 'cache_read_cost_usd_per_task':'Cache-Lesen (USD / Aufgabe, geschätzt)',
 'cache_write_cost_usd_per_task':'Cache-Schreiben (USD / Aufgabe, geschätzt)',
 'reasoning_cost_usd_per_task':'Reasoning (USD / Aufgabe, geschätzt)',
 'answer_cost_usd_per_task':'Antwort (USD / Aufgabe, geschätzt)',
 'fallback_applied':'Modell-Fallbackpreis verwendet (1 = ja)',
 'source_tool_component_complete':'Quellformel-Komponenten verfügbar (1 = ja)','has_tool_time':'Toolzeit laut Quellformel enthalten (1 = ja)',
 'benchmark_task_count':'Aufgabenzahl','estimated_total_seconds_per_task':'Geschätzte Gesamtzeit (Sek. / Aufgabe)',
 'mean_tool_ms_per_task':'Mittlere Toolzeit (Millisek. / Aufgabe)',
 'estimated_seconds_per_task':'Geschätzte Zeit (Sek. / Aufgabe)','estimated_generation_seconds_per_task':'Geschätzte Generierung (Sek. / Aufgabe)',
 'mean_tool_ms_per_attempt':'Mittlere Toolzeit (Millisek. / Versuch)','tool_time_available':'Toolzeit verfügbar (1 = ja)',
 'threshold_raw':'Schwelle (Originalwortlaut)','input_price_raw':'Inputpreis (Original)','output_price_raw':'Outputpreis (Original)',
 'amount_parse_warning':'Hinweis zur Zahl','footnote_text':'Fußnote (Original)',
 'contestant_name':'Modell / Entscheidungskonfiguration','contestant_kind':'Konfigurationstyp','dataset_slug':'Datensatz',
 'decision_or_symmetry_score_0_to_100':'Decision-/Symmetrie-Score (0–100)','cost_usd_per_task':'Kosten (USD / Aufgabe)',
 'median_time_seconds_per_task':'Medianzeit (Sek. / Aufgabe)','brier':'Brier-Score',
 'model_creator_name':'Modellhersteller','pricing_provider_name':'Preisanbieter',
 'input_price_usd_per_1000_1mp_images':'Bild-Eingabe (USD / 1.000 Bilder à 1 MP)',
 'input_price_usd_per_1mp_image_inferred':'Bild-Eingabe (USD / 1-MP-Bild, berechnet)',
 'cache_ratio':'Cache-Anteil (Verhältnis)','input_ratio':'Input-Anteil (Verhältnis)','output_ratio':'Output-Anteil (Verhältnis)',
 'price_usd_per_million_tokens':'Mischpreis (USD / Mio. Token)','cache_price_absent':'Cachepreis fehlt (1 = ja)',
 'benchmark':'Benchmark','subcategory':'Unterkategorie','average_cost_usd_per_task':'Kosten (USD / Aufgabe)',
 'time_to_first_audio_seconds':'Erstes Audio (Sek.)','mean_conversation_audio_seconds':'Mittlere Gesprächsdauer (Sek.)',
 'slice_key':'Aufgabentyp','elo_ci_low':'Elo-Intervall unten','elo_ci_high':'Elo-Intervall oben','appearances':'Bewertungen',
 'task_completion_rate':'Erfolgsrate (Anteil)','task_completion_success_count':'Erfolgreiche Aufgaben','task_completion_failure_count':'Fehlgeschlagene Aufgaben',
 'endpoint_id':'Endpunkt-ID','workload_key':'Input-Token-Klasse','time_to_first_token_seconds':'Erstes Token (Sek.)',
 'component':'Kostenbestandteil','amount_usd_per_index_task':'USD pro Index-Aufgabe',
 'provider_slug':'Provider-Slug','provider_id':'Provider-ID','observed_names':'Beobachtete Namen','observed_modalities':'Beobachtete Bereiche',
 'observed_endpoint_count':'Endpunkte','observed_source_count':'Quellseiten','latest_retrieved_at_utc':'Letzter Abruf (UTC)',
 'quality_index_raw':'Search Index (Anteil, Rohwert)','browsecomp_accuracy_raw':'BrowseComp (Anteil, Rohwert)',
 'deepsearchqa_f1_raw':'DeepSearchQA F1 (Anteil, Rohwert)','omniscience_accuracy_raw':'Omniscience (Anteil, Rohwert)',
 'throughput_median_characters_per_second':'Durchsatz Median (Zeichen / Sek.)',
 'throughput_p05_characters_per_second':'Durchsatz P05 (Zeichen / Sek.)',
 'throughput_p95_characters_per_second':'Durchsatz P95 (Zeichen / Sek.)',
 'benchmark_slug':'Benchmark','detail_path':'Originaldatenpfad','value_type':'Werttyp','value':'Wert',
 'retrieved_at_utc':'Abrufzeit (UTC)','source_sha256':'Quell-SHA-256','page_sha256':'Quell-SHA-256',
 'answer_model_name':'Antwortmodell','answer_model_slug':'Antwortmodell-Slug',
 'average_task_seconds':'Gesamtzeit (Sek. / Aufgabe)','search_time_per_task_seconds':'Suchzeit (Sek. / Aufgabe)',
 'candidate_model_time_seconds_derived':'Modellzeit (Sek. / Aufgabe, abgeleitet)',
 'search_api_cost_usd_per_task':'Suchkosten (USD / Aufgabe)','candidate_model_cost_usd_per_task':'Modellkosten (USD / Aufgabe)',
 'aa_wer_streaming_index':'AA-WER Streaming (Anteil, Rohwert)',
 'aa_agenttalk_streaming_wer':'AA-AgentTalk WER (Anteil, Rohwert)',
 'voxpopuli_streaming_wer':'VoxPopuli WER (Anteil, Rohwert)',
 'earnings22_streaming_wer':'Earnings22 WER (Anteil, Rohwert)',
 'video_price_usd_per_minute':'Preis (USD / Videominute)','tts_price_usd_per_million_chars':'Preis (USD / Mio. Zeichen)',
 'time_percentiles_consistent':'Zeitperzentile konsistent',
 'provider_name':'Provider','endpoint_name':'Endpunkt','price_per_1000_images_usd':'Preis (USD / 1.000 Bilder)',
 'model_quality_elo':'Modellqualität (Elo)','median_generation_seconds':'Median (Sek.)','p05_generation_seconds':'5. Perzentil (Sek.)','p95_generation_seconds':'95. Perzentil (Sek.)',
 'media_type':'Medium','arena_task':'Aufgabe','category_slug':'Unterkategorie','confidence_lower':'95%-Intervall unten','confidence_upper':'95%-Intervall oben',
 'price_usd_per_1000_images':'Preis (USD / 1.000 Bilder)','price_usd_per_video_minute':'Preis (USD / Videominute)',
 'arena_variant':'Arena-Variante','rank':'Rang','elo':'Elo','elo_interval_low':'Intervall unten','elo_interval_high':'Intervall oben',
 'sample_count':'Stichproben','price_usd_per_million_characters':'Preis (USD / Mio. Zeichen)',
 'resolved_model_name':'Modell (über ID ergänzt)','host_name':'API-Provider','array_kind':'Quellarray','price_1m_input_usd':'Input (USD / Mio. Token)','price_1m_output_usd':'Output (USD / Mio. Token)',
 'cache_hit_usd_per_1m':'Cache-Hit (USD / Mio. Token)','cache_write_usd_per_1m':'Cache-Write (USD / Mio. Token)',
 'index_time_per_task_seconds':'Index-Zeit (Sek. / Aufgabe)','output_tokens_per_second':'Output (Token / Sek.)',
 'model':'Modell','speech_to_speech_index':'Speech-to-Speech Index','speech_reasoning_pct':'Reasoning (%)',
 'conversational_dynamics_pct':'Konversation (%)','agentic_performance_pct':'Agentenleistung (%)','task_success_pct':'Aufgabenerfolg (%)',
 'first_audio_seconds':'Erstes Audio (Sek.)','cost_per_hour_input_audio_usd':'Audio-Kosten (USD / Stunde Input)',
 'word_error_rate_pct':'Wortfehlerrate (%)','median_speed_factor':'Median-Geschwindigkeitsfaktor','price_usd_per_1000_minutes':'Preis (USD / 1.000 Min.)',
 'price_per_1000_minutes':'Preis je 1.000 Minuten (Quellfeld)','time_to_final_transcript_seconds':'Finales Transkript (Sek.)',
 'time_to_first_partial_transcript_seconds':'Erstes Teiltranskript (Sek.)',
 'model_name':'Modell','model_slug':'Modell-Slug','effort':'Effort-Level','creator_name':'Modellhersteller',
 'context_window_tokens':'Kontext (Token)','intelligence_index':'Intelligence Index','input_price_per_million':'Input (USD / Mio. Token)',
 'output_price_per_million':'Output (USD / Mio. Token)','cache_hit_price':'Cache-Hit (USD / Mio. Token)',
 'cache_write_price':'Cache-Write (Preisfeld)','output_speed_tokens_per_second':'Output (Token / Sek.)',
 'first_answer_token_seconds':'Erstes Antworttoken (Sek.)','index_cost_per_task_usd_inferred':'Index-Kosten (USD / Aufgabe, abgeleitet)',
 'index_time_per_task_seconds_inferred':'Index-Zeit (Sek. / Aufgabe, abgeleitet)','evaluation_slug':'Benchmark',
 'score_raw':'Score (Rohwert)','score_display_value':'Score (Anzeige)','score_format':'Anzeigeformat',
 'task_count':'Aufgabenanzahl','score':'Score (Rohwert)','cost_per_task_usd_inferred':'Kosten (USD / Aufgabe, abgeleitet)',
 'time_per_task_minutes_inferred':'Zeit (Min. / Aufgabe, abgeleitet)','output_tokens_per_task':'Output (Token / Aufgabe)',
 'provider':'API-Provider','provider_variant':'Provider-Variante','cost_per_task_usd':'Kosten (USD / Aufgabe)',
 'time_per_task_minutes':'Zeit (Min. / Aufgabe)','error_rate_percent':'Fehlerrate (%)','search_index':'Search Index',
 'deepsearchqa_f1':'DeepSearchQA F1','browsecomp_accuracy':'BrowseComp Accuracy','omniscience_accuracy':'Omniscience Accuracy',
 'search_cost_usd_per_1000':'Suchkosten (USD / 1.000 Aufgaben)','model_cost_usd_per_1000':'Modellkosten (USD / 1.000 Aufgaben)',
 'time_per_task_seconds':'Zeit (Sek. / Aufgabe)','agent_name':'Agent','benchmark_name':'Benchmark',
 'mean_reward':'Mittlerer Reward','mean_input_tokens':'Mittlerer Input (Token)','mean_output_tokens':'Mittlerer Output (Token)',
 'price_data_provider':'Preisquelle','source_url':'Quelle'
}
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  p=urllib.parse.urlparse(self.path);args=urllib.parse.parse_qs(p.query);view=args.get('view',['benchmarks'])[0];view=view if view in VIEWS else 'benchmarks';label,table,cols=VIEWS[view];q=args.get('q',[''])[0][:150]
  sql='SELECT '+','.join('"'+x+'"' for x in cols)+' FROM "'+table+'"';params=[]
  if q:
   # LIKE treats user wildcards literally.
   sql+=' WHERE '+' OR '.join('CAST("'+x+'" AS TEXT) LIKE ? ESCAPE \'\\\'' for x in cols if x!='source_url');term='%'+q.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%';params=[term]*len([x for x in cols if x!='source_url'])
  if p.path!='/export.csv': sql+=' LIMIT 2000'
  try:
   with sqlite3.connect(f'file:{DB}?mode=ro',uri=True,timeout=30) as c: rows=c.execute(sql,params).fetchall()
  except sqlite3.Error as e:self.send_error(500,str(e));return
  if p.path=='/export.csv':
   out=io.StringIO(newline='');w=csv.writer(out);w.writerow(cols);w.writerows(rows);body=out.getvalue().encode('utf-8-sig');ctype='text/csv; charset=utf-8'
  elif p.path=='/':
   esc=lambda x:html.escape(str(x),quote=True)
   links=' '.join('<a class="'+('active' if k==view else '')+'" href="/?view='+esc(k)+'">'+esc(v[0])+'</a>' for k,v in VIEWS.items())
   trs=[]
   for row in rows:
    cells=[]
    for col,x in zip(cols,row):
     if x is None:v='—'
     elif isinstance(x,float):v=esc(repr(x))
     elif col=='source_url' and str(x).startswith('https://artificialanalysis.ai/'):v='<a href="'+esc(x)+'" target="_blank" rel="noreferrer">Quelle</a>'
     else:v=esc(x)
     cells.append('<td>'+v+'</td>')
    trs.append('<tr>'+''.join(cells)+'</tr>')
   export='/export.csv?'+urllib.parse.urlencode({'view':view,'q':q})
   body=('''<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>KI-Datenkatalog</title><style>body{font:15px system-ui;margin:0;color:#18243a;background:#f5f7fb}header{background:#14213c;color:white;padding:28px 4vw}h1{margin:0 0 8px}main{padding:22px 4vw}nav{display:flex;gap:8px;flex-wrap:wrap}nav a{padding:9px 13px;background:white;border:1px solid #d8e1ee;border-radius:8px;color:#253b5a;text-decoration:none}nav .active{background:#2254a3;color:white}form{display:flex;gap:8px;margin:22px 0}input{padding:10px;min-width:240px;border:1px solid #bccbe0;border-radius:6px}button,.export{padding:10px 14px;background:#2254a3;border:0;color:white;border-radius:6px;text-decoration:none}.scroll{overflow:auto;background:white;border:1px solid #d8e1ee;border-radius:8px}table{border-collapse:collapse;width:100%;white-space:nowrap}th,td{text-align:left;padding:10px 12px;border-bottom:1px solid #e7edf5}th{position:sticky;top:0;background:#edf2fa;font-size:12px;cursor:pointer}p{line-height:1.5}.note{color:#52627a}</style><header><h1>KI-Datenkatalog</h1><div>Artificial Analysis · archivierte Quellenstände</div></header><main><nav>'''+links+'</nav><h2>'+esc(label)+'</h2><form><input type="hidden" name="view" value="'+esc(view)+'"><input name="q" value="'+esc(q)+'" placeholder="Modell, Benchmark oder Provider suchen"><button>Suchen</button><a class="export" href="'+esc(export)+'">CSV</a></form><p class="note">'+str(len(rows))+' angezeigte Zeilen (höchstens 2.000). Fehlende Werte: —. Der Endpoint Accuracy Index ist relativ zu einem Referenzendpunkt und kann über 100 % liegen. Die Verfügbarkeitsübersicht zählt nur Modell-IDs mit Score aus der kombinierten Modellsicht; spezialisierte Decision-, Speech- oder Harvey-Datensätze sind dort nicht vollständig enthalten. Score-Skalen unterscheiden sich; abgeleitete Einheiten sind im Feldnamen gekennzeichnet. In der Datenlückenansicht können mehrere Gründe gleichzeitig zutreffen; weitere Fallback- oder Plausibilitätsgründe sind möglich. Benchmarkkosten in der Schätzungsansicht sind nach Quellformel und hinterlegten Preisen berechnet, keine einzelnen Rechnungsmessungen. Fehlende Cachepreise können durch den Inputpreis ersetzt werden; dies ist separat markiert. Benchmarkzeiten in der Schätzungsansicht sind aus Tokenzahlen und Ausgaberate geschätzt und keine einzelnen gemessenen Laufzeiten. Bei AA-Briefcase, MKA und VIALS kommt Toolzeit hinzu; die Verfügbarkeit aller Quellformel-Komponenten belegt keinen weiteren tatsächlich gemessenen Overhead; die gesondert gezeigte Indexzeit kann eine andere Zeitdefinition verwenden. Harvey-Kosten sind von der Quelle aus Token- und Preisfeldern berechnete Durchschnittskosten, keine Einzelrechnungen. Decision-Kosten basieren auf den bei der Quelle angesetzten aktuellen Tokenpreisen; Zeiten sind Mediane. Die Erfassung läuft gegebenenfalls noch. Ein Modell kann bei einem Provider mehrere unterschiedliche Quellzeilen haben; die Zeilennummer bewahrt diese Varianten. Provider-Endpunkte können aus mehreren Quellarrays mit unterschiedlichen Preisen stammen; diese sind gesondert ausgewiesen. Chatbot-Monatspreise sind Abo-Preise, keine API-Kosten pro Aufgabe. Preisstaffeln: Die genaue Tokenbasis der Schwellen ist nicht immer angegeben; widersprüchliche oder mehrdeutige Quellwerte bleiben erhalten. Bei Mischpreisen zeigt „Cachepreis fehlt“ an, dass die Quelle für Cache stattdessen den normalen Inputpreis verwendet. Index-Gesamtkosten sind errechnete Werte der Quelle und keine garantierten Rechnungsbeträge. Index-Kostenbestandteile können ineinander enthalten sein und dürfen nicht unbesehen addiert werden. Bei Coding-Agenten gelten angezeigte Kosten und Laufzeiten für den Indexmix, nicht den einzelnen Benchmark. Bei Such-Agenten enthält die Gesamtzeit einen abgeleiteten Modellzeitanteil; Kosten und Zeiten beziehen sich auf den aggregierten Aufgabenmix. Bei TTS benennt der Anwendungscode einige Quellfelder als Durchsatz-Perzentile; diese werden in Zeichen pro Sekunde angezeigt, während die ursprünglichen Feldnamen im Rohdatensatz erhalten bleiben.</p><div class="scroll"><table><thead><tr>'+''.join('<th>'+esc(LABELS.get(x,x))+'</th>' for x in cols)+'</tr></thead><tbody>'+''.join(trs)+'''</tbody></table></div><p class="note">Spaltenköpfe sortieren die angezeigten Zeilen. Quellen und Erfassungsgrenzen: README.md im Datenordner.</p></main><script>
const table=document.querySelector('table'), body=table.tBodies[0];let last=-1,ascending=true;
for(const [index,head] of Array.from(table.tHead.rows[0].cells).entries())head.addEventListener('click',()=>{
 ascending=index===last?!ascending:true;last=index;
 const rows=Array.from(body.rows),number=/^[+-]?(?:\\d+\\.?\\d*|\\.\\d+)(?:e[+-]?\\d+)?$/i;
 rows.sort((a,b)=>{let x=a.cells[index].textContent.trim(),y=b.cells[index].textContent.trim();
 if(x==='—'||x==='')return y==='—'||y===''?0:1;if(y==='—'||y==='')return -1;
 let cmp=number.test(x)&&number.test(y)?Number(x)-Number(y):x.localeCompare(y,'de',{numeric:true,sensitivity:'base'});return ascending?cmp:-cmp;});
 body.replaceChildren(...rows);
});</script></html>''').encode();ctype='text/html; charset=utf-8'
  else:self.send_error(404);return
  self.send_response(200);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(body)));self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(body)
 def log_message(self,*args):pass
if __name__=='__main__':
 print('Lokal öffnen: http://127.0.0.1:8765',flush=True)
 ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
