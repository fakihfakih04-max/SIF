SIF MOBILE & COMPUTER - PHASE 17

FIXED AND VERIFIED:
1. Price Checker now calculates/display ONLY the selected price type:
   Retail -> Retail only
   Wholesale -> Wholesale only
   VIP -> VIP only
   USD + LBP are shown.
2. Price Checker loads products from /api/products and filters locally, avoiding stale/incorrect price-check results.
3. Purchase form is fully wired:
   - Walk-in Supplier or supplier account
   - Product selector
   - Cost auto-fill
   - Quantity
   - VAT ON/OFF
   - Cash/Card/Supplier Account
   - Official PUR invoice
   - Stock increases automatically
4. Backend purchase API was tested successfully with VAT and stock update.
5. START_SIF opens the app with a cache-busting URL.

Login: admin / admin
Run: START_SIF.bat
