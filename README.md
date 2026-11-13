# Model Routing

Dieser private Datenkatalog enthält den auf Nutzerwunsch eingefrorenen Arbeitsstand aus Artificial Analysis: die SQLite-Datenbank einschließlich archivierter Quellseiten, strukturierte Auswertungen, Extraktoren, Prüfungen und eine lokale Suchoberfläche. Die Sammlung wurde beendet; es wird beim Klonen oder Starten der Oberfläche nichts nachgeladen.

- **Datenbank:** `artificial_analysis.sqlite3` (über Git LFS; vollständiger Abruf erfordert `git lfs pull`).
- **Lokale Suche:** `python3 browse.py`, danach `http://127.0.0.1:8765` auf demselben Rechner öffnen.
- **Stand und Grenzen:** `COVERAGE.md`; Methoden und Quellen sind in den jeweiligen `*_BENCHMARKS.md`- und Preisdokumenten erläutert.
- **Wiederherstellung:** `REBUILD.md`; für vollständige Sicherung die SQLite-Datei selbst aufbewahren.

Die Daten sind ein Snapshot, kein Nachweis, dass jede Messung für jedes Modell verfügbar oder dass die Quelle vollständig ist. Fehlende Werte sind nicht null; modellierte Kosten und Zeiten sind als Schätzungen gekennzeichnet. Artificial Analysis untersagt laut seinen Nutzungsbedingungen automatisiertes Scraping; Nutzungs- und Weitergaberechte sind zu beachten.

---

# Artificial Analysis: API-Datenbank

Der Importer speichert offizielle API-Antworten mit Abrufzeit als JSON in SQLite. Ohne API-Schlüssel wurden keine API-Daten geladen. Detail-, Provider-, historische und Rohdaten hängen vom Zugang ab. Fehlende Messungen sind nicht 0; Kosten und Zeit pro Aufgabe sind nicht automatisch aus Tokenpreisen oder Geschwindigkeit gleichzusetzen.

1. API-Schlüssel erstellen und Zugang prüfen: https://artificialanalysis.ai/data-api/docs
2. Schlüssel lokal als Umgebungsvariable `ARTIFICIAL_ANALYSIS_API_KEY` setzen; nicht in Dateien oder Chat schreiben.
3. `python3 import_api.py` ausführen. Optional dokumentierte API-Pfade angeben, z. B. `/language/models /language/providers`. Providerdaten können einen höheren Tarif erfordern.
4. SQLite enthält pro erfolgreicher Antwort Endpunkt, UTC-Abrufzeit, SHA-256 und die vollständige JSON-Antwort. Mehrere Abrufe bleiben erhalten.

Die vollständige Erfassung aller Endpunkte, Paginierung, Detaildaten und normalisierte Auswertung sind noch zu implementieren und anhand des verfügbaren Tarifs zu prüfen. Nutzungs- und Weitergaberechte beachten. Die Nutzungsbedingungen untersagen automatisiertes Website-Scraping: https://artificialanalysis.ai/docs/legal/Terms-of-Use.pdf Abschnitt 4.2(b)(vi). Deshalb ist der offizielle API-Weg vorgesehen.

## Öffentliche Modell-Rangliste

`python3 collect_public.py` erfasst die sichtbare Modell-Rangliste als zusätzlichen Snapshot in `artificial_analysis.sqlite3`. Tabelle `captures` dokumentiert Quelle, Abrufzeit, Prüfsumme und Spaltennamen. `model_observations` enthält Modellvariante, Kontextfenster, Creator, Intelligence Index, Kosten pro Aufgabe in USD, Zeit pro Aufgabe in Minuten und Zeit bis zum ersten Antworttoken in Sekunden; Originalzellen und Links bleiben erhalten. Nicht angezeigte oder nicht numerische Werte werden als NULL gespeichert und sind in den Originalzellen nachvollziehbar. Creator sind Modellhersteller und nicht zwingend Hosting-Provider. Die Werte sind Momentaufnahmen und keine einzelnen Benchmark-Rohmessungen. Andere Seiten, Benchmarkdetails, Providerpreise und historische Daten sind bislang nicht erfasst. Die HTML-Prüfsumme bezieht sich auf die Antwort beim Abruf; das HTML wird nicht archiviert.

## Modell- und Benchmarkdaten

