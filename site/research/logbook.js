const logbook = document.querySelector('.lab');
const content = logbook.querySelector('.lab-content');
const goals = [...logbook.querySelectorAll('[data-goal], [data-group-section]')];
const tree = logbook.querySelector('.lab-goals');
const cropDemo = document.querySelector('.lab-demo');
const browseGoals = document.querySelector('.lab-nav-toggle');
let activeExperiment;
let focusOnNavigation = false;
let toggledByRowClick = false;

function showGoalMenu(open) {
  logbook.toggleAttribute('data-nav-open', open);
  browseGoals.setAttribute('aria-expanded', String(open));
  if (open) tree.querySelector('[aria-current]')?.scrollIntoView({ block: 'nearest' });
}

browseGoals.addEventListener('click', () => showGoalMenu(!logbook.hasAttribute('data-nav-open')));

function setBranch(button, open) {
  button.setAttribute('aria-expanded', String(open));
  document.getElementById(button.getAttribute('aria-controls')).hidden = !open;
}

function revealNavigation(link) {
  if (!toggledByRowClick && link?.previousElementSibling?.matches('.lab-branch-toggle')) {
    setBranch(link.previousElementSibling, true);
  }
  for (let item = link?.parentElement; item && item !== tree; item = item.parentElement) {
    if (item.id.startsWith('branch-')) {
      const toggle = tree.querySelector(`[aria-controls="${item.id}"]`);
      if (toggle) setBranch(toggle, true);
    }
  }
  if (tree.clientHeight) {
    const bounds = tree.getBoundingClientRect();
    const leaf = link?.getBoundingClientRect();
    if (leaf && (leaf.top < bounds.top || leaf.bottom > bounds.bottom)) {
      tree.scrollTop += leaf.top - bounds.top - tree.clientHeight / 3;
    }
  }
}

// Some diagrams have hand-positioned labels. Give the drawing room for the
// longest label at the actual font size rather than letting its edge clip.
function fitDiagrams(container) {
  for (const chart of container.querySelectorAll('svg.lab-diagram[viewBox]')) {
    if (!chart.getClientRects().length) continue;
    const { x, y, width, height } = chart.viewBox.baseVal;
    const bounds = chart.getBBox();
    const left = Math.min(x, bounds.x - 2);
    const top = Math.min(y, bounds.y - 2);
    const right = Math.max(x + width, bounds.x + bounds.width + 2);
    const bottom = Math.max(y + height, bounds.y + bounds.height + 2);
    if (left < x || top < y || right > x + width || bottom > y + height) {
      chart.setAttribute('viewBox', [left, top, right - left, bottom - top].join(' '));
    }
  }
}

const preparedPanels = new WeakSet();
let panelDatabase;

function panelStore(key, action, draft) {
  panelDatabase ??= new Promise((resolve, reject) => {
    const request = indexedDB.open('research-logbook-panels', 1);
    request.onupgradeneeded = () => request.result.createObjectStore('drafts');
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });

  return panelDatabase.then(database => new Promise((resolve, reject) => {
    const transaction = database.transaction('drafts', action === 'get' ? 'readonly' : 'readwrite');
    const store = transaction.objectStore('drafts');
    const request = action === 'put' ? store.put(draft, key) : store[action](key);
    transaction.oncomplete = () => resolve(request.result);
    transaction.onabort = () => reject(transaction.error);
  }));
}

function updateCropControls(entry) {
  const note = entry.querySelector('[data-crop-replacement-note]');
  if (!note) return;
  const visuals = [...entry.querySelectorAll('.lab-panel-visual')];
  const replaced = visuals.some(visual => visual.hidden);
  for (const visual of visuals) visual.inert = replaced;
  note.hidden = !replaced;
}

const replacementSources = new WeakMap();
const preparedSources = new WeakSet();

