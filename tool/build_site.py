"""Build the static portfolio using only Python's standard library."""
import argparse
import hashlib
from html import escape
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
STYLE_VERSION = hashlib.sha256((ROOT / 'tool' / 'style.css').read_bytes()).hexdigest()[:10]
SCRIPT_VERSION = hashlib.sha256((ROOT / 'tool' / 'experiments.js').read_bytes()).hexdigest()[:10]
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
    dict(id='phd', title='Making medical images useful', category='PhD research · Leeds', image='phd.webp',
         line='Deep learning for large medical images.', colour='blue',
         intro='Digital pathology images can be very large. My doctoral research developed a multi-scale pipeline for learning from lymphoma tissue: organise the data, reduce its cost, compare useful representations and inspect what the models learn.',
         goal='Investigate how deep learning can predict supplied expert scores and lymphoma subtype labels from stained tissue images, while making the data practical to process.',
         work='I developed image-preparation and labelling tools, structured cell-, patch- and core-level datasets, compared autoencoder and contrastive representations, and investigated model explanations including Spectral Dream Dimming.',
         result='The thesis reports extraction time reduced from 6 to 3 seconds per sample, patch storage reduced from 26.94 to 3.63 GB, and processed views covering 1,109 cores, 229,683 patches and 9,126,415 cell instances.',
         lesson='Preparing the images and labels took as much thought as choosing the models. Those decisions affected both the computing cost and the results.',
         links=[], visual='phd'),
    dict(id='tuberculosis', title='Finding and counting bacteria', category='St Andrews · MSc research', image='tuberculosis.webp',
         line='Computer vision for tuberculosis microscopy.', colour='teal',
         intro='Bacteria can be faint, overlap one another or blend into the background of a microscope image. At St Andrews, I investigated whether computer vision could help specialists find and count them.',
         goal='Build an inspectable image-analysis pipeline that finds likely bacterial regions and estimates how many cells they contain, with a longer-term interest in studying bacterial changes during treatment.',
         work='I developed the Python/PyTorch pipeline around established detection and counting networks, prepared and labelled images with domain-expert input, built image transformations and experiment records, and investigated performance on increasingly varied data.',
         result='The submitted MSc thesis documents the pipeline, detection overlays, counting experiments and error analysis. A small test on images from a patient unseen during training produced a total count of 91 against an expert count of 106.',
         lesson='Saving the detected regions made it easier to check mistakes. I also found that a close total count could hide errors in individual regions.',
         links=[], visual='tuberculosis'),
    dict(id='telescope', title='Listening to the Milky Way', category='Durham · Radio astronomy', image='telescope.webp',
         line='Studying the Milky Way with a student-built radio telescope.', colour='ochre',
         intro='My Durham project involved working with a student-built radio telescope and processing its observations into preliminary sky maps. It combined practical work on the instrument with programming and data analysis.',
         goal='Explore Milky Way structure through radio observations, connecting practical telescope work with questions about galactic rotation and mass.',
         work='The project combined hardware setup and investigation with programming. Loading, cleaning, visualising and interpreting observations formed a substantial part of the work, alongside automating repeated analysis.',
         result='The project produced preliminary sky maps and data visualisations. My retrospective presentation records the hardware work, data-processing activities and scientific aims, with instrument noise and further automation identified as directions for improvement.',
         lesson='Understanding the telescope mattered as much as writing the analysis. Noise and the way we processed the observations affected what we could learn from them.',
         links=[], visual='telescope'),
    dict(id='morrow', title='Morrow Plan', category='Product · Reflection', image='morrow.png',
         line='Record thoughts and find them again later.', colour='rose',
         intro='Capture a voice note before the thought disappears. Keep recordings, words and photos together, and return to them through a calendar or a persistent collection.',
         goal='Make reflection easy to begin and useful to revisit.',
         work='I conceived the product and directed its design and AI-assisted implementation, contributing code and refining the experience through repeated visual and functional feedback.',
         result='The current project supports guest use, local persistence, recording and playback, calendar organisation and optional account sync. The core design balances quick capture with finding earlier entries.',
         lesson='I wanted recording a thought to be quick, with dates and collections helping people find it later.',
         links=[('Open Morrow Plan', 'https://morrowplan.com/')],
         visual='morrow'),
    dict(id='lorbefor', title='Lorbefor', category='Product · Local connection', image='lorbefor.png',
         line='Find local activities and arrange to take part.', colour='green',
         intro='A map-based product for finding local activities, organising events and connecting around shared interests.',
         goal='Help people move from “what could I do nearby?” to a concrete plan.',
         work='I conceived the product and directed its design and AI-assisted development, contributing code and shaping the map, event and account experiences.',
         result='A web product with map-based discovery, events, attendance and groups. The development work includes account handling and fixes to the real published interface.',
         lesson='Finding an event is only part of the task. Its details and the option to join need to be easy to reach from the map.',
         links=[('Open Lorbefor', 'https://lorbefor.com/')], visual='lorbefor'),
    dict(id='words', title='A map of words', category='St Andrews · Interactive visualisation', image='words.webp',
         line='Explore words and their related meanings.', colour='blue',
         intro='A visual way to explore how words relate. Search for a word, follow its synonyms, inspect alternative meanings and retrace the route you took.',
         goal='Make relationships between words visible and explorable, rather than presenting another flat list of definitions.',
         work='An equal collaboration with Nina Sushko at St Andrews: Nina designed the interface, and I built the underlying data and application logic. The implementation combines HTML, CSS, JavaScript and D3.',
         result='The prototype explores a subset of 484 words. Distance represents shared synonym relationships; size communicates frequency and precision. Search and graph rendering have been checked on the live site.',
         lesson='A network can turn looking up one word into discovering a neighbourhood of related meanings. It represents synonym relationships, not a historical family tree.',
         links=[('Explore the live word map', 'https://samllan.github.io/Words/'), ('Read the source', 'https://github.com/samllan/Words')], visual='words'),
    dict(id='weather', title='The shape of a season', category='AA · Applied mathematics', image='weather.webp',
         line='Modelling seasonal weather with Fourier curves.', colour='ochre',
         intro='At the AA, I used Fourier techniques to model seasonal weather patterns. A year repeats; a seasonal model should be able to join December back to January naturally.',
         goal='Represent the broad seasonal curve while allowing its shape to depart from a single, perfectly symmetric sine wave.',
         work='I applied a sum of periodic sine and cosine components to seasonal weather modelling. Additional harmonics can represent asymmetry and finer structure without losing the annual cycle.',
         result='The project is part of my operational analytics work at the AA. The interactive figure explains the modelling idea using synthetic data; it is not an AA dataset or a recovered project result.',
         lesson='A flexible fit is not automatically a better forecast. The number of harmonics should be chosen with validation; it can otherwise fit noise.',
         links=[], visual='fourier'),
    dict(id='boat', title='Strathclyde boat challenge', category='Engineering · Teamwork', image='boat.jpg',
         line='Our team built the furthest-travelling boat in the challenge.', colour='blue',
         intro='A hands-on boat-building challenge at Strathclyde became a formative experience in practical design and working as a team. The aim was direct: build a boat that would travel the furthest distance.',
         goal='Make a design choice the team could build and put to the test in the distance challenge.',
         work='I helped build the boat and made a key decision about its design. The project brought together physical construction, a shared deadline and decisions that had to become something real.',
         result='Our boat achieved the furthest distance in the challenge, and I received a Team Player award.',
         lesson='A good design decision matters most when the team can turn it into a working result. This became an early, lasting example of how much I enjoy collaborative engineering.',
         links=[], visual='boat'),
    dict(id='lanes', title='Finding the road ahead', category='Computer vision · Coursework', image='lane-overlay.jpg',
         line='Finding lane markings in a road image.', colour='teal',
         intro='An early self-driving-car course project exploring a deceptively simple question: how can a computer identify lane markings in a road image?',
         goal='Find the left and right lane boundaries using classical image processing, and understand where those assumptions stop working.',
         work='The archived Udacity coursework introduced region selection, colour and edge processing, and line detection. The comparison is a small, newly implemented portfolio example: colour selection inside a road region, followed by a line fit on each side.',
         result='The new example produces two boundary overlays for one supplied course image. The short reproducible implementation is linked on this page. This educational single-image example has not been validated for curves, video, poor weather or unfamiliar roads.',
         lesson='Selecting the road region first made this example much simpler. It also made the assumptions and likely failure cases easier to see.',
         links=[('Original coursework', 'https://github.com/samllan/Self-Driving-Car-Lane-Lines'), ('Portfolio example code', 'https://github.com/samllan/samllan.github.io/blob/main/tool/lane_demo.py')], visual='lanes'),
    dict(id='community', title='Building AI communities', category='Leadership · AI Society + AI²', image='community.png',
         line='Organising AI workshops, discussions and events.', colour='orange',
         intro='AI Society Leeds and the AI² forum connect students, researchers and people in industry through learning, discussion and events.',
         goal='Make AI approachable across disciplines and create opportunities to learn from one another.',
         work='I founded and served as President of the AI Society, and organised AI-related community activities. The linked sites document the society and forum; the precise chronology and my AI² role will be set out with the event records.',
         result='Public resources include workshop material, committee information and a university page describing the AI² forum and its past-event archive.',
         lesson='I enjoyed bringing people from different subjects together and helping newcomers get involved.',
         links=[('AI Society Leeds', 'https://aisocietyleeds.wordpress.com/'), ('The AI² forum', 'https://leeds-ai-cdt.github.io/ai_squared/')], visual='community'),
    dict(id='music', title='Music Note Rain', category='Creative technology · Working prototype', image=None,
         line='Falling piano notes with synchronised playback.', colour='violet',
         intro='A piano-note waterfall that turns musical timing into something you can see. The local prototype explores lead, accompaniment and combined arrangements at five levels of complexity.',
         goal='Make a playable musical outline easier to follow, with the sound and falling notes telling the same story.',
         work='I developed the idea and directed its AI-assisted implementation. The prototype combines audio analysis, constrained musical arrangements, note visualisation and local storage.',
         result='The local prototype supports imported recordings, three arrangement types and five difficulty levels. This browser excerpt plays its existing composed demo; it does not analyse uploaded music.',
         lesson='A useful arrangement preserves the musical phrase while reducing the number of gestures a player must perform. Mixed-recording transcription remains experimental.',
         links=[], visual='music'),
    dict(id='ultrasound', title='From echoes to shapes', category='Ultrasound · Research prototype', image='ultrasound.png',
         line='Reconstructing simulated shapes from ultrasound signals.', colour='teal',
         intro='Use a simulator where the object is known, collect the received ultrasound waveforms, then investigate whether a neural network can reconstruct the original shape directly.',
         goal='Explore learned reconstruction as an alternative to a manually designed reconstruction pipeline.',
         work='I explored Field II simulation, radio-frequency waveform processing and PyTorch models that map received signals to an image. The scripts build on Field II examples by Jørgen Arendt Jensen.',
         result='The local archive contains simulation scripts, received-waveform files, model checkpoints, a notebook and a saved training figure. This establishes an exploratory experiment, not a validated imaging system.',
         lesson='Matching a training example is only the beginning. The decisive test is reconstruction of new simulated objects, compared fairly with a conventional method.',
         links=[], visual='ultrasound'),
    dict(id='medicine', title='Incidental AI', category='Medical education · Hackathon prototype', image='medicine.webp',
         line='A hackathon prototype for practising clinical reasoning.', colour='pink',
         intro='A hackathon exploration of generative AI for medical teaching: present a simulated clinical scenario and image, invite a learner to reason about it, and respond conversationally.',
         goal='Explore an interactive way to practise clinical reasoning with generated teaching material.',
         work='Built together in a four-person hackathon team, without AI-assisted coding. The prototype combines a Streamlit interface, scenario generation, image-generation calls and a chat component.',
         result='The archive contains application code and a recorded Streamlit demonstration from September 2023. The code also contains fallback paths and unfinished sections; it is presented as a hackathon concept.',
         lesson='A convincing teaching interface needs reliable, reviewed examples and feedback. Generated scenarios and images do not establish clinical correctness.',
         links=[], visual='medicine'),
]


