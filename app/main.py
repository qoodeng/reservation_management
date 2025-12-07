from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.database import seed_data, get_db
from app.tools import (
    check_account_status,
    get_guest_reservation,
    cancel_guest_reservation,
    make_new_reservation,
    edit_guest_reservation
)

# Dashboard HTML template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hotel Reservation Database</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #0f0f1a 100%);
            min-height: 100vh;
            color: #e0e0e0;
            padding: 2rem;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 3rem; }
        h1 {
            font-size: 2.5rem;
            background: linear-gradient(90deg, #00d4ff, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }
        .subtitle { color: #888; font-size: 1rem; }
        .refresh-btn {
            background: linear-gradient(90deg, #00d4ff, #7c3aed);
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            margin-top: 1rem;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3);
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }
        .stat-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(90deg, #00d4ff, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .stat-label { color: #888; font-size: 0.9rem; margin-top: 0.5rem; }
        .accounts-grid { display: grid; gap: 1.5rem; }
        .account-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            padding: 2rem;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .account-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            border-color: rgba(0, 212, 255, 0.3);
        }
        .account-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
            gap: 1rem;
        }
        .account-id { font-size: 1.5rem; font-weight: 700; color: #00d4ff; }
        .guest-name { font-size: 1.2rem; color: #e0e0e0; }
        .status-badge {
            padding: 0.4rem 1rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        .status-active {
            background: rgba(34, 197, 94, 0.2);
            color: #22c55e;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }
        .status-inactive {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
        .reservations-section h3 {
            color: #888;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 1rem;
        }
        .reservation-list { display: grid; gap: 1rem; }
        .reservation-item {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            align-items: center;
        }
        .res-field { display: flex; flex-direction: column; }
        .res-label {
            font-size: 0.75rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .res-value { font-size: 1rem; color: #e0e0e0; font-weight: 500; }
        .res-status-confirmed { color: #22c55e; }
        .res-status-cancelled { color: #ef4444; }
        .res-status-pending { color: #f59e0b; }
        .no-reservations {
            color: #666;
            font-style: italic;
            padding: 1rem;
            text-align: center;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 8px;
        }
        .last-updated { text-align: center; color: #666; font-size: 0.85rem; margin-top: 2rem; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .live-indicator { display: inline-flex; align-items: center; gap: 0.5rem; color: #22c55e; font-size: 0.85rem; }
        .live-dot { width: 8px; height: 8px; background: #22c55e; border-radius: 50%; animation: pulse 2s infinite; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏨 Hotel Reservation Database</h1>
            <p class="subtitle">Real-time view of agent interactions</p>
            <button class="refresh-btn" onclick="location.reload()">↻ Refresh Data</button>
        </header>
        <div class="stats" id="stats"></div>
        <div class="accounts-grid" id="accounts"></div>
        <div class="last-updated">
            <span class="live-indicator"><span class="live-dot"></span>Live Data</span>
            &nbsp;•&nbsp; Last updated: <span id="timestamp"></span>
        </div>
    </div>
    <script>
        async function loadData() {
            const res = await fetch('/api/accounts');
            const accounts = await res.json();
            
            const stats = {
                total: accounts.length,
                active: accounts.filter(a => a.status === 'Active').length,
                totalRes: accounts.reduce((s, a) => s + (a.reservations?.length || 0), 0),
                confirmed: accounts.reduce((s, a) => s + (a.reservations?.filter(r => r.status === 'Confirmed').length || 0), 0),
                cancelled: accounts.reduce((s, a) => s + (a.reservations?.filter(r => r.status === 'Cancelled').length || 0), 0)
            };
            
            document.getElementById('stats').innerHTML = `
                <div class="stat-card"><div class="stat-value">${stats.total}</div><div class="stat-label">Total Accounts</div></div>
                <div class="stat-card"><div class="stat-value">${stats.active}</div><div class="stat-label">Active Accounts</div></div>
                <div class="stat-card"><div class="stat-value">${stats.totalRes}</div><div class="stat-label">Total Reservations</div></div>
                <div class="stat-card"><div class="stat-value">${stats.confirmed}</div><div class="stat-label">Confirmed</div></div>
                <div class="stat-card"><div class="stat-value">${stats.cancelled}</div><div class="stat-label">Cancelled</div></div>
            `;
            
            document.getElementById('accounts').innerHTML = accounts.map(a => `
                <div class="account-card">
                    <div class="account-header">
                        <div>
                            <div class="account-id">Account #${a.account_id}</div>
                            <div class="guest-name">${a.guest_name}</div>
                        </div>
                        <span class="status-badge ${a.status === 'Active' ? 'status-active' : 'status-inactive'}">${a.status}</span>
                    </div>
                    <div class="reservations-section">
                        <h3>Reservations (${a.reservations?.length || 0})</h3>
                        ${a.reservations?.length ? `<div class="reservation-list">${a.reservations.map(r => `
                            <div class="reservation-item">
                                <div class="res-field"><span class="res-label">Reservation ID</span><span class="res-value">#${r.reservation_id}</span></div>
                                <div class="res-field"><span class="res-label">Check-in Date</span><span class="res-value">${r.date}</span></div>
                                <div class="res-field"><span class="res-label">Room Type</span><span class="res-value">${r.room_type || 'Standard'}</span></div>
                                <div class="res-field"><span class="res-label">Status</span><span class="res-value res-status-${r.status.toLowerCase()}">${r.status}</span></div>
                            </div>
                        `).join('')}</div>` : '<div class="no-reservations">No reservations found</div>'}
                    </div>
                </div>
            `).join('');
            
            document.getElementById('timestamp').textContent = new Date().toLocaleString();
        }
        loadData();
        setInterval(loadData, 5000);
    </script>
</body>
</html>
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await seed_data()
    yield
    # Shutdown

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hotel Reservation Agent API is running. Visit /dashboard for the database viewer."}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Web dashboard to visualize the database."""
    return DASHBOARD_HTML

@app.get("/api/accounts")
async def api_accounts():
    """JSON API endpoint for all accounts data."""
    db = await get_db()
    accounts = []
    async for account in db["accounts"].find({}):
        account["_id"] = str(account["_id"])
        accounts.append(account)
    return accounts

# Expose tools as API endpoints for testing/verification
@app.get("/tools/check_account_status")
async def api_check_account_status(account_id: str):
    return await check_account_status(account_id)

@app.get("/tools/get_guest_reservation")
async def api_get_guest_reservation(account_id: str, search_name: str):
    return await get_guest_reservation(account_id, search_name)

@app.post("/tools/cancel_guest_reservation")
async def api_cancel_guest_reservation(account_id: str, reservation_id: int):
    return await cancel_guest_reservation(account_id, reservation_id)

@app.post("/tools/make_new_reservation")
async def api_make_new_reservation(account_id: str, guest_name: str, check_in_date: str, room_type: str):
    return await make_new_reservation(account_id, guest_name, check_in_date, room_type)

@app.patch("/tools/edit_guest_reservation")
async def api_edit_guest_reservation(
    account_id: str, 
    reservation_id: int, 
    new_check_in_date: str = None, 
    new_room_type: str = None
):
    return await edit_guest_reservation(account_id, reservation_id, new_check_in_date, new_room_type)
