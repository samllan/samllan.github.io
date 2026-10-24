"""Build the static portfolio using only Python's standard library."""
import argparse
from html import escape
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', default='docs', help='Output directory (default: docs)')
OUT = ROOT / parser.parse_args().output
(OUT / 'projects').mkdir(parents=True, exist_ok=True)
(OUT / 'assets').mkdir(exist_ok=True)

# Publication assets are versioned independently of the other project folders.
for source in (ROOT / 'site' / 'assets').iterdir():
    if source.is_file():
        shutil.copyfile(source, OUT / 'assets' / source.name)
shutil.copyfile(ROOT / 'site' / 'flutter_service_worker.js', OUT / 'flutter_service_worker.js')
(OUT / '.nojekyll').touch()

PROJECTS = [
    dict(id='morrow', title='Morrow Plan', category='Product · Reflection', image='morrow.png',
         line='A quiet place for thoughts worth returning to.', colour='rose',
         intro='Capture a voice note before the thought disappears. Keep recordings, words and photos together, and return to them through a calendar or a persistent collection.',
         goal='Make reflection easy to begin and useful to revisit.',
         work='I conceived the product and directed its design and AI-assisted implementation, contributing code and refining the experience through repeated visual and functional feedback.',
         result='The current project supports guest use, local persistence, recording and playback, calendar organisation and optional account sync. The core design balances quick capture with finding earlier entries.',
         lesson='Keep capture simple; let organisation happen without making every thought a filing task.',
         links=[('Open Morrow Plan', 'https://morrowplan.com/')],
         visual='morrow'),
    dict(id='lorbefor', title='Lorbefor', category='Product · Local connection', image='lorbefor.png',
         line='Make nearby possibilities easier to act on.', colour='green',
         intro='A map-based product for finding local activities, organising events and connecting around shared interests.',
         goal='Help people move from “what could I do nearby?” to a concrete plan.',
         work='I conceived the product and directed its design and AI-assisted development, contributing code and shaping the map, event and account experiences.',
         result='A web product with map-based discovery, events, attendance and groups. The development work includes account handling and fixes to the real published interface.',
         lesson='The map needs to lead to a useful next action: discover something, inspect it, then take part.',
         links=[('Open Lorbefor', 'https://lorbefor.com/')], visual='lorbefor'),
    dict(id='words', title='A map of words', category='St Andrews · Interactive visualisation', image='words.webp',
         line='Follow meanings. Discover connections.', colour='blue',
         intro='A visual way to explore how words relate. Search for a word, follow its synonyms, inspect alternative meanings and retrace the route you took.',
         goal='Make relationships between words visible and explorable, rather than presenting another flat list of definitions.',
         work='An equal collaboration with Nina Sushko at St Andrews: Nina designed the interface, and I built the underlying data and application logic. The implementation combines HTML, CSS, JavaScript and D3.',
         result='The prototype explores a subset of 484 words. Distance represents shared synonym relationships; size communicates frequency and precision. Search and graph rendering have been checked on the live site.',
         lesson='A network can turn looking up one word into discovering a neighbourhood of related meanings. It represents synonym relationships, not a historical family tree.',
         links=[('Explore the live word map', 'https://samllan.github.io/Words/'), ('Read the source', 'https://github.com/samllan/Words')], visual='words'),
    dict(id='weather', title='The shape of a season', category='AA · Applied mathematics', image='weather.webp',
         line='Use a repeating model for a repeating year.', colour='ochre',
         intro='At the AA, I used Fourier techniques to model seasonal weather patterns. A year repeats; a seasonal model should be able to join December back to January naturally.',
         goal='Represent the broad seasonal curve while allowing its shape to depart from a single, perfectly symmetric sine wave.',
         work='I applied a sum of periodic sine and cosine components to seasonal weather modelling. Additional harmonics can represent asymmetry and finer structure without losing the annual cycle.',
         result='The project is part of my operational analytics work at the AA. The interactive figure explains the modelling idea using synthetic data; it is not an AA dataset or a recovered project result.',
         lesson='A flexible fit is not automatically a better forecast. The number of harmonics should be chosen with validation; it can otherwise fit noise.',
         links=[], visual='fourier'),
    dict(id='community', title='Building AI communities', category='Leadership · AI Society + AI²', image='community.png',
         line='Give curious people a place to meet and build.', colour='orange',
         intro='AI Society Leeds and the AI² forum connect students, researchers and people in industry through learning, discussion and events.',
         goal='Make AI approachable across disciplines and create opportunities to learn from one another.',
         work='I founded and served as President of the AI Society, and organised AI-related community activities. The linked sites document the society and forum; the precise chronology and my AI² role will be set out with the event records.',
         result='Public resources include workshop material, committee information and a university page describing the AI² forum and its past-event archive.',
         lesson='Community building is a practical contribution: create the setting, bring people together and make it easy for newcomers to take part.',
         links=[('AI Society Leeds', 'https://aisocietyleeds.wordpress.com/'), ('The AI² forum', 'https://leeds-ai-cdt.github.io/ai_squared/')], visual='community'),
    dict(id='music', title='Music Note Rain', category='Creative technology · Working prototype', image=None,
         line='See the music coming. Play into the flow.', colour='violet',
         intro='A piano-note waterfall that turns musical timing into something you can see. The local prototype explores lead, accompaniment and combined arrangements at five levels of complexity.',
         goal='Make a playable musical outline easier to follow, with the sound and falling notes telling the same story.',
         work='I developed the idea and directed its AI-assisted implementation. The prototype combines audio analysis, constrained musical arrangements, note visualisation and local storage.',
         result='The local prototype supports imported recordings, three arrangement types and five difficulty levels. This browser excerpt plays its existing composed demo; it does not analyse uploaded music.',
         lesson='A useful arrangement preserves the musical phrase while reducing the number of gestures a player must perform. Mixed-recording transcription remains experimental.',
         links=[], visual='music'),
    dict(id='ultrasound', title='From echoes to shapes', category='Ultrasound · Research prototype', image='ultrasound.png',
         line='Can a network learn to reconstruct what made an echo?', colour='teal',
         intro='Use a simulator where the object is known, collect the received ultrasound waveforms, then investigate whether a neural network can reconstruct the original shape directly.',
         goal='Explore learned reconstruction as an alternative to a manually designed reconstruction pipeline.',
         work='I explored Field II simulation, radio-frequency waveform processing and PyTorch models that map received signals to an image. The scripts build on Field II examples by Jørgen Arendt Jensen.',
         result='The local archive contains simulation scripts, received-waveform files, model checkpoints, a notebook and a saved training figure. This establishes an exploratory experiment, not a validated imaging system.',
         lesson='Matching a training example is only the beginning. The decisive test is reconstruction of new simulated objects, compared fairly with a conventional method.',
         links=[], visual='ultrasound'),
    dict(id='medicine', title='Incidental AI', category='Medical education · Hackathon prototype', image='medicine.webp',
         line='A clinical scenario becomes a learning conversation.', colour='pink',
         intro='A hackathon exploration of generative AI for medical teaching: present a simulated clinical scenario and image, invite a learner to reason about it, and respond conversationally.',
         goal='Explore an interactive way to practise clinical reasoning with generated teaching material.',
         work='Built together in a four-person hackathon team, without AI-assisted coding. The prototype combines a Streamlit interface, scenario generation, image-generation calls and a chat component.',
         result='The archive contains application code and a recorded Streamlit demonstration from September 2023. The code also contains fallback paths and unfinished sections; it is presented as a hackathon concept.',
         lesson='A convincing teaching interface needs reliable, reviewed examples and feedback. Generated scenarios and images do not establish clinical correctness.',
         links=[], visual='medicine'),
]


