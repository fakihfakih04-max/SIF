PHASE 32 - LAUNCHER HARD FIX
- Uses PowerShell Start-Process with explicit project WorkingDirectory and --app-dir.
- Checks /api/health before opening the browser.
- Writes sif_server.log and sif_server.log.err if startup fails.
- Uses URL version 32 to avoid stale browser tabs.
- Added STOP_SIF.bat.
- Includes Phase 30 Excel import/export.
