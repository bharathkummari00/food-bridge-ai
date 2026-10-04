/**
 * Food Bridge AI - Shared Dynamic Footer Component
 */

function renderFooter() {
  const footerHtml = `
    <footer class="mt-auto bg-slate-900 text-slate-300 pt-16 pb-8 border-t border-slate-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10 mb-12">
          
          <!-- Column 1: Brand -->
          <div class="space-y-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-2xl bg-emerald-500 text-white flex items-center justify-center text-xl shadow-lg shadow-emerald-500/30">
                <i class="fa-solid fa-hand-holding-heart"></i>
              </div>
              <span class="text-xl font-bold text-white font-outfit">Food Bridge <span class="text-amber-400">AI</span></span>
            </div>
            <p class="text-xs text-slate-400 leading-relaxed">
              Connecting surplus food from banquet halls, caterers, and food businesses directly to verified shelters, orphanages, and NGOs. Zero hunger, zero waste.
            </p>
            <div class="flex items-center gap-3 pt-2">
              <span class="w-8 h-8 rounded-full bg-slate-800 hover:bg-emerald-600 text-slate-300 hover:text-white flex items-center justify-center transition cursor-pointer text-xs">
                <i class="fa-brands fa-github"></i>
              </span>
              <span class="w-8 h-8 rounded-full bg-slate-800 hover:bg-emerald-600 text-slate-300 hover:text-white flex items-center justify-center transition cursor-pointer text-xs">
                <i class="fa-brands fa-linkedin-in"></i>
              </span>
              <span class="w-8 h-8 rounded-full bg-slate-800 hover:bg-emerald-600 text-slate-300 hover:text-white flex items-center justify-center transition cursor-pointer text-xs">
                <i class="fa-solid fa-envelope"></i>
              </span>
            </div>
          </div>

          <!-- Column 2: Navigation Links -->
          <div>
            <h4 class="text-sm font-bold text-white uppercase tracking-wider mb-4 border-l-2 border-emerald-500 pl-2">Platform</h4>
            <ul class="space-y-2 text-xs">
              <li><a href="/" class="hover:text-emerald-400 transition">Home Page</a></li>
              <li><a href="/available-food" class="hover:text-emerald-400 transition">Browse Surplus Food</a></li>
              <li><a href="/map-view" class="hover:text-emerald-400 transition">Interactive Food Map</a></li>
              <li><a href="/donate" class="hover:text-emerald-400 transition">Publish Food Donation</a></li>
              <li><a href="/ai-recommendations" class="hover:text-emerald-400 transition">AI Redistribution Engine</a></li>
              <li><a href="/dashboard" class="hover:text-emerald-400 transition">Role Dashboards</a></li>
            </ul>
          </div>

          <!-- Column 3: Active Locations -->
          <div>
            <h4 class="text-sm font-bold text-white uppercase tracking-wider mb-4 border-l-2 border-amber-400 pl-2">Active Hubs</h4>
            <p class="text-xs text-slate-400 mb-3">Serving community centers and shelters across:</p>
            <div class="flex flex-wrap gap-1.5 text-[11px]">
              <span class="bg-slate-800 px-2 py-1 rounded text-emerald-300">Warangal (Hanamkonda)</span>
              <span class="bg-slate-800 px-2 py-1 rounded text-emerald-300">Subedari</span>
              <span class="bg-slate-800 px-2 py-1 rounded text-emerald-300">Kazipet</span>
              <span class="bg-slate-800 px-2 py-1 rounded text-emerald-300">Nakkalagutta</span>
              <span class="bg-slate-800 px-2 py-1 rounded text-emerald-300">Waddepally</span>
              <span class="bg-slate-800 px-2 py-1 rounded text-emerald-300">Hyderabad (Hitech City)</span>
              <span class="bg-slate-800 px-2 py-1 rounded text-emerald-300">Gachibowli</span>
            </div>
          </div>

          <!-- Column 4: AI & Quality Guarantee -->
          <div>
            <h4 class="text-sm font-bold text-white uppercase tracking-wider mb-4 border-l-2 border-emerald-500 pl-2">AI Smart Safety</h4>
            <div class="bg-slate-800/80 p-4 rounded-2xl border border-slate-700 space-y-2">
              <div class="flex items-center gap-2 text-emerald-400 text-xs font-bold">
                <i class="fa-solid fa-shield-halved"></i> 4-Tier Quality Protocol
              </div>
              <p class="text-[11px] text-slate-400 leading-snug">
                Every batch is evaluated with our real-time freshness decay curve and matched with the nearest verified recipient for rapid, safe pickup.
              </p>
              <div class="pt-1 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                <span class="text-[10px] font-semibold text-emerald-300 uppercase tracking-wider">System Live & Operational</span>
              </div>
            </div>
          </div>

        </div>

        <!-- Bottom Line -->
        <div class="pt-8 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-3">
          <p>© 2026 Food Bridge AI System. Built with pride for Sustainable Communities.</p>
          <div class="flex items-center gap-4">
            <span class="text-slate-400">UN SDG #2: Zero Hunger</span>
            <span class="text-slate-400">UN SDG #12: Responsible Consumption</span>
          </div>
        </div>
      </div>
    </footer>
  `;

  const container = document.getElementById("footer-container");
  if (container) {
    container.innerHTML = footerHtml;
  }
}

document.addEventListener("DOMContentLoaded", renderFooter);
