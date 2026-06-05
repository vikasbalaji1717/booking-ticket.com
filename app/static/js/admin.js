// Admin Dashboard Scripts

document.addEventListener('DOMContentLoaded', () => {
  // Page identification
  if (document.getElementById('admin-dashboard-panel')) initDashboard();
  if (document.getElementById('admin-buses-panel')) initBusesPanel();
  if (document.getElementById('admin-routes-panel')) initRoutesPanel();
});

// Helper for modal toggling
function toggleModal(modalId, action = 'open') {
  const modal = document.getElementById(modalId);
  if (!modal) return;
  if (action === 'open') {
    modal.classList.add('active');
  } else {
    modal.classList.remove('active');
  }
}

// ----------------- DASHBOARD PANEL -----------------
async function initDashboard() {
  const tableBody = document.getElementById('recent-bookings-table');
  if (!tableBody) return;
  
  tableBody.innerHTML = '<tr><td colspan="5" class="text-center">Fetching metrics...</td></tr>';
  
  try {
    const response = await fetch('/admin/stats');
    const result = await response.json();
    
    if (result.success) {
      const stats = result.stats;
      
      // Update UI numbers
      document.getElementById('stat-revenue').innerText = `Rs. ${stats.total_revenue.toFixed(2)}`;
      document.getElementById('stat-bookings').innerText = stats.total_bookings;
      document.getElementById('stat-buses').innerText = stats.total_buses;
      document.getElementById('stat-schedules').innerText = stats.active_schedules;
      
      // Update recent bookings table
      if (stats.recent_bookings.length > 0) {
        tableBody.innerHTML = stats.recent_bookings.map(b => {
          let badge = `<span class="badge badge-warning">Pending</span>`;
          if (b.status === 'Confirmed') badge = `<span class="badge badge-success">Confirmed</span>`;
          if (b.status === 'Cancelled') badge = `<span class="badge badge-danger">Cancelled</span>`;
          
          return `
            <tr>
              <td><strong>${b.pnr}</strong></td>
              <td>${b.user}</td>
              <td>${b.route}</td>
              <td>Rs. ${b.amount.toFixed(2)}</td>
              <td>${badge}</td>
            </tr>
          `;
        }).join('');
      } else {
        tableBody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No bookings registered yet.</td></tr>';
      }
    }
  } catch (err) {
    tableBody.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Connection error fetching stats.</td></tr>';
  }
}

// ----------------- BUSES PANEL -----------------
let busList = [];

async function initBusesPanel() {
  loadBusesTable();
  
  const busForm = document.getElementById('bus-editor-form');
  if (busForm) {
    busForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const id = document.getElementById('bus-id-field').value;
      const bus_number = document.getElementById('bus-number-input').value;
      const name = document.getElementById('bus-name-input').value;
      const type = document.getElementById('bus-type-select').value;
      const capacity = parseInt(document.getElementById('bus-capacity-input').value);
      const amenities = document.getElementById('bus-amenities-input').value;
      
      try {
        const response = await fetch('/admin/buses', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id, bus_number, name, type, capacity, amenities })
        });
        const result = await response.json();
        
        if (result.success) {
          showToast(result.message, 'success');
          toggleModal('bus-modal', 'close');
          loadBusesTable();
        } else {
          showToast(result.message, 'danger');
        }
      } catch (err) {
        showToast('Connection error saving bus details.', 'danger');
      }
    });
  }
}

async function loadBusesTable() {
  const tbody = document.getElementById('buses-table-body');
  if (!tbody) return;
  
  tbody.innerHTML = '<tr><td colspan="5" class="text-center">Loading bus fleet...</td></tr>';
  
  try {
    const response = await fetch('/admin/buses');
    const result = await response.json();
    
    if (result.success) {
      busList = result.buses;
      if (busList.length > 0) {
        tbody.innerHTML = busList.map(b => {
          return `
            <tr>
              <td><strong>${b.bus_number}</strong></td>
              <td>${b.name}</td>
              <td>${b.type}</td>
              <td>${b.capacity} Seats</td>
              <td>
                <div style="display:flex; gap:0.5rem;">
                  <button onclick="editBus(${b.id})" class="btn btn-secondary btn-sm" style="padding:0.2rem 0.5rem;">Edit</button>
                  <button onclick="deleteBus(${b.id})" class="btn btn-danger btn-sm" style="padding:0.2rem 0.5rem;">Delete</button>
                </div>
              </td>
            </tr>
          `;
        }).join('');
      } else {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No buses registered in the system.</td></tr>';
      }
    }
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Connection error loading buses.</td></tr>';
  }
}

function openAddBusModal() {
  document.getElementById('bus-id-field').value = '';
  document.getElementById('bus-number-input').value = '';
  document.getElementById('bus-name-input').value = '';
  document.getElementById('bus-capacity-input').value = '40';
  document.getElementById('bus-amenities-input').value = 'WiFi, Charger, Water';
  
  document.getElementById('bus-modal-title').innerText = 'Add New Bus';
  toggleModal('bus-modal', 'open');
}