function setupSource(entry) {
  if (preparedSources.has(entry)) return;
  preparedSources.add(entry);
  const key = JSON.stringify([location.pathname, entry.id, 'source']);
  const link = entry.querySelector('.lab-script-name');
  const name = link.querySelector('code');
  const originalName = name.textContent;
  const date = entry.querySelector('.lab-script-meta');
  const change = entry.querySelector('.lab-source-change');
  const restore = entry.querySelector('.lab-source-restore');
  const picker = entry.querySelector('.lab-source-picker');
  const status = entry.querySelector('.lab-source-status');

  function show(file) {
    if (file) replacementSources.set(link, file);
    else replacementSources.delete(link);
    name.textContent = file?.name || originalName;
    date.hidden = Boolean(file);
    restore.hidden = !file;
  }

  async function commit(file) {
    change.disabled = restore.disabled = true;
    try {
      await panelStore(key, file ? 'put' : 'delete', file);
      show(file);
      status.textContent = file ? 'File saved in this browser.' : 'Original file restored.';
    } catch {
      status.textContent = 'Could not save the file in this browser.';
    } finally {
      change.disabled = restore.disabled = false;
      change.focus();
    }
  }

  change.addEventListener('click', () => picker.click());
  picker.addEventListener('change', () => {
    const file = picker.files[0];
    picker.value = '';
    if (file) commit(file);
  });
  restore.addEventListener('click', () => commit(undefined));
  panelStore(key, 'get').then(show).catch(() => {
    status.textContent = 'Browser storage is unavailable.';
  }).finally(() => { change.hidden = false; });
}

function setupPanel(entry, panel) {
  if (preparedPanels.has(panel)) return;
  preparedPanels.add(panel);
  const key = JSON.stringify([location.pathname, entry.id, panel.dataset.entryPanel]);
  const edit = panel.querySelector('.lab-panel-edit');
  const textForm = panel.querySelector('.lab-panel-text-form');
  const figureEdit = panel.querySelector('.lab-panel-figure-edit');
  const figureForm = panel.querySelector('.lab-panel-figure-form');
  const text = panel.querySelector('.lab-panel-text');
  const originalText = [...text.querySelectorAll('p')].map(p => p.textContent.trim()).join('\n\n');
  const originalHTML = text.innerHTML;
  const visual = panel.querySelector('.lab-panel-visual');
  const figure = panel.querySelector('.lab-panel-replacement');
  const image = figure.querySelector('img');
  const caption = figure.querySelector('figcaption');
  const textStatus = panel.querySelector('.lab-panel-status');
  const figureStatus = panel.querySelector('.lab-panel-figure-status');
  const restoreText = textForm.querySelector('.lab-panel-reset');
  const restoreFigure = figureForm.querySelector('.lab-panel-use-original');
  let draft;
  let imageUrl;
  let busy = false;

  function readView() {
    if (!draft || draft.text === originalText) {
      if (text.querySelector('.lab-panel-draft')) text.innerHTML = originalHTML;
    } else {
      const p = document.createElement('p');
      p.className = 'lab-panel-draft';
      p.textContent = draft.text;
      text.replaceChildren(p);
    }
    if (imageUrl) URL.revokeObjectURL(imageUrl);
    imageUrl = draft?.image ? URL.createObjectURL(draft.image) : undefined;
    if (imageUrl) image.src = imageUrl;
    else image.removeAttribute('src');
    image.alt = draft?.caption || 'Figure added to this panel';
    caption.textContent = draft?.caption || '';
    caption.hidden = !draft?.caption;
    figure.hidden = !imageUrl;
    visual.hidden = Boolean(imageUrl);
    figureEdit.textContent = imageUrl || visual.childElementCount ? 'Change figure' : 'Add figure';
    updateCropControls(entry);
    fitDiagrams(panel);
  }

  function close(form, button) {
    button.hidden = false;
    if (form === textForm) text.hidden = false;
    form.hidden = true;
    button.focus();
  }

  async function save(next, form, button, status) {
    if (busy) return;
    busy = true;
    for (const control of [...textForm.elements, ...figureForm.elements]) control.disabled = true;
    try {
      if (next.image && next.image !== draft?.image) {
        const url = URL.createObjectURL(next.image);
        try {
          const test = new Image();
          test.src = url;
          await test.decode();
        } catch {
          status.textContent = 'This image could not be opened. Choose a PNG, JPEG, WebP or GIF.';
          return;
        } finally {
          URL.revokeObjectURL(url);
        }
      }
      const hasChanges = next.text !== originalText || next.image;
      await panelStore(key, hasChanges ? 'put' : 'delete', next);
      draft = hasChanges ? next : undefined;
      readView();
      status.textContent = 'Saved in this browser.';
      close(form, button);
    } catch {
      status.textContent = 'Could not save here. Your changes are still in the editor.';
    } finally {
      busy = false;
      for (const control of [...textForm.elements, ...figureForm.elements]) control.disabled = false;
    }
  }

  edit.addEventListener('click', () => {
    textForm.elements.description.value = draft?.text ?? originalText;
    restoreText.hidden = !draft || draft.text === originalText;
    textStatus.textContent = '';
    edit.hidden = true;
    text.hidden = true;
    textForm.hidden = false;
    textForm.elements.description.focus();
  });

  figureEdit.addEventListener('click', () => {
    figureForm.reset();
    figureForm.elements.caption.value = draft?.caption || '';
    restoreFigure.hidden = !draft?.image;
    figureStatus.textContent = '';
    figureEdit.hidden = true;
    figureForm.hidden = false;
    figureForm.elements.figure.focus();
  });

  textForm.querySelector('.lab-panel-cancel').addEventListener('click', () => close(textForm, edit));
  figureForm.querySelector('.lab-panel-cancel').addEventListener('click', () => close(figureForm, figureEdit));
  restoreText.addEventListener('click', () => save({ ...draft, text: originalText }, textForm, edit, textStatus));
  restoreFigure.addEventListener('click', () => save(
    { text: draft?.text ?? originalText }, figureForm, figureEdit, figureStatus
  ));
  textForm.addEventListener('submit', event => {
    event.preventDefault();
    save({ ...draft, text: textForm.elements.description.value.trim() }, textForm, edit, textStatus);
  });
  figureForm.addEventListener('submit', event => {
    event.preventDefault();
    const file = figureForm.elements.figure.files[0] || draft?.image;
    if (!file) {
      figureStatus.textContent = 'Choose an image file first.';
      return;
    }
    save({
      text: draft?.text ?? originalText,
      image: file,
      caption: figureForm.elements.caption.value.trim(),
    }, figureForm, figureEdit, figureStatus);
  });

  panelStore(key, 'get').then(saved => {
    draft = saved;
    if (draft) readView();
  }).catch(() => {
    textStatus.textContent = 'Browser storage is unavailable.';
  }).finally(() => {
    edit.hidden = false;
    figureEdit.hidden = false;
    if (!visual.childElementCount && !draft?.image) figureEdit.textContent = 'Add figure';
  });
}

