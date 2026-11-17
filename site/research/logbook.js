const logbook = document.querySelector('.lab');
const content = logbook.querySelector('.lab-content');
const goals = [...logbook.querySelectorAll('[data-goal]')];
const goalLinks = [...logbook.querySelectorAll('.lab-goals a[href^="#"]')];
const cropDemo = document.querySelector('.lab-demo');
let currentGoal;
let cropReady = false;

function setBranch(button, open) {
  button.setAttribute('aria-expanded', String(open));
  document.getElementById(button.getAttribute('aria-controls')).hidden = !open;
}

function revealNavigation(link) {
  if (!link) return;
  for (let item = link.parentElement; item; item = item.parentElement) {
    if (item.matches('details.lab-group')) item.open = true;
    if (item.matches('ul.lab-branch')) {
      setBranch(item.parentElement.querySelector(':scope > .lab-branch-toggle'), true);
    }
  }
  const button = link.parentElement.querySelector(':scope > .lab-branch-toggle');
  if (button) setBranch(button, true);
}

function selectGoal() {
  const [id, encodedFile] = location.hash.slice(1).split('/');
  const active = document.getElementById(id);
  const goal = goals.includes(active) ? active : goals[0];
  const changed = goal !== currentGoal;
  const wasOpen = Boolean(currentGoal);
  if (changed) {
    currentGoal = goal;
    goals.forEach(section => { section.hidden = section !== goal; });
    goalLinks.forEach(link => {
      if (link.hash === '#' + goal.id) {
        link.setAttribute('aria-current', 'location');
        revealNavigation(link);
      } else link.removeAttribute('aria-current');
    });
    content.scrollTop = 0;
    if (wasOpen && matchMedia('(max-width: 700px)').matches) {
      goal.scrollIntoView({ block: 'start', behavior: 'instant' });
    }
  }
  let filename = '';
  try { filename = decodeURIComponent(encodedFile || ''); } catch { /* Ignore a malformed bookmark. */ }
  const links = [...goal.querySelectorAll('.lab-row-file')];
  const selected = links.find(link => link.textContent === filename);
  const files = goal.querySelector('.lab-files-panel');
  if (selected) {
    files.open = true;
    selectRow(selected, !changed);
  } else if (!goal.querySelector('[data-selected]') && links.length) {
    selectRow(links.find(link => link.textContent === files.dataset.defaultFile) || links[0]);
  }
}

function selectRow(link, reveal = false) {
  const goal = link.closest('[data-goal]');
  const row = link.closest('tr');
  const panel = goal.querySelector('.lab-output');
  const filename = link.textContent;
  const former = goal.querySelector('[data-selected]');
  if (former !== row) {
    former?.removeAttribute('data-selected');
    former?.querySelector('.lab-row-file').removeAttribute('aria-current');
    row.dataset.selected = '';
    link.setAttribute('aria-current', 'true');

    const template = [...goal.querySelectorAll('template[data-file]')].find(item => item.dataset.file === filename);
    const example = template.content.cloneNode(true);
    const guide = example.querySelector('[data-markdown]');
    if (guide) guide.replaceWith(filePreview(guide.textContent, link.href));
    panel.querySelector('.lab-output-content').replaceChildren(example);
    panel.querySelector('.lab-output-kind').textContent = filename === 'crop_benchmark.csv'
      ? 'Thesis benchmark'
      : filename.endsWith('.md') ? 'Research notes' : 'Synthetic example';
    panel.querySelector('.lab-output-title').textContent = filename;
    panel.querySelector('[data-preview]').href = link.href;
    panel.querySelector('.lab-share-link').href = '#' + goal.id + '/' + encodeURIComponent(filename);
    panel.hidden = false;
  }
  if (cropDemo && goal.id === 'crop') {
    cropDemo.hidden = !cropReady || filename !== 'prepare_image_regions.py';
  }
  if (reveal) panel.querySelector('.lab-output-head').scrollIntoView({ block: 'nearest' });
}

