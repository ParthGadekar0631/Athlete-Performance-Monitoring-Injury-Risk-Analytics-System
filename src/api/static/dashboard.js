const state = {
  records: [],
  players: [],
  filtered: [],
};

const colors = {
  workload: "#2f6fc9",
  readiness: "#22845a",
  acwr: "#b97716",
  risk: "#c33c3c",
  throwing: "#0f7f8b",
  pitch: "#6b55aa",
  velocity: "#c75b2a",
  grid: "#dce4ea",
  gridStrong: "#c8d3dc",
  text: "#63717d",
};

const $ = (id) => document.getElementById(id);
const number = (value, digits = 1) => Number.isFinite(value) ? value.toFixed(digits) : "--";
const boolValue = (value) => value === true || value === "True" || value === "true" || value === 1 || value === "1";

function average(rows, field) {
  const values = rows.map((row) => Number(row[field])).filter(Number.isFinite);
  if (!values.length) return NaN;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function groupBy(rows, key) {
  return rows.reduce((acc, row) => {
    const groupKey = typeof key === "function" ? key(row) : row[key];
    acc[groupKey] ||= [];
    acc[groupKey].push(row);
    return acc;
  }, {});
}

function sum(rows, field) {
  return rows.reduce((total, row) => total + Number(row[field] || 0), 0);
}

function setOptions(select, values, label, valueField = null, textField = null) {
  select.innerHTML = `<option value="All">All ${label}</option>`;
  values.forEach((item) => {
    const option = document.createElement("option");
    option.value = valueField ? item[valueField] : item;
    option.textContent = textField ? item[textField] : item;
    select.appendChild(option);
  });
}

function initFilters(data) {
  state.players = data.players;
  setOptions($("playerFilter"), data.players, "Players", "player_id", "player_name");
  setOptions($("teamFilter"), data.teams, "Teams");
  setOptions($("positionFilter"), data.positions, "Positions");
  $("startDate").value = data.date_range.min || "";
  $("endDate").value = data.date_range.max || "";

  ["playerFilter", "teamFilter", "positionFilter", "riskFilter", "startDate", "endDate"].forEach((id) => {
    $(id).addEventListener("change", render);
  });
}

function filteredRecords() {
  const player = $("playerFilter").value;
  const team = $("teamFilter").value;
  const position = $("positionFilter").value;
  const risk = $("riskFilter").value;
  const start = $("startDate").value;
  const end = $("endDate").value;

  return state.records.filter((row) => {
    if (player !== "All" && row.player_id !== player) return false;
    if (team !== "All" && row.team !== team) return false;
    if (position !== "All" && row.position !== position) return false;
    if (risk !== "All" && row.risk_category !== risk) return false;
    if (start && row.date < start) return false;
    if (end && row.date > end) return false;
    return true;
  });
}

function aggregateByDate(rows) {
  return Object.entries(groupBy(rows, "date"))
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, values]) => ({
      date,
      workload_score: average(values, "workload_score"),
      readiness_score: average(values, "readiness_score"),
      acwr: average(values, "acwr"),
      injury_risk_score: average(values, "injury_risk_score"),
      pitch_count: average(values, "pitch_count"),
      throwing_volume: average(values, "throwing_volume"),
      velocity_trend: average(values, "velocity_trend"),
    }));
}

function latestSelectedPlayerRows(rows) {
  const selected = $("playerFilter").value;
  if (selected !== "All") return rows.filter((row) => row.player_id === selected);

  const byPlayer = groupBy(rows, "player_id");
  const playerScores = Object.entries(byPlayer).map(([playerId, values]) => ({
    playerId,
    score: average(values.slice(-14), "injury_risk_score"),
  }));
  playerScores.sort((a, b) => b.score - a.score);
  const focusPlayer = playerScores[0]?.playerId;
  return rows.filter((row) => row.player_id === focusPlayer);
}

function pitcherRows(rows) {
  const pitchers = rows.filter((row) => row.position === "Pitcher");
  const selected = $("playerFilter").value;
  if (selected !== "All") {
    const selectedRows = pitchers.filter((row) => row.player_id === selected);
    if (selectedRows.length) return selectedRows;
  }
  const byPlayer = groupBy(pitchers, "player_id");
  const top = Object.entries(byPlayer)
    .map(([playerId, values]) => ({ playerId, throws: sum(values, "throwing_volume") }))
    .sort((a, b) => b.throws - a.throws)[0]?.playerId;
  return pitchers.filter((row) => row.player_id === top);
}

function renderKpis(rows) {
  $("avgWorkload").textContent = number(average(rows, "workload_score"), 0);
  $("avgReadiness").textContent = number(average(rows, "readiness_score"), 1);
  $("avgAcwr").textContent = number(average(rows, "acwr"), 2);
  $("riskDays").textContent = rows.filter((row) => ["Elevated", "High"].includes(row.risk_category)).length.toLocaleString();
  $("spikeDays").textContent = rows.filter((row) => boolValue(row.workload_spike_flag)).length.toLocaleString();
  $("lowRecoveryDays").textContent = rows.filter((row) => boolValue(row.low_recovery_flag)).length.toLocaleString();
  $("recordStatus").textContent = `${rows.length.toLocaleString()} records`;
  $("dateWindow").textContent = rows.length ? `${rows[0].date} to ${rows[rows.length - 1].date}` : "--";
}