function selectExperiment() {
  const [key, encodedFile] = location.hash.slice(1).split('/');
  const goal = goals.find(item => item.id === key) || goals.find(item => item.hasAttribute('data-goal'));
  let filename;
  try { filename = decodeURIComponent(encodedFile || ''); } catch { filename = ''; }
  const overview = goal.querySelector('[data-goal-overview], [data-group-overview]');
  const entries = [...goal.querySelectorAll('[data-experiment]')];
  const defaultFile = goal.querySelector('[data-default-file]')?.dataset.defaultFile;
  const selectedLeaf = filename
    ? (entries.find(item => item.dataset.experiment === filename)
      || entries.find(item => item.dataset.experiment === defaultFile))
    : null;
  const selected = selectedLeaf || overview || entries[0];
  if (activeExperiment && activeExperiment !== selected && activeExperiment.hasAttribute('data-experiment')) {
    closeEditor(activeExperiment);
  }
  goals.forEach(item => { item.hidden = item !== goal; });
  if (overview) overview.hidden = selected !== overview;
  for (const item of entries) item.hidden = item !== selected;
  tree.querySelector('[aria-current]')?.removeAttribute('aria-current');
  const link = selectedLeaf
    ? [...tree.querySelectorAll('.lab-script')].find(item => decodeURIComponent(item.hash.slice(1)) === selectedLeaf.id)
    : tree.querySelector(`.lab-node-link[href="#${goal.id}"]`) || tree.querySelector(`a[href="#${goal.id}"]`);
  link?.setAttribute('aria-current', 'page');
  revealNavigation(link);
  if (selected !== activeExperiment || focusOnNavigation) {
    content.scrollTop = 0;
    if (focusOnNavigation) selected.querySelector('h2')?.focus({ preventScroll: true });
    if (matchMedia('(max-width: 700px)').matches) window.scrollTo(0, 0);
  }
  activeExperiment = selected;
  fitDiagrams(selected);
  if (selected.hasAttribute('data-experiment')) {
    setupSource(selected);
    for (const panel of selected.querySelectorAll('[data-entry-panel]')) setupPanel(selected, panel);
  }
  if (filename && !selectedLeaf) {
    const part = document.getElementById(goal.id + '/' + filename);
    if (part?.hasAttribute('data-home-part')) {
      if (part instanceof HTMLDetailsElement) part.open = true;
      part.scrollIntoView({ block: 'start' });
    }
  }
  focusOnNavigation = false;
  toggledByRowClick = false;
}

