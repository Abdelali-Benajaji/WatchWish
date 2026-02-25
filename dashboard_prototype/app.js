/* ═══════════════════════════════════════════════════════════════
   WatchWish Studio — App Logic (with real backend API)
   ═══════════════════════════════════════════════════════════════ */

const API_BASE = "http://127.0.0.1:5000/api";

document.addEventListener('DOMContentLoaded', async () => {
    lucide.createIcons();

    initSidebar();
    initChartSwitcher();
    initSimulator();
    initModal();
    initNavigation();

    // Try to load real data; fallback to demo data and poll if backend is not up
    let isBackendAlive = await checkBackend();
    if (isBackendAlive) {
        await loadRealData();
    } else {
        console.warn("Serveur indisponible — utilisation des données démo. Tentative de connexion...");
        initDemoKPIs();
        initDemoCharts();
        initDemoTable();

        // Start polling
        const pollInterval = setInterval(async () => {
            isBackendAlive = await checkBackend();
            if (isBackendAlive) {
                console.log("Serveur connecté ! Chargement des données réelles...");
                clearInterval(pollInterval);
                await loadRealData();
            }
        }, 10000); // Check every 10 seconds
    }

    initAudienceRing();
});

async function loadRealData() {
    await Promise.all([loadKPIs(), loadCharts(), loadTopMoviesTable()]);
}

/* ── Backend health check ─────────────────────────────────────── */
async function checkBackend() {
    try {
        const r = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(2000) });
        return r.ok;
    } catch { return false; }
}

/* ═══════════════════════════════════════════════════════════════
   KPIs
   ═══════════════════════════════════════════════════════════════ */
