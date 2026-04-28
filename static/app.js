(function () {
  'use strict';

  // ── State ──────────────────────────────────────────────────────────────────
  let sessionId = null;
  let isWaiting = false;

  // ── DOM refs ───────────────────────────────────────────────────────────────
  const chatArea      = document.getElementById('chat-area');
  const welcome       = document.getElementById('welcome');
  const input         = document.getElementById('message-input');
  const btnSend       = document.getElementById('btn-send');
  const btnNew        = document.getElementById('btn-new-session');
  const themeToggle   = document.getElementById('theme-toggle');
  const crisisBanner  = document.getElementById('crisis-banner');
  const html          = document.documentElement;

  // ── Theme ──────────────────────────────────────────────────────────────────
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  let currentTheme = prefersDark ? 'dark' : 'light';
  html.setAttribute('data-theme', currentTheme);
  updateThemeIcon();

  themeToggle.addEventListener('click', () => {
    currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', currentTheme);
    themeToggle.setAttribute('aria-label',
      `Switch to ${currentTheme === 'dark' ? 'light' : 'dark'} mode`);
    updateThemeIcon();
  });

  function updateThemeIcon() {
    themeToggle.innerHTML = currentTheme === 'dark'
      ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none"
           stroke="currentColor" stroke-width="2" aria-hidden="true">
           <circle cx="12" cy="12" r="5"/>
           <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42
                    M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
         </svg>`
      : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none"
           stroke="currentColor" stroke-width="2" aria-hidden="true">
           <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
         </svg>`;
  }

  // ── Auto-resize textarea ───────────────────────────────────────────────────
  input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 160) + 'px';
  });

  // ── Enter key ──────────────────────────────────────────────────────────────
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  btnSend.addEventListener('click', sendMessage);

  // ── Starter buttons ────────────────────────────────────────────────────────
  document.querySelectorAll('.starter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      input.value = btn.dataset.msg;
      input.style.height = 'auto';
      input.style.height = Math.min(input.scrollHeight, 160) + 'px';
      sendMessage();
    });
  });

  // ── New session ────────────────────────────────────────────────────────────
  btnNew.addEventListener('click', async () => {
    if (!confirm('Start a new session? This will clear the current conversation.')) return;
    await fetch('/new-session', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({session_id: sessionId}),
    });
    sessionId = null;
    personaSentForSession = false;
    isWaiting = false;
    forcePromptOnce = true;
    dismissPersonaPrompt();
    crisisBanner.classList.remove('visible');
    // Clear messages but keep welcome
    Array.from(chatArea.children).forEach(el => {
      if (el.id !== 'welcome') el.remove();
    });
    welcome.style.display = '';
    input.value = '';
    input.style.height = 'auto';
    btnSend.disabled = false;
  });

  // ── Crisis keyword detection ───────────────────────────────────────────────
  const CRISIS_KEYWORDS = [
    'hurt myself', 'end it', "can't go on", 'hopeless', 'no point',
    'suicide', 'self-harm', 'give up', "don't want to be here",
    'want to die', 'not worth it',
  ];
  function checkCrisis(text) {
    const lower = text.toLowerCase();
    return CRISIS_KEYWORDS.some(kw => lower.includes(kw));
  }

  // ── Send message ───────────────────────────────────────────────────────────
  async function sendMessage() {
    const text = input.value.trim();
    if (!text || isWaiting) return;

    // Hide welcome on first message
    welcome.style.display = 'none';

    // Show crisis banner if needed
    if (checkCrisis(text)) crisisBanner.classList.add('visible');

    appendMessage('user', text);
    input.value = '';
    input.style.height = 'auto';

    isWaiting = true;
    btnSend.disabled = true;

    const typingEl = showTyping();

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: buildBody(text),
      });
      const data = await res.json();

      typingEl.remove();
      isWaiting = false;
      btnSend.disabled = false;

      if (data.error) {
        appendMessage('coach', `⚠ Something went wrong: ${data.error}`);
      } else {
        sessionId = data.session_id;
        appendMessage('coach', data.response);
        if (checkCrisis(data.response)) crisisBanner.classList.add('visible');
      }
    } catch (err) {
      typingEl.remove();
      isWaiting = false;
      btnSend.disabled = false;
      appendMessage('coach',
        '⚠ Could not reach the server. Check your connection and try again.');
    }

    input.focus();
  }

  // ── Append a message bubble ────────────────────────────────────────────────
  function appendMessage(role, text) {
    const row = document.createElement('div');
    row.className = `message-row ${role}`;
    row.setAttribute('role', 'listitem');

    const avatar = document.createElement('div');
    avatar.className = `avatar ${role}`;
    avatar.textContent = role === 'coach' ? '🌱' : 'You';
    avatar.setAttribute('aria-hidden', 'true');

    const bubble = document.createElement('div');
    bubble.className = `bubble ${role}`;
    bubble.textContent = text;

    row.appendChild(avatar);
    row.appendChild(bubble);
    chatArea.appendChild(row);
    scrollToBottom();
  }

  // ── Typing indicator ───────────────────────────────────────────────────────
  function showTyping() {
    const row = document.createElement('div');
    row.className = 'message-row coach typing-row';
    row.setAttribute('aria-label', 'Coach is typing');
    row.setAttribute('aria-live', 'polite');

    const avatar = document.createElement('div');
    avatar.className = 'avatar coach';
    avatar.textContent = '🌱';
    avatar.setAttribute('aria-hidden', 'true');

    const bubble = document.createElement('div');
    bubble.className = 'typing-bubble';
    bubble.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';

    row.appendChild(avatar);
    row.appendChild(bubble);
    chatArea.appendChild(row);
    scrollToBottom();
    return row;
  }

  // ── Scroll ─────────────────────────────────────────────────────────────────
  function scrollToBottom() {
    chatArea.scrollTo({top: chatArea.scrollHeight, behavior: 'smooth'});
  }

  // ── Focus input on load ────────────────────────────────────────────────────
  input.focus();

  // ── Persona panel ──────────────────────────────────────────────────────
  let personaData = null;
  let personaSentForSession = false;

  const personaTab     = document.getElementById('persona-tab');
  const personaOverlay = document.getElementById('persona-overlay');
  const personaPanel   = document.getElementById('persona-panel');
  const personaClose   = document.getElementById('persona-close');
  const btnSavePersona = document.getElementById('btn-save-persona');
  const btnSkipPersona = document.getElementById('btn-skip-persona');

  function openPersonaPanel() {
    dismissPersonaPrompt();
    personaPanel.classList.add('open');
    personaOverlay.classList.add('open');
    personaTab.setAttribute('aria-expanded', 'true');
    personaClose.focus();
  }
  function closePersonaPanel() {
    personaPanel.classList.remove('open');
    personaOverlay.classList.remove('open');
    personaTab.setAttribute('aria-expanded', 'false');
    personaTab.focus();
  }

  // ── Persona nudge ──────────────────────────────────────────────────────
  // Default: shows on every input click while persona is at its defaults.
  // New-session override: forces the popup to appear once on the next input
  // click even if the user has already filled out their persona — and uses
  // the "update your profile" wording instead of the default "fill out" tip.
  const personaPrompt      = document.getElementById('persona-prompt');
  const personaPromptClose = document.getElementById('persona-prompt-close');
  let forcePromptOnce = false;

  function showPersonaPrompt() {
    if (!forcePromptOnce && personaData) return;
    const updateMode = forcePromptOnce && personaData !== null;
    forcePromptOnce = false;
    personaPrompt.classList.toggle('update-mode', updateMode);
    personaPrompt.hidden = false;
    personaPrompt.classList.add('open');
  }
  function dismissPersonaPrompt() {
    personaPrompt.classList.remove('open');
    personaPrompt.hidden = true;
  }

  input.addEventListener('click', showPersonaPrompt);

  personaPrompt.querySelectorAll('[data-persona-open]').forEach(btn => {
    btn.addEventListener('click', () => {
      dismissPersonaPrompt();
      openPersonaPanel();
    });
  });
  personaPromptClose.addEventListener('click', dismissPersonaPrompt);

  personaTab.addEventListener('click', openPersonaPanel);
  personaClose.addEventListener('click', closePersonaPanel);
  personaOverlay.addEventListener('click', closePersonaPanel);
  btnSkipPersona.addEventListener('click', () => {
    personaData = null;
    closePersonaPanel();
  });

  document.addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    if (personaPanel.classList.contains('open')) {
      closePersonaPanel();
    } else if (personaPrompt.classList.contains('open')) {
      dismissPersonaPrompt();
    }
  });

  btnSavePersona.addEventListener('click', () => {
    const name = document.getElementById('persona-name').value.trim();
    const age  = document.getElementById('persona-age').value.trim();
    const conditions = Array.from(
      document.querySelectorAll('input[name="condition"]:checked')
    ).map(cb => cb.value);
    const otherCondition = document.getElementById('condition-other').value.trim();
    if (otherCondition && conditions.includes('Other')) {
      const idx = conditions.indexOf('Other');
      conditions[idx] = otherCondition;
    }
    const backstory  = document.getElementById('persona-backstory').value.trim();
    const triggers   = document.getElementById('persona-triggers').value.trim();
    const strengths  = document.getElementById('persona-strengths').value.trim();
    const success    = document.getElementById('persona-success').value.trim();

    personaData = {};
    if (name)       personaData.name = name;
    if (age)        personaData.age  = parseInt(age, 10);
    if (conditions.length) personaData.conditions = conditions;
    if (backstory)  personaData.backstory = backstory;
    if (triggers)   personaData.emotional_triggers = triggers;
    if (strengths)  personaData.existing_strengths = strengths;
    if (success)    personaData.what_success_looks_like = success;

    personaTab.classList.add('has-data');
    closePersonaPanel();
  });

  // Builds the /chat fetch body, attaching persona on first message of session
  function buildBody(text) {
    const body = { message: text, session_id: sessionId };
    if (!personaSentForSession && personaData) {
      body.persona = personaData;
      personaSentForSession = true;
    }
    return JSON.stringify(body);
  }
})();
