/**
 * Food Bridge AI - Shared Dynamic Navbar Component
 */

function renderNavbar() {
  const currentPath = window.location.pathname;

  const navHtml = `
    <!-- Top Demo Quick Switcher Banner -->
    <div class="bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-700 text-white py-1.5 px-4 text-xs font-semibold shadow-inner">
      <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
        <div class="flex items-center gap-2">
          <span class="bg-emerald-500/50 px-2 py-0.5 rounded text-[11px] uppercase tracking-wider font-extrabold text-emerald-100 flex items-center gap-1">
            <i class="fa-solid fa-bolt-lightning text-amber-300"></i> B.Tech Viva Quick Switcher
          </span>
          <span class="hidden md:inline text-emerald-100 text-xs">Switch roles with 1 click to test features:</span>
        </div>
        <div class="flex items-center gap-1.5 flex-wrap">
          <button onclick="switchRole('donor')" class="bg-white/15 hover:bg-white/30 text-white px-2.5 py-1 rounded-full text-xs font-bold transition flex items-center gap-1">
            <span>🧑‍🍳</span> Donor (Royal Banquet)
          </button>
          <button onclick="switchRole('ngo')" class="bg-white/15 hover:bg-white/30 text-white px-2.5 py-1 rounded-full text-xs font-bold transition flex items-center gap-1">
            <span>🤝</span> NGO (Hope Foundation)
          </button>
          <button onclick="switchRole('admin')" class="bg-white/15 hover:bg-white/30 text-white px-2.5 py-1 rounded-full text-xs font-bold transition flex items-center gap-1">
            <span>🛡️</span> Admin Console
          </button>
        </div>
      </div>
    </div>

    <!-- Main Navigation Bar -->
    <header class="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-100 shadow-sm transition">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-20">
          
          <!-- Logo & Brand -->
          <a href="/" class="flex items-center gap-3 group">
            <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-400 text-white flex items-center justify-center text-2xl shadow-lg shadow-emerald-500/25 group-hover:scale-105 transition-transform">
              <i class="fa-solid fa-hand-holding-heart"></i>
            </div>
            <div>
              <div class="flex items-center gap-1.5">
                <span class="text-xl sm:text-2xl font-extrabold tracking-tight text-slate-900 font-outfit">Food Bridge</span>
                <span class="text-xs font-extrabold bg-gradient-to-r from-amber-500 to-orange-500 text-white px-2 py-0.5 rounded-md uppercase tracking-wider shadow-sm">AI</span>
              </div>
              <p class="text-[11px] font-medium text-emerald-600 leading-tight">Food Redistribution System</p>
            </div>
          </a>

          <!-- Desktop Navigation Links -->
          <nav class="hidden lg:flex items-center gap-1 font-semibold text-sm">
            <a href="/" class="px-3.5 py-2 rounded-xl transition ${currentPath === '/' ? 'text-emerald-600 bg-emerald-50 font-bold' : 'text-slate-600 hover:text-emerald-600 hover:bg-slate-50'}">
              <i class="fa-solid fa-house mr-1 text-xs"></i> Home
            </a>
            <a href="/available-food" class="px-3.5 py-2 rounded-xl transition ${currentPath.includes('available-food') ? 'text-emerald-600 bg-emerald-50 font-bold' : 'text-slate-600 hover:text-emerald-600 hover:bg-slate-50'}">
              <i class="fa-solid fa-utensils mr-1 text-xs"></i> Available Food
            </a>
            <a href="/map-view" class="px-3.5 py-2 rounded-xl transition ${currentPath.includes('map-view') ? 'text-emerald-600 bg-emerald-50 font-bold' : 'text-slate-600 hover:text-emerald-600 hover:bg-slate-50'}">
              <i class="fa-solid fa-map-location-dot mr-1 text-xs"></i> Live Food Map
            </a>
            <a href="/donate" class="px-3.5 py-2 rounded-xl transition ${currentPath.includes('donate') ? 'text-emerald-600 bg-emerald-50 font-bold' : 'text-slate-600 hover:text-emerald-600 hover:bg-slate-50'}">
              <i class="fa-solid fa-circle-plus mr-1 text-xs text-amber-500"></i> Donate Food
            </a>
            <a href="/ai-recommendations" class="px-3.5 py-2 rounded-xl transition ${currentPath.includes('ai-recommendations') ? 'text-emerald-600 bg-emerald-50 font-bold' : 'text-slate-600 hover:text-emerald-600 hover:bg-slate-50'}">
              <i class="fa-solid fa-wand-magic-sparkles mr-1 text-xs text-emerald-600"></i> AI Match
            </a>
            <a href="/dashboard" class="px-3.5 py-2 rounded-xl transition ${currentPath.includes('dashboard') ? 'text-emerald-600 bg-emerald-50 font-bold' : 'text-slate-600 hover:text-emerald-600 hover:bg-slate-50'}">
              <i class="fa-solid fa-chart-pie mr-1 text-xs"></i> Dashboard
            </a>
          </nav>

          <!-- Right Action Area: Notifications & Auth -->
          <div class="flex items-center gap-3">
            
            <!-- Notification Bell -->
            <div class="relative">
              <button onclick="toggleNotifDrawer()" class="w-10 h-10 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center transition relative" title="Notifications">
                <i class="fa-regular fa-bell text-base"></i>
                <span id="notif-badge" class="hidden absolute -top-1 -right-1 w-5 h-5 rounded-full bg-rose-500 text-white font-extrabold text-[10px] flex items-center justify-center border-2 border-white animate-pulse">0</span>
              </button>

              <!-- Notifications Dropdown -->
              <div id="notif-dropdown" class="hidden absolute right-0 mt-3 w-80 sm:w-96 bg-white rounded-2xl shadow-2xl border border-slate-100 overflow-hidden z-50 transition-all">
                <div class="p-3.5 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <span class="font-bold text-slate-800 text-sm">Notifications</span>
                    <span class="text-xs bg-emerald-100 text-emerald-700 font-bold px-2 py-0.5 rounded-full">Live Alerts</span>
                  </div>
                  <button onclick="markAllNotifsRead()" class="text-xs text-emerald-600 hover:underline font-semibold">Mark all read</button>
                </div>
                <div id="notif-items-container" class="max-h-80 overflow-y-auto divide-y divide-slate-50">
                  <div class="p-4 text-center text-xs text-slate-400">Loading notifications...</div>
                </div>
                <div class="p-2.5 bg-slate-50 text-center border-t border-slate-100">
                  <a href="/dashboard" class="text-xs font-bold text-slate-600 hover:text-emerald-600">View in Dashboard &rarr;</a>
                </div>
              </div>
            </div>

            <!-- Auth Buttons Section (Dynamic) -->
            <div id="nav-auth-section" class="flex items-center gap-2">
              <div class="w-24 h-8 bg-slate-100 animate-pulse rounded-full"></div>
            </div>

            <!-- Mobile Hamburger Toggle -->
            <button onclick="toggleMobileNav()" class="lg:hidden w-10 h-10 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center hover:bg-slate-200 transition">
              <i class="fa-solid fa-bars text-lg"></i>
            </button>
          </div>

        </div>

        <!-- Mobile Collapsible Menu -->
        <div id="mobile-nav" class="hidden lg:hidden py-4 border-t border-slate-100 space-y-1 text-sm font-semibold">
          <a href="/" class="block px-3 py-2 rounded-lg text-slate-700 hover:bg-emerald-50 hover:text-emerald-600">Home</a>
          <a href="/available-food" class="block px-3 py-2 rounded-lg text-slate-700 hover:bg-emerald-50 hover:text-emerald-600">Available Food</a>
          <a href="/map-view" class="block px-3 py-2 rounded-lg text-slate-700 hover:bg-emerald-50 hover:text-emerald-600">Live Food Map</a>
          <a href="/donate" class="block px-3 py-2 rounded-lg text-slate-700 hover:bg-emerald-50 hover:text-emerald-600">Donate Food</a>
          <a href="/ai-recommendations" class="block px-3 py-2 rounded-lg text-slate-700 hover:bg-emerald-50 hover:text-emerald-600">AI Match Engine</a>
          <a href="/dashboard" class="block px-3 py-2 rounded-lg text-slate-700 hover:bg-emerald-50 hover:text-emerald-600">Dashboard & Analytics</a>
        </div>
      </div>
    </header>
  `;

  const container = document.getElementById("navbar-container");
  if (container) {
    container.innerHTML = navHtml;
  }
}

function toggleMobileNav() {
  const el = document.getElementById("mobile-nav");
  if (el) el.classList.toggle("hidden");
}

document.addEventListener("DOMContentLoaded", renderNavbar);
