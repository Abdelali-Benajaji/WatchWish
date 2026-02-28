/* ═══════════════════════════════════════════════════════════════
   WatchWish Studio — Admin Dashboard App Logic
   ═══════════════════════════════════════════════════════════════ */

const API_BASE = window.location.origin;

document.addEventListener('DOMContentLoaded', async () => {
    lucide.createIcons();
    initSidebar();
    initChartSwitcher();
    initSimulator();
    initModal();
    initNavigation();
    initSearch();
    initMoviesPage();
    initStatisticsPage();
    initStudioPage();
    await loadRealData();
    initAudienceRing();
    initAudiencePage();
});

async function loadRealData() {
    await Promise.all([loadKPIs(), loadCharts(), loadTopMoviesTable(), loadDashboardExtraCharts()]);
}

/* ═══════════════════════════════════════════════════════════════
   KPIs
   ═══════════════════════════════════════════════════════════════ */
async function loadKPIs() {
    try {
        const res = await fetch(`${API_BASE}/dashboard/api/?endpoint=kpis`);
        const json = await res.json();
        const d = json.data;
        animateCounter(".kpi-movies", d.total_movies, 0, "");
        animateCounter(".kpi-revenue", d.total_revenue_b, 1, "B", "$");
        animateCounter(".kpi-roi", d.avg_roi, 1, "x");
        animateCounter(".kpi-rating", d.avg_rating, 1, "/10");
        document.querySelectorAll(".kpi-card").forEach((card, i) => {
            card.addEventListener("click", () => i === 0 ? navigateTo("movies") : navigateTo("statistics"));
        });
    } catch (e) {
        console.error("KPI load failed:", e);
        initDemoKPIs();
    }
}

function initDemoKPIs() {
    animateCounter(".kpi-movies", 1284, 0, "");
    animateCounter(".kpi-revenue", 4.7, 1, "B", "$");
    animateCounter(".kpi-roi", 3.2, 1, "x");
    animateCounter(".kpi-rating", 7.1, 1, "/10");
}

