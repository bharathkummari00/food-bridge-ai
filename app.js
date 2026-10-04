/**
 * Food Bridge AI - Global Core Utilities & State
 */

const AppState = {
  user: null,
  notifications: [],
  unreadCount: 0,
  hierarchy: null
};

// Toast notification helper
function showToast(message, type = "success") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.className = "fixed bottom-5 right-5 z-50 flex flex-col gap-2 pointer-events-none";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  const bg = type === "success" ? "bg-emerald-600 text-white" : 
             type === "error" ? "bg-rose-600 text-white" : 
             type === "warning" ? "bg-amber-500 text-white" : "bg-slate-800 text-white";

  const icon = type === "success" ? "fa-circle-check" :
               type === "error" ? "fa-circle-exclamation" :
               type === "warning" ? "fa-triangle-exclamation" : "fa-bell";

  toast.className = `pointer-events-auto flex items-center gap-3 px-5 py-3 rounded-xl shadow-xl text-sm font-medium transition-all duration-300 transform translate-y-3 opacity-0 ${bg}`;
  toast.innerHTML = `<i class="fa-solid ${icon} text-lg"></i> <span>${message}</span>`;
  container.appendChild(toast);

  // Trigger animation
  requestAnimationFrame(() => {
    toast.classList.remove("translate-y-3", "opacity-0");
  });

  setTimeout(() => {
    toast.classList.add("opacity-0", "translate-y-2");
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Fetch current session user
async function checkAuthSession() {
  try {
    const res = await fetch("/api/auth/me");
    const data = await res.json();
    if (data.authenticated) {
      AppState.user = data.user;
    } else {
      AppState.user = null;
    }
  } catch (err) {
    console.warn("Auth check error:", err);
    AppState.user = null;
  }
  updateAuthUI();
  fetchNotifications();
}

// Update UI elements based on authentication state
function updateAuthUI() {
  const authNav = document.getElementById("nav-auth-section");
  const userGreeting = document.getElementById("user-greeting");

  if (!authNav) return;

  if (AppState.user) {
    const roleBadge = AppState.user.role === "donor" ? "bg-emerald-100 text-emerald-800" :
                      AppState.user.role === "ngo" ? "bg-amber-100 text-amber-800" : "bg-purple-100 text-purple-800";
    
    authNav.innerHTML = `
      <div class="flex items-center gap-3">
        <a href="/dashboard" class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 hover:bg-slate-200 transition">
          <div class="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center font-bold text-xs uppercase">
            ${AppState.user.name.charAt(0)}
          </div>
          <div class="hidden sm:block text-left pr-1">
            <p class="text-xs font-bold leading-tight text-slate-800">${AppState.user.name.split(' ')[0]}</p>
            <span class="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded-full ${roleBadge}">${AppState.user.role}</span>
          </div>
        </a>
        <button onclick="handleLogout()" class="text-xs text-slate-500 hover:text-rose-600 font-semibold px-2 py-1 rounded transition" title="Logout">
          <i class="fa-solid fa-arrow-right-from-bracket"></i>
        </button>
      </div>
    `;
  } else {
    authNav.innerHTML = `
      <div class="flex items-center gap-2">
        <a href="/auth?tab=login" class="text-xs sm:text-sm font-semibold text-slate-700 hover:text-emerald-600 px-3 py-1.5 transition">Login</a>
        <a href="/auth?tab=register" class="btn-primary text-xs sm:text-sm py-1.5 px-4 shadow-sm">Register</a>
      </div>
    `;
  }
}

// 1-Click Role Switcher for easy testing / evaluation
async function switchRole(role) {
  try {
    const res = await fetch("/api/auth/demo-login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role: role })
    });
    const data = await res.json();
    if (data.success) {
      AppState.user = data.user;
      showToast(`Switched to Demo ${role.toUpperCase()}: ${data.user.name}`, "success");
      updateAuthUI();
      // Reload current page if on dashboard or refresh stats
      if (window.location.pathname.includes("dashboard")) {
        window.location.reload();
      }
    } else {
      showToast(data.error || "Failed to switch role", "error");
    }
  } catch (err) {
    showToast("Network error switching role", "error");
  }
}

// Handle Logout
async function handleLogout() {
  try {
    await fetch("/api/auth/logout", { method: "POST" });
    AppState.user = null;
    showToast("Successfully logged out", "info");
    updateAuthUI();
    if (window.location.pathname.includes("dashboard") || window.location.pathname.includes("donate")) {
      window.location.href = "/";
    }
  } catch (err) {
    window.location.reload();
  }
}

// Notifications drawer logic
async function fetchNotifications() {
  try {
    const res = await fetch("/api/notifications");
    const data = await res.json();
    if (data.success) {
      AppState.notifications = data.notifications;
      AppState.unreadCount = data.unread_count;

      const badge = document.getElementById("notif-badge");
      if (badge) {
        if (data.unread_count > 0) {
          badge.textContent = data.unread_count;
          badge.classList.remove("hidden");
        } else {
          badge.classList.add("hidden");
        }
      }
      renderNotificationsList();
    }
  } catch (err) {
    console.warn("Failed to fetch notifications:", err);
  }
}

function toggleNotifDrawer() {
  const drawer = document.getElementById("notif-dropdown");
  if (!drawer) return;
  drawer.classList.toggle("hidden");
  if (!drawer.classList.contains("hidden")) {
    fetchNotifications();
  }
}

function renderNotificationsList() {
  const container = document.getElementById("notif-items-container");
  if (!container) return;

  if (AppState.notifications.length === 0) {
    container.innerHTML = `<div class="p-6 text-center text-slate-400 text-xs"><i class="fa-solid fa-bell-slash text-2xl mb-2"></i><p>No new notifications</p></div>`;
    return;
  }

  container.innerHTML = AppState.notifications.map(n => `
    <div class="p-3 border-b border-slate-100 hover:bg-slate-50 transition text-left cursor-pointer ${n.is_read ? 'opacity-70' : 'bg-emerald-50/40'}" onclick="markNotifRead(${n.id})">
      <div class="flex items-center justify-between mb-1">
        <span class="text-xs font-bold text-slate-800">${n.title}</span>
        <span class="text-[10px] text-slate-400">${n.created_at ? n.created_at.slice(11, 16) : ''}</span>
      </div>
      <p class="text-xs text-slate-600 leading-snug">${n.message}</p>
    </div>
  `).join("");
}

async function markNotifRead(id) {
  try {
    await fetch(`/api/notifications/${id}/read`, { method: "POST" });
    fetchNotifications();
  } catch (err) {
    console.error(err);
  }
}

async function markAllNotifsRead() {
  try {
    await fetch("/api/notifications/read-all", { method: "POST" });
    fetchNotifications();
    showToast("All notifications marked as read", "info");
  } catch (err) {
    console.error(err);
  }
}

// Cascading Location Dropdowns Loader
async function setupLocationHierarchy(citySelectId, areaSelectId, colonySelectId, defaultCity = "Warangal", defaultArea = "Hanamkonda", defaultColony = "Subedari") {
  const citySelect = document.getElementById(citySelectId);
  const areaSelect = document.getElementById(areaSelectId);
  const colonySelect = document.getElementById(colonySelectId);

  if (!citySelect || !areaSelect || !colonySelect) return;

  try {
    if (!AppState.hierarchy) {
      const res = await fetch("/api/locations/hierarchy");
      const data = await res.json();
      AppState.hierarchy = data.hierarchy;
    }

    const h = AppState.hierarchy;

    // Populate Cities
    citySelect.innerHTML = Object.keys(h).map(c => `<option value="${c}" ${c === defaultCity ? 'selected' : ''}>${c}</option>`).join("");

    function updateAreas() {
      const selectedCity = citySelect.value;
      const areas = h[selectedCity] ? Object.keys(h[selectedCity]) : [];
      areaSelect.innerHTML = areas.map(a => `<option value="${a}" ${a === defaultArea ? 'selected' : ''}>${a}</option>`).join("");
      updateColonies();
    }

    function updateColonies() {
      const selectedCity = citySelect.value;
      const selectedArea = areaSelect.value;
      const colonies = (h[selectedCity] && h[selectedCity][selectedArea]) ? h[selectedCity][selectedArea] : [];
      colonySelect.innerHTML = colonies.map(col => `<option value="${col}" ${col === defaultColony ? 'selected' : ''}>${col}</option>`).join("");
    }

    citySelect.addEventListener("change", updateAreas);
    areaSelect.addEventListener("change", updateColonies);

    updateAreas();
  } catch (err) {
    console.error("Location hierarchy error:", err);
  }
}

// "Use My Current Location" button handler
// NEVER exposes coordinates to the user. Matches to nearest City -> Area -> Colony.
function useCurrentLocation(citySelectId, areaSelectId, colonySelectId, addressInputId, statusIndicatorId) {
  const statusEl = statusIndicatorId ? document.getElementById(statusIndicatorId) : null;
  if (statusEl) {
    statusEl.innerHTML = `<span class="text-xs text-emerald-600 font-medium"><i class="fa-solid fa-spinner fa-spin"></i> Detecting nearby locality...</span>`;
  }

  if (!navigator.geolocation) {
    showToast("Geolocation is not supported by your browser", "error");
    if (statusEl) statusEl.innerHTML = "";
    return;
  }

  navigator.geolocation.getCurrentPosition(
    async (position) => {
      try {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;

        const res = await fetch("/api/locations/reverse-geocode", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ latitude: lat, longitude: lng })
        });
        const data = await res.json();

        if (data.success && data.location) {
          const loc = data.location;
          const cityEl = document.getElementById(citySelectId);
          const areaEl = document.getElementById(areaSelectId);
          const colonyEl = document.getElementById(colonySelectId);
          const addressEl = addressInputId ? document.getElementById(addressInputId) : null;

          if (cityEl) cityEl.value = loc.city;
          // Trigger change to update areas
          cityEl.dispatchEvent(new Event("change"));

          setTimeout(() => {
            if (areaEl) {
              areaEl.value = loc.area;
              areaEl.dispatchEvent(new Event("change"));
            }
            setTimeout(() => {
              if (colonyEl) colonyEl.value = loc.colony;
              if (addressEl && loc.landmark && !addressEl.value) {
                addressEl.value = loc.landmark;
              }
            }, 50);
          }, 50);

          showToast(`Location set to: ${loc.display_name}`, "success");
          if (statusEl) {
            statusEl.innerHTML = `<span class="text-xs text-emerald-700 font-semibold"><i class="fa-solid fa-circle-check"></i> Found: ${loc.display_name}</span>`;
          }
        } else {
          showToast("Could not resolve location name", "warning");
          if (statusEl) statusEl.innerHTML = "";
        }
      } catch (err) {
        showToast("Error resolving location name", "error");
        if (statusEl) statusEl.innerHTML = "";
      }
    },
    (err) => {
      // Graceful fallback for permission denied or localhost mock
      console.warn("GPS error/denied:", err.message);
      // Auto fallback to Warangal Central
      showToast("Using default central locality: Warangal -> Hanamkonda -> Subedari", "info");
      if (statusEl) {
        statusEl.innerHTML = `<span class="text-xs text-slate-500">Defaulted to Warangal – Subedari</span>`;
      }
    },
    { timeout: 8000 }
  );
}