function framingKey(entry) {
  return 'research-logbook:framing:' + location.pathname + ':' + entry.id;
}

function savedFraming(entry) {
  try { return localStorage.getItem(framingKey(entry)); } catch { return null; }
}

function closeEditor(entry) {
  entry.querySelector('.lab-framing-form').hidden = true;
  entry.querySelector('.lab-framing-text').hidden = false;
  entry.querySelector('.lab-edit').hidden = false;
}

function setupFraming(entry) {
  const text = entry.querySelector('.lab-framing-text');
  const original = text.textContent;
  const edit = entry.querySelector('.lab-edit');
  const form = entry.querySelector('.lab-framing-form');
  const field = form.elements.framing;
  const restore = form.querySelector('[data-restore]');
  const status = entry.querySelector('.lab-framing-status');
  const saved = savedFraming(entry);
  if (saved !== null) {
    text.textContent = saved;
    status.textContent = 'Edited in this browser';
  }
  edit.hidden = false;
  edit.addEventListener('click', () => {
    field.value = text.textContent;
    restore.hidden = savedFraming(entry) === null;
    form.hidden = false;
    edit.hidden = true;
    text.hidden = true;
    field.focus();
  });

  function save(value) {
    try {
      if (value === original) localStorage.removeItem(framingKey(entry));
      else localStorage.setItem(framingKey(entry), value);
    } catch {
      status.textContent = 'Browser storage is unavailable. Your text is still in the editor.';
      return;
    }
    text.textContent = value;
    status.textContent = value === original ? 'Original framing restored' : 'Saved in this browser';
    closeEditor(entry);
    edit.focus();
  }

  form.addEventListener('submit', event => {
    event.preventDefault();
    const value = field.value.trim();
    if (value) save(value);
    else status.textContent = 'Enter a note before saving.';
  });
  form.querySelector('[data-cancel]').addEventListener('click', () => {
    closeEditor(entry);
    edit.focus();
  });
  restore.addEventListener('click', () => save(original));
}

logbook.classList.add('enhanced');
for (const button of tree.querySelectorAll('.lab-branch-toggle')) {
  button.hidden = false;
  setBranch(button, false);
  button.addEventListener('click', () => setBranch(button, button.getAttribute('aria-expanded') !== 'true'));
}
for (const entry of logbook.querySelectorAll('[data-experiment]')) setupFraming(entry);
logbook.addEventListener('change', event => {
  if (!event.target.matches('[data-image-scale]')) return;
  for (const result of event.target.closest('.lab-io-card').querySelectorAll('[data-scale-result]')) {
    result.hidden = result.dataset.scaleResult !== event.target.value;
  }
});
window.addEventListener('hashchange', selectExperiment);
const dialog = document.querySelector('#file-preview');
const previewContent = document.querySelector('#preview-content');
const previewOpen = document.querySelector('#preview-open');
const sourceDirectory = document.querySelector('.lab-source').href.replace('/tree/', '/blob/');
let previewRequest;
let previewLocalUrl;