def header(prefix=''):
    return f'<header><a class="brand" href="{prefix}index.html">Samuel Llanwarne<span>Research · Products · Play</span></a><nav aria-label="Main"><a href="{prefix}index.html#work">Work</a><a href="{prefix}index.html#about">About</a><a href="https://github.com/samllan">GitHub ↗</a></nav></header>'


def document(title, description, body, prefix='', script=''):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} — Samuel Llanwarne</title><meta name="description" content="{escape(description, quote=True)}">
<link rel="stylesheet" href="{prefix}style.css"></head><body><a class="skip" href="#main">Skip to content</a>
{header(prefix)}{body}<footer><span>Samuel Llanwarne</span><span>Curiosity, made useful.</span><a href="https://github.com/samllan">Find me on GitHub ↗</a></footer>{script}</body></html>'''


def visual(p):
    key = p['visual']
    if key == 'fourier':
        return '''<section class="experiment" aria-label="Fourier demonstration"><div class="experiment-heading"><h2>One year. Several waves.</h2><span>Illustrative · synthetic data</span></div><svg id="fourier" viewBox="0 0 900 340" role="img" aria-label="Seasonal curve and its harmonic approximation"></svg><div class="controls"><label for="harmonics">Harmonics <output id="harmonic-count">1</output></label><input id="harmonics" type="range" min="1" max="4" value="1"><span class="legend"><i></i>Example seasonal shape <b></b>Approximation</span></div><p class="caption">Add harmonics to capture more of this constructed seasonal shape. This demonstrates representation, not forecast accuracy.</p></section>'''
    if key == 'music':
        return '''<section class="experiment music-demo"><div class="experiment-heading"><h2>First Light</h2><span>Composed demo · from the existing prototype</span></div><svg id="rain" viewBox="0 0 900 360" role="img" aria-label="Piano notes falling towards a keyboard"></svg><div class="controls"><button id="play" type="button" disabled>Loading demo…</button><button id="reset" type="button">Restart</button><span id="music-status" role="status">24-second practice pattern · synthesised sound</span></div></section>'''
    if key == 'ultrasound':
        return '<figure class="result-image"><img src="../assets/ultrasound.png" alt="Grayscale shape figure saved with the ultrasound experiment"><figcaption>Saved experimental figure, labelled “FC only network 20 epochs” in the original archive. This is not a held-out evaluation.</figcaption></figure>'
    steps = {
        'morrow': [('Capture', 'Voice, text or a photo'), ('Keep', 'A day or a collection'), ('Return', 'Find the thought again')],
        'lorbefor': [('Discover', 'Explore nearby activities'), ('Choose', 'Inspect an event'), ('Connect', 'Make a local plan')],
        'words': [('Find', 'Search for a word'), ('Follow', 'Explore related meanings'), ('Retrace', 'See where you have been')],
        'community': [('Connect', 'Across disciplines'), ('Share', 'Workshops and conversations'), ('Build', 'A learning community')],
        'medicine': [('Scenario', 'Generated teaching case'), ('Reasoning', 'Learner interpretation'), ('Discussion', 'Conversational feedback')],
    }[key]
    return '<div class="flow" aria-label="Project concept">' + ''.join(f'<div><strong>{a}</strong><span>{b}</span></div>' for a, b in steps) + '</div>'


cards = []
for p in PROJECTS:
    img = f'<img src="assets/{p["image"]}" alt="" loading="lazy">' if p['image'] else '<div class="note-art" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>'
    cards.append(f'''<a class="card {p['colour']} {p['id']}" href="projects/{p['id']}.html">{img}<div class="shade"></div><div class="card-copy"><span class="eyebrow">{p['category']}</span><h3>{p['title']}</h3><p>{p['line']}</p><span class="card-arrow" aria-hidden="true">↗</span></div></a>''')
    links = ''.join(f'<a class="button" href="{url}">{label} ↗</a>' for label, url in p['links'])
    body = f'''<main id="main" class="project"><a class="back" href="../index.html#work">← All work</a><section class="project-intro"><p class="eyebrow">{p['category']}</p><h1>{p['title']}</h1><p class="project-line">{p['line']}</p><p class="intro">{p['intro']}</p>{f'<div class="actions">{links}</div>' if links else ''}</section>{visual(p)}<div class="project-facts"><section><h2>The aim</h2><p>{p['goal']}</p></section><section><h2>The work</h2><p>{p['work']}</p></section><section><h2>What exists</h2><p>{p['result']}</p></section></div><aside class="takeaway"><span class="eyebrow">The useful insight</span><p>{p['lesson']}</p></aside><a class="back" href="../index.html#work">← Explore the other projects</a></main>'''
    script = '<script src="../experiments.js" defer></script>' if p['id'] in ('weather', 'music') else ''
    (OUT / 'projects' / f'{p["id"]}.html').write_text(document(p['title'], p['line'], body, '../', script), encoding='utf-8')

body = f'''<main id="main"><section class="hero"><p class="eyebrow">Physics. AI. Useful things.</p><h1>Follow the curiosity.<br><em>Make something useful.</em></h1><p>I’m Samuel. I explore signals, build products and bring people together.<br>A selection of the things I’ve made, investigated and helped shape.</p><a class="text-link" href="#work">Explore the work ↓</a></section><section id="work" class="work"><div class="section-label"><h2>Selected work</h2><span>Research · Products · Community · Creative technology</span></div><div class="grid">{''.join(cards)}</div></section><section id="about" class="about"><p class="eyebrow">A connected set of interests</p><h2>From a signal<br>to something you can use.</h2><div><p>My background spans physics and astronomy at Durham, computer science at St Andrews, and doctoral research in medical image analysis at Leeds.</p><p>I’m interested in how ideas become understandable and useful: an image reconstructed from a waveform, a map that reveals a relationship, or a product that makes an everyday action easier.</p><p>My recent products combine my own concepts and design direction with AI-assisted development. Collaborative and research projects identify their context and contribution on their individual pages.</p></div></section></main>'''
(OUT / 'index.html').write_text(document('Research, products & play', 'Samuel Llanwarne’s selected projects in research, products, community and creative technology.', body), encoding='utf-8')
for name in ('style.css', 'experiments.js', 'music-demo.json'):
    destination = OUT / 'assets' / name if name.endswith('.json') else OUT / name
    shutil.copyfile(ROOT / 'tool' / name, destination)
print(f'Built {len(PROJECTS)} project pages and a homepage in {OUT}')
