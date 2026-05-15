// Smart-input router + category grid.
// Loads data/tools.json, detects input type via regex, filters and renders cards.

const CATEGORY_LABELS = {
  username: 'Username & Social',
  person:   'People Search',
  email:    'Email Intelligence',
  phone:    'Phone & Telecom',
  domain:   'Domain & DNS',
  ip:       'IP & Infrastructure',
  image:    'Image & Media',
  geo:      'Geolocation & Maps',
  records:  'Public Records',
  leaks:    'Leaks & Breaches',
  dorks:    'Search & Dorks',
  archives: 'Archives & News',
  vehicle:  'Vehicles & Transport',
  general:  'General OSINT',
};

const CATEGORY_ORDER = [
  'username', 'person', 'email', 'phone', 'domain', 'ip',
  'image', 'geo', 'records', 'leaks', 'dorks', 'archives',
  'vehicle', 'general'
];

let TOOLS = [];

function detectInputType(v) {
  v = v.trim();
  if (!v) return null;
  if (/^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i.test(v)) return 'email';
  if (/^https?:\/\//i.test(v)) return 'url';
  if (/^\+?[\d][\d\s()\-]{6,14}$/.test(v) && (v.match(/\d/g) || []).length >= 7) return 'phone';
  if (/^[A-Z0-9][A-Z0-9\s\-]{1,8}$/i.test(v) && /[A-Z]/i.test(v) && /\d/.test(v)) return 'license_plate';
  if (/^[a-z0-9][a-z0-9\-]*(\.[a-z0-9\-]+)+$/i.test(v) && !v.includes('@')) return 'domain';
  if (/^[A-Z][a-z]+(\s+[A-Z][a-z]+)+$/.test(v)) return 'person';
  return 'username';
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
  }[c]));
}

function renderTools(tools, container, limit) {
  if (limit) tools = tools.slice(0, limit);
  if (tools.length === 0) {
    container.innerHTML = '<p class="empty">No tools match that input type.</p>';
    return;
  }
  container.innerHTML = tools.map(t => `
    <a class="tool-card" href="${escapeHtml(t.url)}" target="_blank" rel="noopener noreferrer">
      <h3>${escapeHtml(t.name)}</h3>
      <span class="category">${escapeHtml(CATEGORY_LABELS[t.category] || t.category)}</span>
    </a>
  `).join('');
}

function renderCategoryGrid() {
  const counts = {};
  TOOLS.forEach(t => { counts[t.category] = (counts[t.category] || 0) + 1; });
  const grid = document.getElementById('category-grid');
  grid.innerHTML = CATEGORY_ORDER.map(slug => `
    <a class="category-card" href="/${slug}/">
      <h3>${CATEGORY_LABELS[slug]}</h3>
      <span class="count">${counts[slug] || 0} tools</span>
    </a>
  `).join('');
}

function wireSmartInput() {
  const input = document.getElementById('smart-input');
  const detected = document.getElementById('detected');
  const results = document.getElementById('tool-results');

  input.addEventListener('input', () => {
    const v = input.value;
    const type = detectInputType(v);
    if (!type) {
      detected.textContent = '';
      results.innerHTML = '';
      return;
    }
    detected.textContent = `Detected: ${type.replace('_', ' ')}`;
    const matches = TOOLS.filter(t => t.inputTypes && t.inputTypes.includes(type));
    renderTools(matches, results, 30);
  });
}

fetch('data/tools.json')
  .then(r => r.json())
  .then(tools => {
    TOOLS = tools;
    renderCategoryGrid();
    wireSmartInput();
  })
  .catch(err => {
    console.error('Failed to load tools.json:', err);
    document.getElementById('category-grid').innerHTML = '<p class="empty">Tools data failed to load.</p>';
  });
