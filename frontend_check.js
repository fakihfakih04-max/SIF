
const $=id=>document.getElementById(id), API="/api";
const contentEl=document.getElementById("content");
let demo=true, productsData=[], customersData=[];
async function login(){
  err.textContent="Signing in...";
  const username=u.value.trim(), password=p.value;

  // Real backend authentication when the server is available.
  try{
    const r=await fetch("/api/login",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({username,password})
    });
    const d=await r.json().catch(()=>({}));
    if(r.ok){
      sessionStorage.setItem("sifUser",JSON.stringify(d.user));
      openSIF();
      return;
    }
    if(r.status===401){
      err.textContent=d.detail||"Invalid username or password.";
      return;
    }
  }catch(e){
    // Server unavailable: continue with local admin demo so the UI is not blocked.
  }

  // Local login for testing/offline UI.
  if(username==="admin" && password==="admin"){
    sessionStorage.setItem("sifUser",JSON.stringify({username:"admin",role:"admin",offline:true}));
    openSIF();
  }else{
    err.textContent="Invalid username or password.";
  }
}

function openSIF(){
  document.getElementById("login").classList.add("hidden");
  document.getElementById("app").classList.remove("hidden");
  if(typeof dashboard==="function") dashboard();
}
function logout(){location.reload()}
document.querySelectorAll("#nav button").forEach(b=>b.onclick=()=>{document.querySelectorAll("#nav button").forEach(x=>x.classList.remove("active"));b.classList.add("active");page(b.dataset.page);side.classList.remove("open")});
function page(p){({dashboard,products:liveProductsPage,pos:livePOSPage,mobile:()=>catalogPage('Mobile Phones','Mobile Phones','Phones with photo, price, barcode and stock.'),computers:()=>catalogPage('Computers','Computers & Laptops','Laptops and computers with photo, price, barcode and stock.'),accessories:()=>catalogPage('Accessories','Accessories','Accessories with photo, price, barcode and stock.'),repairs,customers,suppliers,purchases,sales,expenses,stock:stockLivePage,reports,users,settings}[p]||dashboard)()}
function head(t,s,btn=""){return `<div class="head"><div><h1>${t}</h1><p>${s}</p></div>${btn}</div>`}
function dashboard(){contentEl.innerHTML=head("Dashboard","Welcome back, Admin. Your business at a glance.",`<button class="btn primary" onclick="page('pos')">＋ New Sale</button>`)+`
<div class="stats">${stat("Total Sales","$ 2,450","↑ 12%","▣")}${stat("Purchases","$ 1,320","↑ 8%","↙")}${stat("Customers","436","↑ 5%","♙")}${stat("Products","1,254","↑ 3%","◈")}</div>
<div class="grid2"><div class="card"><div class="title"><b>Sales — Last 7 Days</b><span class="muted">This Week</span></div><div class="bars">${[42,61,49,70,64,88,67].map((x,i)=>`<div class="bar" style="height:${x}%"><i>${["14","15","16","17","18","19","20"][i]}</i></div>`).join("")}</div></div>
<div class="card"><div class="title"><b>Top Selling Products</b><span class="muted">View All</span></div><table><tr><th>#</th><th>Product</th><th>Qty</th></tr><tr><td>1</td><td>iPhone 15 Pro 256GB</td><td>12</td></tr><tr><td>2</td><td>Samsung S24 Ultra</td><td>8</td></tr><tr><td>3</td><td>MacBook Air M2</td><td>6</td></tr><tr><td>4</td><td>AirPods Pro 2</td><td>15</td></tr><tr><td>5</td><td>USB-C Cable</td><td>25</td></tr></table></div></div>
<div class="quick"><button onclick="page('pos')">🛒<br>New Sale</button><button onclick="openAddProduct()">＋<br>Add Product</button><button onclick="page('repairs')">⚒<br>New Repair</button><button onclick="page('purchases')">▣<br>New Purchase</button><button onclick="page('customers')">♙<br>Add Customer</button></div>
<div class="grid2"><div class="card"><div class="title"><b>Recent Sales</b></div><table><tr><th>Invoice</th><th>Customer</th><th>Total</th><th>Status</th></tr><tr><td>INV-00125</td><td>Ali Ahmad</td><td>$850</td><td><span class="badge paid">Paid</span></td></tr><tr><td>INV-00124</td><td>Rana Fawaz</td><td>$320</td><td><span class="badge paid">Paid</span></td></tr><tr><td>INV-00123</td><td>Walk-in</td><td>$120</td><td><span class="badge pending">Pending</span></td></tr></table></div>
<div class="card"><div class="title"><b>Repair Status</b></div><p>🔵 In Progress <b style="float:right">12</b></p><p>🟢 Ready <b style="float:right">8</b></p><p>🟠 Waiting Parts <b style="float:right">4</b></p><p>⚪ Delivered <b style="float:right">4</b></p></div></div>`}
function stat(t,v,tr,i){return `<div class="card stat"><div><small>${t}</small><h2>${v}</h2><span class="green">${tr}</span></div><div class="icon">${i}</div></div>`}
function products(){modulePage("Products","Products, barcode, stock, cost and selling price.",`<button class="btn primary" onclick="showForm('product')">＋ Add Product</button>`,productTable())}
function productTable(){return `<div class="toolbar"><input placeholder="Search product / SKU / barcode"><select><option>All Categories</option><option>Mobile Phones</option><option>Computers</option><option>Accessories</option></select><button class="btn light">Filter</button></div><table><tr><th>SKU</th><th>Product</th><th>Category</th><th>Barcode</th><th>Cost</th><th>Price</th><th>Qty</th><th>Status</th></tr>
<tr><td>IPH15P256</td><td>iPhone 15 Pro 256GB</td><td>Mobile</td><td>123456789</td><td>$900</td><td>$1,100</td><td>7</td><td><span class="badge paid">In Stock</span></td></tr>
<tr><td>S24U256</td><td>Samsung S24 Ultra</td><td>Mobile</td><td>223456789</td><td>$760</td><td>$950</td><td>4</td><td><span class="badge paid">In Stock</span></td></tr>
<tr><td>USBC01</td><td>USB-C Cable</td><td>Accessories</td><td>323456789</td><td>$7</td><td>$15</td><td>25</td><td><span class="badge paid">In Stock</span></td></tr></table>`}
function showForm(type){contentEl.insertAdjacentHTML("beforeend",`<div class="card" id="modal" style="margin-top:15px"><div class="title"><b>${type==="product"?"Add Product":"New Record"}</b><button class="btn light" onclick="modal.remove()">Close</button></div><div class="form-grid"><div><label>Name</label><input placeholder="Product name"></div><div><label>SKU</label><input placeholder="SKU"></div><div><label>Barcode</label><input placeholder="Barcode"></div><div><label>Cost</label><input type="number" placeholder="0.00"></div><div><label>Sale Price</label><input type="number" placeholder="0.00"></div><div><label>Quantity</label><input type="number" placeholder="0"></div></div><div class="form-actions"><button class="btn primary" onclick="alert('Record saved in demo mode')">Save</button></div></div>`)}
function modulePage(t,s,action,body){contentEl.innerHTML=head(t,s,action)+`<div class="module">${body}</div>`}
function pos(){modulePage("Point of Sale","Fast checkout with barcode, IMEI/Serial and customer accounts.",`<button class="btn light">Hold Sale</button>`, `<div class="grid2"><div class="card"><div class="toolbar"><input placeholder="Scan barcode or search product"><button class="btn primary">Scan</button></div><table><tr><th>Item</th><th>IMEI/Serial</th><th>Qty</th><th>Price</th><th>Total</th></tr><tr><td>iPhone 15 Pro 256GB</td><td>IMEI required</td><td>1</td><td>$1,100</td><td>$1,100</td></tr></table></div><div class="card"><h3>Checkout</h3><p>Subtotal <b style="float:right">$1,100</b></p><p>Discount <b style="float:right">$0</b></p><hr><h2>Total <b style="float:right">$1,100</b></h2><button class="btn primary" style="width:100%">Cash Payment</button></div></div>`)}
function mobile(){modulePage("Mobile Phones","IMEI 1 / IMEI 2, serial, storage, color and warranty.",`<button class="btn primary">＋ Add Phone</button>`,`<table><tr><th>Device</th><th>IMEI 1</th><th>IMEI 2</th><th>Serial</th><th>Color</th><th>Status</th></tr><tr><td>iPhone 15 Pro 256GB</td><td>352099...</td><td>352100...</td><td>F2L...</td><td>Black</td><td><span class="badge paid">In Stock</span></td></tr></table>`)}
function computers(){modulePage("Computers & Laptops","Serial number, specifications, warranty and device stock.",`<button class="btn primary">＋ Add Computer</button>`,`<table><tr><th>Device</th><th>Serial</th><th>CPU</th><th>RAM</th><th>SSD</th><th>Price</th></tr><tr><td>MacBook Air M2</td><td>FVFG...</td><td>Apple M2</td><td>16 GB</td><td>512 GB</td><td>$1,250</td></tr></table>`)}
function accessories(){modulePage("Accessories","Barcode-based quantity inventory.",`<button class="btn primary">＋ Add Accessory</button>`,productTable())}
function repairs(){modulePage("Repair Center","Track every repair from intake to delivery.",`<button class="btn primary">＋ New Repair</button>`,`<div class="kpis"><div class="kpi">In Progress<b>12</b></div><div class="kpi">Ready<b>8</b></div><div class="kpi">Waiting Parts<b>4</b></div></div><br><table><tr><th>Ticket</th><th>Customer</th><th>Device</th><th>Problem</th><th>Status</th><th>Cost</th></tr><tr><td>REP-00125</td><td>Ali Ahmad</td><td>iPhone 14 Pro</td><td>Screen</td><td><span class="badge progress">In Progress</span></td><td>$120</td></tr></table>`)}
function customers(){modulePage("Customers","Customer accounts, balances and history.",`<button class="btn primary">＋ Add Customer</button>`,`<table><tr><th>Code</th><th>Customer</th><th>Phone</th><th>Balance</th><th>Action</th></tr><tr><td>CUS-0001</td><td>Ali Ahmad</td><td>70 123 456</td><td>$120</td><td><button class="btn light">View</button></td></tr><tr><td>CUS-0002</td><td>Walk-in</td><td>-</td><td>$0</td><td><button class="btn light">View</button></td></tr></table>`)}
function suppliers(){modulePage("Suppliers","Supplier accounts and purchase history.",`<button class="btn primary">＋ Add Supplier</button>`,`<div class="empty">Supplier management is ready for database connection.</div>`)}
function purchases(){modulePage("Purchases","Purchase invoices and stock receiving.",`<button class="btn primary">＋ New Purchase</button>`,`<div class="empty">Create purchase invoices, receive stock and update costs.</div>`)}
function sales(){modulePage("Sales","Sales invoices, payments and customer accounts.",`<button class="btn primary" onclick="page('pos')">＋ New Sale</button>`,`<table><tr><th>Invoice</th><th>Date</th><th>Customer</th><th>Total</th><th>Payment</th></tr><tr><td>INV-00125</td><td>20-09-2026</td><td>Ali Ahmad</td><td>$850</td><td>Cash</td></tr></table>`)}
function expenses(){modulePage("Expenses","Operating expenses and payment records.",`<button class="btn primary">＋ Add Expense</button>`,`<div class="empty">Expense tracking module.</div>`)}
function stock(){modulePage("Stock Management","Real-time quantities, low-stock alerts and stock valuation.",`<button class="btn light">Stock Adjustment</button>`,`<div class="kpis"><div class="kpi">Stock Items<b>1,254</b></div><div class="kpi">Low Stock<b class="orange">18</b></div><div class="kpi">Stock Value<b>$185,420</b></div></div><br>${productTable()}`)}
function reports(){modulePage("Reports","Business reports and printable summaries.",`<button class="btn primary">Export Report</button>`,`<div class="kpis"><div class="kpi">Today Sales<b>$1,245</b></div><div class="kpi">Gross Profit<b>$328</b></div><div class="kpi">Repairs Revenue<b>$560</b></div></div><div class="empty">Sales • Profit • Stock • Customers • Purchases • Repairs reports.</div>`)}
function users(){modulePage("Users & Permissions","Control access by role.",`<button class="btn primary">＋ Add User</button>`,`<table><tr><th>User</th><th>Role</th><th>Status</th></tr><tr><td>admin</td><td>Administrator</td><td><span class="badge paid">Active</span></td></tr><tr><td>cashier</td><td>Cashier</td><td><span class="badge paid">Active</span></td></tr><tr><td>technician</td><td>Repair Technician</td><td><span class="badge paid">Active</span></td></tr></table>`)}
function settings(){modulePage("Settings","Company, currency, invoice, tax and system settings.",`<button class="btn primary">Save Settings</button>`,`<div class="form-grid"><div><label>Company Name</label><input value="SIF Mobile & Computer"></div><div><label>Currency</label><select><option>USD</option><option>LBP</option></select></div><div><label>VAT %</label><input value="11"></div><div><label>Invoice Prefix</label><input value="INV-"></div><div><label>Phone</label><input placeholder="+961"></div><div><label>Address</label><input placeholder="Store address"></div></div>`)}

