const fieldLabels = {
  question: 'Question',
  method: 'What I did',
  result: 'Result and next step',
};
const entryFields = ['title', ...Object.keys(fieldLabels), 'evidence'];
const storageKey = 'research-logbook-draft-v1';
const get = id => document.getElementById('draft-' + id);
const form = get('form');
const nav = get('goals');
const reading = get('reading');
const editor = get('editor');
let book = readSaved() || blankBook();
let selection = firstEntry(book).id;

function firstEntry(data) {
  return data.goals.find(group => group.entries.length)?.entries[0];
}

function blankEntry() {
  return {
    id: crypto.randomUUID(),
    ...Object.fromEntries(entryFields.map(key => [key, ''])),
  };
}

function blankBook() {
  return { version: 1, title: '', goals: [{ title: '', entries: [blankEntry()] }] };
}

function readBook(raw) {
  const data = JSON.parse(raw);
  if (data?.version !== 1 || typeof data.title !== 'string' || !data.goals?.length || !Array.isArray(data.goals)) {
    throw new Error('Choose a draft saved by the Research logbook.');
  }
  const ids = new Set();
  const goals = data.goals.map(group => {
    if (typeof group?.title !== 'string' || !Array.isArray(group.entries)) {
      throw new Error('The draft contains an invalid goal.');
    }
    return {
      title: group.title,
      entries: group.entries.map(entry => {
        if (typeof entry?.id !== 'string' || ids.has(entry.id) || entryFields.some(key => typeof entry[key] !== 'string')) {
          throw new Error('The draft has an incomplete or repeated entry.');
        }
        ids.add(entry.id);
        return { id: entry.id, ...Object.fromEntries(entryFields.map(key => [key, entry[key]])) };
      }),
    };
  });
  if (!ids.size) throw new Error('The draft has no entries.');
  return { version: 1, title: data.title, goals };
}

function readSaved() {
  try {
    const raw = localStorage.getItem(storageKey);
    return raw ? readBook(raw) : null;
  } catch {
    return null;
  }
}

function save() {
  try {
    localStorage.setItem(storageKey, JSON.stringify(book));
    get('status').textContent = 'Draft saved in this browser.';
  } catch {
    get('status').textContent = 'Browser storage is unavailable. Save a draft file to keep your work.';
  }
}

function active() {
  for (const group of book.goals) {
    const entry = group.entries.find(item => item.id === selection);
    if (entry) return { group, entry };
  }
}