def header(prefix=''):
    return f'<header><a class="brand" href="{prefix}index.html">Samuel Llanwarne</a><nav aria-label="Main"><a href="{prefix}index.html#work">Work</a><a href="{prefix}index.html#about">About</a><a href="https://github.com/samllan">GitHub ↗</a></nav></header>'


def document(title, description, body, prefix='', script=''):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} — Samuel Llanwarne</title><meta name="description" content="{escape(description, quote=True)}">
<link rel="stylesheet" href="{prefix}style.css?v={STYLE_VERSION}"></head><body><a class="skip" href="#main">Skip to content</a>
{header(prefix)}{body}<footer><span>Samuel Llanwarne</span><span>Research and personal projects</span><a href="https://github.com/samllan">Find me on GitHub ↗</a></footer>{script}</body></html>'''


def visual(p):
    key = p['visual']
    if key == 'tuberculosis':
        return '''<section class="story-board bacteria-board" aria-label="Tuberculosis research overview"><figure><img src="../assets/tuberculosis.webp" alt="Colourful stylised illustration of bacteria"><figcaption>Portfolio illustration · not a microscopy image</figcaption></figure><div class="story-copy"><p class="eyebrow">Finding bacteria in microscope images</p><h2>Detecting regions and estimating cell counts</h2><p>One network proposes regions of interest. A second estimates the number of bacteria inside each region. Saved crops and predictions make the intermediate decisions available for review.</p><div class="story-tags"><span>Computer vision</span><span>Expert-labelled data</span><span>Inspectable outputs</span></div></div></section><section class="count-study" aria-label="Held-out patient counting result"><div><p class="eyebrow">A small test on an unseen patient</p><h2>Comparing the model with an expert</h2><p>The model counted 14% fewer bacteria overall. It agreed with the expert on about 60% of individual region counts, so the total alone does not tell the whole story.</p></div><div class="count-bars" aria-label="Expert count 106; model count 91"><div><span>Expert count <strong>106</strong></span><div class="bar-track"><i style="width:100%"></i></div></div><div><span>Model count <strong>91</strong></span><div class="bar-track"><i style="width:85.85%"></i></div></div><p>Research prototype · small image subset<br>Image analysis, not a clinical diagnostic evaluation</p></div></section><div class="flow"><div><strong>Locate</strong><span>Detect candidate bacterial regions</span></div><div><strong>Estimate</strong><span>Count cells within each crop</span></div><div><strong>Inspect</strong><span>Review predictions and difficult cases</span></div></div><details class="research-notes"><summary>Research evidence and wider ambitions</summary><p>The detector used Faster R-CNN with a ResNet-50 backbone; the main counting experiments used ResNeXt-50. The work also addressed crop padding for rotation, consistent annotation, model training and experiment logging.</p><p>The thesis reports detection of over 80% of in-focus cells in a tested subset after training the detector on 100 images. This is an image-level prototype result, not patient-level diagnostic sensitivity. The separate unseen-patient counting test is reported above.</p><p>A longer-term aim was to add analysis of bacterial characteristics, including lipid content, to support research into treatment response. That classifier and clinical outcome prediction were not established by this project.</p><p>Source: <em>Understanding Tuberculosis — Computer Vision Based Analysis of Images Acquired Using a Novel Cell Staining Method</em>, Sam Llanwarne, MSc Advanced Computer Science, University of St Andrews, 16 August 2019. Printed pp23–34: pipeline; p37: detection; pp42–43, Table 7: unseen-patient counting; p45: future directions.</p></details>'''
    if key == 'telescope':
        return '''<section class="story-board telescope-board" aria-label="Radio astronomy project overview"><figure><img src="../assets/telescope.webp" alt="Stylised illustration of a mesh radio telescope"><figcaption>Portfolio illustration · not a photograph of the project telescope</figcaption></figure><div class="story-copy"><p class="eyebrow">Hands-on astronomy</p><h2>Working with the telescope and its data</h2><p>Much of the work involved loading, cleaning and interpreting the observations, then turning them into sky maps and plots.</p><div class="story-tags"><span>Instrumentation</span><span>Data analysis</span><span>Scientific computing</span></div></div></section><div class="flow"><div><strong>Observe</strong><span>Understand the telescope and its signals</span></div><div><strong>Process</strong><span>Clean data and automate repeated work</span></div><div><strong>Map</strong><span>Visualise and investigate the Milky Way</span></div></div><section class="sky-question"><p class="eyebrow">The scientific question</p><h2>Mapping the Milky Way</h2><p>We made preliminary sky maps and explored how radio observations could help us study the Milky Way’s structure, rotation and mass. The telescope’s behaviour and the quality of the data set limits on the analysis.</p></section><details class="research-notes"><summary>Project record and scope</summary><p>The recovered five-slide <em>Durham Radio Telescope Project</em> presentation records hardware setup, preliminary sky maps, data visualisations, data cleaning and automation. It also describes enjoyment of sustained research and building explanations by following useful questions.</p><p>The presentation uses “we”; these are project activities rather than a claim of sole ownership of the telescope or every component. Samuel describes this as his Durham master’s project involving a student-built mesh telescope.</p><p>Investigating noise sources, hardware improvements and complete automation appear as future work. No numerical estimate of galactic mass, map resolution or measured performance improvement is claimed here.</p></details>'''
    if key == 'phd':
        return '''<section class="research-impact" aria-label="Measured research contributions"><p class="eyebrow">Engineering results, reported in the thesis</p><div class="impact-grid"><div><strong>2× faster</strong><span>6 → 3 seconds per sample</span><p>Point-and-click extraction versus drawing rectangles, with precision and recall of 1.00 in the reported comparison.</p></div><div><strong>86.5% less</strong><span>26.94 → 3.63 GB</span><p>Patch-image storage through WebP compression. A storage result, not evidence of unchanged diagnostic performance.</p></div><div><strong>9.1 million</strong><span>cell instances processed</span><p>Alongside 229,683 patches and 1,109 tissue cores: different views of the research data, not independent cohorts.</p></div></div></section><div class="flow"><div><strong>Organise</strong><span>Images → labelled data</span></div><div><strong>Represent</strong><span>Cells → patches → cores</span></div><div><strong>Explain</strong><span>Predictions → visual evidence</span></div></div><details class="research-notes"><summary>Scientific findings and where the numbers come from</summary><p>The thesis investigates IHC grading against supplied expert scores and cell-of-origin classification against supplied gene-expression labels for diffuse large B-cell lymphoma.</p><p>IHC grading achieved MAE 0.238 against averaged expert scores. UNI patch features reached 97.0% accuracy and AUC 0.992 in the evaluated data. The thesis identifies non-independent internal validation: these are research results, not independently validated diagnostic performance or evidence of surpassing pathologists.</p><p>Source: <em>Multi-Scale and Multi-Stage Deep Learning for the Classification of Diffuse Large B-cell Lymphoma Histology</em>, Samuel Llanwarne, University of Leeds, June 2026. Printed p70, Table 2.5: extraction; pp71–72: storage; p186: scale; p161, Table 4.4: subtype results; p190: validation limitations.</p></details>'''
    if key == 'boat':
        return '<figure class="boat-figure"><img src="../assets/boat.jpg" alt="Towing-tank setting used in the original Strathclyde project panel"><figcaption>Towing-tank setting: image retained from the original portfolio.</figcaption></figure><div class="flow"><div><strong>Design</strong><span>A key boat-design decision</span></div><div><strong>Build</strong><span>Hands-on team construction</span></div><div><strong>Go further</strong><span>Furthest-distance challenge result</span></div></div><aside class="award"><span class="eyebrow">A personal highlight</span><h2>Team Player award</h2><p>An engineering challenge that became a lasting memory of building something together.</p></aside>'
    if key == 'lanes':
        return '''<section class="experiment" aria-label="Lane-detection example"><div class="experiment-heading"><h2>Look for the boundaries</h2><span>New portfolio demonstration · one course image</span></div><div class="lane-comparison"><img src="../assets/lane-input.jpg" alt="Original road image supplied with the Udacity lane-finding coursework"><img id="lane-overlay" src="../assets/lane-overlay.jpg" alt="The same road with two fitted lane boundaries highlighted" style="clip-path:inset(0 50% 0 0)"></div><div class="controls"><label for="lane-reveal">Reveal the fitted lines</label><input id="lane-reveal" type="range" min="0" max="100" value="50"></div><p class="caption">Course image: Udacity lane-finding materials in the original coursework repository. Overlay: a new colour-selection and line-fit example, prepared for this portfolio in October 2026.</p></section>'''
    if key == 'fourier':
        return '''<section class="experiment" aria-label="Fourier demonstration"><div class="experiment-heading"><h2>Approximating a seasonal curve</h2><span>Illustrative · synthetic data</span></div><svg id="fourier" viewBox="0 0 900 340" role="img" aria-label="Seasonal curve and its harmonic approximation"></svg><div class="controls"><label for="harmonics">Harmonics <output id="harmonic-count">1</output></label><input id="harmonics" type="range" min="1" max="4" value="1"><span class="legend"><i></i>Example seasonal shape <b></b>Approximation</span></div><p class="caption">Add harmonics to capture more of this constructed seasonal shape. This demonstrates representation, not forecast accuracy.</p></section>'''
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
    pictures = {
        'words': ('word-map-screen.png', 'The Word Map interface showing synonyms connected to the word visual', 'The original Word Map prototype, built with Nina Sushko.'),
        'community': ('community.png', 'AI Society Leeds logo', 'AI Society Leeds.'),
        'medicine': ('medicine.webp', 'Illustration used for the medical education project', 'Portfolio illustration for the hackathon project.'),
    }
    picture = ''
    if key in pictures:
        src, alt, caption = pictures[key]
        picture = f'<figure class="project-picture {key}-picture"><img src="../assets/{src}" alt="{alt}" loading="lazy"><figcaption>{caption}</figcaption></figure>'
    return picture + '<div class="flow" aria-label="Project concept">' + ''.join(f'<div><strong>{a}</strong><span>{b}</span></div>' for a, b in steps) + '</div>'


cards = []
for p in PROJECTS:
    img = f'<img src="assets/{p["image"]}" alt="" loading="lazy">' if p['image'] else '<div class="note-art" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>'
    cards.append(f'''<a class="card {p['colour']} {p['id']}" href="projects/{p['id']}.html">{img}<div class="shade"></div><div class="card-copy"><span class="eyebrow">{p['category']}</span><h3>{p['title']}</h3><p>{p['line']}</p><span class="card-arrow" aria-hidden="true">↗</span></div></a>''')
    links = ''.join(f'<a class="button" href="{url}">{label} ↗</a>' for label, url in p['links'])
    body = f'''<main id="main" class="project"><a class="back" href="../index.html#work">← All work</a><section class="project-intro"><p class="eyebrow">{p['category']}</p><h1>{p['title']}</h1><p class="project-line">{p['line']}</p><p class="intro">{p['intro']}</p>{f'<div class="actions">{links}</div>' if links else ''}</section>{visual(p)}<div class="project-facts"><section><h2>The aim</h2><p>{p['goal']}</p></section><section><h2>The work</h2><p>{p['work']}</p></section><section><h2>What exists</h2><p>{p['result']}</p></section></div><aside class="takeaway"><span class="eyebrow">What I learnt</span><p>{p['lesson']}</p></aside><a class="back" href="../index.html#work">← Explore the other projects</a></main>'''
    script = f'<script src="../experiments.js?v={SCRIPT_VERSION}" defer></script>' if p['id'] in ('weather', 'music', 'lanes') else ''
    (OUT / 'projects' / f'{p["id"]}.html').write_text(document(p['title'], p['line'], body, '../', script), encoding='utf-8')

body = f'''<main id="main">
<h1 class="visually-hidden">Selected work by Samuel Llanwarne</h1>
<section id="work" class="work" aria-label="Portfolio"><div class="grid">{''.join(cards)}</div></section>
<section id="about" class="about"><h2>Follow the curiosity.<br><em>Make something useful.</em></h2><div>
<p>My background spans physics and astronomy at Durham, computer science at St Andrews, and doctoral research in medical image analysis at Leeds.</p>
<p>I enjoy working on practical problems, particularly in imaging, data analysis and software. The projects here include research, things I’ve built for myself, and work with other people.</p>
<p>My recent products combine my own concepts and design direction with AI-assisted development. Collaborative and research projects identify their context and contribution on their individual pages.</p>
</div></section></main>'''
(OUT / 'index.html').write_text(document('Research, products & play', 'Samuel Llanwarne’s selected projects in research, products, community and creative technology.', body), encoding='utf-8')
for name in ('style.css', 'experiments.js', 'music-demo.json'):
    destination = OUT / 'assets' / name if name.endswith('.json') else OUT / name
    shutil.copyfile(ROOT / 'tool' / name, destination)
print(f'Built {len(PROJECTS)} project pages and a homepage in {OUT}')