/* Phase 4 live module helpers */
let liveProducts=[];
const API_BASE = (location.protocol === "file:") ? "http://127.0.0.1:8000" : "";
async function apiJSON(url, options={}){
  try{
    const r=await fetch(API_BASE + url, options);
    const d=await r.json().catch(()=>({detail:"Server returned an invalid response"}));
    if(!r.ok) throw new Error(d.detail||("HTTP " + r.status));
    return d;
  }catch(e){
    if(e instanceof TypeError || /Failed to fetch|NetworkError|Load failed/i.test(e.message||"")){
      throw new Error("SIF server is not running. Close this page, run START_SIF.bat, then open http://127.0.0.1:8000/");
    }
    throw e;
  }
}
async function refreshLiveProducts(){
  try{
    liveProducts=await apiJSON("/api/products");
    renderLiveProductTable();
    updatePOSProducts();
  }catch(e){ liveProducts=[]; }
}
function renderLiveProductTable(){
  const el=document.getElementById("liveProducts"); if(!el)return;
  el.innerHTML=liveProducts.length?liveProducts.map(p=>`
    <tr>
      <td>${p.image_url?`<img class="item-thumb" src="${p.image_url}" onerror="this.src='';this.alt='No photo'">`:`<div class="item-thumb">Photo</div>`}</td>
      <td>${p.sku}</td><td><b>${p.name}</b></td><td>${p.barcode||""}</td>
      <td>$${Number(p.cost).toFixed(2)}</td><td>$${Number(p.sale_price).toFixed(2)}</td>
      <td>$${Number(p.wholesale_price||0).toFixed(2)}</td><td>${p.quantity}</td>
      <td><span class="badge ${p.quantity<=p.reorder_level?'pending':'paid'}">${p.quantity<=p.reorder_level?'Low':'OK'}</span></td>
      <td><div class="actions"><button class="btn light" onclick="editProduct(${p.id})">Edit</button><button class="btn danger" onclick="deleteProduct(${p.id})">Delete</button></div></td>
    </tr>`).join(""):`<tr><td colspan="10" class="empty">No products yet. Add your first product.</td></tr>`;
}

function previewProductPhoto(input, previewId, hiddenId){
  const file=input.files&&input.files[0];
  if(!file)return;
  if(!file.type.startsWith("image/")){alert("Please select an image file.");input.value="";return}
  const reader=new FileReader();
  reader.onload=()=>{document.getElementById(hiddenId).value=reader.result;document.getElementById(previewId).src=reader.result};
  reader.readAsDataURL(file);
}

async function saveLiveProduct(){
  const body={
    sku:document.getElementById("psku").value.trim(),
    name:document.getElementById("pname").value.trim(),
    barcode:document.getElementById("pbarcode").value.trim()||null,
    category:document.getElementById("pcat").value,
    product_type:document.getElementById("ptype").value,
    cost:Number(document.getElementById("pcost").value||0),
    sale_price:Number(document.getElementById("pprice").value||0),
    quantity:Number(document.getElementById("pqty").value||0),
    reorder_level:Number(document.getElementById("preorder").value||0),
    imei_required:document.getElementById("pimei").checked,
    serial_required:document.getElementById("pserial").checked,
    warranty_months:Number(document.getElementById("pwarranty").value||0),
    image_url:document.getElementById("pimage").value.trim()||null,
    wholesale_price:Number(document.getElementById("pwholesale").value||0),
    vip_price:Number(document.getElementById("pvip").value||0)
  };
  if(!body.sku||!body.name){alert("SKU and Product Name are required.");return;}
  try{
    await apiJSON("/api/products",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
    alert("Product saved successfully.");
    document.getElementById("productFormLive")?.remove();
    await refreshLiveProducts();
  }catch(e){alert(e.message)}
}
function openAddProduct(category="", productType=""){
  try {
    page("products");
    openLiveProductForm(category, productType);
  } catch(e) {
    console.error(e);
    alert("Unable to open Add Product: " + (e.message || e));
  }
}
function openLiveProductForm(category="", productType=""){
  if(document.getElementById("productFormLive")){ document.getElementById("productFormLive").scrollIntoView({behavior:"smooth",block:"start"}); return; }
  contentEl.insertAdjacentHTML("beforeend",`
  <div class="card" id="productFormLive" style="margin-top:15px">
    <div class="title"><b>Add Product — Live Database</b><button class="btn light" onclick="document.getElementById('productFormLive')?.remove()">Close</button></div>
    <div class="form-grid">
      <div><label>SKU *</label><input id="psku" placeholder="IPH15P256"></div>
      <div><label>Product Name *</label><input id="pname" placeholder="iPhone 15 Pro 256GB"></div>
      <div><label>Barcode</label><input id="pbarcode" placeholder="Scan / type barcode"></div>
      <div><label>Category</label><select id="pcat"><option>Loading categories...</option></select></div>
      <div><label>Type</label><select id="ptype"><option value="">Loading types...</option></select></div>
      <div><label>Cost</label><input id="pcost" type="number" step="0.01" value="0"></div>
      <div><label>Sale Price</label><input id="pprice" type="number" step="0.01" value="0"></div>
      <div><label>Wholesale Price</label><input id="pwholesale" type="number" step="0.01" value="0"></div>
      <div><label>VIP Price</label><input id="pvip" type="number" step="0.01" value="0"></div>
      <div><label>Item Photo</label><input id="pimageFile" type="file" accept="image/*" onchange="previewProductPhoto(this,'pimagePreview','pimage')"><input id="pimage" type="hidden"><img id="pimagePreview" style="display:none;max-width:90px;max-height:70px;margin-top:8px;border-radius:10px;border:1px solid #dbe4ee" alt="Photo preview"></div>
      <div><label>Opening Quantity</label><input id="pqty" type="number" value="0"></div>
      <div><label>Reorder Level</label><input id="preorder" type="number" value="2"></div>
      <div><label>Warranty (months)</label><input id="pwarranty" type="number" value="0"></div>
      <div><label><input id="pimei" type="checkbox" style="width:auto"> IMEI required</label></div>
      <div><label><input id="pserial" type="checkbox" style="width:auto"> Serial required</label></div>
    </div>
    <div class="form-actions"><button class="btn primary" onclick="saveLiveProduct()">Save Product</button></div>
  </div>`);
  loadProductCatalogCombos(category, productType);
  document.getElementById("productFormLive")?.scrollIntoView({behavior:"smooth",block:"start"});
}
async function loadProductCatalogCombos(selectedCategory="", selectedType="") {
  try {
    const [cats,types]=await Promise.all([apiJSON("/api/categories"),apiJSON("/api/product-types")]);
    const c=document.getElementById("pcat"), t=document.getElementById("ptype");
    if(c){ c.innerHTML=cats.map(x=>`<option value="${esc(x.name)}">${esc(x.name)}</option>`).join("") || `<option value="">No categories</option>`; if(selectedCategory) c.value=selectedCategory; }
    if(t){ t.innerHTML=types.map(x=>`<option value="${esc(x.code)}">${esc(x.name)}</option>`).join("") || `<option value="">No types</option>`; if(selectedType) t.value=selectedType; }
  } catch(e) { console.error(e); }
}
function downloadBlob(blob,filename){const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=filename;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},1000)}
async function downloadProductsExcel(){try{const r=await fetch(API+"/api/products/export");if(!r.ok)throw new Error(await r.text());downloadBlob(await r.blob(),"SIF_Products.xlsx")}catch(e){alert("Export failed: "+e.message)}}
async function downloadProductTemplate(){try{const r=await fetch(API+"/api/products/template");if(!r.ok)throw new Error(await r.text());downloadBlob(await r.blob(),"SIF_Products_Import_Template.xlsx")}catch(e){alert("Template download failed: "+e.message)}}
async function importProductsExcel(input){const file=input.files?.[0];if(!file)return;const fd=new FormData();fd.append("file",file);try{const r=await fetch(API+"/api/products/import",{method:"POST",body:fd});const d=await r.json();if(!r.ok)throw new Error(d.detail||"Import failed");alert(`Import complete. Created: ${d.created} | Updated: ${d.updated}${d.error_count?` | Errors: ${d.error_count}`:""}`);await refreshLiveProducts();}catch(e){alert(e.message)}finally{input.value=""}}

function liveProductsPage(){
  modulePage("Products","Live database: products, photos, barcode, prices and quantity.",
    `<button class="btn light" onclick="priceChecker()">⌕ Price Checker</button> <button class="btn light" onclick="downloadProductsExcel()">⇩ Export Excel</button> <button class="btn light" onclick="downloadProductTemplate()">⇩ Excel Template</button> <button class="btn light" onclick="document.getElementById('productExcelInput').click()">⇧ Import Excel</button> <input id="productExcelInput" type="file" accept=".xlsx,.xlsm" style="display:none" onchange="importProductsExcel(this)"> <button class="btn primary" onclick="openLiveProductForm()">＋ Add Product</button>`,
    `<div class="toolbar"><input id="liveSearch" placeholder="Search SKU / product / barcode" oninput="filterLiveProducts()"><button class="btn light" onclick="refreshLiveProducts()">Refresh</button></div>
     <table><thead><tr><th>Photo</th><th>SKU</th><th>Product</th><th>Barcode</th><th>Cost</th><th>Retail</th><th>Wholesale</th><th>Qty</th><th>Status</th><th>Actions</th></tr></thead>
     <tbody id="liveProducts"></tbody></table>`);
  refreshLiveProducts();
}
function filterLiveProducts(){
  const q=(document.getElementById("liveSearch")?.value||"").toLowerCase();
  const el=document.getElementById("liveProducts"); if(!el)return;
  const rows=liveProducts.filter(p=>`${p.sku} ${p.name} ${p.barcode||""}`.toLowerCase().includes(q));
  el.innerHTML=rows.map(p=>`<tr>
    <td>${p.image_url?`<img class="item-thumb" src="${p.image_url}" alt="">`:`<div class="item-thumb">No photo</div>`}</td>
    <td><b>${esc(p.sku)}</b></td><td>${esc(p.name)}</td><td>${esc(p.barcode||"")}</td>
    <td>$${Number(p.cost).toFixed(2)}</td><td>$${Number(p.sale_price).toFixed(2)}</td><td>$${Number(p.wholesale_price||0).toFixed(2)}</td>
    <td>${p.quantity}</td><td>${p.quantity<=p.reorder_level?'<span class="badge pending">Low</span>':'<span class="badge paid">OK</span>'}</td>
    <td><button class="btn light" onclick="editProduct(${p.id})">Edit</button> <button class="btn danger" onclick="deleteProduct(${p.id})">Delete</button> <button class="btn light" onclick="clearProductPhoto(${p.id})">Delete Photo</button></td>
  </tr>`).join("") || `<tr><td colspan="10" class="empty">No products found.</td></tr>`;
}
let cart=[];

