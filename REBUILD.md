# Abgeleitete Daten aus einem vorhandenen Archiv neu aufbauen

Die vollständige SQLite-Datei bleibt die einfachste Sicherung. Das leere Schema und die sechs Quellbelege allein enthalten keine Modellbeobachtungen. Für den folgenden Ablauf wird zusätzlich eine kompatible Sicherung der SQLite-Datei mit `page_archive`, Warteschlange und Capture-Ereignissen benötigt. Der Ablauf wird in einem **neuen, separaten Verzeichnis** ausgeführt; er verändert die Quellsicherung nicht.

1. Python-Skripte, SQL-Dateien sowie `source_evidence.json` und `source_evidence.json.sha256` aus diesem Ordner in ein neues Arbeitsverzeichnis kopieren und dorthin wechseln.
2. Eine leere Arbeitsdatenbank namens `artificial_analysis.sqlite3` anlegen:
   ```sh
   python3 -c "import sqlite3; sqlite3.connect('artificial_analysis.sqlite3').executescript(open('bootstrap_schema.sql', encoding='utf-8').read())"
   ```
3. Archivtabellen und vorhandene Modelllisten-Snapshots aus der Sicherung kopieren und die Formel-/Mappingquellen importieren:
   ```sh
   python3 restore_archive.py /absoluter/pfad/zur/sicherung.sqlite3 artificial_analysis.sqlite3
   python3 source_evidence.py import artificial_analysis.sqlite3
   ```
   Der Archivimport prüft vor dem Kopieren alle komprimierten Archivseiten gegen ihren SHA-256-Hash und hält Prüfung und Kopie in einem konsistenten Datenbanksnapshot und verlangt leere Zieltabellen und übereinstimmende Spaltennamen, Typen, NULL-Regeln, Standardwerte und Primärschlüssel; Indizes werden dabei nicht verglichen. Der Belegimport überprüft Inventar und Inhalts-Hashes.
4. Registry und Metadaten vorbereiten sowie den Standard-Modelllisten-Snapshot aus dem wiederhergestellten Archiv auffrischen:
   ```sh
   python3 extract_benchmark_registry.py
   python3 extract_registry_metadata.py
   python3 extract_embedded_models.py
   ```
   Die aus der Sicherung kopierten anderen Modelllisten-Snapshots bleiben dabei erhalten. Der letzte Befehl erwartet standardmäßig die archivierte Seite `/models/claude-fable-5-1-high`; falls sie nicht im Archiv ist, kann eine andere archivierte Modellseite als vollständige URL angegeben werden. Die Registry wird bei vorhandenem Beleg lokal gelesen.
5. Alle Extraktoren einmal in Abhängigkeitsreihenfolge ausführen:
   ```sh
   python3 update_pipeline.py --once
   python3 validate.py
   python3 coverage.py
   ```
   Ein Schritt mit Fehler-Exitcode oder Timeout verursacht bei `--once` einen Fehler-Exitcode; Einzelheiten stehen in `pipeline_step_runs`. Manche Extraktoren protokollieren einzelne Quellfehler intern und beenden sich dennoch erfolgreich; deshalb zusätzlich die Extraktionslogs und `COVERAGE.md` prüfen. Fehlende Quellseiten können einzelne Extraktoren scheitern lassen. Ein erfolgreicher Lauf mit einer Teilmenge des Archivs bedeutet keine Vollständigkeit der ursprünglichen Website.

Der Ablauf wurde isoliert mit 17 archivierten Seiten und beiden Modelllisten-Snapshots geprüft; dabei wurden Registry, Modellliste und Modell-/Evaluierungsobjekte neu aufgebaut und alle Pipeline-Schritte erfolgreich ausgeführt. Dies ist ein Funktionstest, kein Nachweis, dass eine beliebige Sicherung unverändert oder vollständig ist.