function animateCounter(sel, target, decimals, suffix = "", prefix = "") {
    const el = document.querySelector(sel);
    if (!el) return;
    const duration = 1400, start = performance.now();
    const tick = (now) => {
        const p = Math.min((now - start) / duration, 1);
        const ease = 1 - Math.pow(1 - p, 3);
        el.textContent = prefix + (target * ease).toFixed(decimals) + suffix;
        if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
}

/* ═══════════════════════════════════════════════════════════════
   CHARTS
   ═══════════════════════════════════════════════════════════════ */
let barChart, scatterChart, budgetPieChart, revenueBarChart;

const PALETTE = {
    "Action": { bg: "rgba(229,9,20,.7)", border: "#e50914" },
    "Adventure": { bg: "rgba(255,59,48,.7)", border: "#ff3b30" },
    "Animation": { bg: "rgba(255,107,107,.7)", border: "#ff6b6b" },
    "Comedy": { bg: "rgba(251,191,36,.7)", border: "#fbbf24" },
    "Crime": { bg: "rgba(249,115,22,.7)", border: "#f97316" },
    "Documentary": { bg: "rgba(161,161,170,.7)", border: "#a1a1aa" },
    "Drama": { bg: "rgba(236,72,153,.7)", border: "#ec4899" },
    "Fantasy": { bg: "rgba(178,7,16,.7)", border: "#b20710" },
    "Horror": { bg: "rgba(153,27,27,.7)", border: "#991b1b" },
    "Musical": { bg: "rgba(245,158,11,.7)", border: "#f59e0b" },
    "Mystery": { bg: "rgba(124,58,237,.7)", border: "#7c3aed" },
    "Romance": { bg: "rgba(244,63,94,.7)", border: "#f43f5e" },
    "Sci-Fi": { bg: "rgba(239,68,68,.7)", border: "#ef4444" },
    "Science Fiction": { bg: "rgba(239,68,68,.7)", border: "#ef4444" },
    "Thriller": { bg: "rgba(234,179,8,.7)", border: "#eab308" },
    "War": { bg: "rgba(220,38,38,.7)", border: "#dc2626" },
    "Western": { bg: "rgba(180,83,9,.7)", border: "#b45309" },
};

function colorFor(genre) {
    return PALETTE[genre] || { bg: "rgba(229,9,20,.7)", border: "#e50914" };
}

function chartDefaults() {
    Chart.defaults.color = "#8b8ba7";
    Chart.defaults.borderColor = "rgba(255,255,255,.06)";
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.size = 11;
}

async function loadCharts() {
    try {
        const res = await fetch(`${API_BASE}/admin/dashboard/api/?endpoint=genre_stats`);
        const json = await res.json();
        renderCharts(json.data);
    } catch (e) {
        console.error("Stats load failed:", e);
        renderCharts(DEMO_GENRE_STATS);
    }
}

function renderCharts(stats) {
    chartDefaults();
    const sorted = [...stats].sort((a, b) => b.avg_roi - a.avg_roi).slice(0, 12);
    const labels = sorted.map(d => d.genre);
    const rois = sorted.map(d => d.avg_roi);
    const budgets = sorted.map(d => d.avg_budget);
    const bgs = labels.map(g => colorFor(g).bg);
    const borders = labels.map(g => colorFor(g).border);

    const barCtx = document.getElementById("roiBarChart").getContext("2d");
    const grads = bgs.map((bg, i) => {
        const g = barCtx.createLinearGradient(0, 0, 0, 280);
        g.addColorStop(0, borders[i]);
        g.addColorStop(1, bg.replace(".7", ".1"));
        return g;
    });

    if (barChart) barChart.destroy();
    barChart = new Chart(barCtx, {
        type: "bar",
        data: {
            labels, datasets: [
                { label: "ROI (x)", data: rois, backgroundColor: grads, borderColor: borders, borderWidth: 1.5, borderRadius: 6, barPercentage: .6, yAxisID: "y" },
                { label: "Avg Budget ($M)", data: budgets, backgroundColor: "rgba(255,255,255,.06)", borderColor: "rgba(255,255,255,.12)", borderWidth: 1, borderRadius: 6, barPercentage: .6, yAxisID: "y1" }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            interaction: { mode: "index", intersect: false },
            animation: { duration: 900, easing: "easeOutQuart" },
            plugins: {
                legend: { position: "top", align: "end", labels: { boxWidth: 10, usePointStyle: true, padding: 14 } },
                tooltip: {
                    backgroundColor: "rgba(10,10,26,.94)", borderColor: "rgba(229,9,20,.4)", borderWidth: 1, cornerRadius: 10, padding: 12, titleFont: { weight: 600 },
                    callbacks: { label: ctx => ctx.dataset.label.startsWith("ROI") ? `ROI: ${ctx.raw}x` : `Budget: $${ctx.raw}M` }
                }
            },
            scales: {
                x: { grid: { display: false }, ticks: { padding: 6 } },
                y: { position: "left", title: { display: true, text: "ROI (x)" }, grid: { color: "rgba(255,255,255,.04)" }, ticks: { callback: v => v + "x" }, beginAtZero: true },
                y1: { position: "right", title: { display: true, text: "Avg Budget ($M)" }, grid: { drawOnChartArea: false }, ticks: { callback: v => "$" + v + "M" }, beginAtZero: true }
            },
            onClick: (event, elements) => { if (elements.length > 0) navigateTo('audience', barChart.data.labels[elements[0].index]); }
        }
    });

    const scatterCtx = document.getElementById("roiScatterChart").getContext("2d");
    if (scatterChart) scatterChart.destroy();
    scatterChart = new Chart(scatterCtx, {
        type: "bubble",
        data: { datasets: sorted.map((d, i) => ({ label: d.genre, data: [{ x: d.avg_budget, y: d.avg_roi, r: Math.max(6, d.avg_revenue / 60) }], backgroundColor: bgs[i], borderColor: borders[i], borderWidth: 1.5 })) },
        options: {
            responsive: true, maintainAspectRatio: false,
            animation: { duration: 1100, easing: "easeOutQuart" },
            onClick: (event, elements) => { if (elements.length > 0) navigateTo('audience', scatterChart.data.datasets[elements[0].datasetIndex].label); },
            plugins: {
                legend: { position: "top", align: "end", labels: { boxWidth: 10, usePointStyle: true, padding: 14 } },
                tooltip: {
                    backgroundColor: "rgba(10,10,26,.94)", borderColor: "rgba(229,9,20,.4)", borderWidth: 1, cornerRadius: 10, padding: 12, titleFont: { weight: 600 },
                    callbacks: { title: ctx => ctx[0].dataset.label, label: ctx => [`Budget: $${ctx.raw.x}M`, `ROI: ${ctx.raw.y}x`, `Revenue: $${Math.round(ctx.raw.r * 60)}M`] }
                }
            },
            scales: {
                x: { title: { display: true, text: "Avg Production Budget ($M)" }, grid: { color: "rgba(255,255,255,.04)" }, ticks: { callback: v => "$" + v + "M" } },
                y: { title: { display: true, text: "ROI (x)" }, grid: { color: "rgba(255,255,255,.04)" }, ticks: { callback: v => v + "x" }, beginAtZero: true }
            }
        }
    });
}

function initChartSwitcher() {
    document.querySelectorAll(".chip[data-view]").forEach(chip => {
        chip.addEventListener("click", () => {
            document.querySelectorAll(".chip[data-view]").forEach(c => c.classList.remove("active"));
            chip.classList.add("active");
            const view = chip.dataset.view;
            document.getElementById("roiBarChart").classList.toggle("hidden", view !== "bar");
            document.getElementById("roiScatterChart").classList.toggle("hidden", view !== "scatter");
        });
    });
}

async function loadDashboardExtraCharts() {
    try {
        const res = await fetch(`${API_BASE}/dashboard/api/?endpoint=genre_stats`);
        const json = await res.json();
        renderBudgetPieChart(json.data);
        renderRevenueBarChart(json.data);
    } catch (e) { console.error("Extra charts load failed:", e); }
}

function renderBudgetPieChart(stats) {
    const ctx = document.getElementById("budgetPieChart");
    if (!ctx) return;
    const sorted = [...stats].sort((a, b) => b.avg_budget - a.avg_budget).slice(0, 8);
    const labels = sorted.map(d => d.genre);
    const colors = labels.map(g => colorFor(g).border);
    if (budgetPieChart) budgetPieChart.destroy();
    budgetPieChart = new Chart(ctx, {
        type: 'doughnut',
        data: { labels, datasets: [{ data: sorted.map(d => d.avg_budget), backgroundColor: colors.map(c => c + 'b3'), borderColor: colors, borderWidth: 2 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { boxWidth: 12, padding: 8 } }, tooltip: { backgroundColor: 'rgba(10,10,26,.94)', borderColor: 'rgba(229,9,20,.4)', borderWidth: 1, callbacks: { label: ctx => `${ctx.label}: $${ctx.raw}M avg budget` } } } }
    });
}

function renderRevenueBarChart(stats) {
    const ctx = document.getElementById("revenueBarChart");
    if (!ctx) return;
    const sorted = [...stats].sort((a, b) => b.avg_revenue - a.avg_revenue).slice(0, 8);
    const labels = sorted.map(d => d.genre);
    const colors = labels.map(g => colorFor(g).border);
    if (revenueBarChart) revenueBarChart.destroy();
    revenueBarChart = new Chart(ctx, {
        type: 'bar',
        data: { labels, datasets: [{ label: 'Avg Revenue ($M)', data: sorted.map(d => d.avg_revenue), backgroundColor: colors.map(c => c + 'b3'), borderColor: colors, borderWidth: 1.5, borderRadius: 6 }] },
        options: { responsive: true, maintainAspectRatio: false, indexAxis: 'y', plugins: { legend: { display: false }, tooltip: { backgroundColor: 'rgba(10,10,26,.94)', borderColor: 'rgba(229,9,20,.4)', borderWidth: 1, callbacks: { label: ctx => `Revenue: $${ctx.raw}M` } } }, scales: { x: { grid: { color: 'rgba(255,255,255,.04)' }, ticks: { callback: v => '$' + v + 'M' }, beginAtZero: true }, y: { grid: { display: false } } } }
    });
}

/* ═══════════════════════════════════════════════════════════════
   TOP MOVIES TABLE
   ═══════════════════════════════════════════════════════════════ */
function formatMoney(raw, m_rounded) {
    if (raw == null || raw === 0) return "N/A";
    if (raw >= 1000000) return `$${m_rounded}M`;
    if (raw >= 1000) return `$${Math.round(raw / 1000)}K`;
    return `$${raw}`;
}

async function loadTopMoviesTable() {
    try {
        const res = await fetch(`${API_BASE}/dashboard/api/?endpoint=top_movies&limit=10`);
        const json = await res.json();
        renderTopMoviesTable(json.data);
    } catch (e) { console.error("Top movies load failed:", e); }
}

function renderTopMoviesTable(movies) {
    const tbody = document.querySelector("#genreTableCard tbody");
    if (!tbody || !movies.length) return;

    tbody.innerHTML = movies.map((m, i) => {
        const trend = m.roi >= 3 ? `<span class="up">▲ ${m.roi}x</span>` : `<span>${m.roi}x</span>`;
        const thumb = m.poster
            ? `<img src="${m.poster}" style="width:28px;height:40px;object-fit:cover;border-radius:4px;flex-shrink:0;display:block;" alt="" onerror="this.style.display='none'">`
            : `<span style="width:28px;height:40px;border-radius:4px;background:rgba(229,9,20,.1);flex-shrink:0;display:inline-block;"></span>`;

        const b = (m.budget != null) ? formatMoney(m.budget, m.budget_m) : (m.budget_m ? `$${m.budget_m}M` : "N/A");
        const r = (m.revenue != null) ? formatMoney(m.revenue, m.revenue_m) : (m.revenue_m ? `$${m.revenue_m}M` : "N/A");

        return `<tr class="clickable-row" data-index="${i}">
          <td>${thumb}<span>${m.title}${m.year ? ` (${m.year})` : ""}</span></td>
          <td>${b}</td><td>${r}</td>
          <td>${trend}</td>
          <td class="${m.vote_average >= 7 ? "up" : ""}">⭐ ${m.vote_average}</td>
        </tr>`;
    }).join("");

    tbody.querySelectorAll(".clickable-row").forEach(row => {
        row.style.cursor = "pointer";
        row.addEventListener("click", () => showMovieModal(movies[row.dataset.index]));
    });
}

/* ═══════════════════════════════════════════════════════════════
   AUDIENCE RING
   ═══════════════════════════════════════════════════════════════ */
function initAudienceRing() {
    const ring = document.getElementById("audienceRing");
    if (!ring) return;
    const pctEl = document.getElementById("audiencePct");
    const pct = 85, circumference = 2 * Math.PI * 70;
    const svg = ring.closest("svg");
    const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    const grad = document.createElementNS("http://www.w3.org/2000/svg", "linearGradient");
    grad.setAttribute("id", "ringGrad"); grad.setAttribute("x1", "0"); grad.setAttribute("y1", "0"); grad.setAttribute("x2", "1"); grad.setAttribute("y2", "1");
    [["0", "#e50914"], ["1", "#ff3b30"]].forEach(([o, c]) => { const s = document.createElementNS("http://www.w3.org/2000/svg", "stop"); s.setAttribute("offset", o); s.setAttribute("stop-color", c); grad.append(s); });
    defs.append(grad); svg.prepend(defs);
    ring.style.stroke = "url(#ringGrad)";
    setTimeout(() => { ring.style.strokeDashoffset = circumference * (1 - pct / 100); }, 400);
    let cur = 0;
    const iv = setInterval(() => { if (pctEl) pctEl.textContent = ++cur + "%"; if (cur >= pct) clearInterval(iv); }, 18);
}

/* ═══════════════════════════════════════════════════════════════
   STUDIO SIMULATOR
   ═══════════════════════════════════════════════════════════════ */
function initSimulator() {
    const btn = document.getElementById("analyzePitchBtn");
    const result = document.getElementById("simResult");
    const textarea = document.getElementById("pitchInput");
    if (!btn) return;

    btn.addEventListener("click", async () => {
        const pitch = textarea.value.trim();
        if (!pitch || pitch.length < 10) {
            textarea.focus(); textarea.style.borderColor = "#ef4444";
            setTimeout(() => textarea.style.borderColor = "", 1500); return;
        }
        btn.innerHTML = '<span class="loader"></span> Analyzing...';
        btn.disabled = true; result.classList.add("hidden");
        try {
            const res = await fetch(`${API_BASE}/dashboard/api/?endpoint=simulate`, {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-CSRFToken": getCookie('csrftoken') },
                body: JSON.stringify({ pitch })
            });
            const json = await res.json();
            populateSimResult(json.data || mockSimulate());
            result.classList.remove("hidden");
        } catch (e) {
            console.error("Simulation error:", e);
            populateSimResult(mockSimulate()); result.classList.remove("hidden");
        } finally {
            btn.innerHTML = '<i data-lucide="zap"></i> Analyze Concept';
            btn.disabled = false; lucide.createIcons();
        }
    });
}

function populateSimResult(d) {
    document.querySelector(".sim-score strong").textContent = d.viability + "%";
    const metrics = document.querySelectorAll(".sim-metric-value");
    metrics[0].textContent = "$" + d.est_revenue_m + "M";
    metrics[1].textContent = d.est_roi + "x";
    metrics[2].textContent = d.risk;
    metrics[2].className = "sim-metric-value" + (d.risk === "High" ? " caution" : d.risk === "Medium" ? " warn" : " good");
    const genreBadge = document.querySelector(".sim-genre-badge");
    if (genreBadge) genreBadge.textContent = "Predicted Genre: " + d.predicted_genre;

    const simFilmsWrap = document.getElementById("simFilms");
    if (simFilmsWrap && d.similar_films && d.similar_films.length) {
        simFilmsWrap.innerHTML = d.similar_films.map((f, i) => {
            const genres = (f.genres || '').split("|").slice(0, 2).join(" · ");
            const posterHTML = f.poster
                ? `<img src="${f.poster}" alt="${f.title}" loading="lazy" onerror="this.style.display='none'">`
                : '';

            return `
            <div class="sim-film-card" data-index="${i}">
                <div class="sim-film-poster-wrap">
                    ${posterHTML}
                </div>
                <div class="sim-film-info">
                    <span class="sim-film-title">${f.title}${f.year ? ` (${f.year})` : ""}</span>
                    <span class="sim-film-meta">${genres}</span>
                    <div class="sim-film-match">
                        <i data-lucide="crosshair" style="width:10px;height:10px;"></i>
                        <span>${f.similarity}% Match</span>
                    </div>
                </div>
            </div>`;
        }).join("");

        simFilmsWrap.querySelectorAll(".sim-film-card").forEach(card => {
            card.addEventListener("click", () => showMovieModal(d.similar_films[card.dataset.index]));
        });
        simFilmsWrap.parentElement.classList.remove("hidden");
        lucide.createIcons();
    }
}

function mockSimulate() {
    return { viability: 79, risk: "Medium", predicted_genre: "Sci-Fi", est_revenue_m: 310, est_roi: 2.6, audience_match: 82, similar_films: [] };
}

/* ── Modal ───────────────────────────────────────────────────── */
function initModal() {
    const modal = document.getElementById("movieModal");
    const closeBtn = document.getElementById("closeModal");
    if (!modal || !closeBtn) return;
    closeBtn.addEventListener("click", hideMovieModal);
    modal.addEventListener("click", e => { if (e.target === modal) hideMovieModal(); });
    window.addEventListener("keydown", e => { if (e.key === "Escape" && !modal.classList.contains("hidden")) hideMovieModal(); });
}

function showMovieModal(m) {
    const modal = document.getElementById("movieModal");
    if (!modal || !m) return;

    const posterEl = document.getElementById("modalPoster");
    /* ✅ FIX: always reset src first so previous large image never flashes */
    posterEl.removeAttribute("src");
    posterEl.style.display = m.poster ? "block" : "none";
    if (m.poster) {
        posterEl.onerror = () => { posterEl.style.display = "none"; };
        posterEl.src = m.poster;
    }

    document.getElementById("modalTitle").textContent = m.title || "";
    document.getElementById("modalGenre").textContent = (m.genres || "").split("|").join(" · ");
    document.getElementById("modalYear").textContent = m.year || "";
    document.getElementById("modalOverview").textContent = m.overview || "No synopsis available.";

    document.getElementById("modalBudget").textContent = (m.budget != null) ? formatMoney(m.budget, m.budget_m) : (m.budget_m ? `$${m.budget_m}M` : "N/A");
    document.getElementById("modalRevenue").textContent = (m.revenue != null) ? formatMoney(m.revenue, m.revenue_m) : (m.revenue_m ? `$${m.revenue_m}M` : "N/A");

    document.getElementById("modalROI").textContent = m.roi ? `${m.roi}x` : "N/A";
    document.getElementById("modalRating").textContent = m.vote_average || "0.0";

    modal.classList.remove("hidden");
    document.body.style.overflow = "hidden";
    lucide.createIcons();
}

/* Normalise fields from movies-page API shape then hand off to showMovieModal */
function showMovieDetailModal(movie) {
    showMovieModal({
        ...movie,
        poster: movie.poster || movie.poster_url || "",
        budget_m: movie.budget ? Math.round(movie.budget / 1_000_000) : (movie.budget_m || 0),
        revenue_m: movie.revenue ? Math.round(movie.revenue / 1_000_000) : (movie.revenue_m || 0),
        roi: (movie.budget && movie.revenue && movie.budget > 0)
            ? (movie.revenue / movie.budget).toFixed(1) : (movie.roi || null),
        vote_average: movie.vote_average ? parseFloat(movie.vote_average).toFixed(1) : "0.0",
    });
}

function hideMovieModal() {
    const modal = document.getElementById("movieModal");
    if (modal) { modal.classList.add("hidden"); document.body.style.overflow = ""; }
}

/* ── Sidebar ─────────────────────────────────────────────────── */
function initSidebar() {
    document.querySelectorAll(".nav-item").forEach(item => {
        item.addEventListener("click", e => {
            if (!item.href || item.href.includes('#')) {
                e.preventDefault();
                const page = item.dataset.page;
                if (page) navigateTo(page);
            }
        });
    });
}

function initNavigation() {
    [["backToDash", "dashboard"], ["backToDashFromMovies", "dashboard"], ["backToDashFromStats", "dashboard"], ["backToDashFromStudio", "dashboard"]].forEach(([id, target]) => {
        const el = document.getElementById(id);
        if (el) el.addEventListener("click", () => navigateTo(target));
    });
}

async function navigateTo(view, genre = null) {
    document.querySelectorAll(".nav-item").forEach(n => n.classList.toggle("active", n.dataset.page === view));
    ["dashboard", "studio", "audience", "movies", "statistics"].forEach(v => {
        const el = document.getElementById(v + "View");
        if (el) el.classList.toggle("hidden", v !== view);
    });
    const titles = { dashboard: "Admin Dashboard", studio: "Movie Analyzer Studio", movies: "Movies Database", statistics: "Statistics & Analytics", audience: "Audience Analysis" };
    const pt = document.querySelector(".page-title");
    if (pt) pt.textContent = titles[view] || "Admin Dashboard";
    if (view === "audience") {
        const select = document.getElementById("audienceGenreSelect");
        if (!genre && select && select.value) genre = select.value;
        if (genre) await loadGenreAudience(genre);
    }
    else if (view === "movies") await loadMoviesPage();
    else if (view === "statistics") await loadStatisticsPage();
    else if (view === "studio") lucide.createIcons();
}

let audienceAgeChart, audienceGenderChart, audienceOccChart;

async function initAudiencePage() {
    const tabsContainer = document.getElementById("audienceGenreTabs");
    if (!tabsContainer) return;

    try {
        const res = await fetch(`${API_BASE}/dashboard/api/?endpoint=genre_stats`);
        const json = await res.json();
        const stats = json.data;
        if (stats && stats.length > 0) {
            const sorted = [...stats].sort((a, b) => b.count - a.count);
            const totalCount = stats.reduce((acc, s) => acc + s.count, 0);

            tabsContainer.innerHTML = `<button class="audience-genre-pill active" data-genre="All">All <span class="genre-count">${totalCount}</span></button>` +
                sorted.map(s => `<button class="audience-genre-pill" data-genre="${s.genre}">${s.genre} <span class="genre-count">${s.count}</span></button>`).join('');

            tabsContainer.querySelectorAll(".audience-genre-pill").forEach(pill => {
                pill.addEventListener("click", () => {
                    tabsContainer.querySelectorAll(".audience-genre-pill").forEach(p => p.classList.remove("active"));
                    pill.classList.add("active");
                    loadGenreAudience(pill.dataset.genre);
                });
            });

            // Initial load
            await loadGenreAudience("All");
        }
    } catch (e) { console.error("Failed to load genres for audience pills:", e); }
}

async function loadGenreAudience(genre) {
    const genreKey = genre === "All" ? "" : genre;
    const insight = document.getElementById("genreInsight");
    if (insight) insight.textContent = `Analyzing audience for ${genre}...`;

    // 1. Load Profile
    try {
        const res = await fetch(`${API_BASE}/admin/dashboard/api/?endpoint=audience_profile&genre=${encodeURIComponent(genreKey)}`);
        const json = await res.json();
        if (json.status === 'ok') renderAudienceCharts(json.data);
    } catch (e) { console.error("Audience profile fetch failed:", e); }

    // 2. Load Top Movies
    try {
        const res = await fetch(`${API_BASE}/admin/dashboard/api/?endpoint=top_movies&genre=${encodeURIComponent(genreKey)}&limit=10`);
        const json = await res.json();
        renderVanguardTable(json.data);
    } catch (e) { console.error("Genre movies fetch failed:", e); }
}

function renderAudienceCharts(data) {
    chartDefaults();

    // 1. Age & Gender (Grouped Horizontal Bar)
    const ageCtx = document.getElementById("ageGenderChart").getContext("2d");
    if (audienceAgeChart) audienceAgeChart.destroy();
    audienceAgeChart = new Chart(ageCtx, {
        type: 'bar',
        data: {
            labels: data.age.map(d => d.label),
            datasets: [
                { label: 'Female', data: data.age.map(d => d.female), backgroundColor: '#FF4B91', borderRadius: 2, barThickness: 8 },
                { label: 'Male', data: data.age.map(d => d.male), backgroundColor: '#4A90E2', borderRadius: 2, barThickness: 8 }
            ]
        },
        options: {
            indexAxis: 'y', responsive: true, maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 10, usePointStyle: true, color: '#9ca3af', padding: 20 } }
            },
            scales: {
                x: { grid: { color: 'rgba(255,255,255,.05)' }, ticks: { color: '#6b7280', font: { size: 10 } } },
                y: { grid: { display: false }, ticks: { color: '#9ca3af', font: { size: 11 } } }
            }
        }
    });

    // 2. Gender Ratio (Donut)
    const genCtx = document.getElementById("genderDonutChart").getContext("2d");
    if (audienceGenderChart) audienceGenderChart.destroy();
    audienceGenderChart = new Chart(genCtx, {
        type: 'doughnut',
        data: {
            labels: data.gender.map(d => d.label),
            datasets: [{
                data: data.gender.map(d => d.count),
                backgroundColor: ['#4A90E2', '#FF4B91'], // Male = Blue, Female = Pink
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false, cutout: '80%',
            plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 10, usePointStyle: true, color: '#9ca3af', padding: 20 } }
            }
        }
    });

    // 3. Top Occupations (Horizontal Bar)
    const occCtx = document.getElementById("occupationsChart").getContext("2d");
    if (audienceOccChart) audienceOccChart.destroy();
    audienceOccChart = new Chart(occCtx, {
        type: 'bar',
        data: {
            labels: data.occupation.map(d => d.label),
            datasets: [{
                data: data.occupation.map(d => d.count),
                backgroundColor: '#FF3B30',
                borderRadius: 2,
                barThickness: 12
            }]
        },
        options: {
            indexAxis: 'y', responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { color: 'rgba(255,255,255,.05)' }, ticks: { color: '#6b7280', font: { size: 10 } } },
                y: { grid: { display: false }, ticks: { color: '#9ca3af', font: { size: 11 } } }
            }
        }
    });

    const insight = document.getElementById("genreInsight");
    if (insight) insight.textContent = `Targeting a total of ${data.total_users.toLocaleString()} users across this segment.`;
}