function chartScales(series, width, height, padding) {
  const allValues = series.flatMap((line) => line.values.map((point) => point.value)).filter(Number.isFinite);
  const max = Math.max(...allValues, 1);
  const min = Math.min(...allValues, 0);
  const span = max - min || 1;
  const xMax = Math.max(...series.map((line) => line.values.length), 1) - 1 || 1;
  return {
    x: (index) => padding.left + (index / xMax) * (width - padding.left - padding.right),
    y: (value) => height - padding.bottom - ((value - min) / span) * (height - padding.top - padding.bottom),
    min,
    max,
  };
}

function linePath(values, scales) {
  return values
    .map((point, index) => `${index === 0 ? "M" : "L"} ${scales.x(index).toFixed(1)} ${scales.y(point.value).toFixed(1)}`)
    .join(" ");
}

function renderLineChart(id, rows, seriesConfig) {
  const el = $(id);
  if (!rows.length) {
    el.innerHTML = `<div class="empty-state">No matching records</div>`;
    return;
  }
  const width = 960;
  const height = 330;
  const padding = { top: 34, right: 78, bottom: 46, left: 54 };
  const series = seriesConfig.map((config) => ({
    ...config,
    values: rows.map((row) => ({ date: row.date, value: Number(row[config.field]) })).filter((point) => Number.isFinite(point.value)),
  }));
  const scales = chartScales(series, width, height, padding);
  const ticks = [
    scales.min,
    scales.min + (scales.max - scales.min) * 0.25,
    scales.min + (scales.max - scales.min) * 0.5,
    scales.min + (scales.max - scales.min) * 0.75,
    scales.max,
  ];
  const firstDate = rows[0]?.date || "";
  const lastDate = rows[rows.length - 1]?.date || "";
  const gradientId = `${id}-wash`;

  el.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${id}">
      <defs>
        <linearGradient id="${gradientId}" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stop-color="#f7fafc" stop-opacity="1" />
          <stop offset="100%" stop-color="#ffffff" stop-opacity="1" />
        </linearGradient>
      </defs>
      <rect x="${padding.left}" y="${padding.top}" width="${width - padding.left - padding.right}" height="${height - padding.top - padding.bottom}" rx="6" fill="url(#${gradientId})" stroke="${colors.grid}" />
      ${ticks.map((tick) => `<line x1="${padding.left}" x2="${width - padding.right}" y1="${scales.y(tick)}" y2="${scales.y(tick)}" stroke="${colors.grid}" /><text class="axis-label" x="10" y="${scales.y(tick) + 4}">${number(tick, 1)}</text>`).join("")}
      <text class="axis-label" x="${padding.left}" y="${height - 10}">${firstDate}</text>
      <text class="axis-label" x="${width - padding.right - 72}" y="${height - 10}">${lastDate}</text>
      ${series.map((line) => `<path d="${linePath(line.values, scales)}" fill="none" stroke="${line.color}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" />`).join("")}
      ${series.map((line) => {
        const last = line.values[line.values.length - 1];
        if (!last) return "";
        const x = scales.x(line.values.length - 1);
        const y = scales.y(last.value);
        return `<circle cx="${x}" cy="${y}" r="4.5" fill="#ffffff" stroke="${line.color}" stroke-width="3" />
          <text class="axis-label" x="${Math.min(width - padding.right + 10, x + 10)}" y="${y + 4}">${number(last.value, 1)}</text>`;
      }).join("")}
      ${series.map((line, index) => `<circle cx="${padding.left + index * 145}" cy="12" r="5" fill="${line.color}" /><text class="legend" x="${padding.left + 10 + index * 145}" y="16">${line.label}</text>`).join("")}
    </svg>
  `;
}

function renderBarChart(id, data, colorByKey = null) {
  const el = $(id);
  const entries = Object.entries(data).filter(([, value]) => Number(value) > 0);
  if (!entries.length) {
    el.innerHTML = `<div class="empty-state">No matching records</div>`;
    return;
  }
  const width = 560;
  const height = 280;
  const padding = { top: 28, right: 24, bottom: 70, left: 48 };
  const max = Math.max(...entries.map(([, value]) => value), 1);
  const band = (width - padding.left - padding.right) / entries.length;
  el.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${id}">
      <rect x="${padding.left}" y="${padding.top}" width="${width - padding.left - padding.right}" height="${height - padding.top - padding.bottom}" rx="6" fill="#fbfcfd" stroke="${colors.grid}" />
      <line x1="${padding.left}" x2="${width - padding.right}" y1="${height - padding.bottom}" y2="${height - padding.bottom}" stroke="${colors.gridStrong}" />
      ${entries.map(([key, value], index) => {
        const barHeight = (value / max) * (height - padding.top - padding.bottom);
        const x = padding.left + index * band + 6;
        const y = height - padding.bottom - barHeight;
        const fill = colorByKey?.[key] || colors.blue;
        return `<rect x="${x}" y="${y}" width="${Math.max(14, band - 12)}" height="${barHeight}" rx="5" fill="${fill}" opacity="0.92" />
          <text class="axis-label" x="${x}" y="${height - padding.bottom + 18}" transform="rotate(35 ${x} ${height - padding.bottom + 18})">${key}</text>
          <text class="axis-label" x="${x}" y="${Math.max(14, y - 6)}">${value}</text>`;
      }).join("")}
    </svg>
  `;
}