async function editProduct(id){
  const p=liveProducts.find(x=>x.id===id); if(!p)return;
  contentEl.insertAdjacentHTML("beforeend",`
  <div class="card" id="editProductBox" style="margin-top:15px">
    <div class="title"><b>Edit Product — ${p.name}</b><button class="btn light" onclick="editProductBox.remove()">Close</button></div>
    <div class="form-grid">
      <div><label>SKU</label><input id="eSku" value="${esc(p.sku)}"></div>
      <div><label>Name</label><input id="eName" value="${esc(p.name)}"></div>
      <div><label>Barcode</label><input id="eBarcode" value="${esc(p.barcode||"")}"></div>
      <div><label>Category</label><select id="eCategory"><option value="${esc(p.category||"")}">${esc(p.category||"")}</option></select></div>
      <div><label>Type</label><select id="eType"><option value="${esc(p.product_type||"")}">${esc(p.product_type||"")}</option></select></div>
      <div><label>Cost</label><input id="eCost" type="number" value="${p.cost}"></div>
      <div><label>Sale Price</label><input id="ePrice" type="number" value="${p.sale_price}"></div>
      <div><label>Wholesale Price</label><input id="eWholesale" type="number" value="${p.wholesale_price||0}"></div>
      <div><label>VIP Price</label><input id="eVip" type="number" value="${p.vip_price||0}"></div>
      <div><label>Quantity</label><input id="eQty" type="number" value="${p.quantity}"></div>
      <div><label>Reorder Level</label><input id="eReorder" type="number" value="${p.reorder_level}"></div>
      <div style="grid-column:1/-1"><label>Item Photo</label>
<div class="photo-picker">
  <img id="eImagePreview" class="photo-preview" src="${p.image_url||''}" alt="No photo">
  <div style="flex:1">
    <input id="eImageFile" type="file" accept="image/*" onchange="previewProductPhoto(this,'eImagePreview','eImage')">
    <input id="eImage" type="hidden" value="${esc(p.image_url||"")}">
    <div class="muted" style="margin-top:6px">Choose a replacement photo from your computer / Pictures / Studio.</div>
  </div>
</div></div>
    </div>
    <div class="form-actions"><button class="btn light" onclick="clearEditPhoto(${id})">Delete Photo</button><button class="btn primary" onclick="saveEditProduct(${id})">Save Changes</button></div>
  </div>`);
  loadEditCatalogCombos(p.category||"",p.product_type||"");
  window.scrollTo({top:document.body.scrollHeight,behavior:"smooth"});
}
async function loadEditCatalogCombos(cat,type){try{const [cats,types]=await Promise.all([apiJSON("/api/categories"),apiJSON("/api/product-types")]);const c=document.getElementById("eCategory"),t=document.getElementById("eType");if(c){c.innerHTML=cats.map(x=>`<option value="${esc(x.name)}">${esc(x.name)}</option>`).join("");c.value=cat}if(t){t.innerHTML=types.map(x=>`<option value="${esc(x.code)}">${esc(x.name)} (${esc(x.code)})</option>`).join("");t.value=type}}catch(e){}}
async function clearEditPhoto(id){if(!confirm("Delete this product photo?"))return;const old=liveProducts.find(x=>x.id===id);if(!old)return;try{await apiJSON("/api/products/"+id,{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify({sku:old.sku,name:old.name,barcode:old.barcode||null,category:document.getElementById("eCategory")?.value||old.category||"Accessories",product_type:document.getElementById("eType")?.value||old.product_type||"accessory",cost:Number(old.cost||0),sale_price:Number(old.sale_price||0),wholesale_price:Number(old.wholesale_price||0),vip_price:Number(old.vip_price||0),quantity:Number(old.quantity||0),reorder_level:Number(old.reorder_level||0),warranty_months:Number(old.warranty_months||0),imei_required:!!old.imei_required,serial_required:!!old.serial_required,image_url:null})});document.getElementById("eImage").value="";document.getElementById("eImagePreview").removeAttribute("src");await refreshLiveProducts();alert("Photo deleted.")}catch(e){alert(e.message)}}
function esc(v){return String(v).replace(/&/g,"&amp;").replace(/"/g,"&quot;").replace(/</g,"&lt;").replace(/>/g,"&gt;")}
async function saveEditProduct(id){
  const old=liveProducts.find(x=>x.id===id);
  const body={
    sku:eSku.value.trim(),name:eName.value.trim(),barcode:eBarcode.value.trim()||null,
    category:old.category||"Accessories",product_type:old.product_type||"accessory",
    cost:Number(eCost.value||0),sale_price:Number(ePrice.value||0),
    wholesale_price:Number(eWholesale.value||0),vip_price:Number(eVip.value||0),
    quantity:Number(eQty.value||0),reorder_level:Number(eReorder.value||0),
    warranty_months:old.warranty_months||0,imei_required:!!old.imei_required,
    serial_required:!!old.serial_required,image_url:eImage.value.trim()||null
  };
  try{await apiJSON("/api/products/"+id,{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
    alert("Product updated.");editProductBox.remove();await refreshLiveProducts();
  }catch(e){alert(e.message)}
}
async function deleteProduct(id){
  const p=liveProducts.find(x=>x.id===id); if(!p)return;
  if(!confirm(`Delete "${p.name}"?`))return;
  try{await apiJSON("/api/products/"+id,{method:"DELETE"});alert("Product deleted.");await refreshLiveProducts();}
  catch(e){alert(e.message)}
}
async function clearProductPhoto(id){
  const p=liveProducts.find(x=>x.id===id); if(!p)return;
  if(!p.image_url)return alert("This product has no photo.");
  if(!confirm(`Delete photo from "${p.name}"?`))return;
  try{
    const body={sku:p.sku,name:p.name,barcode:p.barcode||null,category:p.category||"Accessories",product_type:p.product_type||"accessory",cost:Number(p.cost||0),sale_price:Number(p.sale_price||0),wholesale_price:Number(p.wholesale_price||0),vip_price:Number(p.vip_price||0),quantity:Number(p.quantity||0),reorder_level:Number(p.reorder_level||0),warranty_months:Number(p.warranty_months||0),imei_required:!!p.imei_required,serial_required:!!p.serial_required,image_url:null};
    await apiJSON("/api/products/"+id,{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
    await refreshLiveProducts();
  }catch(e){alert(e.message)}
}



function productCard(p){return `<article class="catalog-card">${p.image_url?`<img src="${p.image_url}" alt="${esc(p.name)}">`:`<div class="item-thumb">No Photo</div>`}<h3>${esc(p.name)}</h3><div class="code">${esc(p.sku)} • ${esc(p.barcode||"No barcode")}</div><div class="catalog-price">$${Number(p.sale_price).toFixed(2)}</div><div class="muted">Stock: ${p.quantity} • Wholesale: $${Number(p.wholesale_price||0).toFixed(2)}</div><div class="catalog-actions"><button class="btn light" onclick="editProduct(${p.id})">Edit</button><button class="btn primary" onclick="priceChecker('${esc(p.sku)}')">Price</button></div></article>`}
async function catalogPage(category,title,subtitle){let addCat=category, addType=category==='Mobile Phones'?'mobile':category==='Computers'?'computer':'accessory';modulePage(title,subtitle,`<button class="btn light" onclick="priceChecker()">⌕ Price Checker</button> <button class="btn primary" onclick="openAddProduct('${category}','${addType}')">＋ Add Product</button>`);contentEl.insertAdjacentHTML('beforeend',`<div class="module"><div class="category-pills"><button onclick="catalogPage('Mobile Phones','Mobile Phones','Phones with photo, price, barcode and stock.')">Phones</button><button onclick="catalogPage('Computers','Computers & Laptops','Laptops and computers with photo, price, barcode and stock.')">Computers</button><button onclick="catalogPage('Accessories','Accessories','Accessories with photo, price, barcode and stock.')">Accessories</button><button onclick="stockLivePage()">All Stock</button></div><div id="catalogGrid" class="catalog-grid"></div></div>`);try{let rows=await apiJSON('/api/products');let f=rows.filter(p=>String(p.category).toLowerCase()===category.toLowerCase());document.getElementById('catalogGrid').innerHTML=f.map(productCard).join('')||'<div class="empty">No items found.</div>'}catch(e){document.getElementById('catalogGrid').innerHTML='<div class="empty">Start SIF server first.</div>'}}
let stockData=[];async function stockLivePage(){modulePage('Stock Management','ALL ITEMS — Phones, Computers, Laptops and Accessories.',`<button class="btn primary" onclick="priceChecker()">⌕ Price Checker</button>`);contentEl.insertAdjacentHTML('beforeend',`<div class="module"><div class="toolbar"><input id="stockSearch" placeholder="Search all items / SKU / barcode" oninput="filterStock()"><select id="stockCategory" onchange="filterStock()"><option value="">All Categories</option><option value="Mobile Phones">Phones</option><option value="Computers">Computers</option><option value="Accessories">Accessories</option></select><button class="btn light" onclick="loadStockLive()">Refresh</button></div><div id="stockSummary" class="kpis" style="margin:18px 0"></div><div class="stock-table-wrap"><table><thead><tr><th>Photo</th><th>Code</th><th>Item</th><th>Category</th><th>Barcode</th><th>Cost</th><th>Retail</th><th>Wholesale</th><th>VIP</th><th>Qty</th><th>Status</th><th>Actions</th></tr></thead><tbody id="stockRows"></tbody></table></div></div>`);loadStockLive()}
async function loadStockLive(){try{stockData=await apiJSON('/api/products');renderStockSummary(stockData);renderStock(stockData)}catch(e){let x=document.getElementById('stockRows');if(x)x.innerHTML='<tr><td colspan="12" class="empty">Start SIF server first.</td></tr>';let sm=document.getElementById('stockSummary');if(sm)sm.innerHTML='<div class="kpi"><span>Stock Summary</span><b>Server offline</b></div>'}}
function renderStockSummary(rows){const products=rows.length;const qty=rows.reduce((a,p)=>a+Number(p.quantity||0),0);const cost=rows.reduce((a,p)=>a+Number(p.cost||0)*Number(p.quantity||0),0);const sales=rows.reduce((a,p)=>a+Number(p.sale_price||0)*Number(p.quantity||0),0);const sm=document.getElementById('stockSummary');if(!sm)return;sm.innerHTML=`<div class="kpi"><span>Total Products</span><b>${products.toLocaleString()}</b></div><div class="kpi"><span>Total Quantity</span><b>${qty.toLocaleString()}</b></div><div class="kpi"><span>Total Cost</span><b>$${cost.toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}</b><small>${Math.round(cost*Number(settingsCache.usd_lbp||89500)).toLocaleString()} LBP</small></div><div class="kpi"><span>Total Sales Value</span><b>$${sales.toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}</b><small>${Math.round(sales*Number(settingsCache.usd_lbp||89500)).toLocaleString()} LBP</small></div>`}
function filterStock(){let q=(document.getElementById('stockSearch')?.value||'').toLowerCase(),c=document.getElementById('stockCategory')?.value||'';renderStock(stockData.filter(p=>(!c||p.category===c)&&(`${p.sku} ${p.name} ${p.barcode||''} ${p.category}`).toLowerCase().includes(q)))}
function renderStock(rows){let el=document.getElementById('stockRows');if(!el)return;el.innerHTML=rows.map(p=>`<tr><td>${p.image_url?`<img class="item-thumb" src="${p.image_url}" alt="">`:`<div class="item-thumb"></div>`}</td><td><b>${esc(p.sku)}</b></td><td>${esc(p.name)}</td><td>${esc(p.category)}</td><td>${esc(p.barcode||'')}</td><td>$${Number(p.cost||0).toFixed(2)}</td><td>$${Number(p.sale_price||0).toFixed(2)}</td><td>$${Number(p.wholesale_price||0).toFixed(2)}</td><td>$${Number(p.vip_price||0).toFixed(2)}</td><td><b>${p.quantity}</b></td><td><span class="badge ${p.quantity<=p.reorder_level?'pending':'paid'}">${p.quantity<=p.reorder_level?'LOW STOCK':'IN STOCK'}</span></td><td><button class="btn light" onclick="editProduct(${p.id})">Edit</button> <button class="btn primary" onclick="priceChecker('${esc(p.sku)}')">Price</button></td></tr>`).join('')||'<tr><td colspan="12" class="empty">No stock items.</td></tr>'}
function livePOSPage(){
  modulePage("Point of Sale","Live checkout: select products, build a cart and save the invoice.",
  `<button class="btn light" onclick="cart=[];livePOSPage()">Clear Cart</button>`,
  `<div class="grid2">
    <div class="card"><div class="toolbar"><input id="posSearch" placeholder="Search product or barcode" oninput="renderPOSProducts()"></div><div id="posProducts"></div></div>
    <div class="card"><div class="title"><b>Current Invoice</b><span id="cartCount" class="muted">0 items</span></div>
      <div id="cartLines"></div>
      <hr><p>Subtotal <b id="cartSub" style="float:right">$0.00</b></p>
      <p>Discount <input id="saleDiscount" type="number" value="0" min="0" style="width:100px;float:right" oninput="renderCart()"></p>
      <h2>Total <b id="cartTotal" style="float:right">$0.00</b></h2>
      <select id="payment" style="margin-bottom:10px"><option value="cash">Cash</option><option value="card">Card</option><option value="account">Customer Account</option></select>
      <button class="btn primary" style="width:100%" onclick="completeSale()">Complete Sale</button>
    </div></div>`);
  refreshLiveProducts();
}
function updatePOSProducts(){if(document.getElementById("posProducts")) renderPOSProducts()}
function renderPOSProducts(){
  const el=document.getElementById("posProducts"); if(!el)return;
  const q=(document.getElementById("posSearch")?.value||"").toLowerCase();
  const rows=liveProducts.filter(p=>`${p.name} ${p.sku} ${p.barcode||""}`.toLowerCase().includes(q));
  el.innerHTML=rows.map(p=>`<div class="card" style="display:flex;justify-contentEl:space-between;align-items:center;margin-bottom:8px;padding:12px">
    <div><b>${p.name}</b><div class="muted">${p.sku} • ${p.barcode||"No barcode"} • Stock: ${p.quantity}</div></div>
    <button class="btn primary" ${p.quantity<=0?"disabled":""} onclick="addToCart(${p.id})">$${Number(p.sale_price).toFixed(2)} ＋</button>
  </div>`).join("")||`<div class="empty">No matching products.</div>`;
}
function addToCart(id){
  const p=liveProducts.find(x=>x.id===id); if(!p)return;
  const existing=cart.find(x=>x.product_id===id);
  if(existing){if(existing.quantity<p.quantity)existing.quantity++;}else cart.push({product_id:id,name:p.name,price:Number(p.sale_price),quantity:1,max:p.quantity});
  renderCart();
}
function renderCart(){
  const lines=document.getElementById("cartLines"); if(!lines)return;
  let sub=0;
  lines.innerHTML=cart.map((x,i)=>{let t=x.price*x.quantity;sub+=t;return `<div style="padding:9px 0;border-bottom:1px solid var(--border)">
    <b>${x.name}</b><span style="float:right">$${t.toFixed(2)}</span><div class="muted">Qty <button class="btn light" onclick="changeQty(${i},-1)">−</button> ${x.quantity} <button class="btn light" onclick="changeQty(${i},1)">＋</button></div></div>`}).join("")||`<div class="empty">Cart is empty.</div>`;
  const disc=Number(document.getElementById("saleDiscount")?.value||0), total=Math.max(0,sub-disc);
  document.getElementById("cartSub").textContent="$"+sub.toFixed(2);
  document.getElementById("cartTotal").textContent="$"+total.toFixed(2);
  document.getElementById("cartCount").textContent=cart.reduce((a,x)=>a+x.quantity,0)+" items";
}
function changeQty(i,d){let x=cart[i];x.quantity+=d;if(x.quantity<=0)cart.splice(i,1);else if(x.quantity>x.max)x.quantity=x.max;renderCart()}
async function completeSale(){
  if(!cart.length){alert("Cart is empty.");return}
  const discount=Number(document.getElementById("saleDiscount").value||0);
  try{
    const r=await apiJSON("/api/sales",{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({discount,payment_method:document.getElementById("payment").value,
      items:cart.map(x=>({product_id:x.product_id,quantity:x.quantity,unit_price:x.price}))})});
    alert(`Sale completed: ${r.invoice_no} — $${Number(r.total).toFixed(2)}`);
    cart=[]; await refreshLiveProducts(); renderCart();
  }catch(e){alert(e.message)}
}
document.addEventListener("keydown",e=>{if(e.key==="Enter"&&document.activeElement&&(document.activeElement.id==="u"||document.activeElement.id==="p"))login()});

// ===== PHASE 14 BUSINESS WORKFLOW OVERRIDES =====
let settingsCache={usd_lbp:89500,vat_rate:11,vat_enabled:'true',company_name:'SIF Mobile & Computer',invoice_prefix:'INV-'};
async function loadSettings(){try{settingsCache=Object.assign(settingsCache,await apiJSON('/api/settings'))}catch(e){} return settingsCache}
function moneyDual(usd){const u=Number(usd||0), r=Number(settingsCache.usd_lbp||89500);return `<div class="money-row"><span class="money">$${u.toFixed(2)}</span><span class="money">${Math.round(u*r).toLocaleString()} LBP</span></div>`}
function openModal(title,body,actions=''){const old=document.getElementById('globalModal');if(old)old.remove();document.body.insertAdjacentHTML('beforeend',`<div class="modal-back" id="globalModal"><div class="modal-box"><div class="title"><b>${title}</b><button class="btn light" onclick="globalModal.remove()">Close</button></div>${body}<div class="form-actions">${actions}</div></div></div>`)}
function esc2(v){return String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]))}

async function priceChecker(initial=''){
 await loadSettings();
 const popupMode=new URLSearchParams(location.search).get('priceCheckerWindow')==='1';
 openModal('SIF Professional Price Checker',`<div class="toolbar" style="position:sticky;top:55px;background:#fff;z-index:1;padding:10px 0"><input id="pcq" value="${esc2(initial)}" placeholder="Product name / SKU / barcode" style="flex:1"><select id="pct"><option value="retail">Retail</option><option value="wholesale">Wholesale</option><option value="vip">VIP</option></select><button class="btn primary" id="pcCheckBtn">Check Price</button><button class="btn light" onclick="togglePriceCheckerMax()">⛶ Maximize</button>${popupMode?'':'<button class="btn light" onclick="openPriceCheckerWindow(document.getElementById(\'pcq\')?.value||\'\')">↗ Open Window</button>'}</div><div id="pcResults" style="margin-top:18px"></div>`,popupMode?'':`<button class="btn light" onclick="globalModal.remove()">Close</button>`);
 const sel=document.getElementById('pct'), btn=document.getElementById('pcCheckBtn'), q=document.getElementById('pcq');
 if(btn)btn.onclick=runPriceCheck;
 if(sel)sel.onchange=runPriceCheck;
 if(q)q.onkeydown=e=>{if(e.key==='Enter')runPriceCheck()};
 if(initial) await runPriceCheck();
 else await runPriceCheck();
}
function togglePriceCheckerMax(){const m=document.getElementById('globalModal');if(m)m.classList.toggle('pcMaximized')}
function openPriceCheckerWindow(initial=''){
 const q=encodeURIComponent(initial||'');
 const url=location.origin+location.pathname+'?priceCheckerWindow=1&q='+q;
 const w=window.open(url,'SIFPriceChecker','popup=yes,width='+screen.availWidth+',height='+screen.availHeight+',left=0,top=0,resizable=yes,scrollbars=yes');
 if(w){try{w.moveTo(0,0);w.resizeTo(screen.availWidth,screen.availHeight)}catch(e){} w.focus();} else alert('Please allow popups for Price Checker.');
}

async function runPriceCheck(){
 const q=(document.getElementById('pcq')?.value||'').trim().toLowerCase();
 const type=document.getElementById('pct')?.value||'retail';
 const box=document.getElementById('pcResults'); if(!box)return;
 try{
  const rows=await apiJSON('/api/products');
  const matches=rows.filter(p=>!q || `${p.name||''} ${p.sku||''} ${p.barcode||''}`.toLowerCase().includes(q));
  box.innerHTML=matches.map(p=>{
   const price=type==='wholesale'?Number(p.wholesale_price||0):type==='vip'?Number(p.vip_price||0):Number(p.sale_price||0);
   const label=type==='wholesale'?'WHOLESALE PRICE':type==='vip'?'VIP PRICE':'RETAIL PRICE';
   const lbp=Math.round(price*Number(settingsCache.usd_lbp||89500));
   return `<article class="card" style="max-width:560px"><div style="display:flex;gap:16px;align-items:center">${p.image_url?`<img src="${p.image_url}" style="width:90px;height:90px;object-fit:cover;border-radius:12px">`:`<div class="item-thumb">No Photo</div>`}<div><h2 style="margin:0 0 6px">${esc2(p.name)}</h2><div class="muted">SKU: ${esc2(p.sku)} • Barcode: ${esc2(p.barcode||'-')} • Stock: ${p.quantity}</div></div></div><div style="margin-top:18px"><div class="muted">${label}</div><div class="price-big">$${price.toFixed(2)}</div><div style="font-size:20px;font-weight:800">${lbp.toLocaleString()} LBP</div></div></article>`;
  }).join('')||'<div class="empty">No matching product.</div>';
 }catch(e){box.innerHTML=`<div class="empty">Cannot load products: ${esc2(e.message)}</div>`}
}

async function customers(){const rows=await apiJSON('/api/customers').catch(()=>[]);modulePage('Customers','Customer accounts, balances and history.',`<button class="btn primary" onclick="customerForm()">＋ Add Customer</button>`,`<div class="toolbar"><input id="custQ" placeholder="Search customer / phone / code" oninput="filterCustomers()"></div><div id="custTable"></div>`);window._custRows=rows;renderCustomers(rows)}
function renderCustomers(rows){const el=document.getElementById('custTable');if(!el)return;el.innerHTML=`<table><thead><tr><th>Code</th><th>Customer</th><th>Phone</th><th>Address</th><th>Balance</th></tr></thead><tbody>${rows.map(x=>`<tr><td>${esc2(x.code)}</td><td>${esc2(x.name)}</td><td>${esc2(x.phone||'')}</td><td>${esc2(x.address||'')}</td><td>${moneyDual(x.balance)}</td></tr>`).join('')}</tbody></table>`}
function filterCustomers(){const q=(document.getElementById('custQ').value||'').toLowerCase();renderCustomers((window._custRows||[]).filter(x=>`${x.code} ${x.name} ${x.phone||''}`.toLowerCase().includes(q)))}
function customerForm(){openModal('Add Customer',`<div class="form-grid"><div><label>Code</label><input id="ccode" value="CUS-${String((window._custRows||[]).length+1).padStart(4,'0')}"></div><div><label>Name</label><input id="cname"></div><div><label>Phone</label><input id="cphone"></div><div><label>Address</label><input id="caddr"></div></div>`,`<button class="btn primary" onclick="saveCustomer()">Save Customer</button>`)}
async function saveCustomer(){try{await apiJSON('/api/customers',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code:ccode.value,name:cname.value,phone:cphone.value,address:caddr.value})});globalModal.remove();customers()}catch(e){alert(e.message)}}