`python3 extract_models.py` extrahiert eingebettete aktuelle Modellobjekte aus bereits archivierten Modellseiten. `model_details` enthält das Originalobjekt und stabile ID, Modellslug und Effort-Level. Die SQLite-Views `model_metrics` und `benchmark_task_costs` erleichtern die Abfrage numerischer Felder und der von der Quelle ausgewiesenen gewichteten Evaluierungskosten. NULL bedeutet fehlend, nicht null. Rohfeldnamen und Skalen sind erhalten; Methodik und Einheiten vor Vergleichen prüfen. `python3 extract_tables.py` extrahiert darüber hinaus sichtbare HTML-Tabellen inklusive Quell-URL und Links. Beide Extraktoren sind erneut ausführbar, um neue Archivseiten zu verarbeiten.

Die View `benchmark_results` enthält pro Modell-ID, Effort und Evaluierung den von der Quelle gelieferten Score, `costPerTask`, `timePerTask` und `outputTokensPerTask` sowie das vollständige Ergebnisobjekt. Werte können NULL sein. Die Skala des Scores hängt vom Benchmark ab; Angaben sind ohne bestätigte Methodik nicht zwischen Benchmarks vergleichbar. `benchmark_task_costs` enthält dagegen explizit gewichtete Beiträge und ist nicht mit den Aufgabenkosten in `benchmark_results` gleichzusetzen.

`python3 extract_evaluations.py` verarbeitet neu archivierte Evaluierungsseiten. `evaluation_page_models` speichert die darin eingebetteten Modellobjekte mit jeweiliger Quellseite und Prüfsumme; `evaluation_page_metrics` macht ihre numerischen Rohfelder zugänglich. Dieselbe Modell-ID kann auf mehreren Evaluierungsseiten vorkommen und darf nicht als eigenständiges Modell gezählt werden. Ein Vorkommen eines Modells auf einer Evaluierungsseite beweist nicht, dass jeder gespeicherte Zahlenwert genau diese Evaluation bezeichnet.

`python3 validate.py` prüft die SQLite-Integrität und gleicht verfügbare Index-Aufgabenzeiten und Kosten aus Modellobjekten mit der sichtbaren Rangliste ab. In 29 verglichenen Modellvarianten entsprach die Detailzeit geteilt durch 60 der Minutenanzeige innerhalb 0,11 Minuten; Kosten stimmten innerhalb 0,011 USD. Das belegt die Skalierung für dieses Indexfeld und diesen Datenstand, nicht automatisch für alle einzelnen Evaluierungen.

`evaluation_page_scores` ordnet acht Benchmarkseiten explizit ihren Score-Feldern zu. Die Feldzuordnung wurde anhand identischer, bereits ausdrücklich benannter Ergebnisse in `intelligenceIndexEvaluations` geprüft; bei AA-Briefcase erfolgte der Abgleich über `briefcaseBreakdown.overall.elo`. Die Werte behalten ihre ursprüngliche Skala und Quellenangabe. Unterschiedliche Seiten-Snapshots können abweichende Werte zeigen und sollten nicht stillschweigend zusammengeführt werden.

`python3 extract_providers.py` strukturiert die bereits durch `extract_tables.py` erfassten Tabellen auf Modell-Providerseiten. `provider_observations` enthält pro Modellslug und API-Provider die angezeigten Kosten pro Aufgabe (USD), Zeit pro Aufgabe (Minuten), Zeit bis zum ersten Antworttoken (Sekunden), Fehlerrate und weitere Tabellenzellen einschließlich Quelle und Rohwerten. Leere Symbolzellen sind nicht als Ja/Nein interpretiert. Erfassung nach neuem Abruf erst mit `extract_tables.py`, dann `extract_providers.py` aktualisieren.

`python3 extract_embedded_models.py [archivierte Modell-URL]` sichert eine eingebettete Modellliste aus einer bereits archivierten Modellseite. `embedded_model_snapshots` enthält die unveränderten Modellobjekte pro Quellseite und Seitenprüfsumme. `embedded_benchmark_results` stellt darin enthaltene Index-Evaluierungen mit Score, Kosten, Zeit und Ausgabe-Token pro Aufgabe bereit. Diese ergänzen die Detailseiten; beim Zusammenführen nach Modell-ID, Evaluierung und Quellenstand deduplizieren. Bewertungsmaßstäbe unterscheiden sich je Benchmark.

