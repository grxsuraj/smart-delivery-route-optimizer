let cities = [];
let currentPathNames = [];

// Simple circular layout for the graph — good enough for 10 nodes
function layoutNodes(cityList) {
  const cx = 250, cy = 210, r = 160;
  return cityList.map((c, i) => {
    const angle = (2 * Math.PI * i) / cityList.length;
    return { ...c, x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
  });
}

async function loadCities() {
  const res = await fetch('/api/cities');
  cities = await res.json();

  const sourceSel = document.getElementById('source');
  const destSel = document.getElementById('destination');
  cities.forEach(c => {
    sourceSel.innerHTML += `<option value="${c.name}">${c.name}</option>`;
    destSel.innerHTML += `<option value="${c.name}">${c.name}</option>`;
  });
  destSel.selectedIndex = 1;

  drawGraph([]);
}

function drawGraph(activePathNames) {
  const svg = document.getElementById('graph');
  const positioned = layoutNodes(cities);
  const byName = Object.fromEntries(positioned.map(c => [c.name, c]));

  let edgesHtml = '';

  // draw active path edges
  for (let i = 0; i < activePathNames.length - 1; i++) {
    const a = byName[activePathNames[i]];
    const b = byName[activePathNames[i + 1]];
    if (a && b) {
      edgesHtml += `<line class="edge-line active" x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}"/>`;
    }
  }

  let nodesHtml = '';
  positioned.forEach(c => {
    const isActive = activePathNames.includes(c.name);
    nodesHtml += `
      <circle class="node-circle ${isActive ? 'active' : ''}" cx="${c.x}" cy="${c.y}" r="18"/>
      <text class="node-label" x="${c.x}" y="${c.y + 32}">${c.name}</text>
    `;
  });

  svg.innerHTML = edgesHtml + nodesHtml;
}

async function checkRoute() {
  const source = document.getElementById('source').value;
  const destination = document.getElementById('destination').value;
  const resultDiv = document.getElementById('result');
  resultDiv.innerHTML = 'Calculating shortest path...';

  try {
    const res = await fetch('/api/find-route', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source, destination })
    });
    const data = await res.json();

    if (data.error) {
      resultDiv.innerHTML = `<span class="risk">${data.error}</span>`;
      return;
    }

    currentPathNames = data.path;
    drawGraph(currentPathNames);

    const delayClass = data.delay_risk ? 'risk' : 'safe';
    resultDiv.innerHTML = `
      <b>Route:</b> ${data.path.join(' → ')}<br>
      <b>Total Time:</b> ${data.total_time_min} min<br>
      <b>Predicted Delay:</b> <span class="${delayClass}">${data.predicted_delay_min} min</span><br>
      ${data.delay_risk ? `<b>Alert:</b> ${data.alert_status}` : ''}<br>
      <small>Engine: ${data.engine}</small>
    `;
  } catch (err) {
    resultDiv.innerHTML = `<span class="risk">Error contacting server</span>`;
  }
}

loadCities();
