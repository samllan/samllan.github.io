const fieldLabels = {
  question: 'Question',
  method: 'What I did',
  result: 'Result and next step',
};
const fields = {
  entry: ['title', ...Object.keys(fieldLabels), 'evidence'],
  section: ['title', 'body'],
};
const storageKey = 'research-logbook-draft-v1';
const get = id => document.getElementById('draft-' + id);
const form = get('form');
const nav = get('goals');
const reading = get('reading');
const editor = get('editor');
const rootDrop = get('root-drop');
const collapsed = new Set();
let book = readSaved() || blankBook();
let selection = book.pages[0]?.children?.[0]?.id || book.pages[0]?.id;
let dragging;

function newPage(type) {
  return {
    id: crypto.randomUUID(), type,
    ...Object.fromEntries(fields[type].map(key => [key, ''])),
    ...(type === 'section' ? { children: [] } : {}),
  };
}

function blankBook() {
  const section = newPage('section');
  section.children.push(newPage('entry'));
  return { version: 2, title: '', pages: [section] };
}

function readBook(raw) {
  const data = JSON.parse(raw);
  if (typeof data?.title !== 'string' || ![1, 2].includes(data.version)) {
    throw new Error('Choose a draft saved by the Research logbook.');
  }
  const ids = new Set();
  function validate(pages) {
    if (!Array.isArray(pages)) throw new Error('The draft has an invalid page list.');
    return pages.map(page => {
      const keys = page?.type === 'entry' || page?.type === 'section' ? fields[page.type] : null;
      if (!keys || typeof page.id !== 'string' || !page.id || ids.has(page.id)
          || keys.some(key => typeof page[key] !== 'string')) {
        throw new Error('The draft has an incomplete or repeated page.');
      }
      ids.add(page.id);
      return {
        id: page.id, type: page.type,
        ...Object.fromEntries(keys.map(key => [key, page[key]])),
        ...(page.type === 'section' ? { children: validate(page.children) } : {}),
      };
    });
  }
  let pages = data.pages;
  if (data.version === 1) {
    if (!Array.isArray(data.goals) || data.goals.some(goal => !Array.isArray(goal?.entries))) {
      throw new Error('The draft has an invalid goal list.');
    }
    pages = data.goals.map(goal => ({
      ...newPage('section'), title: goal.title,
      children: goal.entries.map(entry => ({ ...entry, type: 'entry' })),
    }));
  }
  return { version: 2, title: data.title, pages: validate(pages) };
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

function* locations(siblings = book.pages, parent = null, depth = 0) {
  for (const page of siblings) {
    yield { page, siblings, parent, depth };
    if (page.children) yield* locations(page.children, page, depth + 1);
  }
}

function locate(id) {
  return [...locations()].find(({ page }) => page.id === id);
}

function titleOf(page) {
  return page.title.trim() || 'Untitled ' + page.type;
}

function contains(page, target) {
  return page === target || !!page.children?.some(child => contains(child, target));
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
      return '<p><a href="' + html(new URL(reference).href) + '">Open evidence</a></p>';
    } catch {
      // Keep incomplete links visible as written.
    }
  }
  return '<p><strong>Evidence:</strong> ' + html(reference) + '</p>';
}