function filePreview(text, url) {
  if (!url.endsWith('.md')) {
    const code = document.createElement('pre');
    code.textContent = text;
    return code;
  }
  const guide = document.createElement('div');
  guide.className = 'file-reading-guide';
  for (const block of text.trim().split(/\r?\n\s*\r?\n/)) {
    if (block.startsWith('# ')) continue;
    if (block.startsWith('- ')) {
      const list = document.createElement('ul');
      for (const line of block.split(/\r?\n/)) {
        const item = document.createElement('li');
        item.textContent = line.slice(2).replaceAll('**', '');
        list.append(item);
      }
      guide.append(list);
    } else {
      const paragraph = document.createElement('p');
      paragraph.textContent = block.replaceAll('*', '');
      guide.append(paragraph);
    }
  }
  return guide;
}

async function previewFile(link) {
  previewRequest?.abort();
  const request = new AbortController();
  previewRequest = request;
  if (previewLocalUrl) URL.revokeObjectURL(previewLocalUrl);
  previewLocalUrl = undefined;
  const localFile = replacementSources.get(link);
  const filename = localFile?.name || link.closest('[data-experiment]').dataset.experiment;
  document.querySelector('#preview-title').textContent = filename;
  const isScript = link.href.endsWith('.py');
  previewOpen.href = isScript ? sourceDirectory + '/' + link.href.split('/').pop() : link.href;
  previewOpen.textContent = localFile ? 'Open original file ↗' : isScript ? 'Open on GitHub ↗' : 'Open file ↗';
  const download = document.querySelector('#preview-download');
  if (localFile) previewLocalUrl = URL.createObjectURL(localFile);
  download.href = previewLocalUrl || link.href;
  download.download = filename;
  previewContent.textContent = 'Loading file…';
  dialog.showModal();

  if (localFile ? /^image\/(?:png|jpeg|gif|webp)$/.test(localFile.type) : /\.(?:png|svg)$/.test(link.href)) {
    const image = new Image();
    image.alt = document.querySelector('#preview-title').textContent;
    image.src = previewLocalUrl || link.href;
    previewContent.replaceChildren(image);
    return;
  }

  try {
    const response = localFile || await fetch(link.href, { signal: request.signal });
    if (!localFile && !response.ok) throw new Error('HTTP ' + response.status);
    const text = await response.text();
    if (!request.signal.aborted) previewContent.replaceChildren(filePreview(text, filename));
  } catch (error) {
    if (!request.signal.aborted) previewContent.textContent = 'Preview unavailable. Use the links below.';
  }
}

