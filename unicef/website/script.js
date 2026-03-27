/**
 * Weather Forecast Frontend Application
 * Handles all UI interactions and API communication
 */

// ============================================================
// Configuration
// ============================================================

const API_BASE_URL = 'http://localhost:5000';
let currentChart = null;

// Debug logging
const DEBUG = true;
function debug(message, data) {
    if (DEBUG) {
        console.log(`[FORECAST] ${message}`, data || '');
    }
}

// ============================================================
// DOM Elements
// ============================================================

const districtSelect = document.getElementById('district');
const dateInput = document.getElementById('date');
const predictBtn = document.getElementById('predictBtn');
const errorAlert = document.getElementById('errorAlert');
const successAlert = document.getElementById('successAlert');
const loadingState = document.getElementById('loadingState');
const resultsSection = document.getElementById('resultsSection');
const forecastGrid = document.getElementById('forecastGrid');
const chartContainer = document.getElementById('chartContainer');

// ============================================================
// Initialize
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
    setDefaultDate();
    loadDistricts();
    checkAPIHealth();
});

// ============================================================
// Functions
// ============================================================

/**
 * Set date input default to today
 */
function setDefaultDate() {
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
    dateInput.min = today;
}

/**
 * Load districts from API
 */
async function loadDistricts() {
    try {
        debug('Loading districts from API...', API_BASE_URL);
        const response = await fetch(`${API_BASE_URL}/api/districts`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        debug('Districts loaded:', data);

        if (data.status === 'success') {
            districtSelect.innerHTML = '';
            data.districts.forEach((district, index) => {
                const option = document.createElement('option');
                option.value = district;
                option.textContent = district;
                if (index === 0) option.selected = true;
                districtSelect.appendChild(option);
            });
            debug(`Loaded ${data.districts.length} districts`);
        } else {
            throw new Error(data.message || 'Unknown error loading districts');
        }
    } catch (error) {
        console.error('❌ Failed to load districts:', error);
        debug('Districts error:', error.message);
        districtSelect.innerHTML = '<option value="">⚠️ Offline - Cannot load districts</option>';
        showError('Failed to load districts. Ensure backend is running at ' + API_BASE_URL);
    }
}

/**
 * Main prediction handler
 */
async function handlePredict() {
    const district = districtSelect.value;
    const date = dateInput.value;

    if (!district || !date) {
        showError('Please select both district and date');
        return;
    }

    await fetchPrediction(district, date);
}

/**
 * Fetch prediction from API
 */
async function fetchPrediction(district, date) {
    showLoading(true);
    closeAllAlerts();

    try {
        debug('Sending prediction request...', {district, date});
        const response = await fetch(`${API_BASE_URL}/api/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ district, date }),
        });

        debug('Response received:', {status: response.status, ok: response.ok});

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `Server error: ${response.status}`);
        }

        const data = await response.json();
        debug('Prediction data:', data);

        if (data.status === 'success') {
            displayResults(data);
            showSuccess(`Forecast loaded successfully for ${data.district}`);
        } else {
            throw new Error(data.message || 'Invalid response from server');
        }
    } catch (error) {
        console.error('❌ Prediction error:', error);
        debug('Error details:', error);
        
        let userMessage = error.message;
        if (error.message === 'Failed to fetch') {
            userMessage = 'Cannot reach backend server. Is it running at ' + API_BASE_URL + '?';
        }
        showError(`Error: ${userMessage}`);
    } finally {
        showLoading(false);
    }
}

/**
 * Display prediction results
 */
function displayResults(data) {
    const { district, base_date, predictions } = data;

    // Update summary
    document.getElementById('summaryDistrict').textContent = district;
    document.getElementById('summaryDate').textContent = `(${base_date})`;

    // Calculate stats
    const temps = predictions.map(p => p.tmax);
    const avgTemp = (temps.reduce((a, b) => a + b, 0) / temps.length).toFixed(1);
    const maxTemp = Math.max(...temps).toFixed(1);
    const minTemp = Math.min(...temps).toFixed(1);

    document.getElementById('avgTemp').textContent = `${avgTemp}°C`;
    document.getElementById('maxTemp').textContent = `${maxTemp}°C`;
    document.getElementById('minTemp').textContent = `${minTemp}°C`;

    // Render forecast cards
    forecastGrid.innerHTML = '';
    predictions.forEach((prediction) => {
        const card = document.createElement('div');
        card.className = 'forecast-card';
        card.innerHTML = `
            <div class="day-number">Day ${prediction.day}</div>
            <div class="forecast-date">${formatDate(prediction.date)}</div>
            <div class="forecast-temp">
                ${prediction.tmax}<span class="temp-unit">°C</span>
            </div>
        `;
        forecastGrid.appendChild(card);
    });

    // Store predictions for chart
    window.currentPredictions = predictions;
    window.currentDistrict = district;

    resultsSection.classList.remove('hidden');

    // Scroll to results
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

/**
 * Toggle chart visibility
 */
function toggleChart() {
    if (chartContainer.classList.contains('hidden')) {
        chartContainer.classList.remove('hidden');
        if (!currentChart && window.currentPredictions) {
            drawChart();
        }
    } else {
        chartContainer.classList.add('hidden');
    }
}

/**
 * Draw temperature chart using Chart.js
 */
function drawChart() {
    if (!window.currentPredictions) return;

    const ctx = document.getElementById('forecastChart').getContext('2d');

    // Destroy existing chart
    if (currentChart) {
        currentChart.destroy();
    }

    const labels = window.currentPredictions.map(p => `Day ${p.day}`);
    const data = window.currentPredictions.map(p => p.tmax);

    currentChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [
                {
                    label: `Temperature (${window.currentDistrict})`,
                    data,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#3498db',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
                title: {
                    display: true,
                    text: '15-Day Temperature Forecast',
                },
            },
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Temperature (°C)',
                    },
                },
                x: {
                    title: {
                        display: true,
                        text: 'Days',
                    },
                },
            },
        },
    });
}

/**
 * Download predictions as CSV
 */
function downloadCSV() {
    if (!window.currentPredictions) {
        showError('No predictions to download');
        return;
    }

    const { currentDistrict, currentPredictions } = window;

    let csv = 'Day,Date,Temperature (°C)\n';
    currentPredictions.forEach(p => {
        csv += `${p.day},${p.date},${p.tmax}\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `forecast_${currentDistrict}_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    showSuccess('CSV downloaded successfully');
}

/**
 * Check API health
 */
async function checkAPIHealth() {
    try {
        debug('Checking API health at:', API_BASE_URL);
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            console.warn('⚠️ API health check failed with status:', response.status);
            debug('Health check response status:', response.status);
        } else {
            const healthData = await response.json();
            debug('API Health:', healthData);
            console.log('✓ Backend API is healthy');
        }
    } catch (error) {
        console.error('❌ Cannot connect to API:', error.message);
        debug('API connection error:', error);
        showError(
            'Warning: Backend API unreachable at ' + API_BASE_URL + 
            '. Start backend with: python app.py'
        );
    }
}

/**
 * Show loading state
 */
function showLoading(show) {
    if (show) {
        loadingState.classList.remove('hidden');
        predictBtn.disabled = true;
        document.querySelector('.btn-text').classList.add('hidden');
        document.querySelector('.btn-loader').classList.remove('hidden');
    } else {
        loadingState.classList.add('hidden');
        predictBtn.disabled = false;
        document.querySelector('.btn-text').classList.remove('hidden');
        document.querySelector('.btn-loader').classList.add('hidden');
    }
}

/**
 * Show error message
 */
function showError(message) {
    const content = errorAlert.querySelector('.alert-content');
    content.textContent = message;
    errorAlert.classList.remove('hidden');
    setTimeout(() => {
        closeAlert('errorAlert');
    }, 5000);
}

/**
 * Show success message
 */
function showSuccess(message) {
    const content = successAlert.querySelector('.alert-content');
    content.textContent = message;
    successAlert.classList.remove('hidden');
    setTimeout(() => {
        closeAlert('successAlert');
    }, 3000);
}

/**
 * Close specific alert
 */
function closeAlert(alertId) {
    document.getElementById(alertId).classList.add('hidden');
}

/**
 * Close all alerts
 */
function closeAllAlerts() {
    document.querySelectorAll('.alert').forEach(alert => {
        alert.classList.add('hidden');
    });
}

/**
 * Format date to readable format
 */
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

/**
 * Show API status modal
 */
async function showApiStatus() {
    const modal = document.getElementById('apiStatusModal');
    const content = document.getElementById('apiStatusContent');
    modal.classList.remove('hidden');
    document.querySelector('.modal-overlay').classList.remove('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();

        if (response.ok) {
            content.innerHTML = `
                <p><strong>✅ API Status: Healthy</strong></p>
                <p>Service: ${data.service}</p>
                <p>Connected successfully to backend server.</p>
            `;
        } else {
            throw new Error('API not responding');
        }
    } catch (error) {
        content.innerHTML = `
            <p><strong>❌ API Status: Offline</strong></p>
            <p>Error: ${error.message}</p>
            <p>Make sure the backend server is running:</p>
            <pre style="background: #f0f0f0; padding: 10px; border-radius: 5px;">
python app.py
            </pre>
        `;
    }
}

/**
 * Show about modal
 */
function showAbout() {
    const modal = document.getElementById('aboutModal');
    modal.classList.remove('hidden');
    document.querySelector('.modal-overlay').classList.remove('hidden');
}

/**
 * Close modal
 */
function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
    document.querySelector('.modal-overlay').classList.add('hidden');
}

/**
 * Close all modals
 */
function closeAllModals() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.classList.add('hidden');
    });
    document.querySelector('.modal-overlay').classList.add('hidden');
}
      col.className = 'day-col';

      const tempLabel = document.createElement('div');
      tempLabel.className = 'temp-label';
      tempLabel.textContent = t + '°C';

      const bar = document.createElement('div');
      bar.className = 'bar';

      const fill = document.createElement('div');
      fill.className = 'bar-fill';
      // map t to height within bar (min->8% max->100%)
      const pct = Math.round(((t - 28) / (48 - 28)) * 100);
      fill.style.height = Math.max(6, Math.min(100, pct)) + '%';
      // color by thresholds
      if (t >= 41) {
        fill.style.background = 'linear-gradient(180deg,#ff9aa3,#f25c64)';
      } else if (t >= 38) {
        fill.style.background = 'linear-gradient(180deg,#ffd06b,#f6b042)';
      } else {
        fill.style.background = 'linear-gradient(180deg,#6ee7a9,#16c172)';
      }

      bar.appendChild(fill);

      const dayName = document.createElement('div');
      dayName.className = 'day-name';
      dayName.textContent = dayLabel(i);

      col.appendChild(tempLabel);
      col.appendChild(bar);
      col.appendChild(dayName);
      forecastEl.appendChild(col);
    }
  }

  function updateStatus(current) {
    // set indicator color and advice
    if (current >= 41) {
      statusEl.style.background = 'linear-gradient(180deg,#ff9aa3,#f25c64)';
      adviceEl.textContent = 'Next days unsafe for spraying. Plan irrigation today.';
    } else if (current >= 38) {
      statusEl.style.background = 'linear-gradient(180deg,#ffd06b,#f6b042)';
      adviceEl.textContent = 'Caution: high temperatures — avoid spraying in hottest hours.';
    } else {
      statusEl.style.background = 'linear-gradient(180deg,#6ee7a9,#16c172)';
      adviceEl.textContent = '';
    }
  }

  function setCurrent(temp) {
    currentEl.textContent = Math.round(temp) + '°C';
    // real feel: temp +/- up to 3 degrees
    const real = Math.round(temp + (Math.random() - 0.4) * 3);
    realFeelEl.textContent = real + '°C';
    updateStatus(temp);
  }

  // --- WebSocket external temperature input ---
  // If a WS server sends messages of the form:
  // { type: 'current', value: 37.2 }  -> update only current
  // { type: 'full', temps: [36,37,38,...] } -> replace forecast array
  // The client will reconnect automatically on disconnect.
  let ws;
  let externalConnected = false;
  function connectWS(url = 'ws://localhost:8080') {
    try {
      ws = new WebSocket(url);
    } catch (e) {
      console.warn('WS connect failed', e);
      scheduleReconnect();
      return;
    }
    ws.addEventListener('open', () => {
      externalConnected = true;
      console.log('WS connected to', url);
      // on connect, ask for current state
      ws.send(JSON.stringify({ type: 'hello', from: 'client' }));
    });
    ws.addEventListener('message', (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.type === 'current' && typeof msg.value === 'number') {
          temps[0] = Math.max(28, Math.min(48, msg.value));
          setCurrent(temps[0]);
          // update first bar label/height if rendered
          const firstCol = forecastEl.querySelector('.day-col');
          if (firstCol) {
            const firstTempLabel = firstCol.querySelector('.temp-label');
            const fill = firstCol.querySelector('.bar-fill');
            firstTempLabel.textContent = Math.round(temps[0]) + '°C';
            const pct = Math.round(((temps[0] - 28) / (48 - 28)) * 100);
            fill.style.height = Math.max(6, Math.min(100, pct)) + '%';
            if (temps[0] >= 41) fill.style.background = 'linear-gradient(180deg,#ff9aa3,#f25c64)';
            else if (temps[0] >= 38) fill.style.background = 'linear-gradient(180deg,#ffd06b,#f6b042)';
            else fill.style.background = 'linear-gradient(180deg,#6ee7a9,#16c172)';
          }
        } else if (msg.type === 'full' && Array.isArray(msg.temps)) {
          temps = msg.temps.map(t => Math.max(28, Math.min(48, t)));
          renderForecast(temps);
          setCurrent(temps[0]);
        }
      } catch (err) {
        console.warn('Invalid WS message', err);
      }
    });
    ws.addEventListener('close', () => {
      externalConnected = false;
      console.log('WS disconnected, will reconnect');
      scheduleReconnect();
    });
    ws.addEventListener('error', (e) => {
      console.warn('WS error', e);
      ws.close();
    });
  }

  let _reconnectTimer = null;
  function scheduleReconnect() {
    if (_reconnectTimer) return;
    _reconnectTimer = setTimeout(() => {
      _reconnectTimer = null;
      connectWS();
    }, 2000);
  }


  // initial render
  let temps = generateTemps(locationSelect.value);
  renderForecast(temps);
  setCurrent(temps[0]);

  // small dynamic fluctuation for "live" current temperature
  setInterval(() => {
    // change the current day value by a small random amount
    const delta = (Math.random() - 0.5) * 1.2; // -0.6 .. +0.6
    temps[0] = Math.max(28, Math.min(48, temps[0] + delta));
    // also slightly nudge tomorrow forward/back
    if (Math.random() > 0.6) {
      temps[1] = Math.max(28, Math.min(48, temps[1] + (Math.random() - 0.5) * 1.2));
    }
    // update UI
    setCurrent(temps[0]);
    // update only first bar height/text for smoothness
    const firstCol = forecastEl.querySelector('.day-col');
    if (firstCol) {
      const firstTempLabel = firstCol.querySelector('.temp-label');
      const fill = firstCol.querySelector('.bar-fill');
      firstTempLabel.textContent = Math.round(temps[0]) + '°C';
      const pct = Math.round(((temps[0] - 28) / (48 - 28)) * 100);
      fill.style.height = Math.max(6, Math.min(100, pct)) + '%';
      if (temps[0] >= 41) fill.style.background = 'linear-gradient(180deg,#ff9aa3,#f25c64)';
      else if (temps[0] >= 38) fill.style.background = 'linear-gradient(180deg,#ffd06b,#f6b042)';
      else fill.style.background = 'linear-gradient(180deg,#6ee7a9,#16c172)';
    }
  }, 2500);

  locationSelect.addEventListener('change', () => {
    temps = generateTemps(locationSelect.value);
    renderForecast(temps);
    setCurrent(temps[0]);
  });

  // optional: click to read advisory (no real audio provided)
  const listenBtn = document.getElementById('listenBtn');
  listenBtn.addEventListener('click', () => {
    const msg = `Advisory for ${locationSelect.value}: Current ${currentEl.textContent}. ${adviceEl.textContent}`;
    if ('speechSynthesis' in window) {
      const s = new SpeechSynthesisUtterance(msg);
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(s);
    } else {
      alert(msg);
    }
  });

})();