function markup(page, level = 2) {
  const next = Math.min(6, level + 1);
  const heading = (text, size) => '<h' + size + '>' + html(text) + '</h' + size + '>';
  const title = heading(titleOf(page), level);
  if (page.type === 'section') {
    return title + page.body.trim().split(/\r?\n\s*\r?\n/).filter(Boolean).map(block => {
      const lines = block.split(/\r?\n/);
      if (lines.every(line => /^[-*] /.test(line))) {
        return '<ul>' + lines.map(line => '<li>' + html(line.slice(2)) + '</li>').join('') + '</ul>';
      }
      return lines.map(line => /^#{1,6} /.test(line) ? heading(line.replace(/^#+ /, ''), next) : '<p>' + html(line) + '</p>').join('');
    }).join('');
  }
  return title + Object.entries(fieldLabels).filter(([key]) => page[key].trim()).map(([key, label]) =>
    '<section>' + heading(label, next) + '<p>' + html(page[key]) + '</p></section>'
  ).join('') + evidenceMarkup(page.evidence);
}

function refreshTree() {
  function render(list, pages) {
    for (const page of pages) {
      const label = titleOf(page);
      const isOpen = !collapsed.has(page.id);
      const item = document.createElement('li');
      item.innerHTML = '<div class="lab-row draft-tree-row" data-page="' + html(page.id) + '">'
        + '<button type="button" class="lab-tree-handle" draggable="true" aria-label="Move ' + html(label) + '" title="Move ' + html(label) + '"></button>'
        + (page.children?.length ? '<button type="button" class="lab-branch-toggle" aria-label="Pages in ' + html(label) + '" aria-expanded="' + isOpen + '"></button>' : '')
        + '<button type="button" class="draft-page-link"' + (page.id === selection ? ' aria-current="page"' : '') + '>' + html(label) + '</button></div>';
      if (page.children?.length && isOpen) {
        const children = document.createElement('ul');
        children.className = 'lab-children';
        render(children, page.children);
        item.append(children);
      }
      list.append(item);
    }
  }
  nav.replaceChildren();
  render(nav, book.pages);
}

function show() {
  const state = locate(selection);
  const page = state?.page;
  get('title').value = book.title;
  form.hidden = !page;
  get('entry-heading').textContent = page ? (page.type === 'section' ? 'Section' : 'Research entry') : 'Add a page to begin';
  get('preview').disabled = !page;
  if (!page) {
    setEditing(true);
    refreshTree();
    return;
  }
  get('section-fields').hidden = page.type !== 'section';
  get('entry-fields').hidden = page.type !== 'entry';
  for (const field of fields[page.type]) form.elements[field].value = page[field];
  const moves = get('move');
  moves.replaceChildren(new Option('Choose a section', ''));
  if (state.parent) moves.add(new Option('Top level', 'root'));
  for (const option of locations()) {
    const target = option.page;
    if (target.type === 'section' && target !== state.parent && !contains(page, target)) {
      moves.add(new Option('　'.repeat(option.depth) + titleOf(target), 'section:' + target.id));
    }
  }
  moves.disabled = moves.options.length < 2;
  get('up').disabled = state.siblings[0] === page;
  get('down').disabled = state.siblings.at(-1) === page;
  reading.innerHTML = markup(page);
  refreshTree();
}

function setEditing(editing) {
  editor.hidden = !editing;
  reading.hidden = editing;
  get('preview').setAttribute('aria-pressed', String(!editing));
  get('preview').textContent = editing ? 'Preview' : 'Continue editing';
}

function selectPage(id) {
  if (id !== selection) get('move-row').hidden = true;
  selection = id;
  show();
}

function movePage(source, target, placement) {
  const parent = placement === 'inside' ? target?.page : target.parent;
  const siblings = placement === 'inside' ? parent?.children || book.pages : target.siblings;
  if (!source || source.page === target?.page || contains(source.page, parent)) return false;
  source.siblings.splice(source.siblings.indexOf(source.page), 1);
  const index = placement === 'inside' ? siblings.length : siblings.indexOf(target.page) + Number(placement === 'after');
  siblings.splice(index, 0, source.page);
  for (let ancestor = parent; ancestor; ancestor = locate(ancestor.id)?.parent) collapsed.delete(ancestor.id);
  save();
  selectPage(source.page.id);
  return true;
}

get('title').addEventListener('input', event => {
  book.title = event.target.value;
  save();
});
form.addEventListener('input', event => {
  const { page } = locate(selection);
  const { name, value } = event.target;
  if (!fields[page.type].includes(name)) return;
  page[name] = value;
  if (name === 'title') refreshTree();
  save();
});
form.addEventListener('submit', event => event.preventDefault());
get('preview').addEventListener('click', () => {
  reading.innerHTML = markup(locate(selection).page);
  setEditing(editor.hidden);
});

nav.addEventListener('click', event => {
  const button = event.target.closest('button');
  const row = button?.closest('[data-page]');
  if (!row) return;
  const id = row.dataset.page;
  if (button.matches('.lab-branch-toggle')) {
    if (collapsed.has(id)) collapsed.delete(id);
    else collapsed.add(id);
    refreshTree();
    findRow(id)?.querySelector('.lab-branch-toggle').focus();
  } else if (button.matches('.lab-tree-handle')) {
    setEditing(true);
    selectPage(id);
    get('move-row').hidden = false;
    get('move-row').focus();
  } else {
    selectPage(id);
    findRow(id)?.querySelector('.draft-page-link').focus();
  }
});

function findRow(id) {
  return nav.querySelector('[data-page="' + CSS.escape(id) + '"]');
}

document.querySelector('.draft-add').addEventListener('click', event => {
  const add = event.target.closest('[data-add-page]');
  if (!add) return;
  const page = newPage(add.dataset.addPage);
  book.pages.push(page);
  add.closest('details').open = false;
  save();
  setEditing(true);
  selectPage(page.id);
  form.elements.title.focus();
});

get('move').addEventListener('change', event => {
  const value = event.target.value;
  if (value) movePage(locate(selection), value === 'root' ? null : locate(value.slice(8)), 'inside');
});
for (const [id, offset, placement] of [['up', -1, 'before'], ['down', 1, 'after']]) {
  get(id).addEventListener('click', () => {
    const state = locate(selection);
    const neighbor = state.siblings[state.siblings.indexOf(state.page) + offset];
    if (neighbor) movePage(state, locate(neighbor.id), placement);
    if (get(id).disabled) get('move-row').focus();
  });
}

nav.addEventListener('dragstart', event => {
  const row = event.target.closest('.lab-tree-handle')?.closest('[data-page]');
  if (!row) return;
  dragging = locate(row.dataset.page);
  event.dataTransfer.setData('text/plain', dragging.page.id);
  event.dataTransfer.effectAllowed = 'move';
  rootDrop.hidden = false;
});

function clearTarget() {
  document.querySelector('.draft [data-drop]')?.removeAttribute('data-drop');
}

function dropLocation(event) {
  if (!dragging) return;
  if (event.target === rootDrop) return { element: rootDrop, placement: 'inside' };
  const row = event.target.closest('[data-page]');
  if (!row) return;
  const target = locate(row.dataset.page);
  const bounds = row.getBoundingClientRect();
  const ratio = (event.clientY - bounds.top) / bounds.height;
  const placement = target.page.children && ratio > .25 && ratio < .75 ? 'inside' : ratio < .5 ? 'before' : 'after';
  const parent = placement === 'inside' ? target.page : target.parent;
  if (dragging.page !== target.page && !contains(dragging.page, parent)) return { element: row, target, placement };
}

const sidebar = nav.closest('nav');
sidebar.addEventListener('dragover', event => {
  clearTarget();
  const drop = dropLocation(event);
  if (!drop) return;
  event.preventDefault();
  event.dataTransfer.dropEffect = 'move';
  drop.element.dataset.drop = drop.placement;
});
function endDrag() {
  clearTarget();
  dragging = undefined;
  rootDrop.hidden = true;
}
sidebar.addEventListener('dragleave', event => {
  if (!sidebar.contains(event.relatedTarget)) clearTarget();
});
sidebar.addEventListener('drop', event => {
  const drop = dropLocation(event);
  if (!drop) return;
  event.preventDefault();
  movePage(dragging, drop.target, drop.placement);
  endDrag();
});
sidebar.addEventListener('dragend', endDrag);

get('delete').addEventListener('click', () => {
  const { page, siblings, parent } = locate(selection);
  const message = page.children?.length ? 'Delete this section and all pages in it?' : 'Delete this page from your draft?';
  if (!confirm(message)) return;
  siblings.splice(siblings.indexOf(page), 1);
  save();
  selectPage(parent?.id || book.pages[0]?.id);
  (selection ? form.elements.title : document.querySelector('.draft-add summary')).focus();
});

function useBook(nextBook) {
  book = nextBook;
  collapsed.clear();
  setEditing(true);
  save();
  selectPage(book.pages[0]?.children?.[0]?.id || book.pages[0]?.id);
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
  const pages = [...locations()];
  const links = pages.map(({ page }, index) =>
    '<li><a href="#page-' + index + '">' + html(titleOf(page)) + '</a></li>'
  ).join('');
  const contentPages = pages.map(({ page, depth }, index) =>
    '<article id="page-' + index + '">' + markup(page, Math.min(6, depth + 2)) + '</article>'
  ).join('');
  const style = 'body{margin:0;background:#f7f5ec;color:#22352b;font:16px/1.6 system-ui}main{max-width:720px;padding:24px;margin:auto;overflow-wrap:anywhere}a{color:#315744}article{border-top:1px solid #cad4c9;margin:20px 0}article p{white-space:pre-wrap}';
  const content = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' +
    '<title>' + title + '</title><style>' + style + '</style><main><h1>' + title + '</h1><nav aria-label="Pages"><ul>' +
    links + '</ul></nav>' + contentPages + '</main></html>';
  download('research-logbook.html', 'text/html;charset=utf-8', content);
});

show();
get('status').textContent = 'Changes are saved in this browser as you type.';
