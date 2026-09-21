from workers import WorkerEntrypoint, Response
from urllib.parse import urlparse
import json
import hashlib
from datetime import datetime, timezone


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


async def body_json(request):
    try:
        return await request.json()
    except Exception:
        return {}


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        url = urlparse(request.url)
        path = url.path.rstrip("/") or "/"
        method = request.method.upper()

        try:
            # Basic health checks
            if path == "/health":
                return Response.json({"status": "ok", "service": "SIF Mobile & Computer", "mode": "cloudflare-d1"})
            if path == "/api/online-status":
                await self.env.DB.prepare("SELECT 1 AS ok").run()
                return Response.json({"online": True, "database": "D1", "status": "connected"})

            # Authentication
            if path == "/api/login" and method == "POST":
                b = await body_json(request)
                username = str(b.get("username", "")).strip()
                password = str(b.get("password", ""))
                r = await self.env.DB.prepare("SELECT id, username, password_hash, role, active FROM users WHERE username = ? LIMIT 1").bind(username).run()
                rows = r.get("results", [])
                if not rows:
                    return Response.json({"detail": "Invalid username or password."}, status=401)
                u = rows[0]
                if not u.get("active") or u.get("password_hash") != hash_password(password):
                    return Response.json({"detail": "Invalid username or password."}, status=401)
                return Response.json({"user": {"id": u["id"], "username": u["username"], "role": u["role"], "active": bool(u["active"])}})

            # Dashboard - robust D1 version
            if path == "/api/dashboard-test" and method == "GET":
                result = {"ok": True, "database": False, "tables": [], "errors": []}
                try:
                    q = await self.env.DB.prepare("SELECT 1 AS ok").run()
                    result["database"] = True
                    result["probe"] = q.get("results", [])
                except Exception as ex:
                    result["ok"] = False
                    result["errors"].append("DB probe: " + str(ex))
                try:
                    q = await self.env.DB.prepare(
                        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                    ).run()
                    result["tables"] = q.get("results", [])
                except Exception as ex:
                    result["ok"] = False
                    result["errors"].append("Tables: " + str(ex))
                return Response.json(result, status=200)

            if path == "/api/dashboard" and method == "GET":
                data = {
                    "totals": {
                        "products": 0, "customers": 0, "suppliers": 0, "repairs": 0,
                        "quantity": 0, "stock_quantity": 0, "stock_cost": 0,
                        "stock_sales": 0, "stock_sales_value": 0, "low_stock": 0,
                        "customer_receivables": 0, "supplier_payables": 0
                    },
                    "today": {
                        "sales": 0, "sales_count": 0, "purchases": 0,
                        "purchases_count": 0, "expenses": 0, "expenses_count": 0
                    },
                    "sales_7_days": [],
                    "repair_status": {},
                    "top_products": [],
                    "recent_sales": [],
                    "low_stock_items": [],
                    "errors": [],
                    "diagnostic": {"version": "DASHBOARD-FIX-V4", "ok": True}
                }

                async def one(label, sql):
                    try:
                        r = await self.env.DB.prepare(sql).run()
                        rows = r.get("results", []) or []
                        return rows[0] if rows else {}
                    except Exception as ex:
                        data["errors"].append(label + ": " + str(ex))
                        return {}

                async def many(label, sql):
                    try:
                        r = await self.env.DB.prepare(sql).run()
                        return r.get("results", []) or []
                    except Exception as ex:
                        data["errors"].append(label + ": " + str(ex))
                        return []

                # Basic counts
                for table, key in [
                    ("products","products"), ("customers","customers"),
                    ("suppliers","suppliers"), ("repairs","repairs")
                ]:
                    row = await one("count_" + table, f"SELECT COUNT(*) AS c FROM {table}")
                    data["totals"][key] = row.get("c", 0) or 0

                # Inventory
                row = await one(
                    "inventory",
                    "SELECT COALESCE(SUM(quantity),0) AS qty, "
                    "COALESCE(SUM(quantity*cost),0) AS cost, "
                    "COALESCE(SUM(quantity*sale_price),0) AS sales FROM products"
                )
                data["totals"]["quantity"] = row.get("qty", 0) or 0
                data["totals"]["stock_quantity"] = row.get("qty", 0) or 0
                data["totals"]["stock_cost"] = row.get("cost", 0) or 0
                data["totals"]["stock_sales"] = row.get("sales", 0) or 0
                data["totals"]["stock_sales_value"] = row.get("sales", 0) or 0

                row = await one(
                    "low_stock",
                    "SELECT COUNT(*) AS c FROM products "
                    "WHERE quantity <= COALESCE(reorder_level,0)"
                )
                data["totals"]["low_stock"] = row.get("c", 0) or 0

                # Today's figures
                row = await one(
                    "today_sales",
                    "SELECT COALESCE(SUM(total),0) AS total, COUNT(*) AS count "
                    "FROM sales WHERE date(created_at)=date('now')"
                )
                data["today"]["sales"] = row.get("total", 0) or 0
                data["today"]["sales_count"] = row.get("count", 0) or 0

                row = await one(
                    "today_purchases",
                    "SELECT COALESCE(SUM(total),0) AS total, COUNT(*) AS count "
                    "FROM purchases WHERE date(created_at)=date('now')"
                )
                data["today"]["purchases"] = row.get("total", 0) or 0
                data["today"]["purchases_count"] = row.get("count", 0) or 0

                row = await one(
                    "today_expenses",
                    "SELECT COALESCE(SUM(amount),0) AS total, COUNT(*) AS count "
                    "FROM expenses WHERE date(created_at)=date('now')"
                )
                data["today"]["expenses"] = row.get("total", 0) or 0
                data["today"]["expenses_count"] = row.get("count", 0) or 0

                row = await one(
                    "customer_balance",
                    "SELECT COALESCE(SUM(balance),0) AS balance FROM customers"
                )
                data["totals"]["customer_receivables"] = row.get("balance", 0) or 0

                row = await one(
                    "supplier_balance",
                    "SELECT COALESCE(SUM(balance),0) AS balance FROM suppliers"
                )
                data["totals"]["supplier_payables"] = row.get("balance", 0) or 0

                data["sales_7_days"] = await many(
                    "sales_7_days",
                    "SELECT date(created_at) AS date, COALESCE(SUM(total),0) AS total "
                    "FROM sales WHERE date(created_at)>=date('now','-6 day') "
                    "GROUP BY date(created_at) ORDER BY date(created_at)"
                )
                rs = await many(
                    "repair_status",
                    "SELECT status, COUNT(*) AS count FROM repairs GROUP BY status"
                )
                data["repair_status"] = {
                    str(x.get("status") or "unknown"): x.get("count", 0) or 0 for x in rs
                }

                data["top_products"] = await many(
                    "top_products",
                    "SELECT p.name, p.sku, SUM(si.quantity) AS qty, "
                    "SUM(si.total) AS amount FROM sale_items si "
                    "JOIN products p ON p.id=si.product_id "
                    "JOIN sales s ON s.id=si.sale_id "
                    "WHERE date(s.created_at)>=date('now','-30 day') "
                    "GROUP BY si.product_id ORDER BY qty DESC LIMIT 5"
                )

                data["recent_sales"] = await many(
                    "recent_sales",
                    "SELECT s.invoice_no, s.total, s.payment_method, s.created_at, "
                    "COALESCE(c.name,'Walk-in') AS customer_name "
                    "FROM sales s LEFT JOIN customers c ON c.id=s.customer_id "
                    "ORDER BY s.id DESC LIMIT 8"
                )

                data["low_stock_items"] = await many(
                    "low_stock_items",
                    "SELECT id, name, sku, quantity, reorder_level FROM products "
                    "WHERE quantity <= COALESCE(reorder_level,0) "
                    "ORDER BY quantity ASC LIMIT 10"
                )

                data["diagnostic"]["ok"] = len(data["errors"]) == 0
                data["diagnostic"]["error_count"] = len(data["errors"])
                data["diagnostic"]["timestamp"] = datetime.now(timezone.utc).isoformat()

                # IMPORTANT: always 200. Database/query errors are returned in JSON instead
                # of becoming the generic frontend "Server error".
                return Response.json(data, status=200)

            # Simple table GET/POST/PUT/DELETE routes
            tables = {
                "/api/products": "products",
                "/api/customers": "customers",
                "/api/suppliers": "suppliers",
                "/api/categories": "categories",
                "/api/product-types": "product_types",
                "/api/expenses": "expenses",
                "/api/repairs": "repairs",
            }
            if path in tables:
                table = tables[path]
                if method == "GET":
                    r = await self.env.DB.prepare(f"SELECT * FROM {table} ORDER BY id DESC").run()
                    return Response.json(r.get("results", []))
                b = await body_json(request)
                if method == "POST":
                    allowed = {
                        "products": ["sku","barcode","name","category","product_type","cost","sale_price","quantity","reorder_level","imei_required","serial_required","warranty_months","image_url","wholesale_price","vip_price","active"],
                        "customers": ["code","name","phone","address","balance"],
                        "suppliers": ["code","name","phone","address","balance"],
                        "categories": ["name","image_url","active"],
                        "product_types": ["name","code","active"],
                        "expenses": ["description","amount","created_at","category","payment_method","notes"],
                        "repairs": ["ticket_no","customer_id","device_name","imei_or_serial","problem","status","estimated_cost","created_at","sales_price","customer_phone","customer_address","technician","warranty_days","notes"],
                    }[table]
                    cols=[c for c in allowed if c in b]
                    if table in ("products","customers","suppliers","categories","product_types","repairs") and "active" in allowed and "active" not in cols: cols.append("active")
                    vals=[]
                    for c in cols:
                        if c == "active" and c not in b: vals.append(1)
                        elif c == "created_at" and c not in b: vals.append(datetime.now(timezone.utc).isoformat())
                        else: vals.append(b.get(c))
                    placeholders=",".join(["?"]*len(cols))
                    sql=f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders})"
                    await self.env.DB.prepare(sql).bind(*vals).run()
                    r=await self.env.DB.prepare(f"SELECT * FROM {table} ORDER BY id DESC LIMIT 1").run()
                    return Response.json((r.get("results", [{}]) or [{}])[0], status=201)
                return Response.json({"detail":"Unsupported operation"}, status=405)

            m = re_match = None
            # ID routes for products/customers/suppliers/categories/product types/expenses/repairs
            parts = path.strip("/").split("/")
            if len(parts)==3 and parts[0]=="api" and parts[1] in {"products","customers","suppliers","categories","product-types","expenses","repairs"}:
                table = {"products":"products","customers":"customers","suppliers":"suppliers","categories":"categories","product-types":"product_types","expenses":"expenses","repairs":"repairs"}[parts[1]]
                try: rid=int(parts[2])
                except: return Response.json({"detail":"Invalid id"}, status=400)
                if method=="DELETE":
                    await self.env.DB.prepare(f"DELETE FROM {table} WHERE id=?").bind(rid).run()
                    return Response.json({"ok":True})
                if method=="PUT":
                    b=await body_json(request)
                    allowed={
                        "products":["sku","barcode","name","category","product_type","cost","sale_price","quantity","reorder_level","imei_required","serial_required","warranty_months","image_url","wholesale_price","vip_price","active"],
                        "customers":["code","name","phone","address","balance"],"suppliers":["code","name","phone","address","balance"],
                        "categories":["name","image_url","active"],"product_types":["name","code","active"],"expenses":["description","amount","created_at","category","payment_method","notes"],
                        "repairs":["ticket_no","customer_id","device_name","imei_or_serial","problem","status","estimated_cost","created_at","sales_price","customer_phone","customer_address","technician","warranty_days","notes"]}[table]
                    cols=[c for c in allowed if c in b]
                    if not cols:return Response.json({"detail":"No fields supplied"},status=400)
                    sets=",".join([f"{c}=?" for c in cols]); vals=[b[c] for c in cols]+[rid]
                    await self.env.DB.prepare(f"UPDATE {table} SET {sets} WHERE id=?").bind(*vals).run()
                    r=await self.env.DB.prepare(f"SELECT * FROM {table} WHERE id=?").bind(rid).run()
                    rows=r.get("results",[])
                    return Response.json(rows[0] if rows else {}, status=200 if rows else 404)
                if method=="GET":
                    r=await self.env.DB.prepare(f"SELECT * FROM {table} WHERE id=?").bind(rid).run()
                    rows=r.get("results",[])
                    return Response.json(rows[0] if rows else {"detail":"Not found"}, status=200 if rows else 404)

            # Price checker uses products endpoint client-side; keep a direct alias.
            if path == "/api/price-check" and method == "GET":
                r=await self.env.DB.prepare("SELECT * FROM products ORDER BY id DESC").run()
                return Response.json(r.get("results", []))

            # Settings as key/value store
            if path == "/api/settings":
                if method == "GET":
                    r=await self.env.DB.prepare('SELECT "key", value FROM settings ORDER BY "key"').run()
                    return Response.json({str(x.get("key")): x.get("value") for x in r.get("results", [])})
                if method == "POST":
                    b=await body_json(request); key=str(b.get("key","")); value=str(b.get("value",""))
                    await self.env.DB.prepare('INSERT INTO settings("key",value) VALUES(?,?) ON CONFLICT("key") DO UPDATE SET value=excluded.value').bind(key,value).run()
                    return Response.json({"key":key,"value":value})

            # Serve static frontend
            if path == "/api/dashboard-test" and method == "GET":
            return await self.env.ASSETS.fetch(request)
        except Exception as e:
            return Response.json({"detail": "Server error", "error": str(e)}, status=500)