function riskReasons(row) {
  const reasons = [];
  if (Number(row.acwr) > 1.5) reasons.push("High ACWR");
  if (Number(row.recovery_score) < 60) reasons.push("Low recovery");
  if (Number(row.soreness_rating) > 7) reasons.push("High soreness");
  if (Number(row.sleep_hours) < 6) reasons.push("Low sleep");
  if (Number(row.velocity_trend_change) < -0.4) reasons.push("Velocity decline");
  if (boolValue(row.workload_spike_flag)) reasons.push("Workload spike");
  return reasons.length ? reasons.join(", ") : "Review context";
}

function riskClass(risk) {
  return `risk-tag risk-${String(risk || "low").toLowerCase()}`;
}

function renderAlerts(rows) {
  const alerts = rows
    .filter((row) => ["Elevated", "High"].includes(row.risk_category) || row.fatigue_status === "High Risk")
    .sort((a, b) => Number(b.injury_risk_score) - Number(a.injury_risk_score))
    .slice(0, 80);
  $("alertRows").innerHTML = alerts.length
    ? alerts.map((row) => `
      <tr>
        <td>${row.date}</td>
        <td>${row.player_name}</td>
        <td>${row.position}</td>
        <td><span class="${riskClass(row.risk_category)}">${row.risk_category}</span></td>
        <td>${number(Number(row.injury_risk_score), 1)}</td>
        <td>${row.fatigue_status}</td>
        <td>${riskReasons(row)}</td>
      </tr>
    `).join("")
    : `<tr><td colspan="7">No matching alerts</td></tr>`;
}

function render() {
  const rows = filteredRecords().sort((a, b) => a.date.localeCompare(b.date));
  state.filtered = rows;
  renderKpis(rows);

  const byDate = aggregateByDate(rows);
  $("teamTrendNote").textContent = `${rows.length.toLocaleString()} filtered player-days`;
  renderLineChart("teamTrendChart", byDate, [
    { field: "workload_score", label: "Workload", color: colors.workload },
    { field: "readiness_score", label: "Readiness", color: colors.readiness },
    { field: "injury_risk_score", label: "Risk", color: colors.risk },
  ]);

  const playerRows = latestSelectedPlayerRows(rows).sort((a, b) => a.date.localeCompare(b.date));
  $("playerTrendNote").textContent = playerRows.length ? `${playerRows[0].player_name} | ${playerRows[0].position}` : "No player selected";
  renderLineChart("playerTrendChart", playerRows, [
    { field: "workload_score", label: "Workload", color: colors.workload },
    { field: "readiness_score", label: "Readiness", color: colors.readiness },
    { field: "acwr", label: "ACWR", color: colors.acwr },
    { field: "soreness_rating", label: "Soreness", color: colors.risk },
  ]);

  const pitcher = pitcherRows(rows).sort((a, b) => a.date.localeCompare(b.date));
  $("pitcherTrendNote").textContent = pitcher.length ? `${pitcher[0].player_name} | ${pitcher[0].team}` : "No pitcher in selection";
  renderLineChart("pitcherChart", pitcher, [
    { field: "pitch_count", label: "Pitch Count", color: colors.pitch },
    { field: "throwing_volume", label: "Throwing", color: colors.throwing },
    { field: "velocity_trend", label: "Velocity", color: colors.velocity },
    { field: "recovery_score", label: "Recovery", color: colors.readiness },
  ]);

  const riskCounts = groupBy(rows, "risk_category");
  renderBarChart(
    "riskChart",
    {
      Low: riskCounts.Low?.length || 0,
      Moderate: riskCounts.Moderate?.length || 0,
      Elevated: riskCounts.Elevated?.length || 0,
      High: riskCounts.High?.length || 0,
    },
    { Low: "#1f8a5b", Moderate: "#b7791f", Elevated: "#c75b2a", High: "#c03535" }
  );

  const spikeRows = rows.filter((row) => boolValue(row.workload_spike_flag));
  const spikeCounts = Object.fromEntries(
    Object.entries(groupBy(spikeRows, "position")).map(([position, values]) => [position, values.length])
  );
  renderBarChart("spikeChart", spikeCounts);
  renderAlerts(rows);
}

async function loadDashboard() {
  try {
    const response = await fetch("/dashboard/data");
    if (!response.ok) throw new Error(`Dashboard data failed: ${response.status}`);
    const data = await response.json();
    state.records = data.records || [];
    initFilters(data);
    render();
  } catch (error) {
    $("recordStatus").textContent = "Data unavailable";
    document.querySelector(".grid").innerHTML = `<section class="panel"><div class="empty-state">${error.message}</div></section>`;
  }
}

loadDashboard();