async function loadKPIs() {
    try {
        const res = await fetch(`${API_BASE}/kpis`);
        const json = await res.json();
        const d = json.data;
        animateCounter(".kpi-movies", d.total_movies, 0, "");
        animateCounter(".kpi-revenue", d.total_revenue_b, 1, "B", "$");
        animateCounter(".kpi-roi", d.avg_roi, 1, "x");
        animateCounter(".kpi-rating", d.avg_rating, 1, "/10");
    } catch (e) { console.error("KPI load failed:", e); }
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
    const duration = 1400;
    const start = performance.now();
    const tick = (now) => {
        const p = Math.min((now - start) / duration, 1);
        const ease = 1 - Math.pow(1 - p, 3);
        const val = target * ease;
        el.textContent = prefix + val.toFixed(decimals) + suffix;
        if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
}

/* ═══════════════════════════════════════════════════════════════
   CHARTS
   ═══════════════════════════════════════════════════════════════ */
let barChart, scatterChart;

const PALETTE = {
    "Action": { bg: "rgba(59,130,246,.7)", border: "#3b82f6" },
    "Adventure": { bg: "rgba(99,102,241,.7)", border: "#6366f1" },
    "Animation": { bg: "rgba(6,182,212,.7)", border: "#06b6d4" },
    "Comedy": { bg: "rgba(34,197,94,.7)", border: "#22c55e" },
    "Crime": { bg: "rgba(249,115,22,.7)", border: "#f97316" },
    "Documentary": { bg: "rgba(161,161,170,.7)", border: "#a1a1aa" },
    "Drama": { bg: "rgba(236,72,153,.7)", border: "#ec4899" },
    "Fantasy": { bg: "rgba(167,139,250,.7)", border: "#a78bfa" },
    "Horror": { bg: "rgba(239,68,68,.7)", border: "#ef4444" },
    "Musical": { bg: "rgba(251,191,36,.7)", border: "#fbbf24" },
    "Mystery": { bg: "rgba(20,184,166,.7)", border: "#14b8a6" },
    "Romance": { bg: "rgba(244,63,94,.7)", border: "#f43f5e" },
    "Sci-Fi": { bg: "rgba(168,85,247,.7)", border: "#a855f7" },
    "Thriller": { bg: "rgba(234,179,8,.7)", border: "#eab308" },
    "War": { bg: "rgba(132,204,22,.7)", border: "#84cc16" },
    "Western": { bg: "rgba(180,83,9,.7)", border: "#b45309" },
};

function colorFor(genre) {
    return PALETTE[genre] || { bg: "rgba(139,92,246,.7)", border: "#8b5cf6" };
}

function chartDefaults() {
    Chart.defaults.color = "#8b8ba7";
    Chart.defaults.borderColor = "rgba(255,255,255,.06)";
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.size = 11;
}

async function loadCharts() {
    try {
        const res = await fetch(`${API_BASE}/stats`);
        const json = await res.json();
        renderCharts(json.data);
    } catch (e) {
        console.error("Stats load failed:", e);
        renderCharts(DEMO_GENRE_STATS);
    }
}

function initDemoCharts() { renderCharts(DEMO_GENRE_STATS); }

function renderCharts(stats) {
    chartDefaults();

    // Sort by ROI descending, take top 12
    const sorted = [...stats].sort((a, b) => b.avg_roi - a.avg_roi).slice(0, 12);
    const labels = sorted.map(d => d.genre);
    const rois = sorted.map(d => d.avg_roi);
    const budgets = sorted.map(d => d.avg_budget);
    const revenues = sorted.map(d => d.avg_revenue);
    const bgs = labels.map(g => colorFor(g).bg);
    const borders = labels.map(g => colorFor(g).border);

    const barCtx = document.getElementById("roiBarChart").getContext("2d");

    // Gradient fills
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
            labels,
            datasets: [
                {
                    label: "ROI (x)",
                    data: rois,
                    backgroundColor: grads,
                    borderColor: borders,
                    borderWidth: 1.5,
                    borderRadius: 6,
                    barPercentage: .6,
                    yAxisID: "y"
                },
                {
                    label: "Budget moyen ($M)",
                    data: budgets,
                    backgroundColor: "rgba(255,255,255,.06)",
                    borderColor: "rgba(255,255,255,.12)",
                    borderWidth: 1,
                    borderRadius: 6,
                    barPercentage: .6,
                    yAxisID: "y1"
                }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            interaction: { mode: "index", intersect: false },
            animation: { duration: 900, easing: "easeOutQuart" },
            plugins: {
                legend: { position: "top", align: "end", labels: { boxWidth: 10, usePointStyle: true, padding: 14 } },
                tooltip: {
                    backgroundColor: "rgba(10,10,26,.94)",
                    borderColor: "rgba(168,85,247,.3)", borderWidth: 1,
                    cornerRadius: 10, padding: 12, titleFont: { weight: 600 },
                    callbacks: {
                        label: ctx => ctx.dataset.label.startsWith("ROI")
                            ? `ROI : ${ctx.raw}x`
                            : `Budget : $${ctx.raw}M`
                    }
                }
            },
            scales: {
                x: { grid: { display: false }, ticks: { padding: 6 } },
                y: {
                    position: "left",
                    title: { display: true, text: "ROI (x)" },
                    grid: { color: "rgba(255,255,255,.04)" },
                    ticks: { callback: v => v + "x" },
                    beginAtZero: true
                },
                y1: {
                    position: "right",
                    title: { display: true, text: "Budget moyen ($M)" },
                    grid: { drawOnChartArea: false },
                    ticks: { callback: v => "$" + v + "M" },
                    beginAtZero: true
                }
            },
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    const index = elements[0].index;
                    const genre = barChart.data.labels[index];
                    navigateTo('audience', genre);
                }
            }
        }
    });

    // ── Scatter / Bubble ──────────────────────────────────────────
    const scatterCtx = document.getElementById("roiScatterChart").getContext("2d");
    if (scatterChart) scatterChart.destroy();
    scatterChart = new Chart(scatterCtx, {
        type: "bubble",
        data: {
            datasets: sorted.map((d, i) => ({
                label: d.genre,
                data: [{ x: d.avg_budget, y: d.avg_roi, r: Math.max(6, d.avg_revenue / 60) }],
                backgroundColor: bgs[i],
                borderColor: borders[i],
                borderWidth: 1.5
            }))
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            animation: { duration: 1100, easing: "easeOutQuart" },
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    const datasetIndex = elements[0].datasetIndex;
                    const genre = scatterChart.data.datasets[datasetIndex].label;
                    navigateTo('audience', genre);
                }
            },
            plugins: {
                legend: { position: "top", align: "end", labels: { boxWidth: 10, usePointStyle: true, padding: 14 } },
                tooltip: {
                    backgroundColor: "rgba(10,10,26,.94)",
                    borderColor: "rgba(168,85,247,.3)", borderWidth: 1,
                    cornerRadius: 10, padding: 12, titleFont: { weight: 600 },
                    callbacks: {
                        title: ctx => ctx[0].dataset.label,
                        label: ctx => [
                            `Budget : $${ctx.raw.x}M`,
                            `ROI : ${ctx.raw.y}x`,
                            `Revenus : $${Math.round(ctx.raw.r * 60)}M`
                        ]
                    }
                }
            },
            scales: {
                x: {
                    title: { display: true, text: "Budget de production moyen ($M)" },
                    grid: { color: "rgba(255,255,255,.04)" },
                    ticks: { callback: v => "$" + v + "M" }
                },
                y: {
                    title: { display: true, text: "ROI (x)" },
                    grid: { color: "rgba(255,255,255,.04)" },
                    ticks: { callback: v => v + "x" },
                    beginAtZero: true
                }
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

/* ═══════════════════════════════════════════════════════════════
   TOP MOVIES TABLE (real data)
   ═══════════════════════════════════════════════════════════════ */
async function loadTopMoviesTable() {
    try {
        const res = await fetch(`${API_BASE}/movies/top?limit=10`);
        const json = await res.json();
        renderTopMoviesTable(json.data);
    } catch (e) { console.error("Top movies load failed:", e); }
}

function renderTopMoviesTable(movies) {
    const tbody = document.querySelector("#genreTableCard tbody");
    if (!tbody || !movies.length) return;
    tbody.innerHTML = movies.map((m, i) => {
        const genre = (m.genres || "").split("|")[0];
        const color = colorFor(genre).border;
        const trend = m.roi >= 3 ? `<span class="up">▲ ${m.roi}x</span>` : `<span>${m.roi}x</span>`;
        const poster = m.poster ? `<img src="${m.poster}" class="movie-thumb" alt="">` : "";
        return `<tr class="clickable-row" data-index="${i}">
          <td>${poster}<span>${m.title}${m.year ? ` (${m.year})` : ""}</span></td>
          <td>$${m.budget_m}M</td>
          <td>$${m.revenue_m}M</td>
          <td>${trend}</td>
          <td class="${m.vote_average >= 7 ? "up" : ""}">⭐ ${m.vote_average}</td>
        </tr>`;
    }).join("");

    // Add click listeners to rows
    tbody.querySelectorAll(".clickable-row").forEach(row => {
        row.style.cursor = "pointer";
        row.addEventListener("click", () => {
            const movie = movies[row.dataset.index];
            showMovieModal(movie);
        });
    });
}

function initDemoTable() {
    // demo table already rendered in HTML
}

/* ═══════════════════════════════════════════════════════════════
   AUDIENCE RING
   ═══════════════════════════════════════════════════════════════ */
function initAudienceRing() {
    const ring = document.getElementById("audienceRing");
    const pctEl = document.getElementById("audiencePct");
    const pct = 85;
    const circumference = 2 * Math.PI * 70;

    // Add SVG gradient
    const svg = ring.closest("svg");
    const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    const grad = document.createElementNS("http://www.w3.org/2000/svg", "linearGradient");
    grad.setAttribute("id", "ringGrad");
    grad.setAttribute("x1", "0"); grad.setAttribute("y1", "0");
    grad.setAttribute("x2", "1"); grad.setAttribute("y2", "1");
    [["0", "#a855f7"], ["1", "#06b6d4"]].forEach(([offset, color]) => {
        const s = document.createElementNS("http://www.w3.org/2000/svg", "stop");
        s.setAttribute("offset", offset); s.setAttribute("stop-color", color);
        grad.append(s);
    });
    defs.append(grad); svg.prepend(defs);
    ring.style.stroke = "url(#ringGrad)";

    setTimeout(() => {
        ring.style.strokeDashoffset = circumference * (1 - pct / 100);
    }, 400);

    let cur = 0;
    const iv = setInterval(() => {
        pctEl.textContent = ++cur + "%";
        if (cur >= pct) clearInterval(iv);
    }, 18);
}

/* ═══════════════════════════════════════════════════════════════
   STUDIO SIMULATOR
   ═══════════════════════════════════════════════════════════════ */
function initSimulator() {
    const btn = document.getElementById("analyzePitchBtn");
    const result = document.getElementById("simResult");
    const textarea = document.getElementById("pitchInput");

    btn.addEventListener("click", async () => {
        const pitch = textarea.value.trim();
        if (!pitch || pitch.length < 10) {
            textarea.focus();
            textarea.style.borderColor = "#ef4444";
            setTimeout(() => textarea.style.borderColor = "", 1500);
            return;
        }

        // Loading state
        btn.innerHTML = '<span class="loader"></span> Analyse en cours...';
        btn.disabled = true;
        result.classList.add("hidden");

        try {
            const isAlive = await checkBackend();
            let data;

            if (isAlive) {
                const res = await fetch(`${API_BASE}/simulate`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        pitch,
                        genre: document.getElementById("genreSelect").value,
                        budget_tier: document.getElementById("budgetSelect").value
                    })
                });
                const json = await res.json();
                data = json.data;
            } else {
                // Fallback mock
                await new Promise(r => setTimeout(r, 1200));
                data = mockSimulate();
            }

            populateSimResult(data);
            result.classList.remove("hidden");
        } catch (e) {
            console.error("Simulation error:", e);
        } finally {
            btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg> Analyser le Pitch';
            btn.disabled = false;
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

    // Genre badge
    const genreBadge = document.querySelector(".sim-genre-badge");
    if (genreBadge) genreBadge.textContent = "Genre prédit : " + d.predicted_genre;

    // Audience match update
    const pctEl = document.getElementById("audiencePct");
    if (pctEl && d.audience_match) {
        const ring = document.getElementById("audienceRing");
        const circumference = 2 * Math.PI * 70;
        const pct = d.audience_match;
        ring.style.transition = "stroke-dashoffset 1.2s cubic-bezier(.4,0,.2,1)";
        ring.style.strokeDashoffset = circumference * (1 - pct / 100);
        animateCounter("#audiencePct", pct, 0, "%");
    }

    // Similar films
    const simFilmsWrap = document.getElementById("simFilms");
    if (simFilmsWrap && d.similar_films && d.similar_films.length) {
        simFilmsWrap.innerHTML = d.similar_films.map((f, i) => `
          <div class="sim-film-card" data-index="${i}">
            ${f.poster ? `<img src="${f.poster}" alt="${f.title}" class="sim-film-poster">` : '<div class="sim-film-poster-placeholder"></div>'}
            <div class="sim-film-info">
              <span class="sim-film-title">${f.title}${f.year ? ` (${f.year})` : ""}</span>
              <span class="sim-film-meta">${f.genres.split("|").slice(0, 2).join(" · ")}</span>
              ${f.revenue_m ? `<span class="sim-film-revenue">$${f.revenue_m}M recettes · ${f.similarity}% de correspondance</span>` : `<span class="sim-film-revenue">${f.similarity}% de correspondance</span>`}
            </div>
          </div>
        `).join("");

        // Add click listeners to cards
        simFilmsWrap.querySelectorAll(".sim-film-card").forEach(card => {
            card.addEventListener("click", () => {
                const movie = d.similar_films[card.dataset.index];
                showMovieModal(movie);
            });
        });

        simFilmsWrap.parentElement.classList.remove("hidden");
    }
}

function mockSimulate() {
    return {
        viability: 79, risk: "Medium", predicted_genre: "Sci-Fi",
        est_revenue_m: 310, est_roi: 2.6, audience_match: 82,
        similar_films: []
    };
}

/* ── Modal Logic ────────────────────────────────────────────── */
function initModal() {
    const modal = document.getElementById("movieModal");
    const closeBtn = document.getElementById("closeModal");

    if (!modal || !closeBtn) return;

    closeBtn.addEventListener("click", hideMovieModal);
    modal.addEventListener("click", (e) => {
        if (e.target === modal) hideMovieModal();
    });

    // ESC key to close
    window.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && !modal.classList.contains("hidden")) hideMovieModal();
    });
}

