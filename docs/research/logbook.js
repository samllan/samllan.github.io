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
  if (activeExperiment !== selected) closePageMenu();
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

logbook.classList.add('enhanced');
for (const button of tree.querySelectorAll('.lab-branch-toggle')) {
  button.hidden = false;
  setBranch(button, false);
  button.addEventListener('click', () => setBranch(button, button.getAttribute('aria-expanded') !== 'true'));
}
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
  const filename = link.closest('[data-experiment]').dataset.experiment;
  document.querySelector('#preview-title').textContent = filename;
  const isScript = link.href.endsWith('.py');
  previewOpen.href = isScript ? sourceDirectory + '/' + link.href.split('/').pop() : link.href;
  previewOpen.textContent = isScript ? 'Open on GitHub ↗' : 'Open file ↗';
  const download = document.querySelector('#preview-download');
  download.href = link.href;
  download.download = filename;
  previewContent.textContent = 'Loading file…';
  dialog.showModal();

  if (/\.(?:png|svg)$/.test(link.href)) {
    const image = new Image();
    image.alt = document.querySelector('#preview-title').textContent;
    image.src = link.href;
    previewContent.replaceChildren(image);
    return;
  }

  try {
    const response = await fetch(link.href, { signal: request.signal });
    if (!response.ok) throw new Error('HTTP ' + response.status);
    const text = await response.text();
    if (!request.signal.aborted) previewContent.replaceChildren(filePreview(text, filename));
  } catch (error) {
    if (!request.signal.aborted) previewContent.textContent = 'Preview unavailable. Use the links below.';
  }
}

const publicEditNotice = document.querySelector('#public-edit-notice');
let ownerAction;

function closePageMenu() {
  const menu = activeExperiment?.querySelector('.lab-page-menu[open]');
  if (menu) menu.open = false;
}

function requestOwnerAccess(action) {
  if (!action || !publicEditNotice.showModal) return;
  ownerAction = action.closest('.lab-page-menu')?.querySelector('summary') || action;
  closePageMenu();
  if (!publicEditNotice.open) publicEditNotice.showModal();
}

logbook.addEventListener('click', event => requestOwnerAccess(event.target.closest('[data-owner-action]')));
tree.addEventListener('dragstart', event => {
  const handle = event.target.closest('.lab-tree-handle');
  if (!handle) return;
  event.preventDefault();
  requestOwnerAccess(handle);
});

publicEditNotice.addEventListener('close', () => {
  ownerAction?.focus();
  ownerAction = undefined;
});

document.addEventListener('click', event => {
  if (!event.target.closest('.lab-page-menu')) closePageMenu();
});
logbook.addEventListener('keydown', event => {
  const menu = event.target.closest('.lab-page-menu[open]');
  if (event.key === 'Escape' && menu) {
    event.preventDefault();
    closePageMenu();
    menu.querySelector('summary').focus();
  }
});

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
dialog.addEventListener('close', () => previewRequest?.abort());

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