function renderVanguardTable(movies) {
    const tbody = document.querySelector("#genreVanguardTable tbody");
    if (!tbody) return;
    tbody.innerHTML = movies.map((m, i) => `
        <tr class="clickable-row" data-index="${i}">
            <td class="movie-title-cell">${m.title}</td>
            <td style="color:#6b7280;">${m.year || ""}</td>
            <td class="up">${m.roi}x</td>
            <td style="color:#9ca3af;">$${m.revenue_m}M</td>
            <td class="${m.vote_average >= 7 ? 'up' : ''}">⭐ ${m.vote_average}</td>
        </tr>`).join("");
    tbody.querySelectorAll("tr.clickable-row").forEach(row => {
        row.style.cursor = "pointer";
        row.addEventListener("click", () => showMovieModal(movies[row.dataset.index]));
    });
}

/* ── Search & Quick Actions ──────────────────────────────────── */
function initSearch() {
    const globalSearch = document.getElementById("globalSearch");
    if (globalSearch) {
        globalSearch.addEventListener("keypress", async e => {
            if (e.key === "Enter") {
                const q = globalSearch.value.trim();
                if (q) { currentMoviesSearch = q; currentMoviesPage = 1; await navigateTo("movies"); const ms = document.getElementById("moviesSearch"); if (ms) ms.value = q; }
            }
        });
    }
    const map = {
        "quickStatsBtn": () => navigateTo("statistics"),
        "viewAllMoviesBtn": () => navigateTo("movies"),
        "viewStatsBtn": () => navigateTo("statistics"),
        "viewStudioBtn": () => navigateTo("studio"),
        "analyzeGenreBtn": async () => {
            try {
                const res = await fetch(`${API_BASE}/dashboard/api/?endpoint=genre_stats`);
                const json = await res.json();
                if (json.data?.length > 0) navigateTo("audience", [...json.data].sort((a, b) => b.avg_roi - a.avg_roi)[0].genre);
            } catch (e) { console.error(e); }
        }
    };
    Object.entries(map).forEach(([id, fn]) => { const el = document.getElementById(id); if (el) el.addEventListener("click", fn); });
}