`embedded_model_metrics` stellt die numerischen und fehlenden Felder der eingebetteten Modellliste zeilenweise bereit. `embedded_model_leaves` erschließt zusätzlich alle verschachtelten Einzelwerte mit ihrem vollständigen JSON-Pfad, Quellseite und Modell-ID. Dadurch bleiben auch Preisbestandteile, Benchmark-Unterwerte und Tokenangaben auffindbar. Die Originalfeldnamen sind keine bestätigte Dokumentation der Einheiten oder Benchmarkversionen.

`embedded_benchmark_results_readable` zeigt zusätzlich abgeleitete Einheiten für Kosten (USD) und Zeit (Sekunden bzw. Minuten); diese sind als `inferred` gekennzeichnet. Plausibilisierung: Für 113 vollständige Modelle entspricht die Summe der einzelnen Benchmark-Zeiten, gewichtet mit dem Quotienten aus gewichtetem und ungewichtetem Kostenfeld, der Index-Aufgabenzeit bis auf Rundungsfehler. Für 29 Varianten stimmt die Indexzeit geteilt durch 60 mit der sichtbaren Minutenangabe überein; der Indexpreis stimmt mit der USD-Angabe überein. Dies ist eine rechnerische Validierung, keine unabhängige Bestätigung jeder zugrunde liegenden Messung oder Methodikversion.

## Beispielabfragen

```sql
-- Score, Kosten und abgeleitete Zeit je Aufgabe für einen Benchmark:
SELECT model_name, effort, evaluation_slug, score,
       cost_per_task_usd_inferred, time_per_task_minutes_inferred
FROM embedded_benchmark_results_readable
WHERE evaluation_slug = 'aa-briefcase'
ORDER BY score DESC;

-- Alle verfügbaren Rohfelder einer Modellvariante:
SELECT metric_key, value, value_type FROM embedded_model_metrics
WHERE model_slug = 'claude-fable-5-2' ORDER BY metric_key;

-- Sichtbare Angaben pro Hosting-Provider:
SELECT model_slug, provider, cost_per_task_usd, time_per_task_minutes,
       first_answer_token_seconds, error_rate_percent
FROM provider_observations WHERE model_slug = 'claude-fable-5-1-high';
```

In Python öffnen: `sqlite3.connect('artificial_analysis.sqlite3')`. Modellhersteller (`creator`) und API-Provider sind unterschiedliche Konzepte. Gleichnamige Modellbezeichnungen ersetzen keine Modell-ID; Seitenstände und Benchmarks mit unterschiedlichen Skalen nicht unbesehen vermischen.

`benchmark_catalog` verbindet die neun ausdrücklich abgeglichenen Score-Felder für alle Modellvarianten des eingebetteten Snapshots mit den jeweils vorhandenen Kosten und Zeiten aus derselben Quelle. Fehlende Aufgabendaten bleiben NULL. Kosten und Zeit sind wie in `embedded_benchmark_results_readable` als abgeleitete Einheiten gekennzeichnet; alle Scores bleiben in ihrer jeweiligen Originalskala.

`benchmark_registry` enthält aus einem öffentlichen Anwendungscode extrahierte Zuordnungen von Evaluierungs-Slug zu Score-Feld; `registry_sources` bewahrt dafür den ursprünglichen JavaScript-Stand, Abrufzeit und SHA-256. `registry_benchmark_scores` zeigt Scores aus den jeweils passenden Evaluierungsseiten; `embedded_registry_scores` wendet dieselben Feldnamen auf den eingebetteten Modelllisten-Snapshot an. Felder, die dort nicht existieren oder NULL sind, erzeugen keine Ergebniszeile. Die Score-Skalen sind benchmarkspezifisch und werden nicht umgerechnet. Ein identischer Feldname in unterschiedlichen Objektformen ist eine Zuordnung auf Basis des Anwendungscodes und sollte bei auffälligen Werten anhand der Quellseite geprüft werden.

`benchmark_registry_metadata` ergänzt aus demselben archivierten Anwendungscode extrahierte Aufgabenanzahlen, Indexgewichte, Score-Anzeigeformate und die Originaldefinition. Nicht automatisch aufgelöste oder nicht angegebene Werte bleiben NULL; Aufgabenanzahl und Gewicht gelten für den erfassten Quellenstand und können sich mit einer Benchmarkversion ändern. Das Format `.1%` ist das Anzeigeformat für einen Anteilswert; die gespeicherten Rohscores wurden nicht umgerechnet.

