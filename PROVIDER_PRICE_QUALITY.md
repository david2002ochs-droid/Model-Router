# Prüflauf Providerpreise

UTC: 2026-11-13T17:00:43.108944+00:00

Der Vergleich erfolgt je Datensatz direkt gegen das archivierte JSON, nicht gegen einen späteren Anbieterpreis. Unter „Quellzahlen“ zählen auch explizite Nullen; fehlende, nichtnumerische oder `$undefined`-Felder müssen in der numerischen Spalte NULL sein.

| Feld | Quellobjekte | Quellzahlen | Abweichungen / falsch befüllte Leerwerte | explizite Nullen erhalten |
|---|---:|---:|---:|---:|
| LLM price_1m_input_usd | 4487 | 4487 | 0 | 63 |
| LLM price_1m_output_usd | 4487 | 4487 | 0 | 67 |
| LLM cache_hit_usd_per_1m | 4487 | 3291 | 0 | 0 |
| LLM cache_write_usd_per_1m | 4487 | 630 | 0 | 3 |
| Medien price_per_1000_images_usd | 13560 | 480 | 0 | 0 |
| Medien video_price_usd_per_minute | 13560 | 210 | 0 | 0 |
| Medien tts_price_usd_per_million_chars | 13560 | 10890 | 0 | 110 |

- Einander entsprechende `hostModels`-/`rows`-Objekte derselben Quelle und Endpunkt-ID: 2141 Paare; bei 10 unterscheiden sich Input- oder Outputpreise. Die Quellen bleiben getrennt; Ursache nicht als geklärt annehmen.
- Kontextstaffeln: 20 Quellzeilen; 3 mit uneindeutigem Zahlenformat. 1 Basistarif-Fußnoten weichen vom normalen Endpunktpreis ab. Rohangaben bleiben erhalten.
- Cachehaltige Mischpreisszenarien ohne ausgewiesenen Cachepreis: 632. Die ausgewiesene Mischung impliziert hier rechnerisch den normalen Inputpreis; kein tatsächlicher Cachepreis wird erfunden.
- Endpunkt-IDs in Tabellenobjekten: 1173, davon 183 ohne über Endpunkt-ID belegte Provider-UUID und 18 ohne belegte Modell-UUID. 0 beobachtete Endpunkt-UUID-Konflikte. Keine Namensfusion.
- SQLite `quick_check`: ok.

Unterschiedliche Anbieter, Tarifbedingungen, Varianten und Quellenstände sind keine automatisch vergleichbaren unabhängigen Messungen. Ein in der Quelle als 0 gelieferter Betrag belegt nicht, dass jede Nutzung ohne Bedingungen kostenlos ist.