async function suppliers(){const rows=await apiJSON('/api/suppliers').catch(()=>[]);modulePage('Suppliers','Supplier accounts and purchase history.',`<button class="btn primary" onclick="supplierForm()">＋ Add Supplier</button>`,`<div id="supTable"></div>`);window._supRows=rows;document.getElementById('supTable').innerHTML=`<table><tr><th>Code</th><th>Supplier</th><th>Phone</th><th>Address</th><th>Balance</th></tr>${rows.map(x=>`<tr><td>${esc2(x.code)}</td><td>${esc2(x.name)}</td><td>${esc2(x.phone||'')}</td><td>${esc2(x.address||'')}</td><td>${moneyDual(x.balance)}</td></tr>`).join('')}</table>`}
function supplierForm(){openModal('Add Supplier',`<div class="form-grid"><div><label>Code</label><input id="scode" value="SUP-${String((window._supRows||[]).length+1).padStart(4,'0')}"></div><div><label>Name</label><input id="sname"></div><div><label>Phone</label><input id="sphone"></div><div><label>Address</label><input id="saddr"></div></div>`,`<button class="btn primary" onclick="saveSupplier()">Save Supplier</button>`)}
async function saveSupplier(){try{await apiJSON('/api/suppliers',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code:scode.value,name:sname.value,phone:sphone.value,address:saddr.value})});globalModal.remove();suppliers()}catch(e){alert(e.message)}}