`python3 extract_coding_agents.py` extrahiert Agenten-Konfigurationen aus archivierten Coding-Agent-Seiten. `coding_agent_runs` bewahrt den Originaldatensatz und seine Quellseite; `coding_agent_run_summary` zeigt unter anderem Modell, Effort, Indexscore, mittlere Kosten in USD und mittlere Agentenlaufzeit in Sekunden. `coding_agent_benchmark_results` enthält je Konfiguration und Benchmark den mittleren Reward, mittlere Tokenzahlen, Benchmarkreferenz und das Originalergebnis. Dieselbe Konfiguration kann auf mehreren Quellseiten enthalten sein: für Modellzahlen nach `run_id` deduplizieren und Quellenstände beachten. Die Kosten-/Zeitfelder des Runs sind aggregierte Mittelwerte, nicht automatisch pro Einzelbenchmark ausgewiesen.

Für deduplizierte Agentenvergleiche wählen `coding_agent_latest_runs` und `coding_agent_latest_benchmarks` je Run-ID die zuletzt archivierte Quelle und zeigen deren Abrufzeit. Die vollständigen Quellvarianten bleiben in `coding_agent_runs` erhalten; spätere Abrufzeit bedeutet nicht automatisch, dass die Quelldaten inhaltlich aktualisiert wurden.

Da Modelllisten aus unterschiedlichen Seiten und Zeitpunkten Snapshots desselben Bestands enthalten können, enthalten `embedded_registry_scores`, `embedded_benchmark_results` und `benchmark_catalog` bewusst mehrere Quellstände. Für eine je Modell-ID deduplizierte Sicht wählen `embedded_latest_models`, `latest_registry_benchmark_scores` und `latest_index_benchmark_results` jeweils die zuletzt archivierte Quelle und zeigen deren Abrufzeit. Das ist der späteste verfügbare Abruf, kein Nachweis für eine Änderung beim Anbieter.

`extract_search_api.py` erschließt Such-API-Tabellen aus dem Seitenarchiv: Search Index, Baseline Lift, DeepSearchQA F1, BrowseComp Accuracy, AA-Omniscience Accuracy, Such- und Modellkosten in USD **je 1.000 Aufgaben** und Zeit je Aufgabe in Sekunden. `search_api_observations` bewahrt jede Quellzeile, `latest_search_api_observations` dedupliziert nach angezeigtem Variantennamen und wählt den letzten Abruf. Prozentangaben und Indizes behalten die angezeigte Skala. Such- und Modellkosten nicht ohne Kontext mit Kosten pro einzelner Aufgabe verwechseln.

`benchmark_scores_with_metadata` ergänzt die jüngsten Registry-Scores um Aufgabenanzahl und Anzeigeformat. Bei Formatangaben mit `%` ist `score_display_value` der Rohanteil mal 100; `score_raw` bleibt unverändert. Nicht prozentuale Scores werden für die Anzeige nicht verändert. Die Anzeigeformate und Aufgabenanzahlen gehören zum archivierten Registry-Stand und sind kein Nachweis, dass ältere Modellmessungen unter denselben Benchmarkversionen entstanden sind.

`extract_provider_leaderboard.py` strukturiert die globale Provider-Rangliste in `provider_leaderboard_observations`. Sie enthält API-Provider und Modellname samt Index, Kosten/Zeit je Aufgabe, Latenz, Fehlerrate und Originalzellen. Diese Tabelle ist ein separater Seitenstand und ergänzt `provider_observations` aus den Modell-Providerseiten; Quellenstände und Namen vor dem Zusammenführen beachten.

## Lokal durchsuchen

`python3 browse.py` starten und `http://127.0.0.1:8765` im Browser auf demselben Rechner öffnen. Die Oberfläche liest die Datenbank lokal, bietet Suche, Sortierung der angezeigten Zeilen über Spaltenköpfe, Quelllinks und CSV-Export für Benchmarks, Index-Aufgabendaten, Modell-Provider, Such-APIs und Coding-Agenten. Pro Suche werden höchstens 2.000 Zeilen angezeigt; der CSV-Export enthält alle passenden Zeilen. Der Server bindet nur an localhost. Die Oberfläche zeigt den beim jeweiligen Abruf vorhandenen Stand und ergänzt laufend importierte Daten.

