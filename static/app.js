/**
 * SAKTHIDEV // AUTONOMOUS OPERATOR STUDIO (v4.5 ULTIMATE)
 * Client-Side Mission Control & Multi-Theme Engine
 * 
 * Features:
 * - 1-Click Dark Mode 🌙 / Light Mode ☀️ & 5 Cyber Themes
 * - Dynamic Live Wallpapers (Gaming Cyber City, Anime Rooftop, Interactive Neural Canvas, Custom URL)
 * - Interactive HTML5 Canvas Connected Particle Mesh
 * - Welcome Hero Command Deck with Quick Action Starters
 * - Clickable Mission Archives (ChatGPT/Gemini style multi-session history)
 * - Web Audio API Sci-Fi Synthesizer Sound Effects (SFX)
 * - Multimodal Vision (Instant Image Upload & Analysis)
 * - Web Speech API Voice Recognition Input
 * - Discrete Tool Action Pills (Zero Raw JSON Dumps)
 * - Persistent SQLite Multi-Session Database
 */

document.addEventListener('DOMContentLoaded', () => {
  // Instant Cyber Boot Splash Dismissal (No Lag, Silky Smooth 60fps)
  const bootSplash = document.getElementById('cyber-boot-splash');
  if (bootSplash) {
    const telemetry = document.getElementById('splash-telemetry');
    setTimeout(() => {
      if (telemetry) telemetry.textContent = 'ALL SYSTEMS GO // SAKTHIDEV STUDIO READY';
    }, 450);
    setTimeout(() => {
      bootSplash.classList.add('loaded');
      setTimeout(() => {
        try { bootSplash.remove(); } catch(e){}
      }, 600);
    }, 850);
  }

  // DOM Elements
  const htmlRoot = document.documentElement;
  const promptInput = document.getElementById('prompt-input');
  const btnSubmit = document.getElementById('btn-submit');
  const chatStream = document.getElementById('chat-stream');
  const fileBrowser = document.getElementById('file-browser');
  const btnRefreshFiles = document.getElementById('btn-refresh-files');
  const wsInput = document.getElementById('ws-input');
  const btnSwitchWs = document.getElementById('btn-switch-ws');
  const dockWsLabel = document.getElementById('dock-ws-label');
  const quickPresetSelect = document.getElementById('quick-preset-select');

  // Theme & Wallpaper Elements
  const btnToggleTheme = document.getElementById('btn-toggle-theme');
  const themeIcon = document.getElementById('theme-icon');
  const btnOpenWallpapers = document.getElementById('btn-open-wallpapers');
  const wallpaperModal = document.getElementById('wallpaper-modal');
  const btnCloseWallpaperModal = document.getElementById('btn-close-wallpaper-modal');
  const bgImageLayer = document.getElementById('bg-image-layer');
  const bgCanvas = document.getElementById('bg-canvas');
  const bgVideoLayer = document.getElementById('bg-video-layer');
  const sliderBgOpacity = document.getElementById('slider-bg-opacity');
  const labelBgOpacity = document.getElementById('label-bg-opacity');
  const sliderBgBlur = document.getElementById('slider-bg-blur');
  const labelBgBlur = document.getElementById('label-bg-blur');
  const customBgInput = document.getElementById('custom-bg-input');
  const btnApplyCustomBg = document.getElementById('btn-apply-custom-bg');

  // Mission History Elements
  const historySidebar = document.getElementById('history-sidebar');
  const btnToggleHistory = document.getElementById('btn-toggle-history');
  const btnNewMission = document.getElementById('btn-new-mission');
  const missionList = document.getElementById('mission-list');
  const missionSearchInput = document.getElementById('mission-search-input');
  const btnClearAllSessions = document.getElementById('btn-clear-all-sessions');
  const activeMissionLabel = document.getElementById('active-mission-label');

  // Audio SFX Element
  const btnToggleSfx = document.getElementById('btn-toggle-sfx');
  const sfxIcon = document.getElementById('sfx-icon');

  // File Drawer
  const btnToggleExplorer = document.getElementById('btn-toggle-explorer');
  const btnCloseDrawer = document.getElementById('btn-close-drawer');
  const rightDrawer = document.getElementById('right-drawer');

  // Upload Elements
  const btnUploadFile = document.getElementById('btn-upload-file');
  const fileUploadInput = document.getElementById('file-upload-input');
  const uploadPreviewBar = document.getElementById('upload-preview-bar');
  const uploadPreviewImg = document.getElementById('upload-preview-img');
  const uploadPreviewName = document.getElementById('upload-preview-name');
  const btnRemoveUpload = document.getElementById('btn-remove-upload');

  // Voice Input Elements
  const btnVoiceInput = document.getElementById('btn-voice-input');
  const micIcon = document.getElementById('mic-icon');

  // Telemetry Labels
  const dbMemCount = document.getElementById('db-mem-count');
  const telemetryModelLabel = document.getElementById('telemetry-model-label');

  // HUD Elements
  const agentHud = document.getElementById('agent-hud');
  const hudStatusText = document.getElementById('hud-status-text');
  const hudActiveTool = document.getElementById('hud-active-tool');
  const hudTimer = document.getElementById('hud-timer');

  // Mode Switchers
  const toggleCloudMode = document.getElementById('toggle-cloud-mode');
  const toggleOfflineMode = document.getElementById('toggle-offline-mode');

  // Settings Modal Elements
  const settingsModal = document.getElementById('settings-modal');
  const btnOpenSettings = document.getElementById('btn-open-settings');
  const btnCloseModal = document.getElementById('btn-close-modal');
  const settingsForm = document.getElementById('settings-form');
  const providerSelect = document.getElementById('provider-select');
  const modelInput = document.getElementById('model-input');
  const apiKeyInput = document.getElementById('api-key-input');
  const apikeyGroup = document.getElementById('apikey-group');
  const btnToggleKeyView = document.getElementById('btn-toggle-key-view');
  const baseUrlInput = document.getElementById('base-url-input');
  const baseurlGroup = document.getElementById('baseurl-group');

  // State
  let activeEventSource = null;
  let currentWorkspace = '';
  let currentSessionId = `mission_${Date.now()}`;
  let activeAgentTimeline = null;
  let timerInterval = null;
  let elapsedSeconds = 0;
  let currentUploadedFile = null;
  let speechRecognizer = null;
  let isRecording = false;
  let sfxEnabled = true;
  let audioCtx = null;
  let cachedSessions = [];
  let canvasAnimationId = null;

  // Initialize
  init();

  async function init() {
    initThemesAndWallpapers();
    initNeuralCanvas();
    await fetchConfig();
    await fetchFiles();
    await loadSessions();
    setupVoiceRecognition();
    bindEvents();
  }

  // --- Theme & Wallpaper Engine ---
  function initThemesAndWallpapers() {
    let savedTheme = localStorage.getItem('sakthidev_theme') || 'cyber-dark';
    if (savedTheme === 'studio-light') savedTheme = 'cyber-dark';
    setTheme(savedTheme);

    const savedBgType = localStorage.getItem('sakthidev_bg_type') || 'image';
    const savedBgSrc = localStorage.getItem('sakthidev_bg_src') || '/static/wallpaper_cyber_city.jpg';
    const savedOpacity = localStorage.getItem('sakthidev_bg_opacity') || '35';
    const savedBlur = localStorage.getItem('sakthidev_bg_blur') || '16';

    applyBackground(savedBgType, savedBgSrc);
    applyOpacity(savedOpacity);
    applyBlur(savedBlur);

    if (sliderBgOpacity) sliderBgOpacity.value = savedOpacity;
    if (sliderBgBlur) sliderBgBlur.value = savedBlur;
  }

  function setTheme(theme) {
    if (theme === 'studio-light') theme = 'cyber-dark';
    htmlRoot.setAttribute('data-theme', theme);
    localStorage.setItem('sakthidev_theme', theme);

    document.querySelectorAll('.theme-pick-btn').forEach(btn => {
      if (btn.getAttribute('data-set-theme') === theme) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  }

  function applyBackground(type, src) {
    localStorage.setItem('sakthidev_bg_type', type);
    localStorage.setItem('sakthidev_bg_src', src);

    if (type === 'image') {
      bgImageLayer.style.display = 'block';
      bgImageLayer.style.backgroundImage = `url('${src}')`;
      bgCanvas.style.display = 'none';
      bgVideoLayer.style.display = 'none';
    } else if (type === 'canvas') {
      bgImageLayer.style.display = 'none';
      bgCanvas.style.display = 'block';
      bgVideoLayer.style.display = 'none';
    } else if (type === 'video') {
      bgImageLayer.style.display = 'none';
      bgCanvas.style.display = 'none';
      bgVideoLayer.style.display = 'block';
      bgVideoLayer.src = src;
    } else {
      bgImageLayer.style.display = 'none';
      bgCanvas.style.display = 'none';
      bgVideoLayer.style.display = 'none';
    }

    // Highlight card
    document.querySelectorAll('.wallpaper-card').forEach(card => {
      const cType = card.getAttribute('data-bg-type');
      const cSrc = card.getAttribute('data-bg-src');
      if (cType === type && (type !== 'image' || cSrc === src)) {
        card.classList.add('active');
      } else {
        card.classList.remove('active');
      }
    });
  }

  function applyOpacity(val) {
    localStorage.setItem('sakthidev_bg_opacity', val);
    const op = val / 100;
    htmlRoot.style.setProperty('--bg-overlay-opacity', op);
    if (labelBgOpacity) labelBgOpacity.textContent = `${val}%`;
  }

  function applyBlur(val) {
    localStorage.setItem('sakthidev_bg_blur', val);
    htmlRoot.style.setProperty('--glass-blur', `${val}px`);
    if (labelBgBlur) labelBgBlur.textContent = `${val}px`;
  }

  // --- Interactive Neural Canvas Background ---
  function initNeuralCanvas() {
    if (!bgCanvas) return;
    const ctx = bgCanvas.getContext('2d');
    let width = bgCanvas.width = window.innerWidth;
    let height = bgCanvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
      width = bgCanvas.width = window.innerWidth;
      height = bgCanvas.height = window.innerHeight;
    });

    const particles = [];
    const particleCount = 45;

    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.6,
        vy: (Math.random() - 0.5) * 0.6,
        radius: Math.random() * 2 + 1,
        color: i % 2 === 0 ? '#38bdf8' : '#a855f7'
      });
    }

    function renderCanvas() {
      ctx.clearRect(0, 0, width, height);

      // Connect lines
      for (let i = 0; i < particleCount; i++) {
        for (let j = i + 1; j < particleCount; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 130) {
            ctx.beginPath();
            ctx.strokeStyle = `rgba(56, 189, 248, ${0.2 * (1 - dist / 130)})`;
            ctx.lineWidth = 0.8;
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }

      // Draw points
      for (let p of particles) {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.shadowColor = p.color;
        ctx.shadowBlur = 8;
        ctx.fill();

        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0 || p.x > width) p.vx *= -1;
        if (p.y < 0 || p.y > height) p.vy *= -1;
      }

      canvasAnimationId = requestAnimationFrame(renderCanvas);
    }

    renderCanvas();
  }

  // --- Web Audio Synthesizer SFX ---
  function playSfx(type = 'blip') {
    if (!sfxEnabled) return;
    try {
      if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      }
      if (audioCtx.state === 'suspended') {
        audioCtx.resume();
      }

      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.connect(gain);
      gain.connect(audioCtx.destination);

      const now = audioCtx.currentTime;
      if (type === 'blip') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(800, now);
        osc.frequency.exponentialRampToValueAtTime(400, now + 0.08);
        gain.gain.setValueAtTime(0.06, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
        osc.start(now);
        osc.stop(now + 0.08);
      } else if (type === 'dispatch') {
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(320, now);
        osc.frequency.exponentialRampToValueAtTime(960, now + 0.15);
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
        osc.start(now);
        osc.stop(now + 0.15);
      } else if (type === 'complete') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(523.25, now);
        osc.frequency.setValueAtTime(659.25, now + 0.08);
        osc.frequency.setValueAtTime(783.99, now + 0.16);
        gain.gain.setValueAtTime(0.1, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.28);
        osc.start(now);
        osc.stop(now + 0.28);
      }
    } catch (e) {
      console.warn('Audio SFX error:', e);
    }
  }

  function bindEvents() {
    // 1-Click Dark / Light Mode Switcher
    if (btnToggleTheme) {
      btnToggleTheme.addEventListener('click', () => {
        const cur = htmlRoot.getAttribute('data-theme') || 'cyber-dark';
        const next = cur === 'studio-light' ? 'cyber-dark' : 'studio-light';
        setTheme(next);
        playSfx('blip');
      });
    }

    // Wallpaper Modal
    if (btnOpenWallpapers && wallpaperModal) {
      btnOpenWallpapers.addEventListener('click', () => {
        wallpaperModal.classList.add('active');
        playSfx('blip');
      });
      btnCloseWallpaperModal.addEventListener('click', () => wallpaperModal.classList.remove('active'));
    }

    // Theme pickers inside modal
    document.querySelectorAll('.theme-pick-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const t = btn.getAttribute('data-set-theme');
        setTheme(t);
        playSfx('blip');
      });
    });

    // Wallpaper cards inside modal
    document.querySelectorAll('.wallpaper-card').forEach(card => {
      card.addEventListener('click', () => {
        const type = card.getAttribute('data-bg-type');
        const src = card.getAttribute('data-bg-src');
        applyBackground(type, src);
        playSfx('blip');
      });
    });

    // Opacity & Blur sliders
    if (sliderBgOpacity) {
      sliderBgOpacity.addEventListener('input', (e) => applyOpacity(e.target.value));
    }
    if (sliderBgBlur) {
      sliderBgBlur.addEventListener('input', (e) => applyBlur(e.target.value));
    }

    // Custom Wallpaper URL
    if (btnApplyCustomBg && customBgInput) {
      btnApplyCustomBg.addEventListener('click', () => {
        const url = customBgInput.value.trim();
        if (url) {
          const isVideo = url.endsWith('.mp4') || url.endsWith('.webm');
          applyBackground(isVideo ? 'video' : 'image', url);
          playSfx('blip');
        }
      });
    }

    // SFX Toggle
    if (btnToggleSfx) {
      btnToggleSfx.addEventListener('click', () => {
        sfxEnabled = !sfxEnabled;
        if (sfxEnabled) {
          btnToggleSfx.classList.add('active');
          sfxIcon.textContent = '🔊';
          playSfx('blip');
        } else {
          btnToggleSfx.classList.remove('active');
          sfxIcon.textContent = '🔇';
        }
      });
    }

    // Toggle History Sidebar
    if (btnToggleHistory && historySidebar) {
      btnToggleHistory.addEventListener('click', () => {
        historySidebar.classList.toggle('collapsed');
        playSfx('blip');
      });
    }

    // New Mission Button
    if (btnNewMission) {
      btnNewMission.addEventListener('click', startNewMission);
    }

    // Mission Search / Filter
    if (missionSearchInput) {
      missionSearchInput.addEventListener('input', (e) => {
        filterMissionList(e.target.value.trim().toLowerCase());
      });
    }

    // Clear All Sessions
    if (btnClearAllSessions) {
      btnClearAllSessions.addEventListener('click', handleClearAllSessions);
    }

    // Submit Task
    btnSubmit.addEventListener('click', triggerAgentTask);

    promptInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        triggerAgentTask();
      }
    });

    // Switch Workspace Folder
    btnSwitchWs.addEventListener('click', async () => {
      const p = wsInput.value.trim();
      if (p) await updateWorkspaceFolder(p);
    });

    wsInput.addEventListener('keydown', async (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        const p = wsInput.value.trim();
        if (p) await updateWorkspaceFolder(p);
      }
    });

    // Quick Preset Locations
    if (quickPresetSelect) {
      quickPresetSelect.addEventListener('change', async () => {
        const selected = quickPresetSelect.value;
        if (selected) {
          wsInput.value = selected;
          await updateWorkspaceFolder(selected);
          quickPresetSelect.value = '';
        }
      });
    }

    // Refresh Files
    btnRefreshFiles.addEventListener('click', () => fetchFiles());

    // Drawer Toggles
    if (btnToggleExplorer && rightDrawer) {
      btnToggleExplorer.addEventListener('click', () => {
        rightDrawer.classList.toggle('open');
        playSfx('blip');
      });
    }
    if (btnCloseDrawer && rightDrawer) {
      btnCloseDrawer.addEventListener('click', () => {
        rightDrawer.classList.remove('open');
      });
    }

    // File / Image Upload Events
    btnUploadFile.addEventListener('click', () => fileUploadInput.click());
    fileUploadInput.addEventListener('change', handleFileUpload);
    btnRemoveUpload.addEventListener('click', removeUploadedFile);

    // Voice Input Toggle
    btnVoiceInput.addEventListener('click', toggleVoiceRecording);

    // Mode Switchers
    toggleCloudMode.addEventListener('click', async () => {
      toggleCloudMode.classList.add('active');
      toggleOfflineMode.classList.remove('active');
      await saveMode('gemini', 'gemini-3.1-flash-lite');
      appendSystemBubble('☁️ Switched to <strong>Google Gemini Free Tier Cloud</strong> (Multimodal Vision Active).');
      playSfx('blip');
    });

    toggleOfflineMode.addEventListener('click', async () => {
      toggleOfflineMode.classList.add('active');
      toggleCloudMode.classList.remove('active');
      await saveMode('ollama', 'qwen2.5-coder:7b');
      appendSystemBubble('⚡ Switched to <strong>Offline Mode (Ollama)</strong>.<br><small style="color: var(--accent-amber);">Ollama daemon must be active locally.</small>');
      playSfx('blip');
    });

    // Settings Modal
    btnOpenSettings.addEventListener('click', () => {
      settingsModal.classList.add('active');
      playSfx('blip');
    });
    const hideModal = () => settingsModal.classList.remove('active');
    btnCloseModal.addEventListener('click', hideModal);

    // Toggle API Key Visibility
    if (btnToggleKeyView) {
      btnToggleKeyView.addEventListener('click', () => {
        if (apiKeyInput.type === 'password') {
          apiKeyInput.type = 'text';
          btnToggleKeyView.textContent = '🔒 Hide Key';
        } else {
          apiKeyInput.type = 'password';
          btnToggleKeyView.textContent = '👁 Show Key';
        }
      });
    }

    providerSelect.addEventListener('change', () => {
      const prov = providerSelect.value;
      if (prov === 'ollama') {
        modelInput.value = 'qwen2.5-coder:7b';
        apikeyGroup.style.display = 'none';
        baseurlGroup.style.display = 'block';
      } else if (prov === 'gemini') {
        modelInput.value = 'gemini-3.1-flash-lite';
        apikeyGroup.style.display = 'block';
        baseurlGroup.style.display = 'none';
      } else {
        modelInput.value = 'gpt-4o';
        apikeyGroup.style.display = 'block';
        baseurlGroup.style.display = 'block';
      }
    });

    settingsForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        provider: providerSelect.value,
        model: modelInput.value,
        api_key: apiKeyInput.value ? apiKeyInput.value.trim() : null,
        base_url: baseUrlInput.value ? baseUrlInput.value.trim() : null
      };

      try {
        const res = await fetch('/api/config', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          hideModal();
          await fetchConfig();
          appendSystemBubble('⚙️ Settings synchronized and saved to config.json.');
          playSfx('blip');
        }
      } catch (err) {
        alert('Failed to save settings: ' + err.message);
      }
    });
  }

  // --- Clickable Mission History Archives ---
  async function loadSessions() {
    try {
      const res = await fetch('/api/sessions');
      const data = await res.json();
      cachedSessions = data.sessions || [];
      renderMissionList(cachedSessions);

      if (dbMemCount) {
        dbMemCount.textContent = `${cachedSessions.length} MISSIONS LOGGED`;
      }
    } catch (err) {
      console.warn('Error loading sessions:', err);
      missionList.innerHTML = '<div class="mission-loading" style="color: var(--accent-rose);">Failed to load history</div>';
    }
  }

  function renderMissionList(sessions) {
    missionList.innerHTML = '';
    if (!sessions || sessions.length === 0) {
      missionList.innerHTML = `
        <div class="mission-loading">
          No previous missions.<br>
          <small style="color: var(--accent-cyan); cursor: pointer;" onclick="document.getElementById('prompt-input').focus()">Start by dispatching a task!</small>
        </div>
      `;
      return;
    }

    sessions.forEach(s => {
      const card = document.createElement('div');
      card.className = `mission-card ${s.id === currentSessionId ? 'active' : ''}`;
      card.setAttribute('data-id', s.id);

      const timeStr = formatRelativeTime(s.updated_at);
      const icon = getMissionIcon(s.title);

      card.innerHTML = `
        <span style="font-size: 0.95rem;">${icon}</span>
        <div class="mission-card-content">
          <div class="mission-title" title="${escapeHtml(s.title)}">${escapeHtml(s.title)}</div>
          <div class="mission-meta-row">
            <span>${timeStr}</span>
            <span class="mission-badge">${s.msg_count || 1} logs</span>
          </div>
        </div>
        <button class="btn-del-mission" data-del-id="${s.id}" title="Delete Mission Log">✕</button>
      `;

      card.addEventListener('click', (e) => {
        if (e.target.closest('.btn-del-mission')) return;
        selectMission(s.id, s.title, s.workspace);
      });

      const delBtn = card.querySelector('.btn-del-mission');
      delBtn.addEventListener('click', async (e) => {
        e.stopPropagation();
        await deleteMission(s.id);
      });

      missionList.appendChild(card);
    });
  }

  function filterMissionList(query) {
    if (!query) {
      renderMissionList(cachedSessions);
      return;
    }
    const filtered = cachedSessions.filter(s => 
      s.title.toLowerCase().includes(query) || (s.workspace && s.workspace.toLowerCase().includes(query))
    );
    renderMissionList(filtered);
  }

  async function selectMission(sessionId, title, workspace) {
    playSfx('blip');
    currentSessionId = sessionId;
    if (activeMissionLabel) {
      activeMissionLabel.textContent = title ? title.toUpperCase() : 'MISSION LOG';
    }

    document.querySelectorAll('.mission-card').forEach(c => {
      if (c.getAttribute('data-id') === sessionId) {
        c.classList.add('active');
      } else {
        c.classList.remove('active');
      }
    });

    if (workspace && workspace !== currentWorkspace) {
      wsInput.value = workspace;
      await updateWorkspaceFolder(workspace);
    }

    try {
      const res = await fetch(`/api/sessions/${sessionId}`);
      const data = await res.json();
      const messages = data.messages || [];

      chatStream.innerHTML = '';
      if (messages.length === 0) {
        renderWelcomeHero();
      } else {
        messages.forEach(m => {
          if (m.role === 'user') {
            appendUserBubble(m.content, false);
          } else if (m.role === 'assistant') {
            appendAssistantBubble(m.content);
          }
        });
        scrollToBottom();
      }
    } catch (e) {
      console.error('Error fetching mission details:', e);
    }
  }

  async function deleteMission(sessionId) {
    if (!confirm('Delete this mission log from archives?')) return;
    try {
      const res = await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' });
      if (res.ok) {
        if (currentSessionId === sessionId) {
          startNewMission();
        }
        await loadSessions();
        playSfx('blip');
      }
    } catch (e) {
      alert('Failed to delete mission: ' + e.message);
    }
  }

  function startNewMission() {
    playSfx('blip');
    currentSessionId = `mission_${Date.now()}`;
    if (activeMissionLabel) {
      activeMissionLabel.textContent = 'NEW AUTONOMOUS MISSION';
    }

    document.querySelectorAll('.mission-card').forEach(c => c.classList.remove('active'));

    chatStream.innerHTML = '';
    renderWelcomeHero();
    promptInput.value = '';
    promptInput.focus();
  }

  async function handleClearAllSessions() {
    if (!confirm('Are you sure you want to wipe ALL mission archives from SQLite?')) return;
    try {
      const res = await fetch('/api/history/clear', { method: 'POST' });
      if (res.ok) {
        startNewMission();
        await loadSessions();
        appendSystemBubble('🗑️ All mission logs and conversation memories wiped clean.');
      }
    } catch (e) {
      alert('Failed to clear sessions: ' + e.message);
    }
  }

  function renderWelcomeHero() {
    chatStream.innerHTML = `
      <div class="welcome-hero-card">
        <div class="hero-top-row">
          <div class="hero-avatar">⚡</div>
          <div>
            <h2 class="hero-greeting">Vanakkam da machan! 🔥</h2>
            <p class="hero-subtext">Un personal AI Software Engineer <strong>SakthiDev</strong> ready. Enna doubt-naalum kelu, coding or tasks naalum sollu panniduvom!</p>
          </div>
        </div>
      </div>
    `;
  }

  function getMissionIcon(title) {
    const t = (title || '').toLowerCase();
    if (t.includes('image') || t.includes('attachment') || t.includes('png') || t.includes('jpg')) return '🖼️';
    if (t.includes('blockchain') || t.includes('ledger') || t.includes('crypto')) return '⛓️';
    if (t.includes('test') || t.includes('bug') || t.includes('fix')) return '🐞';
    if (t.includes('file') || t.includes('search') || t.includes('find')) return '🔍';
    if (t.includes('build') || t.includes('app') || t.includes('project')) return '🚀';
    return '⚡';
  }

  function formatRelativeTime(timestamp) {
    if (!timestamp) return 'Just now';
    const now = Date.now() / 1000;
    const diff = Math.floor(now - timestamp);
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return new Date(timestamp * 1000).toLocaleDateString([], { month: 'short', day: 'numeric' });
  }

  // --- Voice Input (Web Speech Recognition) ---
  function setupVoiceRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      btnVoiceInput.title = 'Speech Recognition not supported in this browser';
      return;
    }

    speechRecognizer = new SpeechRecognition();
    speechRecognizer.continuous = false;
    speechRecognizer.interimResults = false;
    speechRecognizer.lang = 'en-US';

    speechRecognizer.onstart = () => {
      isRecording = true;
      btnVoiceInput.classList.add('recording');
      micIcon.textContent = '🔴';
      btnVoiceInput.querySelector('span:not(#mic-icon)')?.replaceWith(document.createTextNode(' Listening...'));
      playSfx('blip');
    };

    speechRecognizer.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      if (transcript) {
        const currentVal = promptInput.value.trim();
        promptInput.value = currentVal ? `${currentVal} ${transcript}` : transcript;
        promptInput.focus();
        playSfx('blip');
      }
    };

    speechRecognizer.onerror = (err) => {
      console.warn('Speech Recognition error:', err);
      resetVoiceState();
    };

    speechRecognizer.onend = () => {
      resetVoiceState();
    };
  }

  function toggleVoiceRecording() {
    if (!speechRecognizer) {
      alert('Speech Recognition is not supported by your current browser. Please type or use Chrome/Chromium.');
      return;
    }

    if (isRecording) {
      speechRecognizer.stop();
      resetVoiceState();
    } else {
      try {
        speechRecognizer.start();
      } catch (e) {
        console.error(e);
        resetVoiceState();
      }
    }
  }

  function resetVoiceState() {
    isRecording = false;
    btnVoiceInput.classList.remove('recording');
    micIcon.textContent = '🎤';
    btnVoiceInput.innerHTML = '<span id="mic-icon">🎤</span> Voice Input';
  }

  // --- File / Image Upload ---
  async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      btnUploadFile.disabled = true;
      btnUploadFile.innerHTML = '<span>⏳</span> Uploading...';
      playSfx('blip');

      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();

      if (res.ok) {
        currentUploadedFile = data;
        uploadPreviewName.textContent = data.filename;
        if (data.is_image) {
          uploadPreviewImg.src = data.url;
          uploadPreviewImg.style.display = 'block';
        } else {
          uploadPreviewImg.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="%2338bdf8" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>';
          uploadPreviewImg.style.display = 'block';
        }
        uploadPreviewBar.style.display = 'flex';
        playSfx('blip');
      } else {
        alert('Upload failed: ' + (data.detail || 'Unknown error'));
      }
    } catch (err) {
      alert('Error uploading file: ' + err.message);
    } finally {
      btnUploadFile.disabled = false;
      btnUploadFile.innerHTML = '<span>📎</span> Image / File';
      fileUploadInput.value = '';
    }
  }

  function removeUploadedFile() {
    currentUploadedFile = null;
    uploadPreviewBar.style.display = 'none';
    uploadPreviewImg.src = '';
    playSfx('blip');
  }

  // --- Config & Workspace ---
  async function saveMode(provider, model) {
    try {
      await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, model })
      });
      await fetchConfig();
    } catch (e) {
      console.error(e);
    }
  }

  async function fetchConfig() {
    try {
      const res = await fetch('/api/config');
      const cfg = await res.json();
      currentWorkspace = cfg.current_workspace || '';
      wsInput.value = currentWorkspace;
      dockWsLabel.textContent = formatShortPath(currentWorkspace);

      providerSelect.value = cfg.provider;
      modelInput.value = cfg.model;
      if (cfg.raw_key) apiKeyInput.value = cfg.raw_key;
      if (cfg.base_url) baseUrlInput.value = cfg.base_url;

      if (telemetryModelLabel) {
        telemetryModelLabel.textContent = cfg.model.toUpperCase();
      }

      if (cfg.provider === 'ollama') {
        toggleOfflineMode.classList.add('active');
        toggleCloudMode.classList.remove('active');
        apikeyGroup.style.display = 'none';
        baseurlGroup.style.display = 'block';
      } else {
        toggleCloudMode.classList.add('active');
        toggleOfflineMode.classList.remove('active');
        apikeyGroup.style.display = 'block';
        baseurlGroup.style.display = 'none';
      }
    } catch (e) {
      console.error(e);
    }
  }

  async function updateWorkspaceFolder(path) {
    try {
      const res = await fetch('/api/workspace', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workspace_path: path })
      });
      const data = await res.json();
      if (res.ok) {
        currentWorkspace = data.workspace_path;
        wsInput.value = currentWorkspace;
        dockWsLabel.textContent = formatShortPath(currentWorkspace);
        await fetchFiles();
        appendSystemBubble(`📁 Laptop target directory updated to: <code>${currentWorkspace}</code>`);
      } else {
        alert('Invalid path: ' + data.detail);
      }
    } catch (err) {
      alert('Error updating workspace: ' + err.message);
    }
  }

  async function fetchFiles() {
    try {
      const url = currentWorkspace 
        ? `/api/files?workspace_path=${encodeURIComponent(currentWorkspace)}`
        : '/api/files';
      const res = await fetch(url);
      const data = await res.json();
      fileBrowser.innerHTML = '';

      if (data.items && data.items.length > 0) {
        data.items.forEach(item => {
          const node = document.createElement('div');
          node.className = 'file-node';
          const icon = item.is_dir ? '📁' : '📄';
          node.innerHTML = `<span>${icon}</span> <span>${escapeHtml(item.rel_path)}</span>`;
          fileBrowser.appendChild(node);
        });
      } else {
        fileBrowser.innerHTML = `
          <div class="file-empty-banner">
            ✨ Empty Directory<br>
            SakthiDev is ready to build your project here!
          </div>
        `;
      }
    } catch (e) {
      fileBrowser.innerHTML = '<div class="file-node" style="color: var(--accent-rose);">Error listing directory</div>';
    }
  }

  // --- Task Execution ---
  function triggerAgentTask() {
    let text = promptInput.value.trim();
    if (!text && !currentUploadedFile) return;

    if (currentUploadedFile) {
      const fileNotice = `[Attachment: ${currentUploadedFile.filename} saved at ${currentUploadedFile.file_path}]\n`;
      text = text ? `${fileNotice}${text}` : `${fileNotice}Machan please inspect and process this file.`;
      removeUploadedFile();
    }

    promptInput.value = '';
    appendUserBubble(text);
    playSfx('dispatch');
    startLiveExecution(text);
  }

  function scrollToBottom() {
    requestAnimationFrame(() => {
      chatStream.scrollTop = chatStream.scrollHeight;
    });
  }

  function appendUserBubble(text, shouldScroll = true) {
    // Remove welcome hero if present
    const hero = chatStream.querySelector('.welcome-hero-card');
    if (hero) hero.remove();

    const row = document.createElement('div');
    row.className = 'chat-row';
    row.innerHTML = `
      <div class="avatar-badge avatar-user">S</div>
      <div class="message-body">
        <div class="author-title">
          <span>ARCHITECT SAKTHI // COMMAND DISPATCH</span>
          <span class="system-time-tag">USER VERIFIED</span>
        </div>
        <div class="user-text-bubble">${renderMarkdown(text)}</div>
      </div>
    `;
    chatStream.appendChild(row);
    if (shouldScroll) scrollToBottom();
  }

  function appendAssistantBubble(text) {
    const row = document.createElement('div');
    row.className = 'chat-row';
    row.innerHTML = `
      <div class="avatar-badge avatar-sakthidev">⚡</div>
      <div class="message-body">
        <div class="author-title">
          <span>SAKTHIDEV // AUTONOMOUS OPERATOR</span>
          <span class="system-time-tag">SYNCHRONIZED</span>
        </div>
        <div class="user-text-bubble agent-speech-bubble">${renderMarkdown(text)}</div>
      </div>
    `;
    chatStream.appendChild(row);
  }

  function appendSystemBubble(html) {
    const bubble = document.createElement('div');
    bubble.style.cssText = 'padding: 0.5rem 1rem; border-radius: 8px; background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.25); font-size: 0.8rem; color: #bae6fd; align-self: center; margin: 0.4rem 0; line-height: 1.4; font-family: var(--font-mono);';
    bubble.innerHTML = html;
    chatStream.appendChild(bubble);
    scrollToBottom();
  }

  function createAgentResponseBubble() {
    const row = document.createElement('div');
    row.className = 'chat-row';
    row.innerHTML = `
      <div class="avatar-badge avatar-sakthidev">⚡</div>
      <div class="message-body">
        <div class="author-title">
          <span>SAKTHIDEV // AUTONOMOUS OPERATOR</span>
          <span class="system-time-tag">ENGAGED</span>
        </div>
        <div class="agent-timeline"></div>
      </div>
    `;
    chatStream.appendChild(row);
    scrollToBottom();
    activeAgentTimeline = row.querySelector('.agent-timeline');
  }

  function startLiveExecution(instruction) {
    if (activeEventSource) {
      activeEventSource.close();
    }

    createAgentResponseBubble();
    startHudTimer();
    btnSubmit.disabled = true;

    const url = `/api/agent/stream?instruction=${encodeURIComponent(instruction)}&workspace_path=${encodeURIComponent(currentWorkspace)}&session_id=${encodeURIComponent(currentSessionId)}`;
    activeEventSource = new EventSource(url);

    activeEventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleStreamData(data);
      } catch (err) {
        console.error('Error handling SSE message:', err);
      }
    };

    activeEventSource.onerror = (err) => {
      console.error('SSE Error:', err);
      activeEventSource.close();
      stopHudTimer();
      btnSubmit.disabled = false;
      fetchFiles();
    };
  }

  function startHudTimer() {
    agentHud.classList.add('active');
    hudStatusText.textContent = 'SakthiDev is analyzing task & planning execution...';
    hudActiveTool.textContent = 'Planning';
    elapsedSeconds = 0;
    hudTimer.textContent = '⏱ 00:00s';
    
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
      elapsedSeconds++;
      const m = String(Math.floor(elapsedSeconds / 60)).padStart(2, '0');
      const s = String(elapsedSeconds % 60).padStart(2, '0');
      hudTimer.textContent = `⏱ ${m}:${s}s`;
    }, 1000);
  }

  function stopHudTimer() {
    if (timerInterval) clearInterval(timerInterval);
    agentHud.classList.remove('active');
  }

  // --- SSE Event Handler (No Raw JSON Dumps!) ---
  function handleStreamData(data) {
    const etype = data.type;

    if (etype === 'session_info') {
      currentSessionId = data.session_id;
    } else if (etype === 'thought') {
      hudStatusText.textContent = 'SakthiDev reasoning...';
      hudActiveTool.textContent = `Step ${data.step}`;
    } else if (etype === 'tool_start') {
      const tool = data.tool;
      const args = data.arguments || {};
      const actionSummary = getActionSummary(tool, args);

      hudStatusText.textContent = actionSummary.hudText;
      hudActiveTool.textContent = tool;

      const pillWrapper = document.createElement('div');
      pillWrapper.className = 'tool-action-pill-wrapper';
      pillWrapper.id = `runner_${data.call_id}`;

      pillWrapper.innerHTML = `
        <button type="button" class="tool-action-pill" title="Click to inspect execution details">
          <span>${actionSummary.icon}</span>
          <span>${escapeHtml(actionSummary.label)}</span>
          <span class="pill-status" style="color: var(--accent-cyan); font-size: 0.72rem;">⚡ running...</span>
          <span style="font-size: 0.7rem; opacity: 0.6; margin-left: 0.3rem;">▼</span>
        </button>
        <div class="tool-details-panel">
          <div style="color: var(--text-muted); font-size: 0.7rem; margin-bottom: 0.2rem;"><strong>Arguments:</strong></div>
          <pre style="margin: 0; font-size: 0.74rem;">${escapeHtml(JSON.stringify(args, null, 2))}</pre>
        </div>
      `;

      const pillBtn = pillWrapper.querySelector('.tool-action-pill');
      const panel = pillWrapper.querySelector('.tool-details-panel');
      pillBtn.addEventListener('click', () => {
        panel.classList.toggle('open');
        playSfx('blip');
      });

      activeAgentTimeline.appendChild(pillWrapper);
      scrollToBottom();

    } else if (etype === 'tool_result') {
      const pillWrapper = document.getElementById(`runner_${data.call_id}`);
      if (pillWrapper) {
        const statusSpan = pillWrapper.querySelector('.pill-status');
        if (statusSpan) {
          statusSpan.textContent = '✔ done';
          statusSpan.style.color = 'var(--accent-emerald)';
        }
        const panel = pillWrapper.querySelector('.tool-details-panel');
        if (panel) {
          const resStr = typeof data.result === 'object' ? JSON.stringify(data.result, null, 2) : String(data.result);
          const outDiv = document.createElement('div');
          outDiv.style.marginTop = '0.4rem';
          outDiv.innerHTML = `
            <div style="color: var(--accent-emerald); font-size: 0.7rem; margin-bottom: 0.2rem;"><strong>Output:</strong></div>
            <pre style="margin: 0; font-size: 0.74rem; max-height: 120px; overflow-y: auto;">${escapeHtml(resStr)}</pre>
          `;
          panel.appendChild(outDiv);
        }
      }
      fetchFiles();
      scrollToBottom();

    } else if (etype === 'completed') {
      stopHudTimer();
      btnSubmit.disabled = false;
      playSfx('complete');

      const speechBubble = document.createElement('div');
      speechBubble.className = 'user-text-bubble agent-speech-bubble';
      speechBubble.style.marginTop = '0.5rem';
      speechBubble.innerHTML = renderMarkdown(data.summary || 'Task completed da machan!');
      activeAgentTimeline.appendChild(speechBubble);

      scrollToBottom();
      if (activeEventSource) activeEventSource.close();
      fetchFiles();
      loadSessions();

    } else if (etype === 'error' || etype === 'max_steps_reached') {
      stopHudTimer();
      btnSubmit.disabled = false;

      const bubble = document.createElement('div');
      bubble.style.cssText = 'padding: 0.85rem 1.2rem; border-radius: 8px; background: rgba(244, 63, 94, 0.1); border: 1px solid var(--accent-rose); color: #fda4af; font-size: 0.88rem; margin-top: 0.5rem; font-family: var(--font-mono);';
      bubble.innerHTML = `<strong>❌ Issue:</strong> ${escapeHtml(data.message)}`;
      activeAgentTimeline.appendChild(bubble);

      scrollToBottom();
      if (activeEventSource) activeEventSource.close();
      fetchFiles();
    }
  }

  function getActionSummary(tool, args) {
    if (tool === 'write_file') {
      const file = args.file_path || 'file';
      return { icon: '✏️', label: `Wrote ${formatShortPath(file)}`, hudText: `Writing code to ${file}...` };
    }
    if (tool === 'edit_file') {
      const file = args.file_path || 'file';
      return { icon: '🛠️', label: `Updated ${formatShortPath(file)}`, hudText: `Patching code in ${file}...` };
    }
    if (tool === 'read_file') {
      const file = args.file_path || 'file';
      return { icon: '📖', label: `Read ${formatShortPath(file)}`, hudText: `Reading ${file}...` };
    }
    if (tool === 'run_command') {
      const cmd = args.command || 'bash';
      const shortCmd = cmd.length > 28 ? cmd.slice(0, 25) + '...' : cmd;
      return { icon: '⚡', label: `Bash: ${shortCmd}`, hudText: `Executing command...` };
    }
    if (tool === 'list_directory') {
      return { icon: '📁', label: `Scanned directory`, hudText: `Exploring files in workspace...` };
    }
    if (tool === 'remember') {
      return { icon: '💾', label: `Stored memory: ${args.key || 'fact'}`, hudText: `Saving to SQLite memory...` };
    }
    if (tool === 'task_completed') {
      return { icon: '🎯', label: `Finalized solution`, hudText: `Finalizing solution...` };
    }
    return { icon: '🔧', label: `Used ${tool}`, hudText: `Running ${tool}...` };
  }

  function renderMarkdown(text) {
    if (!text) return '';
    let rendered = escapeHtml(text);

    // Code Blocks: ```code```
    rendered = rendered.replace(/```([\s\S]*?)```/g, (match, p1) => {
      return `<pre style="background: rgba(0,0,0,0.65); padding: 0.85rem; border-radius: 6px; border: 1px solid rgba(56,189,248,0.25); font-family: var(--font-mono); font-size: 0.82rem; overflow-x: auto; margin: 0.6rem 0;"><code>${p1.trim()}</code></pre>`;
    });

    // Inline code: `code`
    rendered = rendered.replace(/`([^`]+)`/g, '<code style="background: rgba(56,189,248,0.12); color: #7dd3fc; padding: 0.12rem 0.38rem; border-radius: 4px; font-family: var(--font-mono); font-size: 0.82rem;">$1</code>');

    // Bold: **text**
    rendered = rendered.replace(/\*\*([^*]+)\*\*/g, '<strong style="font-weight: 700;">$1</strong>');

    // Newlines to <br>
    rendered = rendered.replace(/\n/g, '<br>');

    return rendered;
  }

  function formatShortPath(path) {
    if (!path) return '';
    const parts = path.split('/');
    return parts.length > 2 ? '.../' + parts.slice(-2).join('/') : path;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});