async function purchases(){
 await loadSettings();
 const rows=await apiJSON('/api/purchases').catch(()=>[]);
 modulePage('Purchases','Official purchase invoices, supplier accounts and stock receiving.',`<button class="btn primary" onclick="purchaseForm()">＋ New Purchase</button>`,
 `<div class="module"><table><thead><tr><th>Invoice</th><th>Date</th><th>Supplier</th><th>Subtotal</th><th>VAT</th><th>Total</th><th>Payment</th></tr></thead><tbody>${rows.map(x=>`<tr><td><b>${esc2(x.invoice_no)}</b></td><td>${new Date(x.created_at).toLocaleString()}</td><td>${x.supplier_id?('Supplier #'+x.supplier_id):'Walk-in Supplier'}</td><td>${moneyDual(x.subtotal)}</td><td>${x.vat_enabled?esc2(x.vat_rate+'%'):'No VAT'}</td><td>${moneyDual(x.total)}</td><td>${esc2(x.payment_method)}</td></tr>`).join('')||'<tr><td colspan="7" class="empty">No purchase invoices yet.</td></tr>'}</tbody></table></div>`);
}
async function purchaseForm(){
 try{
  await loadSettings();
  const [ps,sups]=await Promise.all([apiJSON('/api/products'),apiJSON('/api/suppliers')]);
  if(!ps.length){alert('No products available. Add a product first.');return;}
  const productOptions=ps.map(p=>`<option value="${p.id}" data-cost="${Number(p.cost||0)}">${esc2(p.name)} — ${esc2(p.sku)} — Cost $${Number(p.cost||0).toFixed(2)}</option>`).join('');
  const supplierOptions=sups.map(s=>`<option value="${s.id}">${esc2(s.name)}</option>`).join('');
  openModal('New Official Purchase',`<div class="form-grid">
   <div><label>Supplier</label><select id="purSup"><option value="">Walk-in Supplier</option>${supplierOptions}</select></div>
   <div><label>Payment</label><select id="purPay"><option value="cash">Cash</option><option value="card">Card</option><option value="account">Supplier Account</option></select></div>
   <div style="grid-column:1/-1"><label>Product</label><select id="purProd">${productOptions}</select></div>
   <div><label>Quantity</label><input id="purQty" type="number" value="1" min="1" step="1"></div>
   <div><label>Unit Cost USD</label><input id="purCost" type="number" step="0.01" min="0"></div>
   <div><label>VAT</label><label class="switch"><input id="purVat" type="checkbox"> Enable VAT</label></div>
   <div><label>VAT Rate %</label><input id="purVatRate" type="number" value="${Number(settingsCache.vat_rate||11)}" step="0.01" min="0"></div>
   <div><label>Total</label><input id="purTotal" readonly></div>
  </div><div id="purchaseError" class="empty" style="display:none;margin-top:12px"></div>`,
  `<button class="btn light" onclick="document.getElementById('globalModal')?.remove()">Cancel</button><button class="btn primary" id="savePurchaseBtn">Save Official Purchase Invoice</button>`);
  const prod=document.getElementById('purProd'), cost=document.getElementById('purCost'), qty=document.getElementById('purQty'), vat=document.getElementById('purVat'), rate=document.getElementById('purVatRate'), total=document.getElementById('purTotal');
  function recalc(){const sub=Number(cost.value||0)*Number(qty.value||0);const v=vat.checked?sub*Number(rate.value||0)/100:0;total.value=(sub+v).toFixed(2);}
  function setCost(){cost.value=Number(prod.selectedOptions[0]?.dataset.cost||0).toFixed(2);recalc()}
  prod.onchange=setCost; qty.oninput=recalc; cost.oninput=recalc; vat.onchange=recalc; rate.oninput=recalc; setCost();
  document.getElementById('savePurchaseBtn').onclick=savePurchase;
 }catch(e){alert('Purchase screen error: '+e.message)}
}
function setPurchaseCost(){const o=document.getElementById('purProd')?.selectedOptions?.[0];const el=document.getElementById('purCost');if(o&&el){el.value=Number(o.dataset.cost||0).toFixed(2);el.dispatchEvent(new Event('input'));}}
async function savePurchase(){
 const err=document.getElementById('purchaseError');
 try{
  const supplier=document.getElementById('purSup')?.value||'';
  const product=document.getElementById('purProd')?.value||'';
  const qty=Number(document.getElementById('purQty')?.value||0);
  const cost=Number(document.getElementById('purCost')?.value||0);
  const vat=document.getElementById('purVat')?.checked||false;
  const vatRate=Number(document.getElementById('purVatRate')?.value||0);
  const payment=document.getElementById('purPay')?.value||'cash';
  if(!product)throw new Error('Select a product.');
  if(!Number.isInteger(qty)||qty<=0)throw new Error('Quantity must be a whole number greater than 0.');
  if(!Number.isFinite(cost)||cost<0)throw new Error('Unit cost is invalid.');
  const r=await apiJSON('/api/purchases',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({supplier_id:supplier?Number(supplier):null,payment_method:payment,vat_enabled:vat,vat_rate:vat?vatRate:0,items:[{product_id:Number(product),quantity:qty,unit_cost:cost}]})});
  document.getElementById('globalModal')?.remove();
  alert(`Purchase ${r.invoice_no} saved successfully.\nTotal: $${Number(r.total).toFixed(2)}\nStock updated: +${qty}`);
  purchases();
 }catch(e){if(err){err.style.display='block';err.textContent='Purchase failed: '+e.message}else alert('Purchase failed: '+e.message)}
}

async function sales(){const rows=await apiJSON('/api/sales').catch(()=>[]);modulePage('Sales','Official sales invoices, VAT, payments and customer accounts.',`<button class="btn primary" onclick="page('pos')">＋ New Sale</button>`,`<table><tr><th>Invoice</th><th>Date</th><th>Subtotal</th><th>VAT</th><th>Total</th><th>Payment</th></tr>${rows.map(x=>`<tr><td>${x.invoice_no}</td><td>${new Date(x.created_at).toLocaleString()}</td><td>${esc2(x.customer_name||"Walk-in Customer")}</td><td>${moneyDual(x.subtotal)}</td><td>${x.vat_enabled?x.vat_rate+'%':'No VAT'}</td><td>${moneyDual(x.total)}</td><td>${x.payment_method}</td></tr>`).join('')}</table>`)}

async function repairs(){
  const rows=await apiJSON('/api/repairs').catch(()=>[]);
  modulePage('Repair Center','Professional repair intake, customer details, pricing and status tracking.',`<button class="btn primary" onclick="repairForm()">＋ New Repair</button>`,`
  <div class="stats">${stat('Repairs',rows.length,'','⚒')}${stat('Sales Value',moneyDual(rows.reduce((a,x)=>a+Number(x.sales_price||0),0)),'','▣')}${stat('Repair Cost',moneyDual(rows.reduce((a,x)=>a+Number(x.estimated_cost||0),0)),'','◈')}${stat('Profit',moneyDual(rows.reduce((a,x)=>a+Number(x.profit||0),0)),'','↗')}</div>
  <div class="card"><table><tr><th>Ticket</th><th>Customer</th><th>Phone</th><th>Address</th><th>Device</th><th>Problem</th><th>Status</th><th>Cost</th><th>Sales Price</th><th>Profit</th><th>Actions</th></tr>${rows.map(x=>`<tr><td><b>${esc2(x.ticket_no)}</b></td><td>${esc2(x.customer_name)}</td><td>${esc2(x.customer_phone||'')}</td><td>${esc2(x.customer_address||'')}</td><td>${esc2(x.device_name)}</td><td>${esc2(x.problem)}</td><td><span class="badge">${esc2(x.status)}</span></td><td>${moneyDual(x.estimated_cost)}</td><td><b>${moneyDual(x.sales_price)}</b></td><td>${moneyDual(x.profit)}</td><td><button class="btn light" onclick="repairEdit(${x.id})">Edit</button> <button class="btn danger" onclick="repairDelete(${x.id})">Delete</button></td></tr>`).join('')}</table></div>`)
}