`extract_provider_pages.py` strukturiert zusätzlich die Modelltabellen einzelner Providerseiten in `provider_page_models`, einschließlich Provider-Slug, Modellname, Intelligence Index, Kosten/Zeit je Aufgabe, Latenz und Fehlerrate. Quellseite und Rohzellen bleiben erhalten. Leere Funktionssymbole sind keine bestätigten Ja/Nein-Angaben. Diese Tabellen sind von der globalen Rangliste und den Modell-Providerseiten getrennte Quellenstände.

`python3 discover_links.py` ergänzt relevante öffentlich verlinkte Modell-, Provider-, Evaluierungs-, Agenten- und Methodikseiten, die im Archiv gefunden werden, in der Crawling-Warteschlange. `discovered_links` speichert jeweils eine gefundene Quellseite und deren Prüfsumme. Aus Sicherheits- und Abdeckungsgründen werden nur ausgewählte Pfade auf derselben Domain aufgenommen; Parameter, Fragmente und Asset-Dateien werden nicht als eigene Seiten behandelt. Ein laufender Crawler übernimmt neu eingereihte URLs beim nächsten Start.

`combined_latest_benchmark_scores` ergänzt die direkten Registry-Felder um zwei geprüfte Abweichungen in der Objektstruktur: `itBenchSre` auf Modellseiten entspricht `itbenchSre` auf ITBench-Evaluierungsseiten (27 überlappende Werte gleich); `briefcaseBreakdown.overall.elo` entspricht dem ausdrücklich ausgewiesenen AA-Briefcase-Score (45 überlappende Werte gleich). Diese Ergänzungen sind in `latest_verified_field_aliases` getrennt nachvollziehbar.

`latest_combined_benchmark_scores` kombiniert die Score-Felder aus Modelllisten und den passenden Evaluierungsseiten, wählt je Modell-ID und Evaluierung die zuletzt archivierte Quelle und bewahrt die Abrufzeit. Für 927 überlappende Modell-/Evaluierungskombinationen stimmten die Scores zwischen den Quellen beim Abgleich überein. Die Originalansichten bleiben für Quellenvergleiche verfügbar. Score-Werte aus verschiedenen Benchmarkversionen sind nicht automatisch vergleichbar.

`latest_model_facts` bietet je aktuellstem Modellobjekt eine kompakte Übersicht über Modellhersteller, Kontextfenster, Index, Input-/Output- und Cachepreisfelder, Geschwindigkeit, Latenz, Index-Kosten und Index-Zeit. Preise und Leistungsdaten können von unterschiedlichen in der Quelle genannten Providern stammen; diese stehen als eigene Felder dabei. `browse.py` enthält dafür die Ansicht „Modelle und Preise“.

Die Modellseite Claude Fable 5.1 (high) bezeichnet Input-, Output- und Cache-Hit-Preise ausdrücklich als USD pro eine Million Token sowie die Ausgabegeschwindigkeit als Token pro Sekunde. Die lokalen Tabellenüberschriften zeigen diese Einheiten an. Cache-Write-Preise und einzelne andere Felder sollten bei Bedarf anhand der jeweiligen Provider- und Methodikseite geprüft werden.

Die Validierung prüft zusätzlich die jüngste zusammengeführte Score-Ansicht auf doppelte Modell-ID-/Evaluierungspaare und vergleicht gleichnamige numerische Felder zwischen einzelnen Modellseiten und dem jüngsten Modelllisten-Snapshot. Beim geprüften Stand stimmten 10.613 solcher Feldpaare überein; dies ersetzt keine Prüfung der Benchmarkmethodik oder eine Messung der tatsächlichen Modellleistung.

Der Provider-Extraktor `extract_endpoint_prices.py` und die Sprachauswertung `extract_speech_benchmarks.py`, `extract_streaming_speech.py` und `extract_tts_arena.py` laufen in der Aktualisierungspipeline mit. Einzelheiten zu Feldherkunft, Einheiten und abweichenden Providerpreisen stehen in `PROVIDER_ENDPOINTS.md`; Sprachbenchmarkdefinitionen und Grenzen in `SPEECH_BENCHMARKS.md`. Bei einigen Endpunkten unterscheiden sich Preisfelder aus zwei Objektlisten derselben Seite; beide Quellwerte werden getrennt bewahrt und nicht als übereinstimmend behauptet.

