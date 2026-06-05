// Global Helper: Toast Notifications
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  // Custom Icon based on type
  let icon = '';
  if (type === 'success') {
    icon = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`;
  } else if (type === 'danger') {
    icon = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-danger" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`;
  } else {
    icon = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>`;
  }
  
  toast.innerHTML = `
    ${icon}
    <div>${message}</div>
  `;
  
  container.appendChild(toast);
  
  // Slide out after 3.5 seconds
  setTimeout(() => {
    toast.style.animation = 'slideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1) reverse';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// ----------------- PAGE INITS -----------------

document.addEventListener('DOMContentLoaded', () => {
  // Page routing based on DOM indicators
  if (document.getElementById('auth-page')) initAuthPage();
  if (document.getElementById('search-page')) initSearchPage();
  if (document.getElementById('booking-page')) initBookingPage();
  if (document.getElementById('profile-page')) initProfilePage();
  if (document.getElementById('home-page')) initHomePage();
  
  // Ensure login link works even if some CSS/overlay prevents default click
  const loginLink = document.getElementById('login-link');
  if (loginLink) {
    loginLink.addEventListener('click', (e) => {
      // Let normal navigation happen for standard anchors; provide fallback
      // in case another script prevented default.
      if (e.defaultPrevented) {
        window.location.href = loginLink.getAttribute('href') || '/login';
      }
    });
  }
});

// ----------------- HOME PAGE -----------------
function initHomePage() {
  const searchForm = document.getElementById('hero-search-form');
  if (!searchForm) return;
  
  searchForm.addEventListener('submit', (e) => {
    const source = document.getElementById('source-select').value;
    const dest = document.getElementById('dest-select').value;
    const date = document.getElementById('journey-date').value;
    
    if (source === dest) {
      e.preventDefault();
      showToast("Source and destination cannot be the same.", "warning");
    }
  });

  // Setup FAQs
  const faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    question.addEventListener('click', () => {
      const isActive = item.classList.contains('active');
      faqItems.forEach(i => i.classList.remove('active'));
      if (!isActive) {
        item.classList.add('active');
      }
    });
  });
}

// ----------------- LOGIN / REGISTER -----------------
function initAuthPage() {
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const showRegisterLink = document.getElementById('show-register');
  const showLoginLink = document.getElementById('show-login');
  
  if (showRegisterLink && showLoginLink) {
    showRegisterLink.addEventListener('click', (e) => {
      e.preventDefault();
      loginForm.classList.add('hidden');
      registerForm.classList.remove('hidden');
      document.getElementById('auth-card-title').innerText = 'Create Account';
    });
    
    showLoginLink.addEventListener('click', (e) => {
      e.preventDefault();
      registerForm.classList.add('hidden');
      loginForm.classList.remove('hidden');
      document.getElementById('auth-card-title').innerText = 'Welcome Back';
    });
  }
  
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('login-email').value;
      const pass = document.getElementById('login-password').value;
      
      try {
        const response = await fetch('/auth/login', {
          method: 'POST',
          credentials: 'same-origin',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password: pass })
        });
        const result = await response.json();
        
        if (result.success) {
          showToast(result.message, 'success');
          setTimeout(() => {
            // Redirect based on role or return parameter
            const params = new URLSearchParams(window.location.search);
            const next = params.get('next');
            window.location.href = next || '/';
          }, 1000);
        } else {
          showToast(result.message, 'danger');
        }
      } catch (err) {
        showToast('Login connection failed.', 'danger');
      }
    });
  }
  
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const username = document.getElementById('reg-username').value;
      const email = document.getElementById('reg-email').value;
      const pass = document.getElementById('reg-password').value;
      const isAdmin = document.getElementById('reg-admin-toggle') ? document.getElementById('reg-admin-toggle').checked : false;
      
      try {
        const response = await fetch('/auth/register', {
          method: 'POST',
          credentials: 'same-origin',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, email, password: pass, is_admin: isAdmin })
        });
        const result = await response.json();
        
        if (result.success) {
          showToast(result.message, 'success');
          setTimeout(() => {
            window.location.href = '/';
          }, 1000);
        } else {
          showToast(result.message, 'danger');
        }
      } catch (err) {
        showToast('Registration connection failed.', 'danger');
      }
    });
  }
}

// ----------------- SEARCH RESULT PAGE -----------------
let rawSchedules = [];
let searchContext = { source: '', dest: '', date: '' };

function initSearchPage() {
  const container = document.getElementById('search-page');
  const source = container.dataset.source;
  const dest = container.dataset.destination;
  const date = container.dataset.date;
  const provider = container.dataset.provider || 'all';
  
  const providerSelect = document.getElementById('provider-select');
  if (providerSelect) {
    providerSelect.value = provider;
    providerSelect.addEventListener('change', () => {
      fetchSchedules(source, dest, date, providerSelect.value);
    });
  }
  
  fetchSchedules(source, dest, date, provider);
  
  // Set up filter change events
  const filterInputs = document.querySelectorAll('.filter-input');
  filterInputs.forEach(input => {
    input.addEventListener('change', renderFilteredSchedules);
  });
  
  const priceSlider = document.getElementById('price-range-slider');
  if (priceSlider) {
    priceSlider.addEventListener('input', (e) => {
      document.getElementById('price-slider-value').innerText = `Rs. ${e.target.value}`;
      renderFilteredSchedules();
    });
  }
}

async function fetchSchedules(source, dest, date, provider = 'all') {
  const listContainer = document.getElementById('results-list');
  listContainer.innerHTML = '<div class="text-center p-5">Searching for available buses...</div>';
  console.log('[Search Page] fetchSchedules called', { source, dest, date, provider });
  
  try {
    const response = await fetch(`/api/buses/search?source=${encodeURIComponent(source)}&destination=${encodeURIComponent(dest)}&date=${date}&provider=${encodeURIComponent(provider)}`);
    const result = await response.json();
    console.log('[Search API] response', result);
    
    if (result.success) {
      rawSchedules = result.schedules;
      
      // Update max price slider dynamically
      const priceSlider = document.getElementById('price-range-slider');
      if (priceSlider && rawSchedules.length > 0) {
        const maxPriceInList = Math.max(...rawSchedules.map(s => s.price));
        priceSlider.max = Math.ceil(maxPriceInList);
        priceSlider.value = Math.ceil(maxPriceInList);
        document.getElementById('price-slider-value').innerText = `Rs. ${priceSlider.value}`;
      }
      
      renderFilteredSchedules();
    } else {
      listContainer.innerHTML = `<div class="text-danger p-5">${result.message}</div>`;
    }
  } catch (err) {
    listContainer.innerHTML = '<div class="text-danger p-5">Connection failed while fetching schedules.</div>';
  }
}

function renderFilteredSchedules() {
  const listContainer = document.getElementById('results-list');
  const resultCount = document.getElementById('result-count');
  
  // Get Filter values
  const priceMax = parseFloat(document.getElementById('price-range-slider')?.value || 99999);
  
  const activeTypes = [];
  if (document.getElementById('filter-ac')?.checked) activeTypes.push('ac');
  if (document.getElementById('filter-non-ac')?.checked) activeTypes.push('non-ac');
  if (document.getElementById('filter-sleeper')?.checked) activeTypes.push('sleeper');
  if (document.getElementById('filter-seater')?.checked) activeTypes.push('seater');
  
  const activeTimes = [];
  if (document.getElementById('time-morning')?.checked) activeTimes.push('morning');
  if (document.getElementById('time-afternoon')?.checked) activeTimes.push('afternoon');
  if (document.getElementById('time-evening')?.checked) activeTimes.push('evening');

  // Filter schedules locally
  const filtered = rawSchedules.filter(s => {
    // 1. Price
    if (s.price > priceMax) return false;
    
    // 2. Bus Type
    if (activeTypes.length > 0) {
      const typeStr = s.bus.type.toLowerCase();
      let matchType = false;
      
      if (activeTypes.includes('ac') && typeStr.includes('ac') && !typeStr.includes('non-ac')) matchType = true;
      if (activeTypes.includes('non-ac') && typeStr.includes('non-ac')) matchType = true;
      if (activeTypes.includes('sleeper') && typeStr.includes('sleeper')) matchType = true;
      if (activeTypes.includes('seater') && typeStr.includes('seater')) matchType = true;
      
      if (!matchType) return false;
    }
    
    // 3. Time
    if (activeTimes.length > 0) {
      const depHour = new Date(s.departure_time).getHours();
      let matchTime = false;
      
      if (activeTimes.includes('morning') && depHour < 12) matchTime = true;
      if (activeTimes.includes('afternoon') && depHour >= 12 && depHour < 17) matchTime = true;
      if (activeTimes.includes('evening') && depHour >= 17) matchTime = true;
      
      if (!matchTime) return false;
    }
    
    return true;
  });
  
  resultCount.innerText = `${filtered.length} Buses Found`;
  
  if (filtered.length === 0) {
    listContainer.innerHTML = '<div class="text-center p-5 text-muted">No buses match your filter criteria.</div>';
    return;
  }
  
  listContainer.innerHTML = filtered.map(s => {
    const depTime = new Date(s.departure_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const arrTime = new Date(s.arrival_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // Calculate simple duration
    const diffMs = new Date(s.arrival_time) - new Date(s.departure_time);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffMins = Math.round((diffMs % 3600000) / 60000);
    const duration = `${diffHours}h ${diffMins}m`;
    
    const amenitiesHtml = (s.bus.amenities || []).map(a => `<span class="amenity-tag">${a}</span>`).join('');
    const providerBadge = s.provider ? `<span class="provider-badge">${s.provider.toUpperCase()}</span>` : '';
    
    return `
      <div class="schedule-card">
        <div class="schedule-bus-info">
          <h3>${s.bus.name} ${providerBadge}</h3>
          <p class="schedule-bus-number">Bus No. ${s.bus.bus_number}</p>
          <p class="schedule-bus-type">${s.bus.type}</p>
          <div class="schedule-amenities">${amenitiesHtml}</div>
        </div>
        <div class="schedule-timeline">
          <div class="timeline-point">
            <div class="timeline-time">${depTime}</div>
            <div class="timeline-city">${s.route.source}</div>
          </div>
          <div class="timeline-connector">
            <div class="timeline-duration">${duration}</div>
            <div class="timeline-line"></div>
          </div>
          <div class="timeline-point">
            <div class="timeline-time">${arrTime}</div>
            <div class="timeline-city">${s.route.destination}</div>
          </div>
        </div>
        <div class="schedule-checkout">
          <div>
            <div class="schedule-price">Rs. ${s.price.toFixed(2)}</div>
            <div class="schedule-route-label">Departure: ${depTime} · Arrival: ${arrTime}</div>
          </div>
          ${s.provider && s.provider.toLowerCase() === 'ksrtc' ?
            `<button class="btn btn-secondary btn-sm" disabled>External Provider</button>` :
            `<a href="/booking/${s.id}" class="btn btn-primary btn-sm">Book Now</a>`
          }
        </div>
      </div>
    `;
  }).join('');
}

// ----------------- SEAT SELECTION & CHECKOUT -----------------
let selectedSeats = [];
let ticketPrice = 0;

function initBookingPage() {
  const container = document.getElementById('booking-page');
  const scheduleId = container.dataset.scheduleId;
  ticketPrice = parseFloat(container.dataset.price);
  
  loadSeatLayout(scheduleId);
  
  // Payment Type Switcher
  const paymentOptions = document.querySelectorAll('.payment-option');
  paymentOptions.forEach(opt => {
    opt.addEventListener('click', () => {
      paymentOptions.forEach(o => o.classList.remove('active'));
      opt.classList.add('active');
      
      const method = opt.dataset.method;
      document.getElementById('payment-method-input').value = method;
      
      // Update form context
      if (method === 'UPI') {
        document.getElementById('card-details-form').classList.add('hidden');
        document.getElementById('upi-details-form').classList.remove('hidden');
      } else {
        document.getElementById('upi-details-form').classList.add('hidden');
        document.getElementById('card-details-form').classList.remove('hidden');
      }
    });
  });
  
  // Checkout Submit
  const checkoutBtn = document.getElementById('confirm-booking-btn');
  if (checkoutBtn) {
    checkoutBtn.addEventListener('click', submitBooking);
  }
}

async function loadSeatLayout(scheduleId) {
  const grid = document.getElementById('seat-grid');
  grid.innerHTML = '<div class="text-center p-3">Generating seat configuration...</div>';
  
  try {
    const response = await fetch(`/api/buses/schedules/${scheduleId}/seats`);
    const result = await response.json();
    
    if (result.success) {
      grid.innerHTML = '';
      const totalSeats = result.capacity;
      const bookedSeats = result.booked_seats;
      
      // Calculate row arrays (assuming 4 seats per row: A, B [aisle] C, D)
      // Standard seating rows
      const rowsCount = Math.ceil(totalSeats / 4);
      
      for (let r = 0; r < rowsCount; r++) {
        const rowDiv = document.createElement('div');
        rowDiv.className = 'seat-row';
        
        for (let col = 1; col <= 5; col++) {
          if (col === 3) {
            // Aisle spacer
            const aisle = document.createElement('div');
            aisle.className = 'seat-aisle';
            aisle.innerText = 'Aisle';
            rowDiv.appendChild(aisle);
            continue;
          }
          
          // Calculate seat index
          const colIndexOffset = col > 3 ? col - 1 : col;
          const seatNum = r * 4 + colIndexOffset;
          
          if (seatNum > totalSeats) {
            // Empty placeholder for odd capacity
            const spacer = document.createElement('div');
            rowDiv.appendChild(spacer);
            continue;
          }
          
          const seat = document.createElement('div');
          const isBooked = bookedSeats.includes(seatNum);
          
          seat.className = `seat ${isBooked ? 'booked' : 'available'}`;
          seat.innerText = seatNum;
          seat.dataset.seatNum = seatNum;
          
          if (!isBooked) {
            seat.addEventListener('click', () => toggleSeatSelection(seat, seatNum));
          }
          rowDiv.appendChild(seat);
        }
        grid.appendChild(rowDiv);
      }
    }
  } catch (err) {
    grid.innerHTML = '<div class="text-danger">Failed to connect to seat mapping API.</div>';
  }
}

function toggleSeatSelection(seatElement, seatNum) {
  if (seatElement.classList.contains('selected')) {
    seatElement.classList.remove('selected');
    selectedSeats = selectedSeats.filter(s => s !== seatNum);
  } else {
    if (selectedSeats.length >= 6) {
      showToast("Maximum of 6 seats can be booked at a time.", "warning");
      return;
    }
    seatElement.classList.add('selected');
    selectedSeats.push(seatNum);
  }
  
  // Sort selection for clean layout
  selectedSeats.sort((a, b) => a - b);
  updateBookingSummary();
}

function updateBookingSummary() {
  const summarySeats = document.getElementById('summary-seats');
  const summaryPrice = document.getElementById('summary-total-price');
  const checkoutSection = document.getElementById('checkout-details-section');
  const pFormContainer = document.getElementById('passenger-forms');
  
  if (selectedSeats.length === 0) {
    summarySeats.innerText = 'None';
    summaryPrice.innerText = 'Rs. 0.00';
    checkoutSection.classList.add('hidden');
    pFormContainer.innerHTML = '';
    return;
  }
  
  summarySeats.innerText = selectedSeats.join(', ');
  const total = selectedSeats.length * ticketPrice;
  summaryPrice.innerText = `Rs. ${total.toFixed(2)}`;
  checkoutSection.classList.remove('hidden');
  
  // Dynamically generate Passenger forms
  // Keep existing inputs if possible to prevent wiping as user clicks, or build efficiently
  const currentForms = pFormContainer.querySelectorAll('.passenger-card');
  const formsMap = {};
  currentForms.forEach(f => {
    formsMap[f.dataset.seat] = {
      name: f.querySelector('.p-name').value,
      age: f.querySelector('.p-age').value,
      gender: f.querySelector('.p-gender').value
    };
  });
  
  pFormContainer.innerHTML = selectedSeats.map(seat => {
    const old = formsMap[seat] || { name: '', age: '', gender: 'Male' };
    return `
      <div class="passenger-card" data-seat="${seat}">
        <div class="passenger-card-header">
          <span>Passenger for Seat #${seat}</span>
        </div>
        <div class="passenger-grid">
          <div class="form-group">
            <label>Full Name</label>
            <input type="text" class="form-input p-name" placeholder="John Doe" value="${old.name}" required>
          </div>
          <div class="form-group">
            <label>Age</label>
            <input type="number" class="form-input p-age" placeholder="25" min="1" max="120" value="${old.age}" required>
          </div>
          <div class="form-group">
            <label>Gender</label>
            <select class="form-input p-gender">
              <option value="Male" ${old.gender === 'Male' ? 'selected' : ''}>Male</option>
              <option value="Female" ${old.gender === 'Female' ? 'selected' : ''}>Female</option>
              <option value="Other" ${old.gender === 'Other' ? 'selected' : ''}>Other</option>
            </select>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

async function submitBooking() {
  const container = document.getElementById('booking-page');
  const scheduleId = parseInt(container.dataset.scheduleId);
  const checkoutBtn = document.getElementById('confirm-booking-btn');
  
  // 1. Validate passenger inputs
  const cards = document.querySelectorAll('.passenger-card');
  const passengers = [];
  let valid = true;
  
  cards.forEach(card => {
    const seat = parseInt(card.dataset.seat);
    const name = card.querySelector('.p-name').value.trim();
    const age = card.querySelector('.p-age').value;
    const gender = card.querySelector('.p-gender').value;
    
    if (!name || !age) {
      valid = false;
      card.style.borderColor = 'var(--danger)';
    } else {
      card.style.borderColor = 'var(--border-color)';
      passengers.push({ name, age: parseInt(age), gender, seat_number: seat });
    }
  });
  
  if (!valid) {
    showToast("Please fill in passenger details for all selected seats.", "warning");
    return;
  }
  
  // 2. UPI/Card check depending on method
  const method = document.getElementById('payment-method-input').value;
  if (method === 'Card') {
    const cNum = document.getElementById('card-number').value.trim();
    const cExp = document.getElementById('card-expiry').value.trim();
    const cCvv = document.getElementById('card-cvv').value.trim();
    if (!cNum || !cExp || !cCvv) {
      showToast("Please enter credit/debit card credentials.", "warning");
      return;
    }
  } else {
    const upi = document.getElementById('upi-id').value.trim();
    if (!upi) {
      showToast("Please enter your UPI Address.", "warning");
      return;
    }
  }
  
  // Trigger spinner on button
  checkoutBtn.disabled = true;
  checkoutBtn.innerHTML = 'Processing Payment...';
  
  try {
    // Stage 1: Reserve seats and create booking (Pending)
    const reserveResponse = await fetch('/api/bookings/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ schedule_id: scheduleId, passengers })
    });
    
    const reserveResult = await reserveResponse.json();
    
    if (!reserveResponse.ok) {
      showToast(reserveResult.message, 'danger');
      checkoutBtn.disabled = false;
      checkoutBtn.innerHTML = 'Pay & Confirm Booking';
      return;
    }
    
    const bookingId = reserveResult.booking_id;
    
    // Stage 2: Finalize Payment
    const payResponse = await fetch(`/api/bookings/${bookingId}/pay`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ method })
    });
    
    const payResult = await payResponse.json();
    
    if (payResponse.ok) {
      showToast("Payment simulated successfully! Ticket confirmed.", "success");
      setTimeout(() => {
        window.location.href = `/ticket/${payResult.pnr}`;
      }, 1200);
    } else {
      showToast(payResult.message, 'danger');
      checkoutBtn.disabled = false;
      checkoutBtn.innerHTML = 'Pay & Confirm Booking';
    }
    
  } catch (err) {
    showToast("Checkout connection failed. Try again.", "danger");
    checkoutBtn.disabled = false;
    checkoutBtn.innerHTML = 'Pay & Confirm Booking';
  }
}

