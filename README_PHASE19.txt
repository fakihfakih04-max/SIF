SIF Mobile & Computer - PHASE 19

FIXES:
- Correct package root: START_SIF.bat is in the main extracted folder.
- Robust Windows launcher: starts Uvicorn directly with the venv Python (no nested cmd quoting bug).
- Waits for http://127.0.0.1:8017/ to respond before opening the browser.
- Removes obsolete launcher scripts that used port 8000.
- Keeps the Phase 18 Price Checker and Purchase fixes.

START:
1. Close old SIF windows/server windows.
2. Extract this ZIP into a NEW folder.
3. Open the extracted main folder.
4. Double-click START_SIF.bat.
5. Browser should open at http://127.0.0.1:8017/?v=19

PRICE CHECKER:
Retail = only Retail price + USD + LBP.
Wholesale = only Wholesale price + USD + LBP.
VIP = only VIP price + USD + LBP.

PURCHASE:
Walk-in Supplier or named Supplier, product, automatic cost, quantity, VAT ON/OFF, payment, purchase invoice, stock increase.
