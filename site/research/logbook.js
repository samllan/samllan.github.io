const logbook = document.querySelector('.lab');
const content = logbook.querySelector('.lab-content');
const goals = [...logbook.querySelectorAll('[data-goal]')];
const goalLinks = [...logbook.querySelectorAll('.lab-goals a[href^="#"]')];

function selectGoal() {
  const active = goals.find(goal => `#${goal.id}` === location.hash) || goals[0];
  goals.forEach(goal => { goal.hidden = goal !== active; });
  goalLinks.forEach(link => {
    if (link.hash === `#${active.id}`) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
  content.scrollTop = 0;
}

logbook.classList.add('enhanced');
window.addEventListener('hashchange', selectGoal);
selectGoal();

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

logbook.querySelectorAll('.lab-file').forEach(link => {
  link.addEventListener('click', async event => {
    if (!dialog.showModal || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    if (link.dataset.openGoal && location.hash !== `#${link.dataset.openGoal}`) {
      location.hash = link.dataset.openGoal;
      selectGoal();
    }
    previewRequest?.abort();
    const request = new AbortController();
    previewRequest = request;
    document.querySelector('#preview-title').textContent = link.textContent;
    const isScript = link.href.endsWith('.py');
    previewOpen.href = isScript ? `${sourceDirectory}/${link.href.split('/').pop()}` : link.href;
    previewOpen.textContent = isScript ? 'Open on GitHub ↗' : 'Open file ↗';
    document.querySelector('#preview-download').href = link.href;
    previewContent.textContent = 'Loading file…';
    dialog.showModal();

  if (link.href.endsWith('.png') || link.href.endsWith('.svg')) {
      const image = new Image();
      image.alt = link.textContent;
      image.src = link.href;
      previewContent.replaceChildren(image);
      return;
    }

    try {
      const response = await fetch(link.href, { signal: request.signal });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const text = await response.text();
      if (!request.signal.aborted) previewContent.replaceChildren(filePreview(text, link.href));
    } catch (error) {
      if (!request.signal.aborted) previewContent.textContent = 'Preview unavailable. Use the links below.';
    }
  });
});
dialog.addEventListener('close', () => previewRequest?.abort());

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
  document.querySelector('.lab-demo').hidden = false;
  updateCrop();
});
source.src = 'examples/example_grid.png';
