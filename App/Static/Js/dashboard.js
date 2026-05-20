const appShell = document.querySelector('.app-shell');

if (appShell) {
  const gridEl = document.getElementById('grid');
  const logList = document.getElementById('logList');
  const connectionBadge = document.getElementById('connectionBadge');
  const batteryBadge = document.getElementById('batteryBadge');
  const robotStatusText = document.getElementById('robotStatusText');
  const positionText = document.getElementById('positionText');
  const latencyText = document.getElementById('latencyText');
  const signalText = document.getElementById('signalText');
  const commandMessage = document.getElementById('commandMessage');
  const refreshLogsBtn = document.getElementById('refreshLogsBtn');
  const stepInput = document.getElementById('stepInput');
  const gridSize = Number(appShell.dataset.gridSize || 10);
  const role = appShell.dataset.role;
  const lowBatteryThreshold = Number(appShell.dataset.lowBatteryThreshold || 25);
  const pollMs = Number(appShell.dataset.pollSeconds || 2) * 1000;
  const buttons = document.querySelectorAll('.cmd-btn');

  function createGrid() {
    gridEl.innerHTML = '';
    for (let y = gridSize - 1; y >= 0; y--) {
      for (let x = 0; x < gridSize; x++) {
        const cell = document.createElement('div');
        cell.className = 'grid-cell';
        cell.dataset.x = x;
        cell.dataset.y = y;
        cell.textContent = `${x},${y}`;
        gridEl.appendChild(cell);
      }
    }
  }

  function drawRobot(x, y) {
    document.querySelectorAll('.grid-cell').forEach(cell => cell.classList.remove('robot'));
    const cell = document.querySelector(`.grid-cell[data-x="${x}"][data-y="${y}"]`);
    if (cell) {
      cell.classList.add('robot');
      cell.textContent = '🤖';
    }
  }

  function refreshGridLabels() {
    document.querySelectorAll('.grid-cell:not(.robot)').forEach(cell => {
      cell.textContent = `${cell.dataset.x},${cell.dataset.y}`;
    });
  }

  function setConnectionState(state, batteryLevel) {
    connectionBadge.className = 'badge';
    if (state === 'connected') {
      connectionBadge.classList.add('badge-ok');
      connectionBadge.textContent = 'Connected';
    } else if (state === 'signal_lost') {
      connectionBadge.classList.add('badge-bad');
      connectionBadge.textContent = 'Signal Lost';
    } else {
      connectionBadge.classList.add('badge-warn');
      connectionBadge.textContent = 'Reconnecting...';
    }

    batteryBadge.className = 'badge';
    batteryBadge.textContent = `Battery ${batteryLevel}%`;
    batteryBadge.classList.add(batteryLevel <= lowBatteryThreshold ? 'badge-warn' : 'badge-neutral');
  }

  async function loadTelemetry() {
    try {
      connectionBadge.textContent = 'Reconnecting...';
      const response = await fetch('/api/robot/telemetry');
      const data = await response.json();
      setConnectionState(data.connection_status, data.battery_level ?? 0);
      robotStatusText.textContent = `Status: ${data.status}`;
      positionText.textContent = `(${data.position_x}, ${data.position_y})`;
      latencyText.textContent = `${data.latency_ms ?? 0} ms`;
      signalText.textContent = data.signal_strength || 'n/a';
      refreshGridLabels();
      drawRobot(data.position_x ?? 0, data.position_y ?? 0);
    } catch (error) {
      setConnectionState('signal_lost', 0);
      robotStatusText.textContent = 'Status: unreachable';
      commandMessage.textContent = 'Robot API unavailable. UI remains responsive and will retry automatically.';
    }
  }

  async function loadLogs() {
    const response = await fetch('/api/logs');
    const logs = await response.json();
    logList.innerHTML = logs.map(log => `
      <div class="log-item">
        <div><strong>${log.event_type}</strong> ${log.command_type ? `- ${log.command_type}` : ''}</div>
        <div class="small-text">${new Date(log.timestamp).toLocaleString()}</div>
        <div class="small-text">${log.message || ''}</div>
        <div class="small-text">Battery: ${log.battery_level ?? '--'} | Position: (${log.position[0] ?? '--'}, ${log.position[1] ?? '--'})</div>
      </div>
    `).join('');
  }

  async function sendCommand(direction) {
    if (role !== 'commander') {
      commandMessage.textContent = 'Viewer accounts cannot issue robot movement commands.';
      return;
    }
    commandMessage.textContent = 'Sending command...';
    const payload = { direction, steps: Number(stepInput.value || 1) };

    try {
      const response = await fetch('/api/robot/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Command failed');
      }
      commandMessage.textContent = data.detail;
      if (data.telemetry) {
        refreshGridLabels();
        drawRobot(data.telemetry.position_x, data.telemetry.position_y);
      }
      await loadLogs();
    } catch (error) {
      commandMessage.textContent = error.message;
    }
  }

  buttons.forEach(button => button.addEventListener('click', () => sendCommand(button.dataset.direction)));
  refreshLogsBtn.addEventListener('click', loadLogs);
  createGrid();
  loadTelemetry();
  loadLogs();
  setInterval(loadTelemetry, pollMs);
}