logbook.addEventListener('click', event => {
  if (event.defaultPrevented || event.button || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  const link = event.target.closest('a');
  if (link?.hasAttribute('data-preview') && dialog.showModal) {
    event.preventDefault();
    previewFile(link);
  } else if (link?.getAttribute('href')?.startsWith('#')) {
    event.preventDefault();
    if (link.matches('.lab-node-link')) {
      const toggle = link.previousElementSibling;
      if (toggle?.matches('.lab-branch-toggle')) {
        setBranch(toggle, toggle.getAttribute('aria-expanded') !== 'true');
        toggledByRowClick = true;
      }
    }
    focusOnNavigation = true;
    showGoalMenu(false);
    if (link.hash !== location.hash) history.pushState(null, '', link.hash);
    selectExperiment();
  }
});
dialog.addEventListener('close', () => {
  previewRequest?.abort();
  if (previewLocalUrl) URL.revokeObjectURL(previewLocalUrl);
  previewLocalUrl = undefined;
});

function setupCropDemo() {
  const scene = document.querySelector('#crop-image');
  const preview = document.querySelector('#crop-preview');
  const edge = document.querySelector('#crop-edge');
  const undo = document.querySelector('#crop-undo');
  const download = document.querySelector('#crop-download');
  const status = document.querySelector('#crop-status');
  const coordinates = document.querySelector('#crop-coordinates');
  const sceneContext = scene.getContext('2d');
  const previewContext = preview.getContext('2d');
  const marks = [];
  const size = preview.width;
  const cursor = { x: 106, y: 96 };
  const source = new Image();

  function cropPosition({ x, y }) {
    return [Math.min(Math.max(x - size / 2, 0), scene.width - size),
      Math.min(Math.max(y - size / 2, 0), scene.height - size)];
  }

  function drawScene() {
    sceneContext.drawImage(source, 0, 0);
    sceneContext.lineWidth = 2;
    sceneContext.font = 'bold 13px system-ui';
    marks.forEach((mark, index) => {
      const [left, top] = cropPosition(mark);
      sceneContext.strokeStyle = '#f9ecb2';
      sceneContext.strokeRect(left, top, size, size);
      sceneContext.fillStyle = '#1b3126';
      sceneContext.fillRect(left, top, 29, 21);
      sceneContext.fillStyle = '#fffae7';
      sceneContext.fillText(String(index + 1).padStart(2, '0'), left + 6, top + 15);
    });
    sceneContext.strokeStyle = '#fff9d4';
    sceneContext.beginPath();
    sceneContext.moveTo(cursor.x - 7, cursor.y);
    sceneContext.lineTo(cursor.x + 7, cursor.y);
    sceneContext.moveTo(cursor.x, cursor.y - 7);
    sceneContext.lineTo(cursor.x, cursor.y + 7);
    sceneContext.stroke();
  }

  function updateCrop() {
    drawScene();
    previewContext.clearRect(0, 0, size, size);
    const count = marks.length;
    const mark = marks.at(-1);
    previewContext.drawImage(source, ...cropPosition(mark || cursor), size, size, 0, 0, size, size);
    status.textContent = count ? `${count} crop${count === 1 ? '' : 's'} marked` : 'No crops marked';
    if (mark) {
      const [left, top] = cropPosition(mark);
      const shifted = left !== mark.x - size / 2 || top !== mark.y - size / 2;
      const note = shifted ? ' (shifted inward from edge to keep 96 × 96 size)' : '';
      coordinates.textContent = `Core ${count} · Centre (${mark.x}, ${mark.y}) px · Bounds (${left}, ${top}) to (${left + size}, ${top + size}) px${note}`;
    } else {
      coordinates.textContent = '';
    }
    undo.disabled = download.disabled = count === 0;
  }

  function keepInImage(x, y) {
    cursor.x = Math.max(0, Math.min(scene.width - 1, x));
    cursor.y = Math.max(0, Math.min(scene.height - 1, y));
  }

  scene.addEventListener('click', event => {
    const box = scene.getBoundingClientRect();
    keepInImage(Math.floor((event.clientX - box.left) * scene.width / box.width),
      Math.floor((event.clientY - box.top) * scene.height / box.height));
    marks.push({ ...cursor });
    updateCrop();
  });

  scene.addEventListener('keydown', event => {
    const step = event.shiftKey ? 1 : 12;
    const moves = { ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step] };
    if (moves[event.key]) {
      event.preventDefault();
      const [dx, dy] = moves[event.key];
      keepInImage(cursor.x + dx, cursor.y + dy);
      updateCrop();
    } else if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      marks.push({ ...cursor });
      updateCrop();
    }
  });

  edge?.addEventListener('click', () => {
    keepInImage(24, 32);
    marks.push({ ...cursor });
    updateCrop();
  });
  undo.addEventListener('click', () => { marks.pop(); updateCrop(); });
  download.addEventListener('click', () => {
    const rows = marks.map((mark, index) => {
      const [left, top] = cropPosition(mark);
      return ['synthetic-slide', `core-${String(index + 1).padStart(2, '0')}`, mark.x, mark.y,
        left, top, left + size, top + size].join(',');
    });
    const header = 'image_id,core_id,centre_x,centre_y,crop_left,crop_top,crop_right,crop_bottom';
    const url = URL.createObjectURL(new Blob([[header, ...rows].join('\n') + '\n'], { type: 'text/csv' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = 'crop-records.csv';
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });

  source.addEventListener('load', updateCrop);
  source.src = 'examples/example_grid.png';
}

if (!location.hash) {
  const firstGroupToggle = tree.querySelector('.lab-group .lab-branch-toggle');
  if (firstGroupToggle) setBranch(firstGroupToggle, true);
}
if (cropDemo) setupCropDemo();
selectExperiment();
document.fonts.ready.then(() => fitDiagrams(activeExperiment));
logbook.addEventListener('toggle', event => {
  if (event.target.matches('details[open]')) fitDiagrams(event.target);
}, true);