function html(value) {
  const replacements = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
  return String(value).replace(/[&<>"']/g, character => replacements[character]);
}

function evidenceMarkup(value) {
  const reference = value.trim();
  if (!reference) return '';
  if (/^https?:\/\//i.test(reference)) {
    try {
      const url = new URL(reference);
      return '<p><a href="' + html(url.href) + '">Open evidence</a></p>';
    } catch {
      // Keep incomplete links visible as written.
    }
  }
  return '<p><strong>Evidence:</strong> ' + html(reference) + '</p>';
}

function entryMarkup(entry, level) {
  const sections = Object.entries(fieldLabels).filter(([key]) => entry[key].trim()).map(([key, label]) =>
    '<section><h' + (level + 1) + '>' + label + '</h' + (level + 1) + '><p>' + html(entry[key]) + '</p></section>'
  );
  const title = '<h' + level + '>' + html(entry.title || 'Untitled entry') + '</h' + level + '>';
  return title + sections.join('') + evidenceMarkup(entry.evidence);
}

function refreshTree() {
  const state = active();
  const groups = [...nav.querySelectorAll('details')];
  nav.replaceChildren();
  book.goals.forEach((group, index) => {
    const box = document.createElement('details');
    box.className = 'draft-group';
    box.open = group === state.group || Boolean(groups[index]?.open);
    const summary = document.createElement('summary');
    summary.textContent = group.title || 'Untitled goal';
    const list = document.createElement('ul');
    for (const entry of group.entries) {
      const li = document.createElement('li');
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'draft-entry-link';
      button.textContent = entry.title || 'Untitled entry';
      button.dataset.entry = entry.id;
      if (entry === state.entry) button.setAttribute('aria-current', 'page');
      li.append(button);
      list.append(li);
    }
    const add = document.createElement('button');
    add.type = 'button';
    add.textContent = 'Add entry';
    add.dataset.add = index;
    box.append(summary, list, add);
    nav.append(box);
  });
}

function show() {
  const { group, entry } = active();
  get('title').value = book.title;
  form.elements.goal.value = group.title;
  for (const field of entryFields) form.elements[field].value = entry[field];
  const moves = get('move');
  moves.replaceChildren(new Option('Choose a goal', ''));
  book.goals.forEach((option, index) => {
    if (option !== group) moves.add(new Option(option.title || 'Untitled goal', index));
  });
  get('move-row').hidden = book.goals.length < 2;
  reading.innerHTML = entryMarkup(entry, 2);
  refreshTree();
}

function setEditing(editing) {
  editor.hidden = !editing;
  reading.hidden = editing;
  get('preview').setAttribute('aria-pressed', String(!editing));
  get('preview').textContent = editing ? 'Preview' : 'Continue editing';
}

function startEntry(group, newGoal = false) {
  const entry = blankEntry();
  group.entries.push(entry);
  selection = entry.id;
  setEditing(true);
  save();
  show();
  form.elements[newGoal ? 'goal' : 'title'].focus();
}

get('title').addEventListener('input', event => {
  book.title = event.target.value;
  save();
});
form.addEventListener('input', event => {
  const { group, entry } = active();
  const { name, value } = event.target;
  if (name === 'goal') group.title = value;
  else if (entryFields.includes(name)) entry[name] = value;
  else return;
  if (name === 'goal' || name === 'title') refreshTree();
  save();
});
form.addEventListener('submit', event => event.preventDefault());
get('preview').addEventListener('click', () => {
  reading.innerHTML = entryMarkup(active().entry, 2);
  setEditing(editor.hidden);
});
nav.addEventListener('click', event => {
  const button = event.target.closest('button');
  if (button?.dataset.entry) {
    selection = button.dataset.entry;
    show();
    const target = [...nav.querySelectorAll('[data-entry]')].find(link => link.dataset.entry === selection);
    target?.focus();
  } else if (button?.hasAttribute('data-add')) {
    startEntry(book.goals[Number(button.dataset.add)]);
  }
});
get('add-goal').addEventListener('click', () => {
  const group = { title: '', entries: [] };
  book.goals.push(group);
  startEntry(group, true);
});
get('move').addEventListener('change', event => {
  if (event.target.value === '') return;
  const { group, entry } = active();
  const target = book.goals[Number(event.target.value)];
  if (!target || target === group) return;
  target.entries.push(entry);
  group.entries = group.entries.filter(item => item !== entry);
  save();
  show();
});
get('delete').addEventListener('click', () => {
  const { group, entry } = active();
  if (!confirm('Delete this entry from your draft?')) return;
  group.entries = group.entries.filter(item => item !== entry);
  if (!firstEntry(book)) group.entries.push(blankEntry());
  selection = (group.entries[0] || firstEntry(book)).id;
  save();
  show();
  form.elements.title.focus();
});

function useBook(nextBook) {
  book = nextBook;
  selection = firstEntry(book).id;
  setEditing(true);
  save();
  show();
}

get('new').addEventListener('click', () => {
  if (confirm('Start a new logbook? This replaces the current browser draft. Save a draft file first if you want to keep it.')) {
    useBook(blankBook());
    get('title').focus();
  }
});
const upload = get('file');
get('open').addEventListener('click', () => upload.click());
upload.addEventListener('change', async () => {
  const file = upload.files[0];
  upload.value = '';
  if (!file) return;
  try {
    const nextBook = readBook(await file.text());
    if (confirm('Open this file and replace the current browser draft?')) useBook(nextBook);
  } catch (error) {
    get('status').textContent = error instanceof SyntaxError ? 'This file is not a logbook draft.' : error.message;
  }
});

function download(filename, type, content) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

get('save').addEventListener('click', () => download('research-draft.json', 'application/json', JSON.stringify(book, null, 2)));
get('export').addEventListener('click', () => {
  const title = html(book.title || 'Research logbook');
  const links = book.goals.map((goal, index) =>
    '<li><a href="#goal-' + index + '">' + html(goal.title || 'Untitled goal') + '</a></li>'
  ).join('');
  const goals = book.goals.map((goal, index) =>
    '<section id="goal-' + index + '"><h2>' + html(goal.title || 'Untitled goal') + '</h2>' +
    goal.entries.map(entry => '<article>' + entryMarkup(entry, 3) + '</article>').join('') + '</section>'
  ).join('');
  const style = 'body{margin:0;background:#f7f5ec;color:#22352b;font:16px/1.6 system-ui}main{max-width:720px;padding:24px;margin:auto;overflow-wrap:anywhere}a{color:#315744}article{border-top:1px solid #cad4c9;margin:20px 0}article p{white-space:pre-wrap}h4{margin-bottom:0}h4+p{margin-top:4px}';
  const content = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' +
    '<title>' + title + '</title><style>' + style + '</style><main><h1>' + title + '</h1><nav aria-label="Goals"><ul>' +
    links + '</ul></nav>' + goals + '</main></html>';
  download('research-logbook.html', 'text/html;charset=utf-8', content);
});

show();
get('status').textContent = 'Changes are saved in this browser as you type.';