async function repairForm(existing=null){
  const cs=await apiJSON('/api/customers').catch(()=>[]);
  const x=existing||{};
  const opts=cs.map(c=>`<option value="${c.id}" ${Number(c.id)===Number(x.customer_id)?'selected':''}>${esc2(c.name)}</option>`).join('');
  openModal(x.id?'Edit Repair':'New Repair',`<div class="form-grid">
    <div><label>Customer</label><select id="repCust" onchange="fillRepairCustomer()"><option value="">Walk-in Customer</option>${opts}</select></div>
    <div><label>Customer Phone</label><input id="repPhone" value="${esc2(x.customer_phone||'')}"></div>
    <div style="grid-column:1/-1"><label>Customer Address</label><input id="repAddress" value="${esc2(x.customer_address||'')}"></div>
    <div><label>Device / Model</label><input id="repDevice" value="${esc2(x.device_name||'')}" placeholder="iPhone 15 Pro / Dell Laptop"></div>
    <div><label>IMEI / Serial</label><input id="repSerial" value="${esc2(x.imei_or_serial||'')}"></div>
    <div><label>Status</label><select id="repStatus">${['received','diagnosing','waiting_parts','repairing','ready','delivered'].map(s=>`<option value="${s}" ${x.status===s?'selected':''}>${s.replace('_',' ')}</option>`).join('')}</select></div>
    <div><label>Technician</label><input id="repTech" value="${esc2(x.technician||'')}"></div>
    <div style="grid-column:1/-1"><label>Problem / Diagnosis <span style="font-weight:400;color:#64748b">(optional)</span></label><textarea id="repProblem" placeholder="Describe the customer problem or diagnosis (optional)">${esc2(x.problem||'')}</textarea></div>
    <div><label>Repair Cost $</label><input id="repCost" type="number" step="0.01" value="${Number(x.estimated_cost||0)}"></div>
    <div><label>Sales Price $</label><input id="repSales" type="number" step="0.01" value="${Number(x.sales_price||0)}"></div>
    <div><label>Warranty (days)</label><input id="repWarranty" type="number" value="${Number(x.warranty_days||0)}"></div>
    <div style="grid-column:1/-1"><label>Notes</label><textarea id="repNotes">${esc2(x.notes||'')}</textarea></div>
  </div>`,`<button class="btn primary" onclick="saveRepair(${x.id||'null'})">${x.id?'Save Changes':'Save Repair Ticket'}</button>`);
}

async function fillRepairCustomer(){
  const id=Number(document.getElementById('repCust').value||0); if(!id)return;
  const cs=await apiJSON('/api/customers').catch(()=>[]); const c=cs.find(z=>Number(z.id)===id); if(c){document.getElementById('repPhone').value=c.phone||'';document.getElementById('repAddress').value=c.address||'';}
}