// ----------------- USER PROFILE PROFILE & BOOKINGS HISTORY -----------------
function initProfilePage() {
  loadBookingHistory();
}

async function loadBookingHistory() {
  const tbody = document.getElementById('history-table-body');
  if (!tbody) return;
  
  tbody.innerHTML = '<tr><td colspan="6" class="text-center">Loading ticket history...</td></tr>';
  
  try {
    const response = await fetch('/api/bookings/history');
    const result = await response.json();
    
    if (result.success && result.bookings.length > 0) {
      tbody.innerHTML = result.bookings.map(b => {
        const journeyDate = new Date(b.schedule.journey_date).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
        const route = `${b.schedule.route.source} -> ${b.schedule.route.destination}`;
        const seats = b.passengers.map(p => p.seat_number).join(', ');
        
        let statusBadge = `<span class="badge badge-warning">Pending</span>`;
        if (b.status === 'Confirmed') statusBadge = `<span class="badge badge-success">Confirmed</span>`;
        if (b.status === 'Cancelled') statusBadge = `<span class="badge badge-danger">Cancelled</span>`;
        
        // Show cancellation button only if Confirmed and journey date is in future
        const isFuture = new Date(b.schedule.journey_date) > new Date();
        const showCancel = b.status === 'Confirmed' && isFuture;
        const cancelBtn = showCancel ? 
          `<button onclick="confirmCancellation(${b.id}, '${b.pnr}')" class="btn btn-danger btn-sm" style="padding: 0.25rem 0.5rem; font-size:0.75rem;">Cancel</button>` : 
          '';
          
        return `
          <tr>
            <td><strong>${b.pnr}</strong></td>
            <td>${route}</td>
            <td>${journeyDate}</td>
            <td>Seats: ${seats}</td>
            <td>Rs. ${b.total_amount.toFixed(2)}</td>
            <td>${statusBadge}</td>
            <td>
              <div style="display:flex; gap:0.5rem;">
                <a href="/ticket/${b.pnr}" class="btn btn-secondary btn-sm" style="padding: 0.25rem 0.5rem; font-size:0.75rem;">View</a>
                ${cancelBtn}
              </div>
            </td>
          </tr>
        `;
      }).join('');
    } else {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">You have not booked any bus tickets yet.</td></tr>';
    }
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="7" class="text-center text-danger">Connection failed loading history.</td></tr>';
  }
}

async function confirmCancellation(bookingId, pnr) {
  if (confirm(`Are you sure you want to cancel PNR ${pnr}? This will release your seats.`)) {
    try {
      const response = await fetch(`/api/bookings/${bookingId}/cancel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const result = await response.json();
      
      if (response.ok) {
        showToast(result.message, 'success');
        loadBookingHistory(); // reload history
      } else {
        showToast(result.message, 'danger');
      }
    } catch (err) {
      showToast("Connection failed during cancellation.", "danger");
    }
  }
}