`page_capture_events` protokolliert für neue Seitenabrufe URL, endgültige URL, Zeitpunkt und Prüfsumme; für vor Einführung der Tabelle bereits archivierte Seiten wurden verfügbare Ereignisse aus dem damaligen Stand nachgetragen. Frühere Weiterleitungen oder überschriebene HTML-Stände sind dadurch nicht nachträglich rekonstruierbar. `page_archive` bewahrt weiterhin nur die zuletzt gespeicherte HTML-Antwort je URL. Für ältere Modell-Snapshots ohne passendes Capture-Ereignis bleibt der Zeitpunkt unbekannt, sofern der aktuelle Seitenhash nicht übereinstimmt.

Die Bild-/Videoarena enthält mit `media_arena_observations` Gesamtergebnisse und Unterkategorien, einschließlich Modell-/Creator-ID, Elo, verfügbaren Konfidenzintervallen und Preisen. Kategorien und getrennte Arenen dürfen nicht ohne Weiteres verglichen werden. `media_endpoint_records` enthält Bild-Providerendpunkte mit USD je 1.000 Bilder und Generierungszeit-Perzentilen. Ein unabhängiger zweiter Extraktor erfasste dieselben 300 Quell-/Endpunktpaare; ihre Preise und Mediane stimmten bei allen Paaren überein. Dieselbe Endpunkt-ID kann auf mehreren Quellseiten stehen. Siehe die zugehörigen Media-Dokumentationen für den Geltungsbereich.

Video- und TTS-Provider-Endpunkte werden getrennt angezeigt: Video-Preis je Videominute und TTS-Preis je Million Zeichen. Bei 93 TTS-Endpunkten passen die im Rohdatensatz als Zeitperzentile benannten Felder nicht zum Zeitmedian. Der archivierte Anwendungscode bezeichnet sie jedoch ausdrücklich als Durchsatzperzentile in Zeichen pro Sekunde; die Oberfläche zeigt sie mit dieser Einheit. Die Rohfelder und das frühere Konsistenzflag bleiben zur Nachvollziehbarkeit erhalten. Einzelne Quellen können mehrmals erscheinen; Modell-/Endpunkt-IDs und Quellseiten zur Deduplizierung heranziehen.

Die Video-Endpunktzeit ist die Generierungsdauer pro Clip; der Preis bezieht sich auf eine Videominute. Die zugrunde liegende Providerseiten-Auswahl zielt auf 1080p und sechs Sekunden und verwendet sonst die nächstliegenden Einstellungen. Medienkonfigurationen und Benchmark-Arenen sind deshalb nicht ohne Prüfung unmittelbar vergleichbar. Ein zweiter Extraktor bestätigte bei 35 abgeglichenen Video-Endpunkten Preis und Zeitmedian.

Die archivierten Coding-Agent-Vergleichstabellen wiederholen bekannte Konfigurationen. Bei eindeutig nach Agent und Modellnamen vergleichbaren Werten stimmten 336/336 Kosten und 300/300 Laufzeiten nach Rundung mit den bereits gespeicherten Run-Daten überein. Diese Quellkopien wurden nicht als zusätzliche unabhängige Messungen gezählt.

`chatbot_plan_observations` bewahrt zusätzlich monatliche Chatbot-Abopreise und Preisnotizen aus dem Quellverzeichnis. Sie sind keine API- oder Aufgabenkosten. `cache_pricing_source_rows` enthält getrennt die sichtbare Cache-Preistabelle einschließlich Providergruppen, Originalnotizen und Quellen; fehlende Speicherpreise bleiben fehlend.

Zusätzliche Abdeckungsprüfung gegen archivierte Release-Vergleiche: 1.034 Vergleichstabellen ergaben bei neun aktuellen Index-Benchmarks 677 befüllte eindeutige Modell-/Benchmark-Paare; alle waren bereits in der zusammengeführten Score-Ansicht vorhanden. Von diesen stimmten 660 numerisch vergleichbare Paare nach beachteter Quellrundung überein. Diese Stichprobe belegt keine Vollständigkeit aller Benchmarks oder Zeitmessungen.

`python3 export_view_schema.py` exportiert den aktuellen SQLite-View-Stand nach `views_snapshot.sql` und prüft den Wiederaufbau zuvor in einer leeren In-Memory-Datenbank gegen die vorhandenen Tabellenschemata. Der Live-Bestand wird dabei nicht verändert. Das SQL-Snapshot ersetzt bei seiner Ausführung alle gleichnamigen Views und sollte nur auf einer gesicherten Datenbank mit kompatiblen Tabellen angewendet werden; es enthält keine Tabellendaten oder Archivseiten. Die Pipeline aktualisiert das Snapshot nach der Extraktion.

