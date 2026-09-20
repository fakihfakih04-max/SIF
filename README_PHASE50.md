# SIF Mobile & Computer — Phase 50

## Professional Logo + Web Ready
- Added the new SIF ERP gold/black eagle logo to the Login screen.
- Added the same logo to the left sidebar/brand area.
- Added `/brand-logo.png` to the FastAPI app so the logo is served correctly from the web server.
- Official invoice header uses the uploaded Company Logo from Settings when available; otherwise it automatically uses the built-in SIF logo.
- Existing product, POS, stock, purchases, sales, repairs, reports, users, barcode and database features are preserved.

## Online Web
The application is already browser-based (FastAPI + HTML/JS). This package is prepared for online deployment. For production multi-user online use, deploy the FastAPI server with persistent storage; SQLite is suitable for a single server/local deployment, while PostgreSQL is recommended when multiple online users will work concurrently.