function showMovieModal(m) {
    const modal = document.getElementById("movieModal");
    if (!modal) return;

    document.getElementById("modalPoster").src = m.poster || "";
    document.getElementById("modalTitle").textContent = m.title;
    document.getElementById("modalGenre").textContent = (m.genres || "").split("|").join(" · ");
    document.getElementById("modalYear").textContent = m.year || "";
    document.getElementById("modalOverview").textContent = m.overview || "Aucun synopsis disponible pour ce titre.";

    document.getElementById("modalBudget").textContent = m.budget_m ? `$${m.budget_m}M` : "N/A";
    document.getElementById("modalRevenue").textContent = m.revenue_m ? `$${m.revenue_m}M` : "N/A";
    document.getElementById("modalROI").textContent = m.roi ? `${m.roi}x` : "N/A";
    document.getElementById("modalRating").textContent = m.vote_average || "0.0";

    modal.classList.remove("hidden");
    document.body.style.overflow = "hidden"; // Prevent background scroll
}

function hideMovieModal() {
    const modal = document.getElementById("movieModal");
    if (modal) {
        modal.classList.add("hidden");
        document.body.style.overflow = "";
    }
}

/* ── Sidebar ─────────────────────────────────────────────────── */
function initSidebar() {
    document.querySelectorAll(".nav-item").forEach(item => {
        item.addEventListener("click", e => {
            e.preventDefault();
            const page = item.dataset.page;
            if (page) navigateTo(page);
        });
    });
}