/* ═══════════════════════════════════════════════════════════════
   MOVIES PAGE
   ═══════════════════════════════════════════════════════════════ */
let currentMoviesPage = 1, currentMoviesSearch = '', currentMoviesGenre = '';

function initMoviesPage() {
    const searchInput = document.getElementById("moviesSearch");
    const genreFilter = document.getElementById("moviesGenreFilter");
    const prevBtn = document.getElementById("prevPage");
    const nextBtn = document.getElementById("nextPage");
    if (searchInput) { let t; searchInput.addEventListener("input", e => { clearTimeout(t); t = setTimeout(() => { currentMoviesSearch = e.target.value.trim(); currentMoviesPage = 1; loadMoviesPage(); }, 500); }); }
    if (genreFilter) genreFilter.addEventListener("change", e => { currentMoviesGenre = e.target.value; currentMoviesPage = 1; loadMoviesPage(); });
    if (prevBtn) prevBtn.addEventListener("click", () => { if (currentMoviesPage > 1) { currentMoviesPage--; loadMoviesPage(); } });
    if (nextBtn) nextBtn.addEventListener("click", () => { currentMoviesPage++; loadMoviesPage(); });
}

async function loadMoviesPage() {
    const grid = document.getElementById("moviesGrid");
    const pagination = document.getElementById("moviesPagination");
    const pageInfo = document.getElementById("pageInfo");
    const prevBtn = document.getElementById("prevPage");
    const nextBtn = document.getElementById("nextPage");
    const countEl = document.getElementById("moviesCount");
    if (!grid) return;

    grid.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-muted);">Loading movies...</div>';

    try {
        let url = `${API_BASE}/dashboard/movies/?page=${currentMoviesPage}`;
        if (currentMoviesSearch) url += `&search=${encodeURIComponent(currentMoviesSearch)}`;
        if (currentMoviesGenre) url += `&genre=${encodeURIComponent(currentMoviesGenre)}`;

        const res = await fetch(url);
        const data = await res.json();

        if (data.movies && data.movies.length > 0) {
            grid.innerHTML = data.movies.map((movie, i) => {
                const poster = movie.poster || movie.poster_url || '';
                const genres = (movie.genres || '').split('|').slice(0, 3).join(' · ');
                const rating = movie.vote_average ? `⭐ ${parseFloat(movie.vote_average).toFixed(1)}` : '';

                /* ✅ KEY FIX: img lives INSIDE .movie-card-poster wrapper div.
                   The wrapper has aspect-ratio:2/3 + overflow:hidden in CSS.
                   The img fills that box via width/height:100% + object-fit:cover.
                   NEVER give the img the class "movie-card-poster" directly. */
                const posterHTML = poster
                    ? `<div class="movie-card-poster">
                         <img src="${poster}" alt="${movie.title}" loading="lazy"
                              onerror="this.parentElement.style.background='rgba(229,9,20,.08)'">
                       </div>`
                    : `<div class="movie-card-poster movie-card-poster-placeholder"></div>`;

                return `<div class="movie-card" data-index="${i}">
                    ${posterHTML}
                    <div class="movie-card-body">
                        <h3 class="movie-card-title">${movie.title}</h3>
                        <p class="movie-card-genres">${genres}</p>
                        ${rating ? `<span class="movie-card-rating">${rating}</span>` : ''}
                    </div>
                </div>`;
            }).join('');

            grid.querySelectorAll('.movie-card').forEach((card, i) => {
                card.addEventListener('click', () => showMovieDetailModal(data.movies[i]));
            });

            if (countEl) countEl.textContent = `Total: ${data.total}`;
            if (pagination) {
                pagination.style.display = 'flex';
                if (pageInfo) pageInfo.textContent = `Page ${currentMoviesPage}`;
                if (prevBtn) prevBtn.disabled = currentMoviesPage <= 1;
                if (nextBtn) nextBtn.disabled = !data.has_more;
            }
        } else {
            grid.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-muted);">No movies found.</div>';
            if (pagination) pagination.style.display = 'none';
        }
        lucide.createIcons();
    } catch (e) {
        console.error("Movies load failed:", e);
        grid.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-muted);">Failed to load movies.</div>';
    }
}

