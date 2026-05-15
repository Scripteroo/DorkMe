// Google dork builder. Composes a query string from form inputs,
// updates the live preview, opens the result in a new tab on launch.
// No network requests except the final user-initiated Google search.

const DORK_FIELDS = ['site', 'filetype', 'intitle', 'inurl', 'exact', 'exclude'];

function buildQuery() {
  const v = id => document.getElementById('dork-' + id).value.trim();
  const parts = [];
  if (v('site')) parts.push(`site:${v('site')}`);
  if (v('filetype')) parts.push(`filetype:${v('filetype')}`);
  if (v('intitle')) parts.push(`intitle:${v('intitle')}`);
  if (v('inurl')) parts.push(`inurl:${v('inurl')}`);
  if (v('exact')) parts.push(`"${v('exact').replace(/"/g, '')}"`);
  if (v('exclude')) {
    v('exclude').split(/\s+/).forEach(term => {
      if (!term) return;
      parts.push(term.startsWith('-') ? term : `-${term}`);
    });
  }
  return parts.join(' ');
}

function updatePreview() {
  const q = buildQuery();
  const el = document.getElementById('dork-query');
  if (q) {
    el.textContent = q;
    el.classList.remove('empty');
  } else {
    el.textContent = 'your query will appear here...';
    el.classList.add('empty');
  }
}

function showFeedback(text) {
  const f = document.getElementById('dork-feedback');
  f.textContent = text;
  f.classList.add('show');
  setTimeout(() => f.classList.remove('show'), 1500);
}

document.addEventListener('DOMContentLoaded', () => {
  DORK_FIELDS.forEach(id => {
    const el = document.getElementById('dork-' + id);
    if (el) el.addEventListener('input', updatePreview);
  });

  document.getElementById('dork-copy').addEventListener('click', async () => {
    const q = buildQuery();
    if (!q) return showFeedback('Empty');
    try {
      await navigator.clipboard.writeText(q);
      showFeedback('Copied');
    } catch {
      showFeedback('Copy failed');
    }
  });

  document.getElementById('dork-launch').addEventListener('click', () => {
    const q = buildQuery();
    if (!q) return showFeedback('Empty');
    window.open('https://www.google.com/search?q=' + encodeURIComponent(q), '_blank');
  });

  updatePreview();
});
