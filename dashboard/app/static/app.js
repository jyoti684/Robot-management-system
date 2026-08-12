(() => {
  const app = document.getElementById('app');
  const role = app.dataset.role;
  const pollMs = Number(app.dataset.pollMs || 2000);
  const elements = {
    connection: document.getElementById('connection'),
    robotStatus: document.getElementById('robot-status'),
    battery: document.getElementById('battery'),
    batteryBar: document.getElementById('battery-bar'),
    latency: document.getElementById('latency'),
    signal: document.getElementById('signal'),
    coordinates: document.getElementById('coordinates'),
    marker: document.getElementById('robot-marker'),
    updated: document.getElementById('updated-at'),
    warning: document.getElementById('warning'),
    logs: document.getElementById('logs'),
    steps: document.getElementById('steps'),
    permission: document.getElementById('permission-note'),
  };

  function showWarning(message) {
    elements.warning.textContent = message;
    elements.warning.classList.toggle('hidden', !message);
  }

  function updateTelemetry(t) {
    const connected = t.connection_status === 'connected';
    elements.connection.textContent = connected ? 'Connected' : 'Signal Lost';
    elements.connection.className = `status-pill ${connected ? 'good' : 'bad'}`;
    elements.robotStatus.textContent = t.status;
    elements.battery.textContent = `${Number(t.battery_level).toFixed(1)}%`;
    elements.batteryBar.style.width = `${Math.max(0, Math.min(100, t.battery_level))}%`;
    elements.batteryBar.style.background = t.battery_level <= 25 ? '#b33a3a' : '#14845f';
    elements.latency.textContent = `${t.latency_ms} ms`;
    elements.signal.textContent = connected ? (t.latency_ms < 150 ? 'Good' : 'Degraded') : 'Lost';
    elements.coordinates.textContent = `X: ${t.position_x}, Y: ${t.position_y}`;
    elements.updated.textContent = new Date(t.timestamp).toLocaleTimeString();
    const left = 50 + Math.max(-10, Math.min(10, t.position_x)) * 4.4;
    const top = 50 - Math.max(-10, Math.min(10, t.position_y)) * 4.4;
    elements.marker.style.left = `${left}%`;
    elements.marker.style.top = `${top}%`;
    if (!connected) showWarning('Robot API unavailable. Commands are disabled until the connection is restored.');
    else if (t.battery_level <= 25) showWarning(`Low battery: ${Number(t.battery_level).toFixed(1)}%`);
    else showWarning('');
    document.querySelectorAll('.move').forEach(btn => btn.disabled = role !== 'commander' || !connected);
  }

  async function fetchTelemetry() {
    try {
      const response = await fetch('/api/robot/telemetry', {headers: {'Accept': 'application/json'}});
      if (response.status === 401) return window.location.assign('/login');
      if (!response.ok) throw new Error(`Telemetry request failed (${response.status})`);
      updateTelemetry(await response.json());
    } catch (error) {
      elements.connection.textContent = 'Signal Lost';
      elements.connection.className = 'status-pill bad';
      showWarning(error.message);
      document.querySelectorAll('.move').forEach(btn => btn.disabled = true);
    }
  }

  async function loadLogs() {
    const response = await fetch('/api/logs?limit=40');
    if (!response.ok) return;
    const logs = await response.json();
    elements.logs.innerHTML = logs.map(log => `
      <article class="log-entry ${log.event_type}">
        <div class="log-top"><span>${log.event_type.replace('_',' ')}</span><time>${new Date(log.timestamp).toLocaleTimeString()}</time></div>
        <p>${escapeHtml(log.message || '')}</p>
      </article>`).join('') || '<p class="muted">No mission events recorded yet.</p>';
  }

  function escapeHtml(value) {
    return value.replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
  }

  async function move(direction) {
    const response = await fetch('/api/robot/command', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({direction, steps: Number(elements.steps.value)}),
    });
    if (response.status === 403) return showWarning('Viewer accounts cannot execute movement commands.');
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      return showWarning(body.detail || `Command failed (${response.status})`);
    }
    const body = await response.json();
    if (body.telemetry) updateTelemetry(body.telemetry);
    await loadLogs();
  }

  document.querySelectorAll('.move').forEach(button => button.addEventListener('click', () => move(button.dataset.direction)));
  document.getElementById('refresh-logs').addEventListener('click', loadLogs);
  if (role !== 'commander') {
    elements.permission.textContent = 'Viewer mode: movement controls are disabled.';
    document.querySelectorAll('.move').forEach(btn => btn.disabled = true);
  } else {
    elements.permission.textContent = 'Commander mode: authorised movement controls enabled.';
  }
  fetchTelemetry();
  loadLogs();
  setInterval(fetchTelemetry, pollMs);
  setInterval(loadLogs, Math.max(5000, pollMs * 3));
})();