/* ═══════════════════════════════════════════════════════════════
   STATISTICS PAGE
   ═══════════════════════════════════════════════════════════════ */
let genreDistChart, genreRevenueChart;
function initStatisticsPage() { }
function initStudioPage() { }

async function loadStatisticsPage() { await Promise.all([loadStatsKPIs(), loadStatsCharts()]); }

async function loadStatsKPIs() {
    try {
        const res = await fetch(`${API_BASE}/dashboard/api/?endpoint=kpis`);
        const json = await res.json(), d = json.data;
        document.getElementById("statsMovieCount").textContent = d.total_movies || 0;
        document.getElementById("statsRevenue").textContent = `$${d.total_revenue_b || 0}B`;
        document.getElementById("statsROI").textContent = `${d.avg_roi || 0}x`;
        document.getElementById("statsRating").textContent = (d.avg_rating || 0).toFixed(1);
    } catch (e) { console.error("Stats KPIs load failed:", e); }
}

async function loadStatsCharts() {
    try {
        const res = await fetch(`${API_BASE}/dashboard/api/?endpoint=genre_stats`);
        const json = await res.json(), stats = json.data;
        renderGenreDistChart(stats); renderGenreRevenueChart(stats); renderGenreStatsTable(stats);
    } catch (e) { console.error("Stats charts load failed:", e); }
}