function initNavigation() {
    document.getElementById("backToDash").addEventListener("click", () => navigateTo("dashboard"));
}

async function navigateTo(view, genre = null) {
    document.querySelectorAll(".nav-item").forEach(n => {
        n.classList.toggle("active", n.dataset.page === view);
    });

    document.getElementById("dashboardView").classList.toggle("hidden", view !== "dashboard");
    document.getElementById("audienceView").classList.toggle("hidden", view !== "audience");

    if (view === "audience" && genre) {
        loadGenreAudience(genre);
    }
}

async function loadGenreAudience(genre) {
    const title = document.getElementById("audienceGenreTitle");
    title.textContent = genre;

    // Smooth transition
    const grid = document.querySelector(".audience-grid");
    grid.style.opacity = "0";
    setTimeout(() => grid.style.opacity = "1", 200);

    // Fetch genre stats from current state (already loaded in DEMO_GENRE_STATS or real stats)
    const allStats = await fetch(`${API_BASE}/stats`).then(r => r.json()).catch(() => ({ data: [] }));
    const stats = allStats.status === "ok" ? allStats.data.find(s => s.genre === genre) : null;

    if (stats) {
        document.getElementById("genreAvgRoi").textContent = stats.avg_roi + "x";
        document.getElementById("genreAvgBudget").textContent = "$" + stats.avg_budget + "M";

        // Compute "market share" based on count Proportion
        const totalCount = allStats.data.reduce((acc, s) => acc + s.count, 0);
        const share = Math.round((stats.count / totalCount) * 100);
        document.getElementById("genreMarketShare").textContent = share + "%";
    }

    // Fetch top 10 for this genre
    try {
        const res = await fetch(`${API_BASE}/movies/top?genre=${encodeURIComponent(genre)}&limit=10`);
        const json = await res.json();
        renderVanguardTable(json.data);
    } catch (e) { console.error("Genre movies load failed:", e); }

    // Simulate demographic update
    const bars = document.querySelectorAll(".demo-fill");
    bars.forEach(b => b.style.width = "0%");
    setTimeout(() => {
        bars[0].style.width = (70 + Math.random() * 20) + "%";
        bars[1].style.width = (80 + Math.random() * 15) + "%";
        bars[2].style.width = (40 + Math.random() * 30) + "%";
    }, 500);
}