// Request Food Modal Handler
function openRequestModal(donationId, foodName, availableQty, unit, readableLoc) {
  let modal = document.getElementById("request-food-modal");
  if (!modal) {
    modal = document.createElement("div");
    modal.id = "request-food-modal";
    modal.className = "fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm transition-all";
    document.body.appendChild(modal);
  }

  modal.innerHTML = `
    <div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-slate-100 transform transition-all">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-amber-100 text-amber-700 flex items-center justify-center text-lg">
            <i class="fa-solid fa-hand-holding-heart"></i>
          </div>
          <div>
            <h3 class="text-lg font-bold text-slate-800">Request Food</h3>
            <p class="text-xs text-slate-500">Surplus Food Redistribution</p>
          </div>
        </div>
        <button onclick="closeRequestModal()" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center transition">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <div class="mb-4 bg-emerald-50 rounded-2xl p-4 border border-emerald-100">
        <h4 class="font-bold text-slate-800 text-sm mb-1">${foodName}</h4>
        <p class="text-xs text-emerald-800 flex items-center gap-1.5 mb-1">
          <i class="fa-solid fa-boxes-stacked"></i> Available: <strong>${availableQty} ${unit}</strong>
        </p>
        <p class="text-xs text-slate-600 flex items-center gap-1.5">
          <i class="fa-solid fa-location-dot text-emerald-600"></i> ${readableLoc}
        </p>
      </div>

      <form id="submit-request-form" onsubmit="handleRequestSubmit(event, ${donationId})">
        <div class="mb-3">
          <label class="block text-xs font-bold text-slate-700 mb-1">Quantity Needed (${unit})</label>
          <input type="number" id="req-qty" min="1" max="${availableQty}" value="${availableQty}" required
            class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm font-semibold text-slate-800">
        </div>

        <div class="mb-4">
          <label class="block text-xs font-bold text-slate-700 mb-1">Pickup Notes / Estimated Arrival</label>
          <textarea id="req-notes" rows="2" placeholder="e.g. Our NGO volunteer vehicle will arrive within 35 minutes."
            class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm text-slate-700">We have volunteers ready with clean containers for immediate pickup.</textarea>
        </div>

        <div class="flex items-center gap-2">
          <button type="button" onclick="closeRequestModal()" class="btn-secondary flex-1 py-2.5 text-xs font-bold">Cancel</button>
          <button type="submit" class="btn-primary flex-1 py-2.5 text-xs font-bold shadow-md">Confirm Request</button>
        </div>
      </form>
    </div>
  `;

  modal.classList.remove("hidden");
}

function closeRequestModal() {
  const modal = document.getElementById("request-food-modal");
  if (modal) modal.classList.add("hidden");
}

async function handleRequestSubmit(e, donationId) {
  e.preventDefault();
  const qty = document.getElementById("req-qty").value;
  const notes = document.getElementById("req-notes").value;

  try {
    const res = await fetch("/api/requests", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        donation_id: donationId,
        quantity_requested: qty,
        notes: notes
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast("Food request submitted successfully! Donor notified.", "success");
      closeRequestModal();
      if (typeof reloadFoodCards === "function") {
        reloadFoodCards();
      } else {
        setTimeout(() => window.location.reload(), 1200);
      }
    } else {
      showToast(data.error || "Could not submit request", "error");
    }
  } catch (err) {
    showToast("Network error submitting request", "error");
  }
}

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
  checkAuthSession();
});