function renderGenreDistChart(stats) {
    const ctx = document.getElementById("genreDistChart"); if (!ctx) return;
    const sorted = [...stats].sort((a, b) => b.count - a.count).slice(0, 10);
    const labels = sorted.map(d => d.genre), colors = labels.map(g => colorFor(g).border);
    if (genreDistChart) genreDistChart.destroy();
    genreDistChart = new Chart(ctx, { type: 'doughnut', data: { labels, datasets: [{ data: sorted.map(d => d.count), backgroundColor: colors.map(c => c + 'b3'), borderColor: colors, borderWidth: 2 }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { boxWidth: 12, padding: 10 } }, tooltip: { backgroundColor: 'rgba(10,10,26,.94)', borderColor: 'rgba(229,9,20,.4)', borderWidth: 1, callbacks: { label: ctx => `${ctx.label}: ${ctx.raw} movies` } } } } });
}

function renderGenreRevenueChart(stats) {
    const ctx = document.getElementById("genreRevenueChart"); if (!ctx) return;
    const sorted = [...stats].sort((a, b) => b.avg_revenue - a.avg_revenue).slice(0, 10);
    const labels = sorted.map(d => d.genre), colors = labels.map(g => colorFor(g).border);
    if (genreRevenueChart) genreRevenueChart.destroy();
    genreRevenueChart = new Chart(ctx, { type: 'bar', data: { labels, datasets: [{ label: 'Avg Revenue ($M)', data: sorted.map(d => d.avg_revenue), backgroundColor: colors.map(c => c + 'b3'), borderColor: colors, borderWidth: 1.5, borderRadius: 6 }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { backgroundColor: 'rgba(10,10,26,.94)', borderColor: 'rgba(229,9,20,.4)', borderWidth: 1, callbacks: { label: ctx => `Revenue: $${ctx.raw}M` } } }, scales: { x: { grid: { display: false } }, y: { grid: { color: 'rgba(255,255,255,.04)' }, ticks: { callback: v => '$' + v + 'M' }, beginAtZero: true } } } });
}

