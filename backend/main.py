from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pathlib import Path
from pydantic import BaseModel
from sqlalchemy import create_engine, String, Integer, Numeric, Boolean, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, Session
import hashlib, hmac, base64, html as html_lib
import shutil, sqlite3, re, secrets
from datetime import datetime
import os, io
from openpyxl import Workbook, load_workbook

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sif_mobile.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {"pool_pre_ping": True})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password), password_hash)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(40), default="admin")
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class ProductType(Base):
    __tablename__ = "product_types"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    barcode: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    category: Mapped[str] = mapped_column(String(80), default="Accessories")
    product_type: Mapped[str] = mapped_column(String(40), default="accessory")
    cost: Mapped[float] = mapped_column(Numeric(14,2), default=0)
    sale_price: Mapped[float] = mapped_column(Numeric(14,2), default=0)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    reorder_level: Mapped[int] = mapped_column(Integer, default=0)
    imei_required: Mapped[bool] = mapped_column(Boolean, default=False)
    serial_required: Mapped[bool] = mapped_column(Boolean, default=False)
    warranty_months: Mapped[int] = mapped_column(Integer, default=0)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    wholesale_price: Mapped[float] = mapped_column(Numeric(14,2), default=0)
    vip_price: Mapped[float] = mapped_column(Numeric(14,2), default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Device(Base):
    __tablename__ = "devices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    imei1: Mapped[str | None] = mapped_column(String(80), unique=True, nullable=True)
    imei2: Mapped[str | None] = mapped_column(String(80), unique=True, nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True)
    color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    storage: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="in_stock")


class Sale(Base):
    __tablename__ = "sales"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_no: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), nullable=True)
    subtotal: Mapped[float] = mapped_column(Numeric(14,2), default=0)
    discount: Mapped[float] = mapped_column(Numeric(14,2), default=0)
    total: Mapped[float] = mapped_column(Numeric(14,2), default=0)
    payment_method: Mapped[str] = mapped_column(String(30), default="cash")
    status: Mapped[str] = mapped_column(String(30), default="paid")
    vat_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    vat_rate: Mapped[float] = mapped_column(Numeric(5,2), default=0)
    vat_amount: Mapped[float] = mapped_column(Numeric(14,2), default=0)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class SaleItem(Base):
    __tablename__ = "sale_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[float] = mapped_column(Numeric(14,2), default=0)
    total: Mapped[float] = mapped_column(Numeric(14,2), default=0)

class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(180), index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(String(250), nullable=True)
    balance: Mapped[float] = mapped_column(Numeric(14,2), default=0)

class Repair(Base):
    __tablename__ = "repairs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_no: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), nullable=True)
    device_name: Mapped[str] = mapped_column(String(180))
    imei_or_serial: Mapped[str | None] = mapped_column(String(120), nullable=True)
    problem: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(40), default="received")
    estimated_cost: Mapped[float] = mapped_column(Numeric(14,2), default=0)
    sales_price: Mapped[float] = mapped_column(Numeric(14,2), default=0)
    customer_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    customer_address: Mapped[str | None] = mapped_column(String(250), nullable=True)
    technician: Mapped[str | None] = mapped_column(String(120), nullable=True)
    warranty_days: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Supplier(Base):
    __tablename__ = "suppliers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(180), index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(String(250), nullable=True)
    balance: Mapped[float] = mapped_column(Numeric(14,2), default=0)

class Purchase(Base):
    __tablename__ = "purchases"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_no: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"), nullable=True)
    subtotal: Mapped[float] = mapped_column(Numeric(14,2), default=0)
    vat_rate: Mapped[float] = mapped_column(Numeric(5,2), default=0)
    vat_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    total: Mapped[float] = mapped_column(Numeric(14,2), default=0)
    payment_method: Mapped[str] = mapped_column(String(30), default="cash")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class PurchaseItem(Base):
    __tablename__ = "purchase_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    purchase_id: Mapped[int] = mapped_column(ForeignKey("purchases.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_cost: Mapped[float] = mapped_column(Numeric(14,2), default=0)
    total: Mapped[float] = mapped_column(Numeric(14,2), default=0)

class Expense(Base):
    __tablename__ = "expenses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String(250))
    amount: Mapped[float] = mapped_column(Numeric(14,2), default=0)
    category: Mapped[str] = mapped_column(String(100), default="General")
    payment_method: Mapped[str] = mapped_column(String(30), default="cash")
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AccountPayment(Base):
    __tablename__ = "account_payments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    party_type: Mapped[str] = mapped_column(String(20))  # customer / supplier
    party_id: Mapped[int] = mapped_column(Integer)
    amount: Mapped[float] = mapped_column(Numeric(14,2), default=0)
    payment_method: Mapped[str] = mapped_column(String(30), default="cash")
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class SalesReturn(Base):
    __tablename__ = "sales_returns"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    return_no: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"))
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), nullable=True)
    total: Mapped[float] = mapped_column(Numeric(14,2), default=0)
    payment_method: Mapped[str] = mapped_column(String(30), default="cash")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class SalesReturnItem(Base):
    __tablename__ = "sales_return_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    return_id: Mapped[int] = mapped_column(ForeignKey("sales_returns.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[float] = mapped_column(Numeric(14,2), default=0)
    total: Mapped[float] = mapped_column(Numeric(14,2), default=0)

class PurchaseReturn(Base):
    __tablename__ = "purchase_returns"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    return_no: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    purchase_id: Mapped[int] = mapped_column(ForeignKey("purchases.id"))
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"), nullable=True)
    total: Mapped[float] = mapped_column(Numeric(14,2), default=0)
    payment_method: Mapped[str] = mapped_column(String(30), default="cash")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class PurchaseReturnItem(Base):
    __tablename__ = "purchase_return_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    return_id: Mapped[int] = mapped_column(ForeignKey("purchase_returns.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_cost: Mapped[float] = mapped_column(Numeric(14,2), default=0)
    total: Mapped[float] = mapped_column(Numeric(14,2), default=0)

class Setting(Base):
    __tablename__ = "settings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    value: Mapped[str] = mapped_column(String(500), default="")

class LoginIn(BaseModel):
    username: str
    password: str

class UserIn(BaseModel):
    username: str
    password: str = ""
    role: str = "cashier"
    active: bool = True

class ProductIn(BaseModel):
    sku: str
    barcode: str | None = None
    name: str
    category: str = "Accessories"
    product_type: str = "accessory"
    cost: float = 0
    sale_price: float = 0
    quantity: int = 0
    reorder_level: int = 0
    imei_required: bool = False
    serial_required: bool = False
    warranty_months: int = 0
    image_url: str | None = None
    wholesale_price: float = 0
    vip_price: float = 0

class SaleItemIn(BaseModel):
    product_id: int
    quantity: int = 1
    unit_price: float | None = None

class SaleIn(BaseModel):
    customer_id: int | None = None
    discount: float = 0
    payment_method: str = "cash"
    vat_enabled: bool = False
    vat_rate: float = 0
    currency: str = "USD"
    items: list[SaleItemIn]

class SupplierIn(BaseModel):
    code: str
    name: str
    phone: str | None = None
    address: str | None = None

class PurchaseItemIn(BaseModel):
    product_id: int
    quantity: int = 1
    unit_cost: float | None = None

class PurchaseIn(BaseModel):
    supplier_id: int | None = None
    payment_method: str = "cash"
    vat_enabled: bool = False
    vat_rate: float = 0
    items: list[PurchaseItemIn]

class RepairIn(BaseModel):
    customer_id: int | None = None
    device_name: str
    imei_or_serial: str | None = None
    problem: str
    status: str = "received"
    estimated_cost: float = 0
    sales_price: float = 0
    customer_phone: str | None = None
    customer_address: str | None = None
    technician: str | None = None
    warranty_days: int = 0
    notes: str | None = None

class SettingIn(BaseModel):
    key: str
    value: str

class CategoryIn(BaseModel):
    name: str
    image_url: str | None = None

class ProductTypeIn(BaseModel):
    name: str
    code: str | None = None


class CustomerIn(BaseModel):
    code: str
    name: str
    phone: str | None = None
    address: str | None = None

app = FastAPI(title="SIF Mobile & Computer API", version="0.2.2")