async function saveRepair(id=null){try{
  const payload={customer_id:repCust.value?Number(repCust.value):null,device_name:repDevice.value.trim(),imei_or_serial:repSerial.value.trim(),problem:repProblem.value.trim(),status:repStatus.value,estimated_cost:Number(repCost.value||0),sales_price:Number(repSales.value||0),customer_phone:repPhone.value.trim(),customer_address:repAddress.value.trim(),technician:repTech.value.trim(),warranty_days:Number(repWarranty.value||0),notes:repNotes.value.trim()};
  const r=await apiJSON(id?`/api/repairs/${id}`:'/api/repairs',{method:id?'PUT':'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  globalModal.remove();alert(id?'Repair updated successfully':`Repair ${r.ticket_no} saved successfully`);repairs();
}catch(e){alert(e.message)}}

async function repairEdit(id){const rows=await apiJSON('/api/repairs');const x=rows.find(r=>Number(r.id)===Number(id));if(x)repairForm(x)}
async function repairDelete(id){if(!confirm('Delete this repair ticket?'))return;try{await apiJSON(`/api/repairs/${id}`,{method:'DELETE'});repairs()}catch(e){alert(e.message)}}

async function settings(){await loadSettings();modulePage('Back Office / Settings','Company, currency, invoice, VAT and editable product catalog.',`<button class="btn primary" onclick="saveSettings()">Save Settings</button>`,`<div class="form-grid"><div><label>Company Name</label><input id="setCompany" value="${esc2(settingsCache.company_name)}"></div><div><label>USD → LBP</label><input id="setRate" type="number" value="${Number(settingsCache.usd_lbp)}"></div><div><label>VAT %</label><input id="setVat" type="number" step="0.01" value="${Number(settingsCache.vat_rate)}"></div><div><label class="switch"><input id="setVatOn" type="checkbox" ${String(settingsCache.vat_enabled)==='true'?'checked':''}> Enable VAT by default</label></div><div><label>Invoice Prefix</label><input id="setPrefix" value="${esc2(settingsCache.invoice_prefix)}"></div></div><div class="card" style="margin-top:18px"><div class="title"><b>Categories & Product Types</b><span class="muted">Add, edit, delete and they instantly appear in Add Product.</span></div><div class="grid2"><div><h3>Categories</h3><div class="form-grid"><input id="newCatName" placeholder="Category name"><input id="newCatImage" type="file" accept="image/*"><button class="btn primary" onclick="addBackOfficeCategory()">＋ Add Category</button></div><div id="categoryAdminList" style="margin-top:12px"></div></div><div><h3>Product Types</h3><div class="form-grid"><input id="newTypeName" placeholder="Type name"><input id="newTypeCode" placeholder="Code e.g. mobile"><button class="btn primary" onclick="addBackOfficeType()">＋ Add Type</button></div><div id="typeAdminList" style="margin-top:12px"></div></div></div></div>`);loadCatalogAdmin()}
async function loadCatalogAdmin(){
  try{
    const [cats,types]=await Promise.all([apiJSON('/api/categories'),apiJSON('/api/product-types')]);
    const ce=document.getElementById('categoryAdminList'), te=document.getElementById('typeAdminList');
    if(ce) ce.innerHTML=cats.map(c=>`<div class="card" style="display:flex;align-items:center;gap:10px;margin:6px 0;padding:9px">
      ${c.image_url?`<img src="${c.image_url}" style="width:48px;height:48px;object-fit:cover;border-radius:8px">`:`<div class="item-thumb" style="width:48px;height:48px">No</div>`}
      <div style="flex:1"><b>${esc2(c.name)}</b></div>
      <button class="btn light" onclick="openCategoryEditor(${c.id})">Edit</button>
      <button class="btn danger" onclick="deleteBackOfficeCategory(${c.id})">Delete</button>
    </div>`).join('') || '<div class="empty">No categories.</div>';
    if(te) te.innerHTML=types.map(t=>`<div class="card" style="display:flex;align-items:center;gap:10px;margin:6px 0;padding:9px">
      <div style="flex:1"><b>${esc2(t.name)}</b> <span class="muted">(${esc2(t.code)})</span></div>
      <button class="btn light" onclick="openTypeEditor(${t.id})">Edit</button>
      <button class="btn danger" onclick="deleteBackOfficeType(${t.id})">Delete</button>
    </div>`).join('') || '<div class="empty">No product types.</div>';
  }catch(e){alert(e.message)}
}
async function openCategoryEditor(id){
  const cats=await apiJSON('/api/categories'); const c=cats.find(x=>x.id===id); if(!c)return;
  const old=document.getElementById('catalogEditor'); if(old)old.remove();
  document.body.insertAdjacentHTML('beforeend',`<div id="catalogEditor" class="modal-back"><div class="modal-box" style="max-width:560px;width:92%;background:#fff;padding:22px">
    <div class="title"><b>Edit Category</b><button class="btn light" onclick="document.getElementById('catalogEditor').remove()">Close</button></div>
    <label>Category Name</label><input id="editCatName" value="${esc2(c.name)}">
    <label style="margin-top:12px">Category Image</label>
    <input id="editCatImage" type="file" accept="image/*" onchange="previewCategoryEditImage(event)">
    <div id="editCatPhotoArea" style="margin-top:12px">
      ${c.image_url?`<div style="display:flex;align-items:center;gap:12px"><img id="editCatPreview" src="${c.image_url}" style="width:100px;height:100px;object-fit:cover;border-radius:10px;border:1px solid #dbe5ef"><button type="button" class="btn danger" onclick="deleteCategoryPhoto(${id})">🗑 Delete Photo</button></div>`:`<div class="muted">No category photo.</div>`}
    </div>
    <div class="form-actions" style="margin-top:16px"><button class="btn primary" onclick="saveCategoryEditor(${id})">Save Changes</button></div>
  </div></div>`);
}
function previewCategoryEditImage(e){const f=e.target.files?.[0];if(!f)return;const area=document.getElementById('editCatPhotoArea');const r=new FileReader();r.onload=()=>{area.innerHTML=`<div style="display:flex;align-items:center;gap:12px"><img id="editCatPreview" src="${r.result}" style="width:100px;height:100px;object-fit:cover;border-radius:10px;border:1px solid #dbe5ef"><span class="muted">New photo selected</span></div>`};r.readAsDataURL(f)}
async function deleteCategoryPhoto(id){
  if(!confirm('Delete this category photo?'))return;
  const c=(await apiJSON('/api/categories')).find(x=>x.id===id); if(!c)return;
  try{
    await apiJSON('/api/categories/'+id,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:c.name,image_url:null})});
    const input=document.getElementById('editCatImage'); if(input)input.value='';
    const area=document.getElementById('editCatPhotoArea'); if(area)area.innerHTML='<div class="muted">No category photo.</div>';
    await loadCatalogAdmin();
    alert('Category photo deleted.');
  }catch(e){alert(e.message)}
}
async function saveCategoryEditor(id){
  const c=(await apiJSON('/api/categories')).find(x=>x.id===id); if(!c)return;
  const f=document.getElementById('editCatImage')?.files?.[0]; let image=c.image_url||null; if(f) image=await fileToDataUrl(f);
  const name=document.getElementById('editCatName').value.trim(); if(!name)return alert('Category name is required.');
  try{await apiJSON('/api/categories/'+id,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,image_url:image})});document.getElementById('catalogEditor')?.remove();await loadCatalogAdmin();await loadProductCatalogCombos();alert('Category updated successfully.')}catch(e){alert(e.message)}
}
async function deleteBackOfficeCategory(id){if(!confirm('Delete this category?'))return;try{await apiJSON('/api/categories/'+id,{method:'DELETE'});await loadCatalogAdmin();await loadProductCatalogCombos();alert('Category deleted.')}catch(e){alert(e.message)}}
async function openTypeEditor(id){
  const types=await apiJSON('/api/product-types'); const t=types.find(x=>x.id===id); if(!t)return;
  const old=document.getElementById('catalogEditor'); if(old)old.remove();
  document.body.insertAdjacentHTML('beforeend',`<div id="catalogEditor" class="modal-back"><div class="modal-box" style="max-width:560px;width:92%;background:#fff;padding:22px">
    <div class="title"><b>Edit Product Type</b><button class="btn light" onclick="document.getElementById('catalogEditor').remove()">Close</button></div>
    <label>Type Name</label><input id="editTypeName" value="${esc2(t.name)}">
    <label style="margin-top:12px">Type Code</label><input id="editTypeCode" value="${esc2(t.code)}">
    <div class="form-actions" style="margin-top:16px"><button class="btn primary" onclick="saveTypeEditor(${id})">Save Changes</button></div>
  </div></div>`);
}
async function saveTypeEditor(id){
  const name=document.getElementById('editTypeName').value.trim(), code=document.getElementById('editTypeCode').value.trim(); if(!name||!code)return alert('Type name and code are required.');
  try{await apiJSON('/api/product-types/'+id,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,code})});document.getElementById('catalogEditor')?.remove();await loadCatalogAdmin();await loadProductCatalogCombos();alert('Product type updated successfully.')}catch(e){alert(e.message)}
}
async function addBackOfficeType(){const name=document.getElementById('newTypeName').value.trim();const code=document.getElementById('newTypeCode').value.trim();if(!name)return alert('Type name is required.');try{await apiJSON('/api/product-types',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,code:code||null})});document.getElementById('newTypeName').value='';document.getElementById('newTypeCode').value='';await loadCatalogAdmin();await loadProductCatalogCombos();alert('Type added. It is now available in Add Product.')}catch(e){alert(e.message)}}
async function deleteBackOfficeType(id){if(!confirm('Delete this product type?'))return;try{await apiJSON('/api/product-types/'+id,{method:'DELETE'});await loadCatalogAdmin();await loadProductCatalogCombos();alert('Type deleted.')}catch(e){alert(e.message)}}
function fileToDataUrl(file){return new Promise((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(r.result);r.onerror=reject;r.readAsDataURL(file)})}
async function saveSettings(){for(const [key,val] of [['company_name',setCompany.value],['usd_lbp',setRate.value],['vat_rate',setVat.value],['vat_enabled',String(setVatOn.checked)],['invoice_prefix',setPrefix.value]])await apiJSON('/api/settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key,value:val})});await loadSettings();alert('Settings saved');settings()}

async function reports(){const r=await apiJSON('/api/reports/summary').catch(()=>({}));modulePage('Reports','Business overview and official document totals.',`<button class="btn primary" onclick="page('sales')">Sales Invoices</button>`,`<div class="stats">${stat('Products',r.products||0,'','◈')}${stat('Customers',r.customers||0,'','♙')}${stat('Suppliers',r.suppliers||0,'','▤')}${stat('Repairs',r.repairs||0,'','⚒')}</div><div class="grid2"><div class="card"><h3>Sales Total</h3>${moneyDual(r.sales_total||0)}</div><div class="card"><h3>Purchases Total</h3>${moneyDual(r.purchase_total||0)}</div></div>`)}

// POS with VAT / customer / currency and official invoice preview
async function livePOSPage(){await loadSettings();modulePage('Point of Sale','Official sales invoice — Retail / Wholesale / VIP, VAT optional, USD + LBP.',`<button class="btn light" onclick="cart=[];livePOSPage()">Clear Cart</button>`,`<div class="grid2"><div class="card"><div class="toolbar"><input id="posSearch" placeholder="Scan barcode or search product" oninput="renderPOSProducts()"></div><div id="posProducts"></div></div><div class="card"><div class="title"><b>Current Invoice</b><span id="cartCount" class="muted">0 items</span></div><div class="form-grid"><div><label>Price Type</label><select id="posType" onchange="applyPOSPriceType()"><option value="retail">Retail</option><option value="wholesale">Wholesale</option><option value="vip">VIP</option></select></div><div><label>Customer</label><select id="posCustomer"><option value="">Walk-in Customer</option></select></div></div><div id="cartLines"></div><hr><p>Subtotal <b id="cartSub" style="float:right">$0.00</b></p><p>Discount <input id="saleDiscount" type="number" value="0" min="0" style="width:100px;float:right" oninput="renderCart()"></p><label class="switch"><input id="saleVat" type="checkbox" ${String(settingsCache.vat_enabled)==='true'?'checked':''} onchange="renderCart()"> VAT <span>${settingsCache.vat_rate}%</span></label><h2>Total <b id="cartTotal" style="float:right">$0.00</b></h2><div id="cartLbp" class="muted"></div><select id="payment" style="margin:10px 0"><option value="cash">Cash</option><option value="card">Card</option><option value="account">Customer Account</option></select><button class="btn primary" style="width:100%" onclick="completeSale()">Save Official Invoice</button></div></div>`);refreshLiveProducts();loadPOSCustomers()}
async function loadPOSCustomers(){try{const rows=await apiJSON("/api/customers");const el=document.getElementById("posCustomer");if(el)el.innerHTML=`<option value="">Walk-in Customer</option>${rows.map(c=>`<option value="${c.id}">${esc2(c.name)}${c.phone?" — "+esc2(c.phone):""}</option>`).join("")}`}catch(e){}}
function applyPOSPriceType(){cart.forEach(x=>{const p=liveProducts.find(p=>p.id===x.product_id);if(p)x.price=Number(document.getElementById('posType').value==='vip'?p.vip_price:document.getElementById('posType').value==='wholesale'?p.wholesale_price:p.sale_price)});renderCart()}
function addToCart(id){const p=liveProducts.find(x=>x.id===id);if(!p)return;const existing=cart.find(x=>x.product_id===id);const type=document.getElementById('posType')?.value||'retail';const price=Number(type==='vip'?p.vip_price:type==='wholesale'?p.wholesale_price:p.sale_price);if(existing){if(existing.quantity<p.quantity)existing.quantity++}else cart.push({product_id:id,name:p.name,price,quantity:1,max:p.quantity});renderCart()}
function renderCart(){const lines=document.getElementById('cartLines');if(!lines)return;let sub=0;lines.innerHTML=cart.map((x,i)=>{let t=x.price*x.quantity;sub+=t;return `<div style="padding:9px 0;border-bottom:1px solid var(--border)"><b>${esc2(x.name)}</b><span style="float:right">$${t.toFixed(2)}</span><div class="muted">Qty <button class="btn light" onclick="changeQty(${i},-1)">−</button> ${x.quantity} <button class="btn light" onclick="changeQty(${i},1)">＋</button></div></div>`}).join('')||'<div class="empty">Cart is empty.</div>';const disc=Number(document.getElementById('saleDiscount')?.value||0),net=Math.max(0,sub-disc),vat=document.getElementById('saleVat')?.checked?net*Number(settingsCache.vat_rate||0)/100:0,total=net+vat;document.getElementById('cartSub').textContent='$'+sub.toFixed(2);document.getElementById('cartTotal').textContent='$'+total.toFixed(2);document.getElementById('cartLbp').textContent=Math.round(total*Number(settingsCache.usd_lbp||89500)).toLocaleString()+' LBP';document.getElementById('cartCount').textContent=cart.reduce((a,x)=>a+x.quantity,0)+' items'}
async function completeSale(){if(!cart.length)return alert('Cart is empty');try{const type=document.getElementById('posType').value;const r=await apiJSON('/api/sales',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({customer_id:document.getElementById('posCustomer').value?Number(document.getElementById('posCustomer').value):null,discount:Number(document.getElementById('saleDiscount').value||0),payment_method:document.getElementById('payment').value,vat_enabled:document.getElementById('saleVat').checked,vat_rate:Number(settingsCache.vat_rate||0),currency:'USD',items:cart.map(x=>({product_id:x.product_id,quantity:x.quantity,unit_price:x.price}))})});showInvoice(r.invoice_no,r.subtotal,r.vat,r.total,document.getElementById("posCustomer").selectedOptions[0]?.textContent||"Walk-in Customer");cart=[];await refreshLiveProducts();renderCart()}catch(e){alert(e.message)}}
function showInvoice(no,sub,vat,total,customer){openModal('Official Invoice',`<div class="invoice-preview" id="printArea"><h2>${esc2(settingsCache.company_name)}</h2><p>Invoice: <b>${no}</b><br>Customer: <b>${esc2(customer)}</b><br>Date: ${new Date().toLocaleString()}</p><hr><p>Subtotal: $${Number(sub).toFixed(2)}</p><p>VAT: $${Number(vat||0).toFixed(2)}</p><h2>Total: $${Number(total).toFixed(2)}</h2><p>${Math.round(Number(total)*Number(settingsCache.usd_lbp||89500)).toLocaleString()} LBP</p><p style="text-align:center">Thank you</p></div>`,`<button class="btn primary" onclick="window.print()">Print Official Invoice</button>`)}



/* ===== PHASE 20 PROFESSIONAL POS / PRICE WINDOW / OFFICIAL DOCUMENTS ===== */
async function priceChecker(initial=''){
 const popupMode=new URLSearchParams(location.search).get('priceCheckerWindow')==='1';
 if(!popupMode){ openPriceCheckerWindow(initial); return; }
 await loadSettings();
 document.title='SIF Professional Price Checker';
 document.body.className='price-window';
 document.body.innerHTML=`<header class="pw-head"><div><div class="pw-brand">SIF <span>Mobile & Computer</span></div><div style="font-size:12px;color:#c8d9eb;margin-top:7px">PROFESSIONAL PRICE CHECKER</div></div><div class="pw-row"><button class="pw-btn" onclick="maximizePriceChecker()">⛶ Maximize</button><button class="pw-btn" style="background:#e8eef6;color:#10213d" onclick="window.close()">Close</button></div></header><main class="pw-body"><section class="pw-search"><div class="pw-row"><input id="pcq" value="${esc2(initial)}" placeholder="Search product, SKU or barcode" style="flex:1;min-width:260px"><select id="pct"><option value="retail">RETAIL</option><option value="wholesale">WHOLESALE</option><option value="vip">VIP</option></select><button class="pw-btn" id="pcCheckBtn">CHECK PRICE</button></div></section><section id="pcResults" class="pw-grid"></section></main>`;
 document.getElementById('pcCheckBtn').onclick=runPriceCheck;document.getElementById('pct').onchange=runPriceCheck;document.getElementById('pcq').onkeydown=e=>{if(e.key==='Enter')runPriceCheck()};
 setTimeout(()=>{try{window.moveTo(0,0);window.resizeTo(screen.availWidth,screen.availHeight)}catch(e){}},50);
 await runPriceCheck();
}
function maximizePriceChecker(){try{window.moveTo(0,0);window.resizeTo(screen.availWidth,screen.availHeight);window.focus()}catch(e){}}
async function runPriceCheck(){const q=(document.getElementById('pcq')?.value||'').trim().toLowerCase(),type=document.getElementById('pct')?.value||'retail',box=document.getElementById('pcResults');if(!box)return;try{const rows=await apiJSON('/api/products');const matches=rows.filter(p=>!q||`${p.name} ${p.sku} ${p.barcode||''}`.toLowerCase().includes(q));box.innerHTML=matches.map(p=>{const price=type==='retail'?Number(p.sale_price||0):type==='wholesale'?Number(p.wholesale_price||0):Number(p.vip_price||0);const label=type==='retail'?'RETAIL PRICE':type==='wholesale'?'WHOLESALE PRICE':'VIP PRICE';const lbp=Math.round(price*Number(settingsCache.usd_lbp||89500));return `<article class="pw-card"><div style="display:flex;gap:12px;align-items:center">${p.image_url?`<img src="${p.image_url}" style="width:92px;height:92px;object-fit:contain;border-radius:12px;background:#f5f8fc">`:`<div class="item-thumb">No Photo</div>`}<div><h3 style="margin:0">${esc2(p.name)}</h3><div class="pw-meta">${esc2(p.sku)} • ${esc2(p.barcode||'-')} • Stock ${p.quantity}</div></div></div><div class="pw-meta" style="margin-top:14px">${label}</div><div class="pw-price">$${price.toFixed(2)}</div><div style="font-size:18px;font-weight:900">${lbp.toLocaleString()} LBP</div></article>`}).join('')||'<div class="empty" style="grid-column:1/-1">No matching product.</div>'}catch(e){box.innerHTML=`<div class="empty" style="grid-column:1/-1">${esc2(e.message)}</div>`}}

let purchaseLines20=[];
async function purchaseForm(){await loadSettings();try{const [ps,sups]=await Promise.all([apiJSON('/api/products'),apiJSON('/api/suppliers')]);if(!ps.length){alert('Add products first.');return}purchaseLines20=[];window.purchaseProducts20=ps;const prodOpts=ps.map(p=>`<option value="${p.id}">${esc2(p.name)} — ${esc2(p.sku)} — Cost $${Number(p.cost||0).toFixed(2)}</option>`).join(''),supOpts=sups.map(s=>`<option value="${s.id}">${esc2(s.name)}</option>`).join('');openModal('OFFICIAL PURCHASE INVOICE',`<div class="form-grid"><div><label>Supplier</label><select id="p20sup"><option value="">Walk-in Supplier</option>${supOpts}</select></div><div><label>Payment</label><select id="p20pay"><option value="cash">Cash</option><option value="card">Card</option><option value="account">Supplier Account</option></select></div><div style="grid-column:1/-1"><label>Product</label><select id="p20prod">${prodOpts}</select></div><div><label>Quantity</label><input id="p20qty" type="number" min="1" value="1"></div><div><label>Unit Cost USD</label><input id="p20cost" type="number" min="0" step="0.01"></div><div><button class="btn light" id="p20add">＋ Add Item</button></div><div><label class="switch"><input id="p20vat" type="checkbox"> VAT</label></div><div><label>VAT Rate %</label><input id="p20rate" type="number" value="${Number(settingsCache.vat_rate||11)}" step="0.01"></div></div><div id="p20lines" style="margin-top:16px"></div><div class="card" style="margin-top:14px"><b>Subtotal</b><span id="p20sub" style="float:right">$0.00</span><br><b>VAT</b><span id="p20vatamt" style="float:right">$0.00</span><hr><h2>Total <span id="p20total" style="float:right">$0.00</span></h2></div>`,`<button class="btn light" onclick="globalModal.remove()">Cancel</button><button class="btn primary" id="p20save">Save Official Purchase</button>`);const sync=()=>{const p=window.purchaseProducts20.find(x=>x.id==p20prod.value);p20cost.value=Number(p?.cost||0).toFixed(2)};sync();p20prod.onchange=sync;p20add.onclick=()=>{const p=window.purchaseProducts20.find(x=>x.id==p20prod.value),q=Number(p20qty.value||0),c=Number(p20cost.value||0);if(!p||q<=0||c<0)return alert('Check product, quantity and cost.');purchaseLines20.push({product_id:p.id,name:p.name,quantity:q,unit_cost:c});renderPurchase20()};p20vat.onchange=renderPurchase20;p20rate.oninput=renderPurchase20;p20save.onclick=savePurchase20;renderPurchase20()}catch(e){alert('Purchase error: '+e.message)}}
function renderPurchase20(){const el=document.getElementById('p20lines');if(!el)return;let sub=0;el.innerHTML=purchaseLines20.map((x,i)=>{const t=x.quantity*x.unit_cost;sub+=t;return `<div style="padding:10px;border-bottom:1px solid var(--border)"><b>${esc2(x.name)}</b> × ${x.quantity}<span style="float:right">$${t.toFixed(2)} <button class="btn danger" onclick="purchaseLines20.splice(${i},1);renderPurchase20()">×</button></span></div>`}).join('')||'<div class="empty">Add items to purchase.</div>';const vat=p20vat.checked?sub*Number(p20rate.value||0)/100:0;p20sub.textContent='$'+sub.toFixed(2);p20vatamt.textContent='$'+vat.toFixed(2);p20total.textContent='$'+(sub+vat).toFixed(2)}
async function savePurchase20(){try{if(!purchaseLines20.length)throw Error('Add at least one item.');const r=await apiJSON('/api/purchases',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({supplier_id:p20sup.value?Number(p20sup.value):null,payment_method:p20pay.value,vat_enabled:p20vat.checked,vat_rate:p20vat.checked?Number(p20rate.value||0):0,items:purchaseLines20.map(x=>({product_id:x.product_id,quantity:x.quantity,unit_cost:x.unit_cost}))})});const supplier=p20sup.selectedOptions[0]?.textContent||'Walk-in Supplier';const html=officialPurchaseInvoice20(r,supplier);globalModal.remove();openModal('OFFICIAL PURCHASE INVOICE',html,`<button class="btn primary" onclick="printInvoice20()">Print Official Invoice</button>`);purchaseLines20=[]}catch(e){alert('Purchase failed: '+e.message)}}
function officialPurchaseInvoice20(r,supplier){return `<div class="invoice-preview" id="purchasePrintArea"><h1 style="margin:0">${esc2(settingsCache.company_name)}</h1><h3>OFFICIAL PURCHASE INVOICE</h3><p>Invoice: <b>${esc2(r.invoice_no)}</b><br>Date: ${new Date().toLocaleString()}<br>Supplier: <b>${esc2(supplier)}</b></p><table style="width:100%;border-collapse:collapse"><tr><th style="text-align:left">Item</th><th>Qty</th><th>Cost</th><th>Total</th></tr>${purchaseLines20.map(x=>`<tr><td>${esc2(x.name)}</td><td style="text-align:center">${x.quantity}</td><td style="text-align:right">$${x.unit_cost.toFixed(2)}</td><td style="text-align:right">$${(x.unit_cost*x.quantity).toFixed(2)}</td></tr>`).join('')}</table><hr><p>Subtotal <b style="float:right">$${Number(r.subtotal).toFixed(2)}</b></p><p>VAT <b style="float:right">$${Number(r.vat||0).toFixed(2)}</b></p><h2>Total <b style="float:right">$${Number(r.total).toFixed(2)}</b></h2><p style="text-align:right">${Math.round(Number(r.total)*Number(settingsCache.usd_lbp||89500)).toLocaleString()} LBP</p></div>`}
function printInvoice20(){const a=document.getElementById('purchasePrintArea');if(!a)return;const w=window.open('','_blank','width=900,height=900');if(!w)return;w.document.write('<html><head><title>Official Purchase Invoice</title><style>body{font-family:Arial;padding:30px}table{width:100%;border-collapse:collapse}th,td{padding:8px;border-bottom:1px solid #ddd}</style></head><body>'+a.outerHTML+'</body></html>');w.document.close();w.print()}

