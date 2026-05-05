/* ══════════════════════════════════════════════════
   AnomalyAI — dashboard.js
   Handles: drag-drop upload, charts, accordion, UI FX
══════════════════════════════════════════════════ */

/* ─ Drag-and-drop upload ────────────────────────── */
(function initUpload() {
  const zone = document.querySelector('.upload-zone');
  const input = document.getElementById('fileInput');
  const nameDisplay = document.getElementById('fileName');

  if (!zone) return;

  zone.addEventListener('click', () => input.click());

  zone.addEventListener('dragover', e => {
    e.preventDefault();
    zone.classList.add('drag-over');
  });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) attachFile(file);
  });

  input.addEventListener('change', () => {
    if (input.files[0]) attachFile(input.files[0]);
  });

  function attachFile(file) {
    if (!file.name.endsWith('.csv')) {
      showToast('Only CSV files are supported.', 'danger');
      return;
    }
    // Assign to the form input
    const dt = new DataTransfer();
    dt.items.add(file);
    input.files = dt.files;
    if (nameDisplay) nameDisplay.textContent = `📄 ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    zone.classList.add('selected');
  }
})();


/* ─ Contamination range slider ──────────────────── */
(function initSlider() {
  const slider = document.getElementById('contamination');
  const display = document.getElementById('contamValue');
  if (!slider) return;
  display.textContent = parseFloat(slider.value).toFixed(2);
  slider.addEventListener('input', () => {
    display.textContent = parseFloat(slider.value).toFixed(2);
  });
})();


/* ─ Checkbox items highlight ────────────────────── */
document.querySelectorAll('.checkbox-item input[type="checkbox"]').forEach(cb => {
  const parent = cb.closest('.checkbox-item');
  cb.addEventListener('change', () => {
    parent.classList.toggle('checked', cb.checked);
  });
  if (cb.checked) parent.classList.add('checked');
});


/* ─ Loading overlay on form submit ──────────────── */
(function initLoading() {
  const form = document.getElementById('detectionForm');
  const overlay = document.getElementById('loadingOverlay');
  if (!form || !overlay) return;
  form.addEventListener('submit', () => {
    overlay.classList.add('active');
  });
})();


/* ─ Accordion ────────────────────────────────────── */
document.querySelectorAll('.acc-header').forEach(header => {
  header.addEventListener('click', () => {
    const item = header.closest('.acc-item');
    const isOpen = item.classList.contains('open');
    // Close all
    document.querySelectorAll('.acc-item').forEach(i => i.classList.remove('open'));
    if (!isOpen) item.classList.add('open');
  });
});


/* ─ Toast notification ───────────────────────────── */
function showToast(msg, type = 'info') {
  const existing = document.getElementById('toastContainer');
  const container = existing || (() => {
    const c = document.createElement('div');
    c.id = 'toastContainer';
    c.style.cssText = 'position:fixed;bottom:1.5rem;right:1.5rem;z-index:9999;display:flex;flex-direction:column;gap:8px;';
    document.body.appendChild(c);
    return c;
  })();

  const colors = { success: '#34d399', danger: '#fb7185', warning: '#fbbf24', info: '#38bdf8' };
  const toast = document.createElement('div');
  toast.style.cssText = `
    background:#111d35;border:1px solid ${colors[type] || colors.info}33;
    border-left:3px solid ${colors[type] || colors.info};
    color:${colors[type] || colors.info};
    padding:10px 16px;border-radius:8px;font-size:0.87rem;font-weight:500;
    max-width:320px;box-shadow:0 8px 24px rgba(0,0,0,0.4);
    animation:fadeUp 0.3s ease;
  `;
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.4s'; setTimeout(() => toast.remove(), 400); }, 3500);
}


/* ─ Animate stat bars ────────────────────────────── */
window.addEventListener('load', () => {
  document.querySelectorAll('.stat-bar-fill').forEach(bar => {
    const target = bar.dataset.width || '0';
    bar.style.width = '0%';
    requestAnimationFrame(() => { bar.style.width = target + '%'; });
  });
});


/* ─ Charts (results page) ────────────────────────── */
window.initCharts = function (chartData) {
  if (!chartData) return;

  const CYAN   = '#38bdf8';
  const CORAL  = '#fb7185';
  const GREEN  = '#34d399';
  const PURPLE = '#a78bfa';
  const chartDefaults = {
    color: '#8ba3c7',
    plugins: { legend: { labels: { color: '#8ba3c7', font: { family: "'DM Sans', sans-serif", size: 12 } } } },
    scales: {
      x: { ticks: { color: '#4a6285' }, grid: { color: 'rgba(99,179,237,0.07)' } },
      y: { ticks: { color: '#4a6285' }, grid: { color: 'rgba(99,179,237,0.07)' } },
    },
  };

  /* Scatter chart */
  const scatterCtx = document.getElementById('scatterChart');
  if (scatterCtx && chartData.scatter) {
    const s = chartData.scatter;
    new Chart(scatterCtx, {
      type: 'scatter',
      data: {
        datasets: [
          {
            label: 'Normal',
            data: s.normal.x.map((x, i) => ({ x, y: s.normal.y[i] })),
            backgroundColor: GREEN + '99',
            pointRadius: 4,
          },
          {
            label: 'Anomaly',
            data: s.anomaly.x.map((x, i) => ({ x, y: s.anomaly.y[i] })),
            backgroundColor: CORAL + 'cc',
            pointRadius: 7,
            pointStyle: 'triangle',
          },
        ],
      },
      options: {
        ...chartDefaults,
        plugins: {
          ...chartDefaults.plugins,
          tooltip: { callbacks: { label: ctx => `(${ctx.parsed.x.toFixed(2)}, ${ctx.parsed.y.toFixed(2)})` } },
        },
        scales: {
          x: { ...chartDefaults.scales.x, title: { display: true, text: s.x_label, color: '#8ba3c7' } },
          y: { ...chartDefaults.scales.y, title: { display: true, text: s.y_label, color: '#8ba3c7' } },
        },
      },
    });
  }

  /* Line chart */
  const lineCtx = document.getElementById('lineChart');
  if (lineCtx && chartData.line) {
    const l = chartData.line;
    const pointColors = l.statuses.map(s => s === 'Anomaly' ? CORAL : GREEN);
    new Chart(lineCtx, {
      type: 'line',
      data: {
        labels: l.labels,
        datasets: [{
          label: 'Anomaly Score',
          data: l.scores,
          borderColor: CYAN,
          backgroundColor: CYAN + '15',
          borderWidth: 1.5,
          fill: true,
          tension: 0.35,
          pointRadius: l.statuses.map(s => s === 'Anomaly' ? 5 : 2),
          pointBackgroundColor: pointColors,
        }],
      },
      options: { ...chartDefaults, plugins: { ...chartDefaults.plugins } },
    });
  }

  /* Pie chart */
  const pieCtx = document.getElementById('pieChart');
  if (pieCtx && chartData.pie) {
    const p = chartData.pie;
    new Chart(pieCtx, {
      type: 'doughnut',
      data: {
        labels: p.labels,
        datasets: [{
          data: p.values,
          backgroundColor: [GREEN + 'cc', CORAL + 'cc'],
          borderColor: ['#0d1525', '#0d1525'],
          borderWidth: 3,
          hoverOffset: 8,
        }],
      },
      options: {
        cutout: '68%',
        plugins: {
          legend: { position: 'bottom', labels: { color: '#8ba3c7', padding: 16, font: { size: 13 } } },
          tooltip: {
            callbacks: {
              label: ctx => {
                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                const pct = ((ctx.raw / total) * 100).toFixed(1);
                return ` ${ctx.label}: ${ctx.raw} (${pct}%)`;
              },
            },
          },
        },
      },
    });
  }

  /* Distribution bar charts */
  const distCtx = document.getElementById('distChart');
  if (distCtx && chartData.distributions) {
    const dist = chartData.distributions;
    const colName = Object.keys(dist)[0];
    const values  = dist[colName];

    // Build histogram bins
    const bins = 20;
    const min = Math.min(...values);
    const max = Math.max(...values);
    const step = (max - min) / bins;
    const counts = Array(bins).fill(0);
    const labels = [];
    for (let i = 0; i < bins; i++) {
      labels.push((min + i * step).toFixed(1));
    }
    values.forEach(v => {
      let idx = Math.floor((v - min) / step);
      if (idx >= bins) idx = bins - 1;
      counts[idx]++;
    });

    new Chart(distCtx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: colName,
          data: counts,
          backgroundColor: PURPLE + '88',
          borderColor: PURPLE,
          borderWidth: 1,
          borderRadius: 3,
        }],
      },
      options: {
        ...chartDefaults,
        plugins: { ...chartDefaults.plugins },
        scales: {
          x: { ...chartDefaults.scales.x, title: { display: true, text: 'Value', color: '#8ba3c7' } },
          y: { ...chartDefaults.scales.y, title: { display: true, text: 'Frequency', color: '#8ba3c7' } },
        },
      },
    });
  }
};