function setupSort(goal) {
  const body = goal.querySelector('.lab-files tbody');
  const workflowOrder = [...body.rows];
  if (workflowOrder.length < 2) return;
  const control = goal.querySelector('.lab-order');
  const names = new Intl.Collator('en', { numeric: true });
  control.hidden = false;
  control.querySelector('select').addEventListener('change', event => {
    const order = event.target.value;
    const rows = [...workflowOrder];
    if (order === 'file') rows.sort((a, b) => names.compare(a.querySelector('code').textContent, b.querySelector('code').textContent));
    if (order === 'year') rows.sort((a, b) => Number(b.dataset.sourceYear) - Number(a.dataset.sourceYear));
    body.append(...rows);
  });
}

logbook.classList.add('enhanced');
goals.forEach(setupSort);
logbook.querySelectorAll('.lab-branch-toggle').forEach(button => {
  button.hidden = false;
  setBranch(button, false);
  button.addEventListener('click', () => setBranch(button, button.getAttribute('aria-expanded') !== 'true'));
});
window.addEventListener('hashchange', selectGoal);

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
  document.querySelector('#preview-title').textContent = link.closest('.lab-output').querySelector('.lab-output-title').textContent;
  const isScript = link.href.endsWith('.py');
  previewOpen.href = isScript ? sourceDirectory + '/' + link.href.split('/').pop() : link.href;
  previewOpen.textContent = isScript ? 'Open on GitHub ↗' : 'Open file ↗';
  document.querySelector('#preview-download').href = link.href;
  previewContent.textContent = 'Loading file…';
  dialog.showModal();

  if (link.href.endsWith('.png') || link.href.endsWith('.svg')) {
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
    if (!request.signal.aborted) previewContent.replaceChildren(filePreview(text, link.href));
  } catch (error) {
    if (!request.signal.aborted) previewContent.textContent = 'Preview unavailable. Use the links below.';
  }
}

logbook.addEventListener('click', event => {
  if (event.defaultPrevented || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  const link = event.target.closest('a');
  if (link?.hasAttribute('data-preview')) {
    if (dialog.showModal) {
      event.preventDefault();
      previewFile(link);
    }
  } else if (link?.classList.contains('lab-script')) {
    event.preventDefault();
    const goal = document.getElementById(link.dataset.openGoal);
    const target = '#' + goal.id + '/' + encodeURIComponent(link.textContent);
    if (location.hash !== target) location.hash = target;
    selectGoal();
    const rowLink = [...goal.querySelectorAll('.lab-row-file')].find(item => item.href === link.href);
    if (rowLink) selectRow(rowLink, true);
  } else if (link?.classList.contains('lab-row-file')) {
    event.preventDefault();
    selectRow(link, true);
  } else if (!event.target.closest('a, button, select') && !getSelection()?.toString()) {
    const rowLink = event.target.closest('.lab-files tbody tr')?.querySelector('.lab-row-file');
    if (rowLink) selectRow(rowLink, true);
  }
});

dialog.addEventListener('close', () => previewRequest?.abort());

function setupCropDemo() {
  const scene = document.querySelector('#crop-image');
  const preview = document.querySelector('#crop-preview');
  const undo = document.querySelector('#crop-undo');
  const download = document.querySelector('#crop-download');
  const status = document.querySelector('#crop-status');
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
    if (count) previewContext.drawImage(source, ...cropPosition(marks[count - 1]), size, size, 0, 0, size, size);
    status.textContent = count ? `${count} crop${count === 1 ? '' : 's'} marked` : 'No crops marked';
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
      drawScene();
    } else if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      marks.push({ ...cursor });
      updateCrop();
    }
  });

  undo.addEventListener('click', () => { marks.pop(); updateCrop(); });
  download.addEventListener('click', () => {
    const rows = marks.map(({ x, y }, index) => `${String(index + 1).padStart(2, '0')},${x},${y}`);
    const url = URL.createObjectURL(new Blob([['label,x,y', ...rows].join('\n') + '\n'], { type: 'text/csv' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = 'clicks.csv';
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });

  source.addEventListener('load', () => {
    cropReady = true;
    const selected = cropDemo.closest('[data-goal]').querySelector('[data-selected] code');
    cropDemo.hidden = selected?.textContent !== 'prepare_image_regions.py';
    updateCrop();
  });
  source.src = 'examples/example_grid.png';
}

if (cropDemo) setupCropDemo();
selectGoal();
