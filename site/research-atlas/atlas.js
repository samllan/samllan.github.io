(() => {
  const get = id => document.getElementById('atlas-' + id);
  const canvas = get('canvas'), ctx = canvas.getContext('2d');
  const query = get('query'), method = get('method'), dialog = get('dialog');
  const tooltip = get('tooltip'), results = get('results');
  const collections = new Map(), baskets = {papers: new Set(), wiki: new Set()};
  const colours = ['#cf8b59', '#d6ac71', '#cad296', '#76bca2', '#428f88'];
  const edits = ['#79afd3', '#a2beca', '#d2d7c7', '#dc9b83', '#c2745c'];
  const format = new Intl.NumberFormat('en-GB');
  let source = 'papers', data, points = [], matches = null, view = {zoom: 1, x: 0, y: 0};
  let width = 0, height = 0, frame = 0, loadId = 0, drag;

  function node(tag, text, cls) {
    const element = document.createElement(tag);
    if (text) element.textContent = text;
    if (cls) element.className = cls;
    return element;
  }

  function control(text, action, label) {
    const button = node('button', text);
    button.type = 'button';
    if (label) button.setAttribute('aria-label', label);
    button.addEventListener('click', action);
    return button;
  }

  const paper = () => source === 'papers';
  const basket = () => baskets[source];
  const title = i => data.records[i][1];

  function schedule() {
    if (!frame) frame = requestAnimationFrame(draw);
  }

  function geometry() {
    if (!data) return;
    const positions = data.maps[method.value];
    const max = Math.max(1, ...data.records.map(row => row[3] || 0));
    points = data.records.map(([id, , , reach, spread], i) => {
      const count = data.edits?.[id];
      const fill = paper() ? colours[Math.round(4 * (1 - spread / 255))]
        : count == null ? '#83978f' : edits[Math.round(4 * Math.min(1, Math.log1p(count) / Math.log1p(1500)))];
      return {i, x: positions[2*i] / 65535 - .5, y: positions[2*i+1] / 65535 - .5,
        r: .85 + 3.1 * Math.log1p(reach || 0) / Math.log1p(max), fill};
    }).sort((a,b) => b.r - a.r);
    schedule();
  }

  function draw() {
    frame = 0;
    ctx.clearRect(0, 0, width, height);
    if (!data) return;
    const scale = Math.min(width * .87, height * .85) * view.zoom;
    const cx = width / 2 + view.x, cy = height / 2 + view.y;
    const rings = [];
    for (const point of points) {
      const {i, r, fill} = point;
      const x = point.sx = cx + point.x * scale, y = point.sy = cy + point.y * scale;
      if (x < -10 || y < -10 || x > width + 10 || y > height + 10) continue;
      const selected = basket().has(i);
      ctx.globalAlpha = selected || !matches || matches.has(i) ? .95 : .12;
      ctx.fillStyle = fill;
      ctx.beginPath();
      ctx.arc(x, y, r, 0, 2 * Math.PI);
      ctx.fill();
      if (selected) rings.push(point);
    }
    ctx.globalAlpha = 1;
    ctx.lineWidth = 1.6;
    ctx.strokeStyle = '#fff2a5';
    for (const point of rings) {
      ctx.beginPath();
      ctx.arc(point.sx, point.sy, point.r + 4, 0, 2 * Math.PI);
      ctx.stroke();
    }
  }

  new ResizeObserver(() => {
    const bounds = canvas.getBoundingClientRect();
    width = bounds.width;
    height = bounds.height;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    schedule();
  }).observe(canvas);

  function pointAt(x, y) {
    let best = 13 ** 2, hit;
    for (const point of points) {
      if (matches && !matches.has(point.i) && !basket().has(point.i)) continue;
      const distance = (x - point.sx) ** 2 + (y - point.sy) ** 2;
      if (distance < best) { best = distance; hit = point; }
    }
    return hit;
  }

  canvas.addEventListener('pointerdown', e => {
    if (e.button !== 0 || e.pointerType === 'touch' || view.zoom === 1) return;
    drag = {x: e.clientX, y: e.clientY, baseX: view.x, baseY: view.y, moved: false};
    canvas.setPointerCapture(e.pointerId);
  });
  canvas.addEventListener('pointermove', e => {
    if (drag && (drag.moved || Math.hypot(e.clientX - drag.x, e.clientY - drag.y) > 4)) {
      drag.moved = true;
      view.x = drag.baseX + e.clientX - drag.x;
      view.y = drag.baseY + e.clientY - drag.y;
      tooltip.hidden = true;
      schedule();
      return;
    }
    if (!data || e.pointerType === 'touch') return;
    const x = e.offsetX, y = e.offsetY, hit = pointAt(x, y);
    tooltip.hidden = !hit;
    if (!hit) return;
    tooltip.textContent = title(hit.i);
    tooltip.style.left = Math.max(6, Math.min(x + 14, width - tooltip.offsetWidth - 6)) + 'px';
    tooltip.style.top = Math.max(6, Math.min(y + 14, height - tooltip.offsetHeight - 6)) + 'px';
  });
  canvas.addEventListener('pointerleave', () => { tooltip.hidden = true; });
  canvas.addEventListener('pointercancel', () => { drag = null; });
  canvas.addEventListener('click', e => {
    if (!drag?.moved) {
      const hit = pointAt(e.offsetX, e.offsetY);
      if (hit) toggle(hit.i);
    }
    drag = null;
  });

  function resetView() {
    view = {zoom: 1, x: 0, y: 0};
    tooltip.hidden = true;
    schedule();
  }
  get('reset').onclick = resetView;
  function zoom(factor) {
    view.zoom = Math.min(5, Math.max(1, view.zoom * factor));
    if (view.zoom === 1) resetView();
    schedule();
  }
  get('plus').onclick = () => zoom(1.35);
  get('minus').onclick = () => zoom(1 / 1.35);

  function renderBasket() {
    const selected = [...basket()];
    get('picks').replaceChildren(...selected.map(i => {
      const li = node('li');
      li.append(node('span', title(i)), control('×', () => toggle(i), 'Remove ' + title(i)));
      return li;
    }));
    get('pick-count').textContent = selected.length + ' of 3';
    get('empty').hidden = selected.length > 0;
    get('open').disabled = selected.length === 0;
    schedule();
  }

  function toggle(i) {
    const selected = basket(), status = get('status');
    status.textContent = '';
    if (selected.has(i)) selected.delete(i);
    else if (selected.size < 3) selected.add(i);
    else status.textContent = 'Remove a selection to add another.';
    renderBasket();
    for (const button of results.querySelectorAll('button')) {
      button.setAttribute('aria-pressed', selected.has(Number(button.dataset.index)));
    }
  }

  function filter() {
    const term = query.value.trim().toLocaleLowerCase();
    matches = null;
    results.replaceChildren();
    results.hidden = !term || !data;
    if (data && term) {
      matches = new Set();
      data.records.forEach((row, i) => {
        if (row[1].toLocaleLowerCase().includes(term)) matches.add(i);
      });
      for (const i of [...matches].slice(0, 8)) {
        const button = control(title(i), () => toggle(i));
        button.dataset.index = i;
        button.setAttribute('aria-pressed', basket().has(i));
        results.append(button);
      }
      if (!matches.size) results.append(node('p', 'No matches.', 'atlas-status'));
    }
    updateCount();
    schedule();
  }

  function updateCount() {
    if (!data) return;
    const count = format.format(data.records.length);
    get('count').textContent = matches ? format.format(matches.size) + ' matches of ' + count
      : count + (paper() ? ' papers' : ' pages');
  }

  function updateMethod() {
    const description = {
      blend: 'This layout combines the text map with ' + (paper() ? 'the citation map.' : 'the page-link map.'),
      text: 'MiniLM converts article text into vectors. The map places records with similar vectors closer together.',
      topics: 'Records sit near others with similar mixtures of topics, including records that span several themes.',
      links: paper() ? 'Nearby papers tend to cite one another or share references within the sample.'
        : 'Nearby pages tend to link to one another or have links in common within the sample.'
    };
    get('explanation').textContent = description[method.value];
    resetView();
    geometry();
  }

  async function load(next) {
    const requestId = ++loadId;
    source = next;
    data = null;
    points = [];
    matches = null;
    query.value = '';
    query.disabled = true;
    get('example').hidden = !paper();
    get('example').disabled = true;
    get('count').textContent = 'Loading map…';
    get('status').textContent = '';
    get('key').replaceChildren();
    document.querySelectorAll('[data-source]').forEach(button =>
      button.setAttribute('aria-pressed', button.dataset.source === source));
    method.options[3].textContent = paper() ? 'Citation proximity' : 'Page-link proximity';
    renderBasketWhenLoading();
    filter();
    resetView();
    try {
      if (!collections.has(next)) {
        const response = await fetch('../assets/research-atlas-' + next + '.json');
        if (!response.ok) throw new Error('Collection unavailable');
        collections.set(next, await response.json());
      }
      if (requestId !== loadId) return;
      data = collections.get(next);
      query.disabled = false;
      query.placeholder = paper() ? 'Try amyloid or sleep' : 'Try memory or learning';
      get('example').disabled = false;
      const ramp = node('span', '', paper() ? 'atlas-ramp' : 'atlas-ramp edits');
      ramp.setAttribute('aria-hidden', 'true');
      get('key').append(node('span', paper() ? 'Less text alignment' : 'Fewer edits'), ramp,
        node('span', paper() ? 'More alignment' : 'More edits · grey = unsampled'),
        node('span', paper() ? 'Size = citations' : 'Size = page views'));
      updateCount();
      updateMethod();
      renderBasket();
    } catch {
      if (requestId === loadId) {
        get('count').textContent = 'Map unavailable';
        get('status').textContent = 'Select the collection again to retry.';
      }
    }
  }

  function renderBasketWhenLoading() {
    get('picks').replaceChildren();
    get('pick-count').textContent = '0 of 3';
    get('open').disabled = true;
    get('empty').hidden = false;
  }

  function summary(i) {
    const [id, name, year, reach] = data.records[i];
    const card = node('article'), heading = node('h3'), link = node('a', name);
    link.href = (paper() ? 'https://pubmed.ncbi.nlm.nih.gov/' : 'https://simple.wikipedia.org/?curid=') + id;
    heading.append(link);
    const units = paper() ? ' citations' : (data.reachWindow === 'hour' ? ' page views in the sampled hour' : ' page views');
    card.append(node('p', [year, reach == null ? '' : format.format(reach) + units].filter(Boolean).join(' · ')), heading);
    const checked = data.checked?.[id];
    if (!checked) {
      card.append(node('p', paper() ? 'Open the source to read the abstract and publication details.' : 'Open the source to read the page and its references.'));
      return card;
    }
    card.append(node('p', checked.finding));
    const scope = node('dl');
    for (const [label,key] of [['Population','population'], ['Measure','measure'], ['Outcome','outcome'], ['Timing','time']]) {
      scope.append(node('dt', label), node('dd', checked[key]));
    }
    card.append(scope, node('p', 'Checked against the abstract'));
    return card;
  }

  function compare() {
    const selected = [...basket()];
    if (!selected.length) return;
    const grid = node('div', '', 'atlas-dialog-grid');
    grid.append(...selected.map(summary));
    get('dialog-title').textContent = selected.length === 1 ? 'Record summary' : 'Comparison';
    const content = get('dialog-content');
    content.replaceChildren(grid);
    const pairs = [];
    selected.forEach((left, a) => selected.slice(a + 1).forEach((right, index) => {
      const key = [data.records[left][0], data.records[right][0]].sort().join('/');
      const score = data.scores?.[key];
      if (score == null) return;
      const pair = node('section', '', 'atlas-pair');
      pair.append(node('h3', 'Papers ' + (a + 1) + ' and ' + (a + index + 2) + ' · ' + score.toFixed(2) + ' text similarity'));
      pair.append(node('p', key === '39948000/42009653'
        ? 'Both studies assess diagnostic discrimination in Chinese cohorts. They use different assay setups and report different metrics.'
        : 'The diagnostic study distinguishes groups at assessment. The Shanghai study follows people initially free of dementia to examine later outcomes.'));
      pairs.push(pair);
    }));
    if (pairs.length) content.append(node('h3', 'How the studies relate'), node('p', 'MiniLM compares the wording. Study scope and findings help you judge whether the evidence addresses the same question.'), ...pairs);
    dialog.showModal();
  }

  query.addEventListener('input', filter);
  method.addEventListener('change', updateMethod);
  document.querySelectorAll('[data-source]').forEach(button => button.addEventListener('click', () => {
    if (button.dataset.source !== source || !data) load(button.dataset.source);
  }));
  get('open').onclick = compare;
  get('example').onclick = () => {
    const index = new Map(data.records.map((row, i) => [row[0], i]));
    baskets.papers = new Set(data.example.map(id => index.get(id)));
    get('status').textContent = '';
    query.value = '';
    filter();
    renderBasket();
    compare();
  };
  load('papers');
})();