function renderGenreStatsTable(stats) {
    const tbody = document.querySelector("#statsGenreTable tbody"); if (!tbody) return;
    tbody.innerHTML = [...stats].sort((a, b) => b.avg_roi - a.avg_roi).map(s => `
        <tr><td><strong>${s.genre}</strong></td><td>${s.count}</td><td>$${s.avg_budget}M</td><td>$${s.avg_revenue}M</td><td class="${s.avg_roi >= 3 ? 'up' : ''}">${s.avg_roi}x</td></tr>`).join('');
}

/* ── Helpers ─────────────────────────────────────────────────── */
function getCookie(name) {
    const found = (document.cookie || '').split(';').map(c => c.trim()).find(c => c.startsWith(name + '='));
    return found ? decodeURIComponent(found.split('=')[1]) : null;
}

const DEMO_GENRE_STATS = [
    { genre: "Horror", avg_budget: 18, avg_revenue: 96, avg_roi: 5.3, count: 150 },
    { genre: "Animation", avg_budget: 95, avg_revenue: 410, avg_roi: 4.3, count: 200 },
    { genre: "Sci-Fi", avg_budget: 142, avg_revenue: 485, avg_roi: 3.4, count: 180 },
    { genre: "Comedy", avg_budget: 42, avg_revenue: 135, avg_roi: 3.2, count: 300 },
    { genre: "Action", avg_budget: 165, avg_revenue: 520, avg_roi: 3.2, count: 350 },
    { genre: "Drama", avg_budget: 38, avg_revenue: 112, avg_roi: 2.9, count: 400 },
];