@app.middleware("http")
async def no_cache(request, call_next):
    response = await call_next(request)
    if request.url.path == "/" or request.url.path.endswith(".html"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
    return response
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/", include_in_schema=False)
def web_app():
    return FileResponse(Path(__file__).resolve().parent.parent / "frontend" / "index.html")

@app.get("/brand-logo.png", include_in_schema=False)
def brand_logo():
    logo_path = Path(__file__).resolve().parent.parent / "frontend" / "brand-logo.png"
    return FileResponse(logo_path, media_type="image/png")

def demo_product_image(name: str, category: str) -> str:
    # Professional lightweight product-card image, stored directly with the demo item.
    title = html_lib.escape(name[:28])
    cat = html_lib.escape(category[:18])
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="720" height="520" viewBox="0 0 720 520">
    <defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#eef6ff"/><stop offset="1" stop-color="#d9e8f7"/></linearGradient></defs>
    <rect width="720" height="520" rx="30" fill="url(#g)"/>
    <circle cx="360" cy="210" r="120" fill="#ffffff" stroke="#c7d9ea" stroke-width="5"/>
    <rect x="300" y="120" width="120" height="180" rx="22" fill="#0a1d35"/>
    <rect x="312" y="135" width="96" height="140" rx="12" fill="#1a8df0"/>
    <circle cx="360" cy="286" r="7" fill="#ffffff"/>
    <text x="360" y="365" text-anchor="middle" font-family="Arial" font-size="28" font-weight="700" fill="#10213d">{title}</text>
    <text x="360" y="405" text-anchor="middle" font-family="Arial" font-size="18" fill="#718198">{cat}</text>
    <text x="360" y="450" text-anchor="middle" font-family="Arial" font-size="15" font-weight="700" fill="#148bf0">SIF MOBILE &amp; COMPUTER</text>
    </svg>"""
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")

def seed_demo_catalog(db):
    if db.query(Product).count() > 0:
        return
    items = [
        ("IPH15P256","iPhone 15 Pro 256GB","MOBILE","mobile",900,1100,990,950,7,"352099150001"),
        ("IPH15PM256","iPhone 15 Pro Max 256GB","MOBILE","mobile",1050,1290,1160,1120,5,"352099150002"),
        ("S24U256","Samsung Galaxy S24 Ultra 256GB","MOBILE","mobile",760,950,850,820,6,"352099150003"),
        ("A55-256","Samsung Galaxy A55 256GB","MOBILE","mobile",285,360,325,310,12,"352099150004"),
        ("REDMI13P","Xiaomi Redmi Note 13 Pro","MOBILE","mobile",210,285,255,240,10,"352099150005"),
        ("MBA-M2-512","MacBook Air M2 512GB","COMPUTERS","computer",980,1250,1120,1080,4,"MBA2026001"),
        ("DELL-I5-16","Dell Latitude i5 16GB","COMPUTERS","computer",520,690,620,590,5,"DELL2026002"),
        ("HP-I7-16","HP ProBook i7 16GB","COMPUTERS","computer",610,790,710,680,3,"HP2026003"),
        ("LEN-I5-16","Lenovo ThinkPad i5 16GB","COMPUTERS","computer",550,720,650,620,6,"LEN2026004"),
        ("ASUS-I7-16","ASUS VivoBook i7 16GB","COMPUTERS","computer",590,770,690,660,4,"ASUS2026005"),
        ("USBC-1M","USB-C Cable 1m","ACCESSORIES","accessory",4,10,8,7,35,"ACC10001"),
        ("20W-CHG","20W Fast Charger","ACCESSORIES","accessory",7,18,15,13,28,"ACC10002"),
        ("65W-CHG","65W Laptop USB-C Charger","ACCESSORIES","accessory",18,39,33,29,15,"ACC10003"),
        ("AIRPODS2","AirPods 2","ACCESSORIES","accessory",85,125,110,102,8,"ACC10004"),
        ("AIRPODS-P2","AirPods Pro 2","ACCESSORIES","accessory",170,235,210,195,6,"ACC10005"),
        ("BT-MOUSE","Bluetooth Wireless Mouse","ACCESSORIES","accessory",8,20,17,15,22,"ACC10006"),
        ("KB-WL","Wireless Keyboard","ACCESSORIES","accessory",12,29,25,22,16,"ACC10007"),
        ("PHONE-CASE","Premium Phone Case","ACCESSORIES","accessory",5,15,12,10,40,"ACC10008"),
    ]
    for sku,name,cat,ptype,cost,retail,wholesale,vip,qty,barcode in items:
        db.add(Product(
            sku=sku, name=name, category=cat.title(), product_type=ptype,
            cost=cost, sale_price=retail, wholesale_price=wholesale, vip_price=vip,
            quantity=qty, reorder_level=3, barcode=barcode,
            warranty_months=12 if ptype in ("mobile","computer") else 0,
            image_url=demo_product_image(name, cat.title())
        ))
    db.commit()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(engine)
    # Seed editable catalog categories and types.
    db_seed = SessionLocal()
    try:
        defaults = [("Mobile Phones","mobile"),("Computers & Laptops","computer"),("Accessories","accessory")]
        for name, code in defaults:
            if not db_seed.query(Category).filter(Category.name == name).first():
                db_seed.add(Category(name=name))
            if not db_seed.query(ProductType).filter(ProductType.code == code).first():
                db_seed.add(ProductType(name={"mobile":"Mobile","computer":"Computer","accessory":"Accessory"}[code], code=code))
        # Normalize the names of the three built-in types for existing databases.
        type_names={"mobile":"Mobile","computer":"Computer","accessory":"Accessory"}
        for code,label in type_names.items():
            t=db_seed.query(ProductType).filter(ProductType.code==code,ProductType.active==True).first()
            if t: t.name=label
        db_seed.commit()
    finally:
        db_seed.close()
    # Lightweight SQLite migration for existing SIF test databases.
    if DATABASE_URL.startswith("sqlite"):
        from sqlalchemy import text as sql_text
        with engine.begin() as conn:
            cols = {r[1] for r in conn.execute(sql_text("PRAGMA table_info(products)")).fetchall()}
            additions = {
                "image_url": "ALTER TABLE products ADD COLUMN image_url VARCHAR(500)",
                "wholesale_price": "ALTER TABLE products ADD COLUMN wholesale_price NUMERIC(14,2) DEFAULT 0",
                "vip_price": "ALTER TABLE products ADD COLUMN vip_price NUMERIC(14,2) DEFAULT 0",
            }
            for name, stmt in additions.items():
                if name not in cols:
                    conn.execute(sql_text(stmt))
            sale_cols = {r[1] for r in conn.execute(sql_text("PRAGMA table_info(sales)")).fetchall()}
            sale_add = {
                "vat_enabled": "ALTER TABLE sales ADD COLUMN vat_enabled BOOLEAN DEFAULT 0",
                "vat_rate": "ALTER TABLE sales ADD COLUMN vat_rate NUMERIC(5,2) DEFAULT 0",
                "vat_amount": "ALTER TABLE sales ADD COLUMN vat_amount NUMERIC(14,2) DEFAULT 0",
                "currency": "ALTER TABLE sales ADD COLUMN currency VARCHAR(10) DEFAULT 'USD'",
            }
            for name, stmt in sale_add.items():
                if name not in sale_cols:
                    conn.execute(sql_text(stmt))

            # Repair fields added in later releases.
            repair_cols = {r[1] for r in conn.execute(sql_text("PRAGMA table_info(repairs)")).fetchall()}
            repair_add = {
                "sales_price": "ALTER TABLE repairs ADD COLUMN sales_price NUMERIC(14,2) DEFAULT 0",
                "customer_phone": "ALTER TABLE repairs ADD COLUMN customer_phone VARCHAR(50)",
                "customer_address": "ALTER TABLE repairs ADD COLUMN customer_address VARCHAR(250)",
                "technician": "ALTER TABLE repairs ADD COLUMN technician VARCHAR(120)",
                "warranty_days": "ALTER TABLE repairs ADD COLUMN warranty_days INTEGER DEFAULT 0",
                "notes": "ALTER TABLE repairs ADD COLUMN notes VARCHAR(1000)",
            }
            for name, stmt in repair_add.items():
                if name not in repair_cols:
                    conn.execute(sql_text(stmt))
            expense_cols = {r[1] for r in conn.execute(sql_text("PRAGMA table_info(expenses)")).fetchall()}
            expense_add = {
                "category": "ALTER TABLE expenses ADD COLUMN category VARCHAR(100) DEFAULT 'General'",
                "payment_method": "ALTER TABLE expenses ADD COLUMN payment_method VARCHAR(30) DEFAULT 'cash'",
                "notes": "ALTER TABLE expenses ADD COLUMN notes VARCHAR(500)",
            }
            for name, stmt in expense_add.items():
                if name not in expense_cols:
                    conn.execute(sql_text(stmt))
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(username="admin", password_hash=hash_password("admin"), role="admin"))
            db.commit()
        # Load demo catalog on a fresh local database.
        seed_demo_catalog(db)
    finally:
        db.close()

def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/products/export")
def export_products(db: Session = Depends(db_session)):
    wb=Workbook(); ws=wb.active; ws.title="Products"
    headers=["SKU","Barcode","Name","Category","Type","Cost","Retail Price","Wholesale Price","VIP Price","Quantity","Reorder Level","Warranty Months","IMEI Required","Serial Required","Photo URL"]
    ws.append(headers)
    for p in db.query(Product).filter(Product.active==True).order_by(Product.id.asc()).all():
        ws.append([p.sku,p.barcode or "",p.name,p.category or "",p.product_type or "",float(p.cost or 0),float(p.sale_price or 0),float(p.wholesale_price or 0),float(p.vip_price or 0),int(p.quantity or 0),int(p.reorder_level or 0),int(p.warranty_months or 0),"Yes" if p.imei_required else "No","Yes" if p.serial_required else "No",p.image_url or ""])
    for c in ws[1]: c.font=c.font.copy(bold=True)
    ws.freeze_panes="A2"
    bio=io.BytesIO(); wb.save(bio); bio.seek(0)
    return StreamingResponse(bio,media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",headers={"Content-Disposition":"attachment; filename=SIF_Products.xlsx"})

@app.get("/api/products/export.xlsx")
def export_products_xlsx(db: Session = Depends(db_session)):
    return export_products(db)

@app.get("/api/products/template")
def product_import_template():
    wb=Workbook(); ws=wb.active; ws.title="Products"
    headers=["SKU","Barcode","Name","Category","Type","Cost","Retail Price","Wholesale Price","VIP Price","Quantity","Reorder Level","Warranty Months","IMEI Required","Serial Required","Photo URL"]
    ws.append(headers); ws.append(["SKU-001","123456789","Example Product","Accessories","accessory",10,15,13,12,10,2,12,"No","No",""])
    for c in ws[1]: c.font=c.font.copy(bold=True)
    ws.freeze_panes="A2"
    bio=io.BytesIO(); wb.save(bio); bio.seek(0)
    return StreamingResponse(bio,media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",headers={"Content-Disposition":"attachment; filename=SIF_Products_Import_Template.xlsx"})

@app.get("/api/products/template.xlsx")
def product_import_template_xlsx():
    return product_import_template()

@app.post("/api/excel/import-products")
async def import_products(file: UploadFile = File(...), db: Session = Depends(db_session)):
    raw = await file.read()
    name = (file.filename or "").lower()
    try:
        if name.endswith((".xlsx", ".xlsm")):
            wb = load_workbook(io.BytesIO(raw), data_only=True)
            ws = wb.active
            rows = list(ws.iter_rows(values_only=True))
        elif name.endswith(".xls"):
            # Support the HTML-table .xls files produced by the earlier template fallback.
            from html.parser import HTMLParser
            class _TableParser(HTMLParser):
                def __init__(self):
                    super().__init__(); self.rows=[]; self.row=None; self.cell=[]; self.in_td=False
                def handle_starttag(self, tag, attrs):
                    if tag.lower() == "tr": self.row=[]
                    elif tag.lower() in ("td","th"): self.cell=[]; self.in_td=True
                def handle_endtag(self, tag):
                    if tag.lower() in ("td","th") and self.in_td:
                        self.row.append("".join(self.cell).strip()); self.in_td=False
                    elif tag.lower()=="tr" and self.row is not None:
                        if self.row: self.rows.append(tuple(self.row))
                        self.row=None
                def handle_data(self, data):
                    if self.in_td: self.cell.append(data)
            parser=_TableParser(); parser.feed(raw.decode("utf-8", errors="ignore")); rows=parser.rows
            if not rows: raise ValueError("The .xls file does not contain a readable table")
        else:
            raise ValueError("Please upload .xlsx, .xlsm, or .xls")
    except Exception as e:
        raise HTTPException(400, f"Invalid Excel file: {e}")
    if not rows: raise HTTPException(400,"Excel file is empty")
    headers=[str(x or "").strip().lower() for x in rows[0]]
    if "sku" not in headers or "name" not in headers: raise HTTPException(400,"Excel must contain SKU and Name columns")
    def val(row,key,default=""):
        try:i=headers.index(key.lower())
        except ValueError:return default
        return row[i] if i<len(row) and row[i] is not None else default
    def num(row,key,default=0):
        try:return float(val(row,key,default) or default)
        except:return float(default)
    def integer(row,key,default=0): return int(num(row,key,default))
    def yes(row,key): return str(val(row,key,"No")).strip().lower() in ("yes","true","1","y")
    created=updated=0; errors=[]
    for rn,row in enumerate(rows[1:],2):
        if not any(x not in (None,"") for x in row): continue
        sku=str(val(row,"sku","")).strip(); name=str(val(row,"name","")).strip()
        if not sku or not name: errors.append(f"Row {rn}: SKU and Name are required"); continue
        try:
            category=str(val(row,"category","Accessories")).strip() or "Accessories"
            ptype=str(val(row,"type",val(row,"product_type","accessory"))).strip() or "accessory"
            barcode=str(val(row,"barcode","")).strip() or None
            if barcode:
                clash=db.query(Product).filter(Product.barcode==barcode,Product.sku!=sku).first()
                if clash: raise ValueError(f"Barcode {barcode} already belongs to SKU {clash.sku}")
            if not db.query(Category).filter(Category.name==category,Category.active==True).first(): db.add(Category(name=category,active=True)); db.flush()
            if not db.query(ProductType).filter(ProductType.code==ptype,ProductType.active==True).first(): db.add(ProductType(name=ptype.title(),code=ptype,active=True)); db.flush()
            fields=dict(sku=sku,barcode=barcode,name=name,category=category,product_type=ptype,cost=num(row,"cost"),sale_price=num(row,"retail price",num(row,"sale_price")),wholesale_price=num(row,"wholesale price",num(row,"wholesale_price")),vip_price=num(row,"vip price",num(row,"vip_price")),quantity=integer(row,"quantity"),reorder_level=integer(row,"reorder level",integer(row,"reorder_level")),warranty_months=integer(row,"warranty months",integer(row,"warranty_months")),imei_required=yes(row,"imei required"),serial_required=yes(row,"serial required"),image_url=str(val(row,"photo url",val(row,"image_url",""))).strip() or None)
            p=db.query(Product).filter(Product.sku==sku).first()
            if p:
                for k,v in fields.items(): setattr(p,k,v)
                updated+=1
            else: db.add(Product(**fields)); created+=1
        except Exception as e: errors.append(f"Row {rn}: {e}")
    if errors and created==0 and updated==0: db.rollback(); raise HTTPException(400,"Import failed: "+" | ".join(errors[:8]))
    db.commit(); return {"success":True,"created":created,"updated":updated,"errors":errors[:20],"error_count":len(errors)}


@app.post("/api/products/import")
async def import_products_legacy(file: UploadFile = File(...), db: Session = Depends(db_session)):
    return await import_products(file, db)

@app.get("/api/products/{product_id}")
def product_detail(product_id: int, db: Session = Depends(db_session)):
    p = db.query(Product).filter(Product.id == product_id, Product.active == True).first()
    if not p:
        raise HTTPException(404, "Product not found")
    return {"id":p.id,"sku":p.sku,"barcode":p.barcode,"name":p.name,"cost":float(p.cost),
            "sale_price":float(p.sale_price),"quantity":p.quantity,"reorder_level":p.reorder_level,
            "imei_required":p.imei_required,"serial_required":p.serial_required,
            "image_url":p.image_url,"wholesale_price":float(p.wholesale_price),"vip_price":float(p.vip_price)}

@app.post("/api/sales")
def create_sale(data: SaleIn, db: Session = Depends(db_session)):
    if not data.items:
        raise HTTPException(400, "Sale must contain at least one item")
    subtotal = 0.0
    checked = []
    for item in data.items:
        if item.quantity <= 0:
            raise HTTPException(400, "Quantity must be greater than zero")
        p = db.query(Product).filter(Product.id == item.product_id, Product.active == True).first()
        if not p:
            raise HTTPException(404, f"Product {item.product_id} not found")
        if p.quantity < item.quantity:
            raise HTTPException(400, f"Insufficient stock for {p.name}. Available: {p.quantity}")
        price = float(p.sale_price) if item.unit_price is None else float(item.unit_price)
        line_total = price * item.quantity
        subtotal += line_total
        checked.append((p, item.quantity, price, line_total))
    net = max(0.0, subtotal - float(data.discount))
    vat_amount = round(net * (float(data.vat_rate) / 100.0), 2) if data.vat_enabled else 0.0
    total = round(net + vat_amount, 2)
    next_no = db.query(func.count(Sale.id)).scalar() + 1
    invoice_no = f"INV-{next_no:05d}"
    sale = Sale(invoice_no=invoice_no, customer_id=data.customer_id, subtotal=subtotal,
                discount=float(data.discount), total=total, payment_method=data.payment_method,
                vat_enabled=data.vat_enabled, vat_rate=float(data.vat_rate) if data.vat_enabled else 0,
                vat_amount=vat_amount, currency=data.currency)
    db.add(sale)
    db.flush()
    if data.customer_id and data.payment_method == "account":
        c = db.query(Customer).filter(Customer.id == data.customer_id).first()
        if c: c.balance = float(c.balance or 0) + total
    for p, qty, price, line_total in checked:
        p.quantity -= qty
        db.add(SaleItem(sale_id=sale.id, product_id=p.id, quantity=qty,
                        unit_price=price, total=line_total))
    db.commit()
    return {"success":True,"id":sale.id,"invoice_no":sale.invoice_no,"subtotal":subtotal,
            "discount":float(data.discount),"vat":vat_amount,"vat_rate":float(sale.vat_rate),"total":total}

@app.get("/api/sales")
def list_sales(db: Session = Depends(db_session)):
    rows = db.query(Sale).order_by(Sale.id.desc()).limit(100).all()
    return [{"id":s.id,"invoice_no":s.invoice_no,"customer_id":s.customer_id,
             "customer_name":(db.query(Customer).filter(Customer.id==s.customer_id).first().name if s.customer_id and db.query(Customer).filter(Customer.id==s.customer_id).first() else "Walk-in Customer"),
             "subtotal":float(s.subtotal),"discount":float(s.discount),"total":float(s.total),
             "payment_method":s.payment_method,"status":s.status,"vat_enabled":s.vat_enabled,
             "vat_rate":float(s.vat_rate),"vat_amount":float(s.vat_amount),
             "created_at":s.created_at.isoformat()} for s in rows]



@app.get("/api/sales/{sale_id}")
def get_sale(sale_id: int, db: Session = Depends(db_session)):
    s=db.query(Sale).filter(Sale.id==sale_id).first()
    if not s: raise HTTPException(404,"Sale not found")
    c=db.query(Customer).filter(Customer.id==s.customer_id).first() if s.customer_id else None
    items=[]
    for it in db.query(SaleItem).filter(SaleItem.sale_id==s.id).all():
        p=db.query(Product).filter(Product.id==it.product_id).first()
        items.append({"id":it.id,"product_id":it.product_id,"name":p.name if p else "Deleted Product","sku":p.sku if p else "","barcode":p.barcode if p else "","quantity":it.quantity,"unit_price":float(it.unit_price),"total":float(it.total)})
    return {"id":s.id,"invoice_no":s.invoice_no,"customer_id":s.customer_id,"customer_name":c.name if c else "Walk-in Customer","subtotal":float(s.subtotal),"discount":float(s.discount),"total":float(s.total),"payment_method":s.payment_method,"status":s.status,"vat_enabled":s.vat_enabled,"vat_rate":float(s.vat_rate),"vat_amount":float(s.vat_amount),"currency":s.currency,"created_at":s.created_at.isoformat(),"items":items}

@app.put("/api/sales/{sale_id}")
def update_sale(sale_id:int, data:SaleIn, db:Session=Depends(db_session)):
    s=db.query(Sale).filter(Sale.id==sale_id).first()
    if not s: raise HTTPException(404,"Sale not found")
    if not data.items: raise HTTPException(400,"Sale must contain at least one item")
    old=db.query(SaleItem).filter(SaleItem.sale_id==s.id).all()
    # restore old stock first
    for it in old:
        p=db.query(Product).filter(Product.id==it.product_id).first()
        if p: p.quantity += it.quantity
    db.query(SaleItem).filter(SaleItem.sale_id==s.id).delete(synchronize_session=False)
    subtotal=0.0; checked=[]
    try:
        for item in data.items:
            p=db.query(Product).filter(Product.id==item.product_id,Product.active==True).first()
            if not p: raise HTTPException(404,f"Product {item.product_id} not found")
            if item.quantity<=0: raise HTTPException(400,"Quantity must be greater than zero")
            if p.quantity < item.quantity: raise HTTPException(400,f"Insufficient stock for {p.name}. Available: {p.quantity}")
            price=float(p.sale_price) if item.unit_price is None else float(item.unit_price)
            ln=price*item.quantity; subtotal+=ln; checked.append((p,item.quantity,price,ln))
        net=max(0.0,subtotal-float(data.discount)); vat=round(net*(float(data.vat_rate)/100),2) if data.vat_enabled else 0.0; total=round(net+vat,2)
        if s.customer_id and s.payment_method == "account":
            oldc=db.query(Customer).filter(Customer.id==s.customer_id).first()
            if oldc: oldc.balance=float(oldc.balance or 0)-float(s.total or 0)
        if data.customer_id and data.payment_method == "account":
            newc=db.query(Customer).filter(Customer.id==data.customer_id).first()
            if newc: newc.balance=float(newc.balance or 0)+total
        s.customer_id=data.customer_id; s.subtotal=subtotal; s.discount=float(data.discount); s.total=total; s.payment_method=data.payment_method; s.vat_enabled=data.vat_enabled; s.vat_rate=float(data.vat_rate) if data.vat_enabled else 0; s.vat_amount=vat; s.currency=data.currency
        for p,qty,price,ln in checked:
            p.quantity-=qty; db.add(SaleItem(sale_id=s.id,product_id=p.id,quantity=qty,unit_price=price,total=ln))
        db.commit()
        return {"success":True,"id":s.id,"invoice_no":s.invoice_no,"subtotal":subtotal,"discount":float(s.discount),"vat":vat,"total":total}
    except Exception:
        db.rollback(); raise

@app.delete("/api/sales/{sale_id}")
def delete_sale(sale_id:int, db:Session=Depends(db_session)):
    s=db.query(Sale).filter(Sale.id==sale_id).first()
    if not s: raise HTTPException(404,"Sale not found")
    for it in db.query(SaleItem).filter(SaleItem.sale_id==s.id).all():
        p=db.query(Product).filter(Product.id==it.product_id).first()
        if p: p.quantity += it.quantity
    if s.customer_id and s.payment_method == "account":
        c=db.query(Customer).filter(Customer.id==s.customer_id).first()
        if c: c.balance=float(c.balance or 0)-float(s.total or 0)
    db.query(SaleItem).filter(SaleItem.sale_id==s.id).delete(synchronize_session=False)
    db.delete(s); db.commit(); return {"success":True}

@app.put("/api/products/{product_id}")
def update_product(product_id: int, data: ProductIn, db: Session = Depends(db_session)):
    p = db.query(Product).filter(Product.id == product_id, Product.active == True).first()
    if not p:
        raise HTTPException(404, "Product not found")
    duplicate = db.query(Product).filter(Product.sku == data.sku, Product.id != product_id).first()
    if duplicate:
        raise HTTPException(409, "SKU already exists")
    if data.barcode:
        duplicate_barcode = db.query(Product).filter(Product.barcode == data.barcode, Product.id != product_id).first()
        if duplicate_barcode:
            raise HTTPException(409, "Barcode already exists")
    for key, value in data.model_dump().items():
        setattr(p, key, value)
    db.commit()
    return {"success": True, "id": p.id}

@app.delete("/api/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(db_session)):
    p = db.query(Product).filter(Product.id == product_id, Product.active == True).first()
    if not p:
        raise HTTPException(404, "Product not found")
    p.active = False
    db.commit()
    return {"success": True}

@app.get("/api/price-check")
def price_check(q: str = "", customer_type: str = "retail", db: Session = Depends(db_session)):
    rows = db.query(Product).filter(Product.active == True).all()
    ql = q.strip().lower()
    if ql:
        rows = [p for p in rows if ql in (p.name or "").lower() or ql in (p.sku or "").lower() or ql in (p.barcode or "").lower()]
    rate = float((db.query(Setting).filter(Setting.key=="usd_lbp").first().value) if db.query(Setting).filter(Setting.key=="usd_lbp").first() else 89500)
    out=[]
    for p in rows:
        if customer_type == "wholesale": label,price = "Wholesale",float(p.wholesale_price)
        elif customer_type == "vip": label,price = "VIP",float(p.vip_price)
        else: label,price = "Retail",float(p.sale_price)
        out.append({"id":p.id,"name":p.name,"sku":p.sku,"barcode":p.barcode,"stock":p.quantity,"image_url":p.image_url,"selected_type":label,"customer_price":price,"customer_price_lbp":round(price*rate),"usd_lbp":rate})
    return out

@app.post("/api/stock/adjust")
def adjust_stock(product_id: int, quantity: int, db: Session = Depends(db_session)):
    p = db.query(Product).filter(Product.id == product_id, Product.active == True).first()
    if not p:
        raise HTTPException(404, "Product not found")
    new_qty = p.quantity + quantity
    if new_qty < 0:
        raise HTTPException(400, "Stock cannot become negative")
    p.quantity = new_qty
    db.commit()
    return {"success":True,"product_id":p.id,"quantity":p.quantity}

@app.get("/api/suppliers")
def list_suppliers(db: Session = Depends(db_session)):
    return [{"id":s.id,"code":s.code,"name":s.name,"phone":s.phone,"address":s.address,"balance":float(s.balance)} for s in db.query(Supplier).order_by(Supplier.id.desc()).all()]

@app.post("/api/suppliers")
def create_supplier(data: SupplierIn, db: Session = Depends(db_session)):
    s=Supplier(**data.model_dump()); db.add(s); db.commit(); db.refresh(s); return {"id":s.id,"code":s.code,"name":s.name,"phone":s.phone,"address":s.address,"balance":float(s.balance)}

@app.get("/api/purchases")
def list_purchases(db: Session = Depends(db_session)):
    return [{"id":p.id,"invoice_no":p.invoice_no,"supplier_id":p.supplier_id,"subtotal":float(p.subtotal),"vat_enabled":p.vat_enabled,"vat_rate":float(p.vat_rate),"total":float(p.total),"payment_method":p.payment_method,"created_at":p.created_at.isoformat()} for p in db.query(Purchase).order_by(Purchase.id.desc()).all()]

@app.post("/api/purchases")
def create_purchase(data: PurchaseIn, db: Session = Depends(db_session)):
    if not data.items: raise HTTPException(400,"Purchase must contain at least one item")
    sub=0.0; checked=[]
    for item in data.items:
        p=db.query(Product).filter(Product.id==item.product_id,Product.active==True).first()
        if not p: raise HTTPException(404,f"Product {item.product_id} not found")
        if item.quantity<=0: raise HTTPException(400,"Quantity must be greater than zero")
        cost=float(item.unit_cost if item.unit_cost is not None else p.cost); total=cost*item.quantity; sub+=total; checked.append((p,item.quantity,cost,total))
    vat=round(sub*(data.vat_rate/100),2) if data.vat_enabled else 0.0; total=round(sub+vat,2)
    inv=f"PUR-{db.query(Purchase).count()+1:05d}"; pur=Purchase(invoice_no=inv,supplier_id=data.supplier_id,subtotal=sub,vat_enabled=data.vat_enabled,vat_rate=data.vat_rate if data.vat_enabled else 0,total=total,payment_method=data.payment_method); db.add(pur); db.flush()
    for p,qty,cost,ln in checked:
        p.quantity += qty; p.cost=cost; db.add(PurchaseItem(purchase_id=pur.id,product_id=p.id,quantity=qty,unit_cost=cost,total=ln))
    if data.supplier_id:
        sup=db.query(Supplier).filter(Supplier.id==data.supplier_id).first()
        if sup and data.payment_method=="account": sup.balance=float(sup.balance)+total
    db.commit(); return {"id":pur.id,"invoice_no":inv,"subtotal":sub,"vat":vat,"total":total}


@app.get("/api/purchases/{purchase_id}")
def get_purchase(purchase_id:int, db:Session=Depends(db_session)):
    p=db.query(Purchase).filter(Purchase.id==purchase_id).first()
    if not p: raise HTTPException(404,"Purchase not found")
    sup=db.query(Supplier).filter(Supplier.id==p.supplier_id).first() if p.supplier_id else None
    items=[]
    for it in db.query(PurchaseItem).filter(PurchaseItem.purchase_id==p.id).all():
        prod=db.query(Product).filter(Product.id==it.product_id).first()
        items.append({"id":it.id,"product_id":it.product_id,"name":prod.name if prod else "Deleted Product","sku":prod.sku if prod else "","barcode":prod.barcode if prod else "","quantity":it.quantity,"unit_cost":float(it.unit_cost),"total":float(it.total)})
    return {"id":p.id,"invoice_no":p.invoice_no,"supplier_id":p.supplier_id,"supplier_name":sup.name if sup else "Walk-in Supplier","subtotal":float(p.subtotal),"vat_enabled":p.vat_enabled,"vat_rate":float(p.vat_rate),"total":float(p.total),"payment_method":p.payment_method,"created_at":p.created_at.isoformat(),"items":items}

@app.put("/api/purchases/{purchase_id}")
def update_purchase(purchase_id:int, data:PurchaseIn, db:Session=Depends(db_session)):
    pch=db.query(Purchase).filter(Purchase.id==purchase_id).first()
    if not pch: raise HTTPException(404,"Purchase not found")
    if not data.items: raise HTTPException(400,"Purchase must contain at least one item")
    old=db.query(PurchaseItem).filter(PurchaseItem.purchase_id==pch.id).all()
    for it in old:
        prod=db.query(Product).filter(Product.id==it.product_id).first()
        if prod: prod.quantity -= it.quantity
    db.query(PurchaseItem).filter(PurchaseItem.purchase_id==pch.id).delete(synchronize_session=False)
    subtotal=0.0; checked=[]
    try:
        for item in data.items:
            prod=db.query(Product).filter(Product.id==item.product_id,Product.active==True).first()
            if not prod: raise HTTPException(404,f"Product {item.product_id} not found")
            if item.quantity<=0: raise HTTPException(400,"Quantity must be greater than zero")
            cost=float(item.unit_cost if item.unit_cost is not None else prod.cost); ln=cost*item.quantity; subtotal+=ln; checked.append((prod,item.quantity,cost,ln))
        vat=round(subtotal*(float(data.vat_rate)/100),2) if data.vat_enabled else 0.0; total=round(subtotal+vat,2)
        if pch.supplier_id and pch.payment_method == "account":
            olds=db.query(Supplier).filter(Supplier.id==pch.supplier_id).first()
            if olds: olds.balance=float(olds.balance or 0)-float(pch.total or 0)
        if data.supplier_id and data.payment_method == "account":
            news=db.query(Supplier).filter(Supplier.id==data.supplier_id).first()
            if news: news.balance=float(news.balance or 0)+total
        pch.supplier_id=data.supplier_id; pch.subtotal=subtotal; pch.vat_enabled=data.vat_enabled; pch.vat_rate=float(data.vat_rate) if data.vat_enabled else 0; pch.total=total; pch.payment_method=data.payment_method
        for prod,qty,cost,ln in checked:
            prod.quantity += qty; prod.cost=cost; db.add(PurchaseItem(purchase_id=pch.id,product_id=prod.id,quantity=qty,unit_cost=cost,total=ln))
        db.commit(); return {"success":True,"id":pch.id,"invoice_no":pch.invoice_no,"subtotal":subtotal,"vat":vat,"total":total}
    except Exception:
        db.rollback(); raise

@app.delete("/api/purchases/{purchase_id}")
def delete_purchase(purchase_id:int, db:Session=Depends(db_session)):
    pch=db.query(Purchase).filter(Purchase.id==purchase_id).first()
    if not pch: raise HTTPException(404,"Purchase not found")
    for it in db.query(PurchaseItem).filter(PurchaseItem.purchase_id==pch.id).all():
        prod=db.query(Product).filter(Product.id==it.product_id).first()
        if prod: prod.quantity -= it.quantity
    if pch.supplier_id and pch.payment_method == "account":
        sup=db.query(Supplier).filter(Supplier.id==pch.supplier_id).first()
        if sup: sup.balance=float(sup.balance or 0)-float(pch.total or 0)
    db.query(PurchaseItem).filter(PurchaseItem.purchase_id==pch.id).delete(synchronize_session=False)
    db.delete(pch); db.commit(); return {"success":True}

@app.get("/api/repairs")
def list_repairs(db: Session = Depends(db_session)):
    rows=db.query(Repair).order_by(Repair.id.desc()).all()
    out=[]
    for r in rows:
        c=db.query(Customer).filter(Customer.id==r.customer_id).first() if r.customer_id else None
        out.append({"id":r.id,"ticket_no":r.ticket_no,"customer_id":r.customer_id,
                    "customer_name": c.name if c else "Walk-in Customer",
                    "customer_phone": r.customer_phone or (c.phone if c else ""),
                    "customer_address": r.customer_address or (c.address if c else ""),
                    "device_name":r.device_name,"imei_or_serial":r.imei_or_serial,
                    "problem":r.problem,"status":r.status,"estimated_cost":float(r.estimated_cost or 0),
                    "sales_price":float(r.sales_price or 0),
                    "profit":float(r.sales_price or 0)-float(r.estimated_cost or 0),
                    "technician":r.technician or "","warranty_days":int(r.warranty_days or 0),
                    "notes":r.notes or "","created_at":r.created_at.isoformat()})
    return out

@app.post("/api/repairs")
def create_repair(data: RepairIn, db: Session = Depends(db_session)):
    if not data.device_name.strip(): raise HTTPException(400,"Device name is required")
    ticket=f"REP-{db.query(Repair).count()+1:05d}"
    r=Repair(ticket_no=ticket,**data.model_dump())
    db.add(r); db.commit(); db.refresh(r)
    return {"id":r.id,"ticket_no":ticket,"status":r.status}

@app.put("/api/repairs/{repair_id}")
def update_repair(repair_id:int,data:RepairIn,db:Session=Depends(db_session)):
    r=db.query(Repair).filter(Repair.id==repair_id).first()
    if not r: raise HTTPException(404,"Repair not found")
    for k,v in data.model_dump().items(): setattr(r,k,v)
    db.commit(); return {"ok":True}

@app.delete("/api/repairs/{repair_id}")
def delete_repair(repair_id:int,db:Session=Depends(db_session)):
    r=db.query(Repair).filter(Repair.id==repair_id).first()
    if not r: raise HTTPException(404,"Repair not found")
    db.delete(r); db.commit(); return {"ok":True}

@app.get("/api/settings")
def get_settings(db:Session=Depends(db_session)):
    vals={s.key:s.value for s in db.query(Setting).all()}
    vals.setdefault("company_name","SIF Mobile & Computer"); vals.setdefault("usd_lbp","89500"); vals.setdefault("vat_rate","11"); vals.setdefault("vat_enabled","true"); vals.setdefault("invoice_prefix","INV-"); vals.setdefault("company_phone",""); vals.setdefault("company_email",""); vals.setdefault("company_address",""); vals.setdefault("company_logo","")
    return vals

@app.post("/api/settings")
def set_setting(data:SettingIn,db:Session=Depends(db_session)):
    s=db.query(Setting).filter(Setting.key==data.key).first()
    if not s: s=Setting(key=data.key,value=data.value); db.add(s)
    else: s.value=data.value
    db.commit(); return {"ok":True}

@app.get("/api/users")
def list_users(db: Session = Depends(db_session)):
    rows=db.query(User).order_by(User.id.asc()).all()
    return [{"id":u.id,"username":u.username,"role":u.role,"active":bool(u.active)} for u in rows]

@app.post("/api/users")
def create_user(data: UserIn, db: Session = Depends(db_session)):
    username=data.username.strip()
    if not username: raise HTTPException(400,"Username is required")
    if not data.password: raise HTTPException(400,"Password is required for a new user")
    if db.query(User).filter(User.username==username).first(): raise HTTPException(400,"Username already exists")
    role=data.role.strip().lower() or "cashier"
    allowed={"admin","manager","cashier","technician","accountant"}
    if role not in allowed: raise HTTPException(400,"Invalid role")
    u=User(username=username,password_hash=hash_password(data.password),role=role,active=bool(data.active))
    db.add(u); db.commit(); db.refresh(u)
    return {"success":True,"id":u.id,"username":u.username,"role":u.role,"active":bool(u.active)}

@app.put("/api/users/{user_id}")
def update_user(user_id:int,data:UserIn,db:Session=Depends(db_session)):
    u=db.query(User).filter(User.id==user_id).first()
    if not u: raise HTTPException(404,"User not found")
    username=data.username.strip()
    if not username: raise HTTPException(400,"Username is required")
    clash=db.query(User).filter(User.username==username,User.id!=user_id).first()
    if clash: raise HTTPException(400,"Username already exists")
    role=data.role.strip().lower() or u.role
    if role not in {"admin","manager","cashier","technician","accountant"}: raise HTTPException(400,"Invalid role")
    # Never allow the main admin to become inactive.
    if u.username=="admin":
        u.active=True; u.role="admin"
    else:
        u.username=username; u.role=role; u.active=bool(data.active)
    if data.password:
        u.password_hash=hash_password(data.password)
    db.commit()
    return {"success":True,"id":u.id,"username":u.username,"role":u.role,"active":bool(u.active)}

@app.delete("/api/users/{user_id}")
def delete_user(user_id:int,db:Session=Depends(db_session)):
    u=db.query(User).filter(User.id==user_id).first()
    if not u: raise HTTPException(404,"User not found")
    if u.username=="admin": raise HTTPException(400,"Main admin cannot be deleted")
    db.delete(u); db.commit(); return {"success":True}

@app.get("/api/reports/summary")
def report_summary(db:Session=Depends(db_session)):
    sales_total=float(db.query(func.coalesce(func.sum(Sale.total),0)).scalar() or 0)
    purchase_total=float(db.query(func.coalesce(func.sum(Purchase.total),0)).scalar() or 0)
    expense_total=float(db.query(func.coalesce(func.sum(Expense.amount),0)).scalar() or 0) if 'Expense' in globals() else 0
    stock_cost=float(db.query(func.coalesce(func.sum(Product.cost*Product.quantity),0)).scalar() or 0)
    stock_sales=float(db.query(func.coalesce(func.sum(Product.sale_price*Product.quantity),0)).scalar() or 0)
    customer_balance=float(db.query(func.coalesce(func.sum(Customer.balance),0)).scalar() or 0)
    supplier_balance=float(db.query(func.coalesce(func.sum(Supplier.balance),0)).scalar() or 0)
    return {"products":db.query(Product).filter(Product.active==True).count(),"customers":db.query(Customer).count(),"suppliers":db.query(Supplier).count(),"sales":db.query(Sale).count(),"purchases":db.query(Purchase).count(),"repairs":db.query(Repair).count(),"sales_count":db.query(Sale).count(),"purchase_count":db.query(Purchase).count(),"expense_count":db.query(Expense).count() if 'Expense' in globals() else 0,"sales_total":sales_total,"purchase_total":purchase_total,"expense_total":expense_total,"gross_margin":sales_total-stock_cost,"stock_cost":stock_cost,"stock_sales":stock_sales,"customer_balance":customer_balance,"supplier_balance":supplier_balance}


@app.get("/api/reports/details")
def report_details(report_type:str="sales", db:Session=Depends(db_session)):
    t=report_type.strip().lower()
    if t=="sales":
        rows=db.query(Sale).order_by(Sale.id.desc()).limit(200).all()
        return {"title":"Sales Report","columns":["Invoice","Date","Customer","Payment","Total"],"rows":[[x.invoice_no,x.created_at.strftime("%Y-%m-%d %H:%M") if x.created_at else "",(db.query(Customer).filter(Customer.id==x.customer_id).first().name if x.customer_id and db.query(Customer).filter(Customer.id==x.customer_id).first() else "Walk-in Customer"),x.payment_method,float(x.total)] for x in rows]}
    if t=="purchases":
        rows=db.query(Purchase).order_by(Purchase.id.desc()).limit(200).all()
        return {"title":"Purchases Report","columns":["Invoice","Date","Supplier","Payment","Total"],"rows":[[x.invoice_no,x.created_at.strftime("%Y-%m-%d %H:%M") if x.created_at else "",(db.query(Supplier).filter(Supplier.id==x.supplier_id).first().name if x.supplier_id and db.query(Supplier).filter(Supplier.id==x.supplier_id).first() else "Walk-in Supplier"),x.payment_method,float(x.total)] for x in rows]}
    if t=="expenses":
        rows=db.query(Expense).order_by(Expense.id.desc()).limit(200).all()
        return {"title":"Expenses Report","columns":["Date","Category","Description","Payment","Amount"],"rows":[[x.created_at.strftime("%Y-%m-%d %H:%M") if x.created_at else "",x.category or "",x.description or "",x.payment_method or "",float(x.amount)] for x in rows]}
    if t=="stock":
        rows=db.query(Product).filter(Product.active==True).order_by(Product.name.asc()).limit(500).all()
        return {"title":"Stock Report","columns":["SKU","Product","Barcode","Qty","Cost","Retail Value"],"rows":[[x.sku,x.name,x.barcode or "",x.quantity,float(x.cost)*x.quantity,float(x.sale_price)*x.quantity] for x in rows]}
    if t=="customers":
        rows=db.query(Customer).order_by(Customer.name.asc()).limit(500).all()
        return {"title":"Customers Report","columns":["Code","Customer","Phone","Balance"],"rows":[[x.code or "",x.name,x.phone or "",float(x.balance or 0)] for x in rows]}
    if t=="suppliers":
        rows=db.query(Supplier).order_by(Supplier.name.asc()).limit(500).all()
        return {"title":"Suppliers Report","columns":["Code","Supplier","Phone","Balance"],"rows":[[x.code or "",x.name,x.phone or "",float(x.balance or 0)] for x in rows]}
    if t=="repairs":
        rows=db.query(Repair).order_by(Repair.id.desc()).limit(200).all()
        return {"title":"Repairs Report","columns":["Ticket","Date","Customer","Device","Status","Sales","Profit"],"rows":[[x.ticket_no,x.created_at.strftime("%Y-%m-%d %H:%M") if x.created_at else "",(db.query(Customer).filter(Customer.id==x.customer_id).first().name if x.customer_id and db.query(Customer).filter(Customer.id==x.customer_id).first() else "Walk-in"),x.device_name or "",x.status or "",float(x.sales_price or 0),float((x.sales_price or 0)-(x.estimated_cost or 0))] for x in rows]}
    raise HTTPException(400,"Unknown report type")

# ===== PHASE 47: BARCODE CENTER + DATABASE TOOLS =====
def _sqlite_db_path() -> Path:
    if not DATABASE_URL.startswith("sqlite"):
        raise HTTPException(400, "Database tools are available for the local SQLite database only.")
    raw = DATABASE_URL.replace("sqlite:///", "", 1)
    return Path(raw).resolve()

def _next_internal_barcode(db: Session) -> str:
    # Internal Code-128 numeric barcode range. Keep it numeric for scanner compatibility.
    used = {str(p.barcode).strip() for p in db.query(Product).filter(Product.barcode.isnot(None)).all() if p.barcode}
    nums=[]
    for b in used:
        if re.fullmatch(r"\d{12}", b):
            try: nums.append(int(b))
            except ValueError: pass
    candidate = max(nums + [200000000000]) + 1
    while str(candidate) in used:
        candidate += 1
    if candidate > 999999999999:
        raise HTTPException(400, "Internal barcode range is full.")
    return f"{candidate:012d}"

@app.post("/api/products/{product_id}/generate-barcode")
def generate_product_barcode(product_id:int, db:Session=Depends(db_session)):
    p=db.query(Product).filter(Product.id==product_id, Product.active==True).first()
    if not p: raise HTTPException(404,"Product not found")
    if p.barcode and str(p.barcode).strip():
        return {"success":True,"barcode":str(p.barcode),"generated":False,"message":"Product already has a barcode."}
    p.barcode=_next_internal_barcode(db)
    db.commit()
    return {"success":True,"barcode":p.barcode,"generated":True}

@app.post("/api/products/generate-barcode")
def generate_product_barcode_by_id(data:dict, db:Session=Depends(db_session)):
    try: product_id=int(data.get("product_id"))
    except Exception: raise HTTPException(400,"product_id is required")
    return generate_product_barcode(product_id, db)

@app.get("/api/database/export")
def export_database():
    db_path=_sqlite_db_path()
    if not db_path.exists(): raise HTTPException(404,"Database file not found")
    return FileResponse(db_path, media_type="application/x-sqlite3", filename="SIF_Mobile_Computer_Backup.db")

@app.post("/api/database/import")
async def import_database(file: UploadFile = File(...)):
    raw=await file.read()
    if len(raw)<16 or raw[:16] != b"SQLite format 3\x00":
        raise HTTPException(400,"Invalid SQLite database file.")
    target=_sqlite_db_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    temp=target.with_suffix(".importing.db")
    backup=target.with_name(target.stem + "_before_import_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".db")
    try:
        temp.write_bytes(raw)
        con=sqlite3.connect(str(temp));
        try:
            ok=con.execute("PRAGMA quick_check").fetchone()
            if not ok or str(ok[0]).lower()!="ok": raise ValueError("SQLite quick_check failed")
            tables={r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type=\'table\'").fetchall()}
            required={"users","products","settings","sales","sale_items","purchases","purchase_items"}
            missing=sorted(required-tables)
            if missing: raise ValueError("Not a SIF database. Missing tables: "+", ".join(missing))
        finally: con.close()
        if target.exists(): shutil.copy2(target, backup)
        engine.dispose()
        shutil.copy2(temp, target)
        temp.unlink(missing_ok=True)
        return {"success":True,"message":"Database imported successfully.","backup":backup.name}
    except Exception as e:
        temp.unlink(missing_ok=True)
        raise HTTPException(500,f"Database import failed: {e}")

@app.post("/api/database/reset")
def reset_database(mode:str="business"):
    # Safe reset: always make a backup first. Factory reset also restores defaults.
    db_path=_sqlite_db_path()
    backup=None
    if db_path.exists():
        backup=db_path.with_name(db_path.stem + "_backup_before_reset_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".db")
        shutil.copy2(db_path, backup)
    engine.dispose()
    if db_path.exists(): db_path.unlink()
    Base.metadata.create_all(engine)
    db=SessionLocal()
    try:
        # Restore catalog defaults used by the application.
        defaults=[("Mobile Phones","mobile"),("Computers & Laptops","computer"),("Accessories","accessory")]
        for name,code in defaults:
            if not db.query(Category).filter(Category.name==name).first(): db.add(Category(name=name))
            if not db.query(ProductType).filter(ProductType.code==code).first(): db.add(ProductType(name={"mobile":"Mobile","computer":"Computer","accessory":"Accessory"}[code],code=code))
        db.add(User(username="admin",password_hash=hash_password("admin"),role="admin",active=True))
        if mode=="factory":
            for key,value in {"company_name":"SIF Mobile & Computer","usd_lbp":"89500","vat_rate":"11","vat_enabled":"true","invoice_prefix":"INV-","company_phone":"","company_email":"","company_address":"","company_logo":""}.items():
                db.add(Setting(key=key,value=value))
        db.commit()
        if mode=="factory": seed_demo_catalog(db)
    finally: db.close()
    return {"success":True,"mode":mode,"backup":backup.name if backup else None,"message":"Database reset successfully. Restart SIF if you were using the old browser tab."}

@app.get("/api/health")
def health():
    return {"status":"ok","service":"SIF Mobile & Computer API"}

@app.post("/api/login")
def login(data: LoginIn, db: Session = Depends(db_session)):
    user = db.query(User).filter(User.username == data.username, User.active == True).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"success": True, "user": {"id":user.id,"username":user.username,"role":user.role}}

@app.get("/api/dashboard")
def dashboard(db: Session = Depends(db_session)):
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    seven_start = today_start.replace(hour=0, minute=0, second=0, microsecond=0)
    from datetime import timedelta
    seven_start = today_start - timedelta(days=6)

    active_products = db.query(Product).filter(Product.active == True).all()
    customers = db.query(Customer).all()
    suppliers = db.query(Supplier).all()
    sales_today = db.query(Sale).filter(Sale.created_at >= today_start).all()
    purchases_today = db.query(Purchase).filter(Purchase.created_at >= today_start).all()
    expenses_today = db.query(Expense).filter(Expense.created_at >= today_start).all()
    sales_7 = db.query(Sale).filter(Sale.created_at >= seven_start).all()

    # Seven-day sales series, oldest to newest, so the frontend can draw a real chart.
    sales_by_day = {}
    for i in range(7):
        d = (seven_start + timedelta(days=i)).date()
        sales_by_day[d.isoformat()] = 0.0
    for sale in sales_7:
        d = sale.created_at.date().isoformat()
        if d in sales_by_day:
            sales_by_day[d] += float(sale.total or 0)

    # Top products by quantity sold in the last 30 days.
    month_start = today_start - timedelta(days=30)
    top_rows = (db.query(Product.name, Product.sku, func.sum(SaleItem.quantity).label("qty"),
                         func.sum(SaleItem.total).label("amount"))
                  .join(SaleItem, SaleItem.product_id == Product.id)
                  .join(Sale, Sale.id == SaleItem.sale_id)
                  .filter(Sale.created_at >= month_start)
                  .group_by(Product.id)
                  .order_by(func.sum(SaleItem.quantity).desc())
                  .limit(5).all())

    recent = db.query(Sale).order_by(Sale.id.desc()).limit(8).all()
    recent_sales = []
    for sale in recent:
        c = db.query(Customer).filter(Customer.id == sale.customer_id).first() if sale.customer_id else None
        recent_sales.append({
            "invoice_no": sale.invoice_no, "customer_name": c.name if c else "Walk-in Customer",
            "total": float(sale.total or 0), "payment_method": sale.payment_method,
            "status": sale.status, "created_at": sale.created_at.isoformat()
        })

    repair_rows = db.query(Repair).all()
    repair_status = {}
    for r in repair_rows:
        key = (r.status or "received").strip().lower()
        repair_status[key] = repair_status.get(key, 0) + 1

    low_stock = sorted(
        [p for p in active_products if p.quantity <= p.reorder_level],
        key=lambda x: (x.quantity - x.reorder_level, x.name.lower())
    )[:8]

    stock_cost = sum(float(p.cost or 0) * int(p.quantity or 0) for p in active_products)
    stock_sales = sum(float(p.sale_price or 0) * int(p.quantity or 0) for p in active_products)

    return {
        "today": {
            "sales": sum(float(x.total or 0) for x in sales_today),
            "sales_count": len(sales_today),
            "purchases": sum(float(x.total or 0) for x in purchases_today),
            "purchases_count": len(purchases_today),
            "expenses": sum(float(x.amount or 0) for x in expenses_today),
            "expenses_count": len(expenses_today),
        },
        "totals": {
            "products": len(active_products),
            "quantity": sum(int(p.quantity or 0) for p in active_products),
            "customers": len(customers),
            "suppliers": len(suppliers),
            "repairs": len(repair_rows),
            "low_stock": len([p for p in active_products if p.quantity <= p.reorder_level]),
            "stock_cost": stock_cost,
            "stock_sales": stock_sales,
            "customer_receivables": sum(max(0.0, float(c.balance or 0)) for c in customers),
            "supplier_payables": sum(max(0.0, float(s.balance or 0)) for s in suppliers),
        },
        "sales_7_days": [{"date": d, "total": round(v, 2)} for d, v in sales_by_day.items()],
        "top_products": [{"name": r[0], "sku": r[1], "qty": int(r[2] or 0), "amount": float(r[3] or 0)} for r in top_rows],
        "recent_sales": recent_sales,
        "repair_status": repair_status,
        "low_stock_items": [{"id": p.id, "name": p.name, "sku": p.sku, "quantity": p.quantity, "reorder_level": p.reorder_level} for p in low_stock],
    }

@app.get("/api/categories")
def categories(db: Session = Depends(db_session)):
    rows = db.query(Category).filter(Category.active == True).order_by(Category.name.asc()).all()
    return [{"id":c.id,"name":c.name,"image_url":c.image_url} for c in rows]

@app.post("/api/categories")
def create_category(data: CategoryIn, db: Session = Depends(db_session)):
    name=data.name.strip()
    if not name: raise HTTPException(400,"Category name is required")
    if db.query(Category).filter(Category.name.ilike(name)).first(): raise HTTPException(409,"Category already exists")
    c=Category(name=name,image_url=data.image_url or None); db.add(c); db.commit(); db.refresh(c)
    return {"success":True,"id":c.id,"name":c.name}

@app.put("/api/categories/{category_id}")
def update_category(category_id:int,data:CategoryIn,db:Session=Depends(db_session)):
    c=db.query(Category).filter(Category.id==category_id,Category.active==True).first()
    if not c: raise HTTPException(404,"Category not found")
    name=data.name.strip()
    other=db.query(Category).filter(Category.name.ilike(name),Category.id!=category_id,Category.active==True).first()
    if other: raise HTTPException(409,"Category already exists")
    old=c.name; c.name=name; c.image_url=data.image_url or None
    for p in db.query(Product).filter(Product.active==True,Product.category==old).all(): p.category=name
    db.commit(); return {"success":True}

@app.delete("/api/categories/{category_id}")
def delete_category(category_id:int,db:Session=Depends(db_session)):
    c=db.query(Category).filter(Category.id==category_id,Category.active==True).first()
    if not c: raise HTTPException(404,"Category not found")
    if db.query(Product).filter(Product.active==True,Product.category==c.name).count(): raise HTTPException(400,"Category is used by products. Move products first.")
    c.active=False; db.commit(); return {"success":True}

@app.get("/api/product-types")
def product_types(db:Session=Depends(db_session)):
    rows=db.query(ProductType).filter(ProductType.active==True).order_by(ProductType.name.asc()).all()
    return [{"id":t.id,"name":t.name,"code":t.code} for t in rows]

@app.post("/api/product-types")
def create_product_type(data:ProductTypeIn,db:Session=Depends(db_session)):
    name=data.name.strip(); code=(data.code or name.lower().replace(" ","_")).strip()
    if not name or not code: raise HTTPException(400,"Type name is required")
    if db.query(ProductType).filter((ProductType.name.ilike(name)) | (ProductType.code.ilike(code))).first(): raise HTTPException(409,"Product type already exists")
    t=ProductType(name=name,code=code); db.add(t); db.commit(); db.refresh(t); return {"success":True,"id":t.id,"name":t.name,"code":t.code}

@app.put("/api/product-types/{type_id}")
def update_product_type(type_id:int,data:ProductTypeIn,db:Session=Depends(db_session)):
    t=db.query(ProductType).filter(ProductType.id==type_id,ProductType.active==True).first()
    if not t: raise HTTPException(404,"Product type not found")
    name=data.name.strip(); code=(data.code or name.lower().replace(" ","_")).strip()
    other=db.query(ProductType).filter(((ProductType.name.ilike(name)) | (ProductType.code.ilike(code))),ProductType.id!=type_id,ProductType.active==True).first()
    if other: raise HTTPException(409,"Product type already exists")
    old=t.code; t.name=name; t.code=code
    for p in db.query(Product).filter(Product.active==True,Product.product_type==old).all(): p.product_type=code
    db.commit(); return {"success":True}

@app.delete("/api/product-types/{type_id}")
def delete_product_type(type_id:int,db:Session=Depends(db_session)):
    t=db.query(ProductType).filter(ProductType.id==type_id,ProductType.active==True).first()
    if not t: raise HTTPException(404,"Product type not found")
    if db.query(Product).filter(Product.active==True,Product.product_type==t.code).count(): raise HTTPException(400,"Product type is used by products. Move products first.")
    t.active=False; db.commit(); return {"success":True}

@app.get("/api/products")
def products(db: Session = Depends(db_session)):
    rows = db.query(Product).filter(Product.active == True).order_by(Product.id.desc()).all()
    return [{"id":p.id,"sku":p.sku,"barcode":p.barcode,"name":p.name,"category":p.category,
             "product_type":p.product_type,"cost":float(p.cost),"sale_price":float(p.sale_price),
             "quantity":p.quantity,"reorder_level":p.reorder_level,
             "imei_required":p.imei_required,"serial_required":p.serial_required,
             "warranty_months":p.warranty_months,"image_url":p.image_url,
             "wholesale_price":float(p.wholesale_price),"vip_price":float(p.vip_price)} for p in rows]

@app.post("/api/products")
def create_product(data: ProductIn, db: Session = Depends(db_session)):
    if db.query(Product).filter(Product.sku == data.sku).first():
        raise HTTPException(409, "SKU already exists")
    if data.barcode and db.query(Product).filter(Product.barcode == data.barcode).first():
        raise HTTPException(409, "Barcode already exists")
    p = Product(**data.model_dump())
    db.add(p); db.commit(); db.refresh(p)
    return {"success":True,"id":p.id}

@app.get("/api/customers")
def customers(db: Session = Depends(db_session)):
    rows = db.query(Customer).order_by(Customer.id.desc()).all()
    return [{"id":c.id,"code":c.code,"name":c.name,"phone":c.phone,"address":c.address,"balance":float(c.balance)} for c in rows]

@app.post("/api/customers")
def create_customer(data: CustomerIn, db: Session = Depends(db_session)):
    if db.query(Customer).filter(Customer.code == data.code).first():
        raise HTTPException(409, "Customer code already exists")
    c = Customer(**data.model_dump())
    db.add(c); db.commit(); db.refresh(c)
    return {"success":True,"id":c.id}


@app.get("/api/purchases/{purchase_id}")
def get_purchase(purchase_id:int, db:Session=Depends(db_session)):
    p=db.query(Purchase).filter(Purchase.id==purchase_id).first()
    if not p: raise HTTPException(404,"Purchase not found")
    sup=db.query(Supplier).filter(Supplier.id==p.supplier_id).first() if p.supplier_id else None
    items=[]
    for it in db.query(PurchaseItem).filter(PurchaseItem.purchase_id==p.id).all():
        prod=db.query(Product).filter(Product.id==it.product_id).first()
        items.append({"id":it.id,"product_id":it.product_id,"name":prod.name if prod else "Deleted Product","sku":prod.sku if prod else "","barcode":prod.barcode if prod else "","quantity":it.quantity,"unit_cost":float(it.unit_cost),"total":float(it.total)})
    return {"id":p.id,"invoice_no":p.invoice_no,"supplier_id":p.supplier_id,"supplier_name":sup.name if sup else "Walk-in Supplier","subtotal":float(p.subtotal),"vat_enabled":p.vat_enabled,"vat_rate":float(p.vat_rate),"total":float(p.total),"payment_method":p.payment_method,"created_at":p.created_at.isoformat(),"items":items}

@app.put("/api/purchases/{purchase_id}")
def update_purchase(purchase_id:int, data:PurchaseIn, db:Session=Depends(db_session)):
    pch=db.query(Purchase).filter(Purchase.id==purchase_id).first()
    if not pch: raise HTTPException(404,"Purchase not found")
    if not data.items: raise HTTPException(400,"Purchase must contain at least one item")
    old=db.query(PurchaseItem).filter(PurchaseItem.purchase_id==pch.id).all()
    for it in old:
        prod=db.query(Product).filter(Product.id==it.product_id).first()
        if prod: prod.quantity -= it.quantity
    db.query(PurchaseItem).filter(PurchaseItem.purchase_id==pch.id).delete(synchronize_session=False)
    subtotal=0.0; checked=[]
    try:
        for item in data.items:
            prod=db.query(Product).filter(Product.id==item.product_id,Product.active==True).first()
            if not prod: raise HTTPException(404,f"Product {item.product_id} not found")
            if item.quantity<=0: raise HTTPException(400,"Quantity must be greater than zero")
            cost=float(item.unit_cost if item.unit_cost is not None else prod.cost); ln=cost*item.quantity; subtotal+=ln; checked.append((prod,item.quantity,cost,ln))
        vat=round(subtotal*(float(data.vat_rate)/100),2) if data.vat_enabled else 0.0; total=round(subtotal+vat,2)
        pch.supplier_id=data.supplier_id; pch.subtotal=subtotal; pch.vat_enabled=data.vat_enabled; pch.vat_rate=float(data.vat_rate) if data.vat_enabled else 0; pch.total=total; pch.payment_method=data.payment_method
        for prod,qty,cost,ln in checked:
            prod.quantity += qty; prod.cost=cost; db.add(PurchaseItem(purchase_id=pch.id,product_id=prod.id,quantity=qty,unit_cost=cost,total=ln))
        db.commit(); return {"success":True,"id":pch.id,"invoice_no":pch.invoice_no,"subtotal":subtotal,"vat":vat,"total":total}
    except Exception:
        db.rollback(); raise

@app.delete("/api/purchases/{purchase_id}")
def delete_purchase(purchase_id:int, db:Session=Depends(db_session)):
    pch=db.query(Purchase).filter(Purchase.id==purchase_id).first()
    if not pch: raise HTTPException(404,"Purchase not found")
    for it in db.query(PurchaseItem).filter(PurchaseItem.purchase_id==pch.id).all():
        prod=db.query(Product).filter(Product.id==it.product_id).first()
        if prod: prod.quantity -= it.quantity
    db.query(PurchaseItem).filter(PurchaseItem.purchase_id==pch.id).delete(synchronize_session=False)
    db.delete(pch); db.commit(); return {"success":True}

@app.get("/api/repairs")
def repairs(db: Session = Depends(db_session)):
    rows = db.query(Repair).order_by(Repair.id.desc()).all()
    return [{"id":r.id,"ticket_no":r.ticket_no,"customer_id":r.customer_id,"device_name":r.device_name,
             "imei_or_serial":r.imei_or_serial,"problem":r.problem,"status":r.status,
             "estimated_cost":float(r.estimated_cost),"created_at":r.created_at.isoformat()} for r in rows]


# ===== PHASE 45: EXPENSES, PAYMENTS, STATEMENTS, RETURNS =====
class ExpenseIn(BaseModel):
    description: str
    amount: float
    category: str = "General"
    payment_method: str = "cash"
    notes: str | None = None

class PaymentIn(BaseModel):
    party_id: int
    amount: float
    payment_method: str = "cash"
    notes: str | None = None

class ReturnItemIn(BaseModel):
    product_id: int
    quantity: int

class ReturnIn(BaseModel):
    original_id: int
    items: list[ReturnItemIn]
    payment_method: str = "cash"

@app.get("/api/expenses")
def list_expenses(db: Session=Depends(db_session)):
    rows=db.query(Expense).order_by(Expense.id.desc()).all()
    return [{"id":e.id,"description":e.description,"amount":float(e.amount),"category":e.category,"payment_method":e.payment_method,"notes":e.notes or "","created_at":e.created_at.isoformat()} for e in rows]

@app.post("/api/expenses")
def create_expense(data: ExpenseIn, db: Session=Depends(db_session)):
    if not data.description.strip() or data.amount<=0: raise HTTPException(400,"Description and positive amount are required")
    e=Expense(**data.model_dump()); db.add(e); db.commit(); db.refresh(e); return {"success":True,"id":e.id}

@app.put("/api/expenses/{expense_id}")
def update_expense(expense_id:int,data:ExpenseIn,db:Session=Depends(db_session)):
    e=db.query(Expense).filter(Expense.id==expense_id).first()
    if not e: raise HTTPException(404,"Expense not found")
    for k,v in data.model_dump().items(): setattr(e,k,v)
    db.commit(); return {"success":True}

@app.delete("/api/expenses/{expense_id}")
def delete_expense(expense_id:int,db:Session=Depends(db_session)):
    e=db.query(Expense).filter(Expense.id==expense_id).first()
    if not e: raise HTTPException(404,"Expense not found")
    db.delete(e); db.commit(); return {"success":True}

def _party_balance(db, party_type, party_id):
    if party_type=="customer":
        c=db.query(Customer).filter(Customer.id==party_id).first(); return float(c.balance or 0) if c else 0
    s=db.query(Supplier).filter(Supplier.id==party_id).first(); return float(s.balance or 0) if s else 0

@app.get("/api/payments/{party_type}/{party_id}")
def list_payments(party_type:str,party_id:int,db:Session=Depends(db_session)):
    if party_type not in ("customer","supplier"): raise HTTPException(400,"Invalid party type")
    rows=db.query(AccountPayment).filter(AccountPayment.party_type==party_type,AccountPayment.party_id==party_id).order_by(AccountPayment.id.desc()).all()
    return [{"id":p.id,"amount":float(p.amount),"payment_method":p.payment_method,"notes":p.notes or "","created_at":p.created_at.isoformat()} for p in rows]

@app.post("/api/payments/{party_type}")
def create_payment(party_type:str,data:PaymentIn,db:Session=Depends(db_session)):
    if party_type not in ("customer","supplier"): raise HTTPException(400,"Invalid party type")
    if data.amount<=0: raise HTTPException(400,"Payment must be greater than zero")
    if party_type=="customer":
        party=db.query(Customer).filter(Customer.id==data.party_id).first()
        if not party: raise HTTPException(404,"Customer not found")
        if data.amount > float(party.balance or 0): raise HTTPException(400,"Payment exceeds customer balance")
        party.balance=float(party.balance or 0)-data.amount
    else:
        party=db.query(Supplier).filter(Supplier.id==data.party_id).first()
        if not party: raise HTTPException(404,"Supplier not found")
        if data.amount > float(party.balance or 0): raise HTTPException(400,"Payment exceeds supplier payable")
        party.balance=float(party.balance or 0)-data.amount
    p=AccountPayment(party_type=party_type,party_id=data.party_id,amount=data.amount,payment_method=data.payment_method,notes=data.notes)
    db.add(p); db.commit(); db.refresh(p); return {"success":True,"id":p.id,"balance":_party_balance(db,party_type,data.party_id)}

@app.get("/api/statements/{party_type}/{party_id}")
def statement(party_type:str,party_id:int,db:Session=Depends(db_session)):
    if party_type=="customer":
        party=db.query(Customer).filter(Customer.id==party_id).first()
        if not party: raise HTTPException(404,"Customer not found")
        events=[]
        for s in db.query(Sale).filter(Sale.customer_id==party_id,Sale.payment_method=="account").all(): events.append({"date":s.created_at.isoformat(),"type":"Sale Invoice","ref":s.invoice_no,"debit":float(s.total),"credit":0})
        for r in db.query(SalesReturn).filter(SalesReturn.customer_id==party_id).all(): events.append({"date":r.created_at.isoformat(),"type":"Sales Return","ref":r.return_no,"debit":0,"credit":float(r.total)})
        for p in db.query(AccountPayment).filter(AccountPayment.party_type=="customer",AccountPayment.party_id==party_id).all(): events.append({"date":p.created_at.isoformat(),"type":"Payment","ref":f"PAY-{p.id:05d}","debit":0,"credit":float(p.amount)})
        name=party.name
    elif party_type=="supplier":
        party=db.query(Supplier).filter(Supplier.id==party_id).first()
        if not party: raise HTTPException(404,"Supplier not found")
        events=[]
        for p in db.query(Purchase).filter(Purchase.supplier_id==party_id,Purchase.payment_method=="account").all(): events.append({"date":p.created_at.isoformat(),"type":"Purchase Invoice","ref":p.invoice_no,"debit":float(p.total),"credit":0})
        for r in db.query(PurchaseReturn).filter(PurchaseReturn.supplier_id==party_id).all(): events.append({"date":r.created_at.isoformat(),"type":"Purchase Return","ref":r.return_no,"debit":0,"credit":float(r.total)})
        for p in db.query(AccountPayment).filter(AccountPayment.party_type=="supplier",AccountPayment.party_id==party_id).all(): events.append({"date":p.created_at.isoformat(),"type":"Payment","ref":f"PAY-{p.id:05d}","debit":0,"credit":float(p.amount)})
        name=party.name
    else: raise HTTPException(400,"Invalid party type")
    events.sort(key=lambda x:x["date"])
    bal=0
    for e in events: bal+=e["debit"]-e["credit"]; e["balance"]=round(bal,2)
    return {"party_type":party_type,"party_id":party_id,"name":name,"balance":round(bal,2),"events":events}

@app.get("/api/returns/sales")
def list_sales_returns(db:Session=Depends(db_session)):
    rows=db.query(SalesReturn).order_by(SalesReturn.id.desc()).all()
    return [{"id":r.id,"return_no":r.return_no,"sale_id":r.sale_id,"customer_id":r.customer_id,"total":float(r.total),"payment_method":r.payment_method,"created_at":r.created_at.isoformat()} for r in rows]

@app.post("/api/returns/sales")
def create_sales_return(data:ReturnIn,db:Session=Depends(db_session)):
    sale=db.query(Sale).filter(Sale.id==data.original_id).first()
    if not sale: raise HTTPException(404,"Original sale not found")
    original=db.query(SaleItem).filter(SaleItem.sale_id==sale.id).all(); requested={x.product_id:x.quantity for x in data.items}
    total=0; checked=[]
    for pid,qty in requested.items():
        it=next((x for x in original if x.product_id==pid),None)
        already=sum(x.quantity for rr in db.query(SalesReturn).filter(SalesReturn.sale_id==sale.id).all() for x in db.query(SalesReturnItem).filter(SalesReturnItem.return_id==rr.id,SalesReturnItem.product_id==pid).all())
        if not it or qty<=0 or qty+already>it.quantity: raise HTTPException(400,"Return quantity exceeds sold quantity")
        total+=float(it.unit_price)*qty; checked.append((pid,qty,float(it.unit_price)))
    no=f"SRET-{db.query(SalesReturn).count()+1:05d}"; r=SalesReturn(return_no=no,sale_id=sale.id,customer_id=sale.customer_id,total=total,payment_method=data.payment_method); db.add(r); db.flush()
    for pid,qty,price in checked:
        prod=db.query(Product).filter(Product.id==pid).first(); prod.quantity += qty; db.add(SalesReturnItem(return_id=r.id,product_id=pid,quantity=qty,unit_price=price,total=price*qty))
    if sale.customer_id and sale.payment_method=="account":
        c=db.query(Customer).filter(Customer.id==sale.customer_id).first(); c.balance=max(0,float(c.balance or 0)-total)
    db.commit(); return {"success":True,"return_no":no,"total":total}

@app.get("/api/returns/purchases")
def list_purchase_returns(db:Session=Depends(db_session)):
    rows=db.query(PurchaseReturn).order_by(PurchaseReturn.id.desc()).all()
    return [{"id":r.id,"return_no":r.return_no,"purchase_id":r.purchase_id,"supplier_id":r.supplier_id,"total":float(r.total),"payment_method":r.payment_method,"created_at":r.created_at.isoformat()} for r in rows]

@app.post("/api/returns/purchases")
def create_purchase_return(data:ReturnIn,db:Session=Depends(db_session)):
    purchase=db.query(Purchase).filter(Purchase.id==data.original_id).first()
    if not purchase: raise HTTPException(404,"Original purchase not found")
    original=db.query(PurchaseItem).filter(PurchaseItem.purchase_id==purchase.id).all(); requested={x.product_id:x.quantity for x in data.items}
    total=0; checked=[]
    for pid,qty in requested.items():
        it=next((x for x in original if x.product_id==pid),None)
        already=sum(x.quantity for rr in db.query(PurchaseReturn).filter(PurchaseReturn.purchase_id==purchase.id).all() for x in db.query(PurchaseReturnItem).filter(PurchaseReturnItem.return_id==rr.id,PurchaseReturnItem.product_id==pid).all())
        if not it or qty<=0 or qty+already>it.quantity: raise HTTPException(400,"Return quantity exceeds purchased quantity")
        total+=float(it.unit_cost)*qty; checked.append((pid,qty,float(it.unit_cost)))
    no=f"PRET-{db.query(PurchaseReturn).count()+1:05d}"; r=PurchaseReturn(return_no=no,purchase_id=purchase.id,supplier_id=purchase.supplier_id,total=total,payment_method=data.payment_method); db.add(r); db.flush()
    for pid,qty,cost in checked:
        prod=db.query(Product).filter(Product.id==pid).first()
        if not prod or prod.quantity<qty: raise HTTPException(400,"Insufficient stock for return")
        prod.quantity-=qty; db.add(PurchaseReturnItem(return_id=r.id,product_id=pid,quantity=qty,unit_cost=cost,total=cost*qty))
    if purchase.supplier_id and purchase.payment_method=="account":
        sup=db.query(Supplier).filter(Supplier.id==purchase.supplier_id).first(); sup.balance=max(0,float(sup.balance or 0)-total)
    db.commit(); return {"success":True,"return_no":no,"total":total}

@app.get("/api/returns/sales/{return_id}")
def sales_return_detail(return_id:int,db:Session=Depends(db_session)):
    r=db.query(SalesReturn).filter(SalesReturn.id==return_id).first()
    if not r: raise HTTPException(404,"Sales return not found")
    items=[]
    for i in db.query(SalesReturnItem).filter(SalesReturnItem.return_id==r.id).all():
        p=db.query(Product).filter(Product.id==i.product_id).first(); items.append({"name":p.name if p else "Deleted Product","sku":p.sku if p else "","quantity":i.quantity,"unit_price":float(i.unit_price),"total":float(i.total)})
    return {"id":r.id,"return_no":r.return_no,"sale_id":r.sale_id,"total":float(r.total),"payment_method":r.payment_method,"created_at":r.created_at.isoformat(),"items":items}

@app.get("/api/returns/purchases/{return_id}")
def purchase_return_detail(return_id:int,db:Session=Depends(db_session)):
    r=db.query(PurchaseReturn).filter(PurchaseReturn.id==return_id).first()
    if not r: raise HTTPException(404,"Purchase return not found")
    items=[]
    for i in db.query(PurchaseReturnItem).filter(PurchaseReturnItem.return_id==r.id).all():
        p=db.query(Product).filter(Product.id==i.product_id).first(); items.append({"name":p.name if p else "Deleted Product","sku":p.sku if p else "","quantity":i.quantity,"unit_cost":float(i.unit_cost),"total":float(i.total)})
    return {"id":r.id,"return_no":r.return_no,"purchase_id":r.purchase_id,"total":float(r.total),"payment_method":r.payment_method,"created_at":r.created_at.isoformat(),"items":items}