function renderVanguardTable(movies) {
    const tbody = document.querySelector("#genreVanguardTable tbody");
    if (!tbody) return;
    tbody.innerHTML = movies.map((m, i) => `
        <tr class="clickable-row">
            <td>${m.title}</td>
            <td>${m.year || ""}</td>
            <td class="up">${m.roi}x</td>
            <td>$${m.revenue_m}M</td>
            <td>⭐ ${m.vote_average}</td>
        </tr>
    `).join("");

    tbody.querySelectorAll("tr").forEach((row, i) => {
        row.style.cursor = "pointer";
        row.addEventListener("click", () => showMovieModal(movies[i]));
    });
}

/* ── Demo data (fallback) ─────────────────────────────────────── */
const DEMO_GENRE_STATS = [
    { genre: "Horror", avg_budget: 18, avg_revenue: 96, avg_roi: 5.3 },
    { genre: "Animation", avg_budget: 95, avg_revenue: 410, avg_roi: 4.3 },
    { genre: "Sci-Fi", avg_budget: 142, avg_revenue: 485, avg_roi: 3.4 },
    { genre: "Comedy", avg_budget: 42, avg_revenue: 135, avg_roi: 3.2 },
    { genre: "Action", avg_budget: 165, avg_revenue: 520, avg_roi: 3.2 },
    { genre: "Drama", avg_budget: 38, avg_revenue: 112, avg_roi: 2.9 },
];