async function livePOSPage(){await loadSettings();const cs=await apiJSON('/api/customers').catch(()=>[]);modulePage('Point of Sale','OFFICIAL SALES INVOICE — multiple items, customer, VAT and print.',`<button class="btn light" onclick="cart=[];livePOSPage()">Clear Cart</button>`,`<div class="grid2"><div class="card"><div class="toolbar"><input id="posSearch" placeholder="Search product / barcode" oninput="renderPOSProducts()"></div><div id="posProducts"></div></div><div class="card"><div class="title"><b>OFFICIAL SALES INVOICE</b><span id="cartCount" class="muted">0 items</span></div><div class="form-grid"><div><label>Price Type</label><select id="posType" onchange="applyPOSPriceType()"><option value="retail">Retail</option><option value="wholesale">Wholesale</option><option value="vip">VIP</option></select></div><div><label>Customer</label><select id="posCustomer"><option value="">Walk-in Customer</option>${cs.map(c=>`<option value="${c.id}">${esc2(c.name)}</option>`).join('')}</select></div><div><label>Payment</label><select id="payment"><option value="cash">Cash</option><option value="card">Card</option><option value="account">Customer Account</option></select></div><div><label>Discount USD</label><input id="saleDiscount" type="number" value="0" min="0" step="0.01" oninput="renderCart()"></div><div><label>VAT Rate %</label><input id="saleVatRate20" type="number" value="${Number(settingsCache.vat_rate||11)}" step="0.01" oninput="renderCart()"></div><div><label class="switch"><input id="saleVat" type="checkbox" ${String(settingsCache.vat_enabled)==='true'?'checked':''} onchange="renderCart()"> VAT</label></div></div><div id="cartLines"></div><hr><p>Subtotal <b id="cartSub" style="float:right">$0.00</b></p><p>VAT <b id="cartVat20" style="float:right">$0.00</b></p><h2>Total <b id="cartTotal" style="float:right">$0.00</b></h2><div id="cartLbp" class="muted"></div><button class="btn primary" style="width:100%;margin-top:12px" onclick="completeSale20()">SAVE + OFFICIAL INVOICE</button></div></div>`);refreshLiveProducts();renderCart()}
function renderCart(){const el=document.getElementById('cartLines');if(!el)return;let sub=0;el.innerHTML=cart.map((x,i)=>{const t=x.price*x.quantity;sub+=t;return `<div style="padding:10px;border-bottom:1px solid var(--border)"><b>${esc2(x.name)}</b><span style="float:right">$${t.toFixed(2)}</span><div class="muted">Qty <button class="btn light" onclick="changeQty(${i},-1)">−</button> ${x.quantity} <button class="btn light" onclick="changeQty(${i},1)">＋</button></div></div>`}).join('')||'<div class="empty">Invoice is empty.</div>';const d=Number(document.getElementById('saleDiscount')?.value||0),net=Math.max(0,sub-d),rate=Number(document.getElementById('saleVatRate20')?.value||0),vat=document.getElementById('saleVat')?.checked?net*rate/100:0,total=net+vat;document.getElementById('cartSub').textContent='$'+sub.toFixed(2);document.getElementById('cartVat20').textContent='$'+vat.toFixed(2);document.getElementById('cartTotal').textContent='$'+total.toFixed(2);document.getElementById('cartLbp').textContent=Math.round(total*Number(settingsCache.usd_lbp||89500)).toLocaleString()+' LBP';document.getElementById('cartCount').textContent=cart.reduce((a,x)=>a+x.quantity,0)+' items'}
async function completeSale20(){if(!cart.length)return alert('Invoice is empty.');try{const r=await apiJSON('/api/sales',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({customer_id:document.getElementById('posCustomer').value?Number(document.getElementById('posCustomer').value):null,discount:Number(document.getElementById('saleDiscount').value||0),payment_method:document.getElementById('payment').value,vat_enabled:document.getElementById('saleVat').checked,vat_rate:Number(document.getElementById('saleVatRate20').value||0),currency:'USD',items:cart.map(x=>({product_id:x.product_id,quantity:x.quantity,unit_price:x.price}))})});const customer=document.getElementById('posCustomer').selectedOptions[0]?.textContent||'Walk-in Customer';const html=`<div class="invoice-preview" id="salesPrintArea"><h1 style="margin:0">${esc2(settingsCache.company_name)}</h1><h3>OFFICIAL SALES INVOICE</h3><p>Invoice: <b>${esc2(r.invoice_no)}</b><br>Date: ${new Date().toLocaleString()}<br>Customer: <b>${esc2(customer)}</b></p><table style="width:100%;border-collapse:collapse"><tr><th style="text-align:left">Item</th><th>Qty</th><th>Unit</th><th>Total</th></tr>${cart.map(x=>`<tr><td>${esc2(x.name)}</td><td style="text-align:center">${x.quantity}</td><td style="text-align:right">$${x.price.toFixed(2)}</td><td style="text-align:right">$${(x.price*x.quantity).toFixed(2)}</td></tr>`).join('')}</table><hr><p>Subtotal <b style="float:right">$${Number(r.subtotal).toFixed(2)}</b></p><p>Discount <b style="float:right">$${Number(r.discount).toFixed(2)}</b></p><p>VAT <b style="float:right">$${Number(r.vat||0).toFixed(2)}</b></p><h2>Total <b style="float:right">$${Number(r.total).toFixed(2)}</b></h2><p style="text-align:right">${Math.round(Number(r.total)*Number(settingsCache.usd_lbp||89500)).toLocaleString()} LBP</p><div style="margin-top:35px;display:flex;justify-content:space-between"><span>Customer Signature: __________</span><span>Authorized Signature: __________</span></div></div>`;openModal('OFFICIAL SALES INVOICE',html,`<button class="btn primary" onclick="printSales20()">PRINT OFFICIAL INVOICE</button>`);cart=[];await refreshLiveProducts();}catch(e){alert(e.message)}}
function printSales20(){const a=document.getElementById('salesPrintArea');if(!a)return;const w=window.open('','_blank','width=900,height=900');if(!w){alert('Allow popups for printing.');return}w.document.write('<html><head><title>Official Sales Invoice</title><style>body{font-family:Arial;padding:30px}table{width:100%;border-collapse:collapse}th,td{padding:8px;border-bottom:1px solid #ddd}</style></head><body>'+a.outerHTML+'</body></html>');w.document.close();w.focus();w.print()}

(function(){const params=new URLSearchParams(location.search);if(params.get('priceCheckerWindow')==='1'){document.body.classList.add('price-checker-window');const l=document.getElementById('login'),a=document.getElementById('app');if(l)l.classList.add('hidden');if(a)a.classList.add('hidden');setTimeout(()=>priceChecker(params.get('q')||''),0);}})();