function editBus(id) {
  const bus = busList.find(b => b.id === id);
  if (!bus) return;
  
  document.getElementById('bus-id-field').value = bus.id;
  document.getElementById('bus-number-input').value = bus.bus_number;
  document.getElementById('bus-name-input').value = bus.name;
  document.getElementById('bus-type-select').value = bus.type;
  document.getElementById('bus-capacity-input').value = bus.capacity;
  document.getElementById('bus-amenities-input').value = bus.amenities.join(', ');
  
  document.getElementById('bus-modal-title').innerText = 'Edit Bus Details';
  toggleModal('bus-modal', 'open');
}

async function deleteBus(id) {
  if (confirm("Are you sure you want to delete this bus? All associated schedules will be deleted.")) {
    try {
      const response = await fetch(`/admin/buses/${id}/delete`, { method: 'POST' });
      const result = await response.json();
      if (response.ok) {
        showToast(result.message, 'success');
        loadBusesTable();
      } else {
        showToast(result.message, 'danger');
      }
    } catch (err) {
      showToast("Connection failed during bus deletion.", 'danger');
    }
  }
}

// ----------------- ROUTES & SCHEDULES PANEL -----------------
let routeList = [];
let scheduleList = [];

async function initRoutesPanel() {
  loadRoutesTable();
  loadSchedulesTable();
  
  // Route Form Submit
  const routeForm = document.getElementById('route-editor-form');
  if (routeForm) {
    routeForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const id = document.getElementById('route-id-field').value;
      const source = document.getElementById('route-source-input').value;
      const destination = document.getElementById('route-dest-input').value;
      const distance_km = parseFloat(document.getElementById('route-distance-input').value);
      
      try {
        const response = await fetch('/admin/routes', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id, source, destination, distance_km })
        });
        const result = await response.json();
        
        if (result.success) {
          showToast(result.message, 'success');
          toggleModal('route-modal', 'close');
          loadRoutesTable();
        } else {
          showToast(result.message, 'danger');
        }
      } catch (err) {
        showToast('Connection error saving route details.', 'danger');
      }
    });
  }
  
  // Schedule Form Submit
  const scheduleForm = document.getElementById('schedule-editor-form');
  if (scheduleForm) {
    scheduleForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const id = document.getElementById('sched-id-field').value;
      const bus_id = parseInt(document.getElementById('sched-bus-select').value);
      const route_id = parseInt(document.getElementById('sched-route-select').value);
      const price = parseFloat(document.getElementById('sched-price-input').value);
      const departure_time = document.getElementById('sched-dep-input').value;
      const arrival_time = document.getElementById('sched-arr-input').value;
      const journey_date = document.getElementById('sched-date-input').value;
      
      try {
        const response = await fetch('/admin/schedules', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id, bus_id, route_id, price, departure_time, arrival_time, journey_date })
        });
        const result = await response.json();
        
        if (result.success) {
          showToast(result.message, 'success');
          toggleModal('schedule-modal', 'close');
          loadSchedulesTable();
        } else {
          showToast(result.message, 'danger');
        }
      } catch (err) {
        showToast('Connection error saving journey schedule.', 'danger');
      }
    });
  }
}

// Routes list CRUD
async function loadRoutesTable() {
  const tbody = document.getElementById('routes-table-body');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="4" class="text-center">Loading routes...</td></tr>';
  
  try {
    const response = await fetch('/admin/routes');
    const result = await response.json();
    if (result.success) {
      routeList = result.routes;
      if (routeList.length > 0) {
        tbody.innerHTML = routeList.map(r => `
          <tr>
            <td><strong>${r.source}</strong></td>
            <td><strong>${r.destination}</strong></td>
            <td>${r.distance_km} KM</td>
            <td>
              <div style="display:flex; gap:0.5rem;">
                <button onclick="editRoute(${r.id})" class="btn btn-secondary btn-sm" style="padding:0.2rem 0.5rem;">Edit</button>
                <button onclick="deleteRoute(${r.id})" class="btn btn-danger btn-sm" style="padding:0.2rem 0.5rem;">Delete</button>
              </div>
            </td>
          </tr>
        `).join('');
      } else {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No routes registered.</td></tr>';
      }
    }
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="4" class="text-center text-danger">Connection error loading routes.</td></tr>';
  }
}

function openAddRouteModal() {
  document.getElementById('route-id-field').value = '';
  document.getElementById('route-source-input').value = '';
  document.getElementById('route-dest-input').value = '';
  document.getElementById('route-distance-input').value = '100';
  document.getElementById('route-modal-title').innerText = 'Add Route';
  toggleModal('route-modal', 'open');
}

function editRoute(id) {
  const route = routeList.find(r => r.id === id);
  if (!route) return;
  document.getElementById('route-id-field').value = route.id;
  document.getElementById('route-source-input').value = route.source;
  document.getElementById('route-dest-input').value = route.destination;
  document.getElementById('route-distance-input').value = route.distance_km;
  document.getElementById('route-modal-title').innerText = 'Edit Route';
  toggleModal('route-modal', 'open');
}