Für eine **neue leere Datenbank** erzeugt `bootstrap_schema.sql` alle beim Export vorhandenen Tabellenschemata, Indizes und Views; es enthält keinerlei Beobachtungen oder Quellseiten. Beispiel aus dem Datenordner: `python3 -c "import sqlite3; sqlite3.connect('leer.sqlite3').executescript(open('bootstrap_schema.sql', encoding='utf-8').read())"`. Danach müssen die Quelldaten separat und im Rahmen des verfügbaren Zugangs eingelesen werden; das Schema allein reproduziert keine Daten. Für die bereits befüllte Arbeitsdatenbank ist kein Bootstrap nötig. `export_view_schema.py` testet beide SQL-Snapshots zuerst in isolierten leeren In-Memory-Datenbanken.

`source_evidence.json` sichert zusätzlich sechs archivierte JavaScript-Quellartefakte für Berechnungsformeln und Feldzuordnungen einschließlich URL, Zeitstempel und SHA-256. `python3 source_evidence.py export` erneuert diesen kleinen Belegexport aus der vorhandenen Datenbank. Nach dem Bootstrap einer leeren Datenbank kann `python3 source_evidence.py import leer.sqlite3` die Quellartefakte wieder einlesen; dabei wird jeder Inhalt gegen seinen Hash geprüft. Diese Belege enthalten nicht die vollständigen Webseitenarchive oder die Beobachtungsdaten. Für eine vollständige Datensicherung weiterhin die SQLite-Datei selbst sichern.

Beim Belegimport werden auch bereits vorhandene gleichschlüssige Inhalte mit dem Manifest verglichen. Bei abweichendem oder beschädigtem Inhalt bricht der Import ab; er meldet keinen stillen Erfolg. Diese Fehlerbehandlung wurde mit einer absichtlich beschädigten Testdatenbank überprüft.

Ein getesteter Ablauf zum Neuaufbau abgeleiteter Daten aus einer kompatiblen Archivkopie steht in `REBUILD.md`. `update_pipeline.py --once` gibt bei einem fehlgeschlagenen Schritt einen Fehler-Exitcode aus; die automatische Pipeline meldet außerdem die einzelnen Schritte in `pipeline_step_runs`.

Der Belegexport enthält eine separate SHA-256-Datei für das Manifest. Sie erkennt unbeabsichtigte Änderungen, wenn sie getrennt unverändert aufbewahrt wird; sie ist keine kryptografische Signatur oder unabhängige Authentizitätsgarantie. `restore_archive.py` prüft jede archivierte Seite nach dem Entpacken gegen den gespeicherten SHA-256, bevor kopiert wird.

`python3 verify_archive.py` überprüft neue oder anhand des gespeicherten Hashes geänderte archivierte Seiten durch Entpacken und SHA-256-Vergleich. `python3 verify_archive.py --full` prüft alle aktuellen Seiten erneut; dies ist nötig, um auch eine nach der letzten Prüfung beschädigte Blob-Zelle mit unverändertem gespeichertem Hash aufzudecken. Ergebnisse stehen in `archive_integrity_checks`; `coverage.py` weist geprüfte und noch nicht geprüfte Seiten aus.

`model_benchmark_availability` zählt je Benchmark-/Indexbezeichnung die Modell-IDs mit einem Score und darunter jene mit Index-Teilkosten, Index-Teilzeit oder berechenbaren Kosten-/Zeitschätzungen. Sie zeigt Lücken in der kombinierten Modellsicht; separate Spezialbestände wie Decision, Speech und Harvey sind darin nicht vollständig enthalten. Die Zählung sagt nicht, dass fehlende Werte auf der gesamten Website nicht existieren.

Bei einer Stichprobe von 600 archivierten Evaluierungs- und Modellseiten war das einzige gefundene interne Pfad-/Query-Schlüsselmuster `critpt-subset` auf der CritPt-v2-Seite. Der Hard-Subset-Score ist als eigener Registry-Eintrag `critpt-v2-hard` aus den Modellobjekten erfasst. Da `discover_links.py` Query-Parameter nicht als eigene URLs einreiht, ist die Stichprobe kein Beweis, dass keine weiteren parameterabhängigen Ansichten existieren.