/* ── Loader CSS ──────────────────────────────────────────────── */
const _style = document.createElement("style");
_style.textContent = `
.loader { width:14px;height:14px;border:2px solid rgba(255,255,255,.3);border-top-color:#fff;border-radius:50%;animation:spin .6s linear infinite;display:inline-block; }
@keyframes spin { to { transform:rotate(360deg); } }

.sim-metric-value.warn { color: var(--orange); }
.sim-metric-value.good { color: var(--green); }

/* Similar films row */
.sim-films-section { margin-top:18px; }
.sim-films-label { font-size:.72rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.5px;margin-bottom:10px;font-weight:600; }
.sim-films-list { display:flex;flex-direction:column;gap:8px; }
.sim-film-card { display:flex;align-items:center;gap:12px;padding:10px 12px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.05);border-radius:10px;transition:background .2s; }
.sim-film-card:hover { background:rgba(255,255,255,.06); }
.sim-film-poster { width:38px;height:54px;object-fit:cover;border-radius:5px;flex-shrink:0; }
.sim-film-poster-placeholder { width:38px;height:54px;background:rgba(255,255,255,.06);border-radius:5px;flex-shrink:0; }
.sim-film-info { display:flex;flex-direction:column;gap:2px; }
.sim-film-title { font-size:.8rem;font-weight:600;color:var(--text-primary); }
.sim-film-meta  { font-size:.7rem;color:var(--text-muted); }
.sim-film-revenue { font-size:.7rem;color:var(--cyan);font-weight:500; }

/* Top movies table */
.movie-thumb { width:30px;height:42px;object-fit:cover;border-radius:4px;flex-shrink:0; }
#genreTableCard td:first-child { display:flex;align-items:center;gap:10px; }

/* Audience counter target */
#audiencePct { cursor:default; }
`;
document.head.appendChild(_style);