async function deleteRoute(id) {
  if (confirm("Are you sure you want to delete this route? This will delete all scheduled buses for this route.")) {
    try {
      const response = await fetch(`/admin/routes/${id}/delete`, { method: 'POST' });
      const result = await response.json();
      if (response.ok) {
        showToast(result.message, 'success');
        loadRoutesTable();
        loadSchedulesTable();
      } else {
        showToast(result.message, 'danger');
      }
    } catch (err) {
      showToast("Connection failed.", 'danger');
    }
  }
}

// Schedules list CRUD
async function loadSchedulesTable() {
  const tbody = document.getElementById('schedules-table-body');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="6" class="text-center">Loading schedules...</td></tr>';
  
  try {
    const response = await fetch('/admin/schedules');
    const result = await response.json();
    if (result.success) {
      scheduleList = result.schedules;
      if (scheduleList.length > 0) {
        tbody.innerHTML = scheduleList.map(s => {
          const journeyDate = new Date(s.journey_date).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
          const depTime = new Date(s.departure_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
          const arrTime = new Date(s.arrival_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
          
          return `
            <tr>
              <td>${s.bus ? s.bus.name : 'Deleted'} (${s.bus ? s.bus.bus_number : 'N/A'})</td>
              <td>${s.route ? s.route.source : 'N/A'} -> ${s.route ? s.route.destination : 'N/A'}</td>
              <td>${journeyDate}</td>
              <td>${depTime} / ${arrTime}</td>
              <td>Rs. ${s.price.toFixed(2)}</td>
              <td>
                <div style="display:flex; gap:0.5rem;">
                  <button onclick="editSchedule(${s.id})" class="btn btn-secondary btn-sm" style="padding:0.2rem 0.5rem;">Edit</button>
                  <button onclick="deleteSchedule(${s.id})" class="btn btn-danger btn-sm" style="padding:0.2rem 0.5rem;">Delete</button>
                </div>
              </td>
            </tr>
          `;
        }).join('');
      } else {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No scheduled buses.</td></tr>';
      }
    }
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Connection error loading schedules.</td></tr>';
  }
}

async function openAddScheduleModal() {
  document.getElementById('sched-id-field').value = '';
  document.getElementById('sched-price-input').value = '450';
  document.getElementById('sched-dep-input').value = '';
  document.getElementById('sched-arr-input').value = '';
  document.getElementById('sched-date-input').value = '';
  
  // Fetch buses and routes lists to populate drop-downs
  await populateDropdowns();
  
  document.getElementById('schedule-modal-title').innerText = 'Schedule Bus Route';
  toggleModal('schedule-modal', 'open');
}

async function populateDropdowns() {
  const busSelect = document.getElementById('sched-bus-select');
  const routeSelect = document.getElementById('sched-route-select');
  
  // Fetch lists
  const busResponse = await fetch('/admin/buses');
  const busData = await busResponse.json();
  const routeResponse = await fetch('/admin/routes');
  const routeData = await routeResponse.json();
  
  if (busData.success) {
    busSelect.innerHTML = busData.buses.map(b => `<option value="${b.id}">${b.name} (${b.bus_number}) - ${b.capacity} seats</option>`).join('');
  }
  if (routeData.success) {
    routeSelect.innerHTML = routeData.routes.map(r => `<option value="${r.id}">${r.source} to ${r.destination} (${r.distance_km} KM)</option>`).join('');
  }
}

async function editSchedule(id) {
  const s = scheduleList.find(item => item.id === id);
  if (!s) return;
  
  await populateDropdowns();
  
  document.getElementById('sched-id-field').value = s.id;
  document.getElementById('sched-bus-select').value = s.bus.id;
  document.getElementById('sched-route-select').value = s.route.id;
  document.getElementById('sched-price-input').value = s.price;
  
  // Format dates for input datetime-local formats: YYYY-MM-DDTHH:MM
  const dep = new Date(s.departure_time);
  const arr = new Date(s.arrival_time);
  
  const pad = num => String(num).padStart(2, '0');
  
  const formatDateTimeLocal = date => `${date.getFullYear()}-${pad(date.getMonth()+1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
  
  document.getElementById('sched-dep-input').value = formatDateTimeLocal(dep);
  document.getElementById('sched-arr-input').value = formatDateTimeLocal(arr);
  document.getElementById('sched-date-input').value = s.journey_date;
  
  document.getElementById('schedule-modal-title').innerText = 'Edit Journey Schedule';
  toggleModal('schedule-modal', 'open');
}

async function deleteSchedule(id) {
  if (confirm("Are you sure you want to cancel this scheduled journey? All booking tickets for this schedule will be removed.")) {
    try {
      const response = await fetch(`/admin/schedules/${id}/delete`, { method: 'POST' });
      const result = await response.json();
      if (response.ok) {
        showToast(result.message, 'success');
        loadSchedulesTable();
      } else {
        showToast(result.message, 'danger');
      }
    } catch (err) {
      showToast("Connection failed.", 'danger');
    }
  }
}
