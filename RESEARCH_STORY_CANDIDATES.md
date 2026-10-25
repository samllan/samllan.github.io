# Portfolio story and imagery candidates

Reviewed 25 October 2026. Evidence bank for all 13 portfolio panels. Scores and image ideas are planning notes, not public-facing achievement claims. Tuberculosis and radio astronomy pages prepared from this evidence; publication status is recorded in the local portfolio audit.

Ratings estimate how impressive and useful a point is to a general industry audience, given current evidence. 5 = lead story; 4 = strong supporting evidence; 3 = worthwhile detail; 2 = secondary; 1 = omit. These are editorial judgments, not research rankings.

## St Andrews tuberculosis

Primary source: *Thesis Submission.pdf*, Samuel's St Andrews research archive. Image suggestions in brackets distinguish existing artifacts from imagery still to recover or create. Existing illustrations are not photographs or research results.

59 pages. *Understanding Tuberculosis - Computer Vision Based Analysis of Images Acquired Using a Novel Cell Staining Method*. MSc Advanced Computer Science, 16 August 2019. Page references below are printed pages; add 5 for PDF page number.

| Candidate | Rating | Evidence and meaning |
|---|---|---|
| Built a complete research pipeline for locating and counting tuberculosis bacteria in fluorescence images (Images: existing thesis Figure16 pipeline; existing colourful `site/assets/tuberculosis.webp` illustration) | 5 | pp23-34: annotation, coordinate conversion, crops, preprocessing, detection, counting, logs and evaluation. Demonstrates ownership beyond training one model. |
| Tested on images from a patient unseen during training (Images: existing Table7; new public count-comparison bars derived from its numbers) | 4 | pp42-43: third-patient test, expert count 106 versus predicted 91 (14% lower), 60% exact region-count accuracy. A small held-out test, not clinical validation. |
| Made intermediate decisions inspectable (Images: existing Table4 detection overlays and saved crop examples; select approved images before publishing) | 4 | pp23-26: saved boxes, crops, scores and a central InfoFile joining labels and predictions. An expert can inspect mistakes instead of receiving only a total. |
| Worked with a domain expert on genuinely ambiguous data (Images: existing Figures30,32,33 difficult examples; possible recreated schematic of overlapping cells) | 4 | pp28-29,33,37: touching cells, blurred cells, uncertain counts, and labeling consistency. Shows interdisciplinary work and awareness that labels are measurements with limitations. |
| Designed specialist detection and counting stages (Images: existing Figures16,25; simplified detect/crop/count flow already on public page) | 4 | pp24-27: Faster R-CNN with ResNet-50 backbone proposes regions; a separate ResNeXt-50 counting model estimates counts. Existing architectures adapted and combined, not invented. |
| Reported detection of over 80% of in-focus cells in the tested subset (Images: existing Table4 overlay, with the scope stated alongside) | 4 | p37: report states fewer than 5% false positives at confidence threshold 0.2; detector trained on 100 images. Evaluation denominator and sample detail are limited. This is not patient diagnostic sensitivity. |
| Solved an unusual augmentation problem without accidentally including neighboring cells (Images: existing Figure24 rotation/padding diagram; possible before/after crop illustration) | 4 | pp30-32: synthesized plausible crop padding using noise, smoothing and fading edge values; sqrt(2) expansion permits rotations. Concrete evidence of inventive practical implementation. |
| Built traceable data preparation and experiment records (Images: existing Table3 InfoFile excerpt; possible cleaned diagram linking labels to predictions) | 4 | pp23-24,32-33: InfoFile, coordinates, count labels, predictions, hyperparameters, anomaly logs. Valuable to engineering and analytics audiences. |
| Identified weaker performance on more varied data (Images: existing Tables5-7; possible comparison plot with total-count and region-accuracy metrics kept separate) | 4 | pp39-43: small homogeneous case 246 vs253 total; mixed case 406 vs334; unseen case106 vs91. Aggregate count error can hide errors on individual regions. Shows evaluation maturity. |
| Chose models with speed and hardware limits in mind (Images: possible model-comparison diagram; recover run logs before plotting measured timings) | 3 | pp6,26,37: compared Inception, DenseNet and ResNet families; ResNet-18 used for faster tuning; main runs ResNeXt-50. Local 6GB GPU. Avoid unmeasured deployment or cost-saving claims. |
| Investigated training behavior rather than treating models as magic (Images: existing Figures27-29,31 learning curves and Figure35 learning-rate formulation) | 3 | pp26-27,32-35,38-44: adaptive learning rate, batch size, loss functions, validation checkpoints and overfitting. Appendix contains learning-rate formulation. |
| Reused a better annotation tool to save effort (Images: existing Figure21 LabelImg screenshot, credit the tool) | 3 | p29: moved from an initial purpose-built Java utility to LabelImg. Do not claim Samuel authored the Java utility; the thesis does not establish that. |
| Prepared corresponding crops from two stain channels (Images: possible paired Auramine/LipidTOX crops from archive, subject to reuse clearance) | 3 | pp6,23: detector coordinates map to Auramine and LipidTOX images, supporting later biological analysis. Lipid phenotype classification was unimplemented. |
| Wanted to reduce repetitive visual search for specialists (Images: possible whole-image versus selected-region schematic; existing detection overlays) | 4 | pp4-6,24-26: practical motivation and inspectable regions. Say designed to help focus review; no measured technician time saving or clinical outcome demonstrated. |
| Wanted to study why some bacteria survive treatment (Images: possible clearly labelled concept showing counts and cell characteristics over time; no invented results) | 4 | pp3-4,8,45: motivation for lipid/shape phenotype extensions. An ambition and research direction, not a demonstrated treatment-response predictor or discovery. |
| Proposed further segmentation and a review interface (Images: existing Figure34 hand-crafted segmentation target; future interface would be a concept mockup) | 2 | p45: hand-crafted segmentation target, possible U-Net, GUI and additional phenotype modules. Useful context, not completed capabilities. |

### Numerical and publication notes

- Do not reuse old global TB burden statistics as present-day facts.
- The report's abstract blends broader diagnostic motivation with image-level detection results. Keep those separate.
- Table 5 reports 246 versus253 total (2.85% excess). Its caption says 71% accuracy, but the displayed confusion matrix appears to imply 106/169 = 62.7% exact matches. Do not headline 71% without checking original outputs.
- Table 7 is stronger to describe plainly: 91 versus106 total, 14.15% undercount; 32/53 exact region matches, approximately60%. Aggregate agreement is not per-object accuracy.
- No patient identifiers, raw patient folder contents or trained models are needed for the public story.
- Candidate visual: Figure16 pipeline, Table4 detection overlays (printedp36), Figures24/32 padding, Figure33 difficult examples. Confirm image reuse rights before public use; thesis authorship is not automatic ownership of all supplied microscopy data.

Suggested board direction: **Finding and counting bacteria in complex microscopy images.** Lead with overlay, explain detect/crop/count, then one small held-out result with scope, and the expert-review design.

## Durham radio telescope

Primary source: *Durham Radio Telescope Project Presentation.pptx*, Samuel's personal research archive.

Five-slide retrospective, authored Sam Llanwarne. File metadata dates the presentation to May2019; this does not establish the Durham project's dates. Full Durham thesis, code, original sky maps and measured results remain unlocated. Slides use 'we'; exact division of team contributions remains unconfirmed. User describes a Durham master's project mapping the Milky Way and building/checking a student-built mesh telescope.

| Candidate | Rating | Evidence and meaning |
|---|---|---|
| Worked with a physical radio telescope and its data (Images: existing `site/assets/telescope.webp` illustration; original telescope photo still to find) | 5 | Slide3 says hardware setup and understanding throughout; combines instrumentation with computation. User adds student-built mesh telescope context. Do not imply sole design/build ownership. |
| Created sky maps from observations (Images: original sky map still to recover; do not substitute an invented map as a result) | 4 | Slide3 explicitly says created sky maps, characterized as fairly crude. Visually promising; retrieve an actual map before claiming resolution or coverage. |
| Made messy observational data usable (Images: possible processing flow; original raw/cleaned plot still to recover) | 4 | Slide3 identifies loading, cleaning, interpretation and automation as the main work. Broadly transferable data-engineering and analytical skill. |
| Connected local engineering with a galaxy-scale question (Images: existing telescope illustration paired with a labelled conceptual observation diagram, to create) | 4 | Slide2 separates terrestrial hardware/programming from interpretation of extraterrestrial observations. Strong conceptual story supported by the task framing. |
| Used computation to extend and automate analysis (Images: existing public observe/process/map flow; code or notebook screenshot still to recover) | 4 | Slides3-4: data manipulation and automation were substantial, with reflection on computational leverage. No measured time saving or complete automation demonstrated. |
| Created visualizations to understand observations (Images: original plots still to recover; no numerical reconstruction from memory) | 3 | Slide3. Retrieve actual plots before describing features revealed in them. |
| Pursued explanations of Milky Way structure, rotation and mass (Images: possible clearly labelled conceptual rotation diagram; measured rotation curve not recovered) | 4 | Slide2 lists these as possible goals and interpretation tasks. No recovered numerical estimate or successful weighing of the galaxy. |
| Considered noise sources and instrument improvements (Images: possible signal/noise schematic labelled illustrative; hardware sketches still to find) | 3 | Slide5 lists contacting/understanding noise sources and contemplating hardware redesign as future work. Evidence of awareness, not proof of completed noise suppression or redesign. |
| Saw value in reusable code and continuity between researchers (Images: possible analysis-stage diagram; original code/handover evidence still to find) | 3 | Slides2-3 mention support for future/previous researchers and reflection on template-like code. Do not call it an adopted software platform or documented handoff without artifacts. |
| Enjoyed sustained research and building explanations in layers (Images: existing slide4 reflection; possible brief quote beside the telescope illustration) | 3 | Slide4 explicitly describes enjoyment of prolonged project work and progressing from crude observations to higher-level insights by asking questions. A useful personal voice, not a standalone achievement. |

Suggested board direction: **Listening to the Milky Way.** Explain telescope/observation/cleaning/map. Reserve claims about rotation, galaxy mass or telescope redesign until the thesis or plots establish outcomes.

## Shared interpretation

These are portfolio interpretations, not factual claims stated in the documents:

- 5/5: A consistent interest in making hard-to-see phenomena measurable, across microscopy and astronomy (Images: existing bacteria and telescope illustrations as a paired composition).
- 4/5: Building the practical bridge from raw observations to understandable evidence (Images: possible shared observation/process/interpret diagram).
- 4/5: Using computation to relieve repetitive analysis while keeping physical or biological meaning in view (Images: existing detection workflow paired with a recovered telescope workflow, when available).
- 4/5: Iterative, curious research: build, inspect anomalies, refine, and identify what the evidence supports (Images: existing thesis error examples; original astronomy plots still to find).

## PhD: Making medical images useful

Evidence: June2026 Leeds corrections thesis and current PhD page. Image candidates from the thesis need selection and review before public use.

| Potential point with imagery | Score | Evidence / scope |
|---|---|---|
| Made very large pathology datasets practical to process (Images: existing `site/assets/phd.webp` illustration; possible cell/patch/core scale diagram) | 5 | Thesis reports 1,109 cores,229,683 patches,9,126,415 cell instances; different views, not independent cohorts. |
| Halved extraction time in the reported comparison (Images: existing public 6-to-3-second metric; thesis Table2.5) | 4 | Point-and-click versus rectangle extraction, reported precision/recall1.00; no general clinical-workflow saving claimed. |
| Reduced patch-image storage by86.5% (Images: existing public26.94-to-3.63GB metric; possible proportional storage blocks) | 4 | WebP storage result, not proof of unchanged diagnostic quality. |
| Investigated representations and explanations across biological scales (Images: possible approved thesis explanation examples and scale diagram; existing organise/represent/explain flow) | 4 | Autoencoders,contrastive learning and Spectral Dream Dimming; internal validation limits apply to classification metrics. |

## Morrow Plan

Evidence: current product/source and portfolio page. Product screenshots should use fictional entries.

| Potential point with imagery | Score | Evidence / scope |
|---|---|---|
| Turned a personal product idea into a usable reflection tool (Images: existing `site/assets/morrow.png` logo; clean app screenshot to capture) | 4 | Samuel's concept/design direction and AI-assisted implementation; avoid implying all code was written manually. |
| Joined voice,text and photos around thoughts worth revisiting (Images: possible demo entry with fictional text and recording controls) | 4 | Recording/playback and entry types exist; no user-outcome study claimed. |
| Made earlier thoughts findable through dates and collections (Images: possible calendar-to-entry screenshot pair) | 3 | Existing calendar and persistent collection concepts. |
| Balanced an easy guest start with optional account sync (Images: possible small guest-to-account flow and non-personal saved collection) | 3 | Supported project functionality; no unsupported privacy/security guarantees. |

## Lorbefor

Evidence: current product/source and portfolio page. Use public or fictional events in screenshots.

| Potential point with imagery | Score | Evidence / scope |
|---|---|---|
| Connected local discovery with the next practical action (Images: existing `site/assets/lorbefor.png` logo; clean map/event screenshot to capture) | 4 | Samuel's product concept and design direction, with AI-assisted implementation. |
| Built a path from map to event participation (Images: possible map,event detail,attendance sequence) | 4 | Map discovery,events and attendance exist; no participation-growth metric claimed. |
| Explored shared interests through groups and local activities (Images: possible fictional group/event example) | 3 | Existing product functionality, not evidence of an established user community. |
| Improved a real published interface through iteration (Images: possible dated before/after pair from retained screenshots) | 3 | Current project records include published-interface fixes; select a concrete documented change. |

## A map of words

Evidence: existing live Word Map and source, current portfolio page, Samuel's role clarification.

| Potential point with imagery | Score | Evidence / scope |
|---|---|---|
| Made word relationships explorable as a visual network (Images: existing live D3 graph screenshot to capture; existing `site/assets/words.webp` illustration) | 4 | Prototype contains484 words and working search; synonym relationships, not historical etymology. |
| Built the data and application logic in an equal partnership (Images: possible data-to-graph flow alongside an actual interface screenshot) | 4 | Nina Sushko handled design/UI; Samuel handled underlying data/application logic. |
| Encoded information through distance and node size (Images: possible annotated close-up of actual graph with a short legend) | 3 | Distance represents shared synonyms; size communicates frequency/precision. |
| Encouraged discovery through related meanings and navigation history (Images: possible three-step screenshot sequence from a real search) | 3 | Search,exploration and retracing are part of the prototype; no user-study result. |

## The shape of a season

Evidence: Samuel's AA explanation and synthetic public Fourier demonstration; original employer results not recovered.

| Potential point with imagery | Score | Evidence / scope |
|---|---|---|
| Chose a periodic model for a repeating seasonal problem (Images: existing interactive Fourier chart; existing `site/assets/weather.webp` illustration) | 4 | AA seasonal weather modelling context; published chart is synthetic. |
| Used additional harmonics to capture asymmetric seasonal shapes (Images: existing slider at1 and4 harmonics; possible overlay of component waves) | 4 | Demonstrates representation beyond a single sinusoid, not proven forecast improvement. |
| Made a mathematical idea understandable through interaction (Images: existing live slider and resulting curve) | 3 | Public demonstration is implemented and interactive. |
| Recognised that fitting more detail can also fit noise (Images: possible clearly labelled illustrative train/validation comparison, to create) | 3 | A modelling lesson; original cross-validation results are not available. |

## Strathclyde boat challenge

Evidence: Samuel's account; original illustration retained. Exact date,distance and independent award documentation not recovered.

| Potential point with imagery | Score | Evidence / scope |
|---|---|---|
| Helped build the boat that travelled furthest in the challenge (Images: existing `site/assets/boat.jpg` towing-tank illustration; actual boat/team photo still to find) | 4 | Challenge result, not a world record or measured distance claim. |
| Made a key design decision that became a physical build (Images: possible design sketch once the actual decision is described) | 4 | User-confirmed contribution; do not invent hull or propulsion details. |
| Received a Team Player award (Images: possible certificate or award photo, still to find; existing public award callout) | 4 | User-confirmed; supporting document not recovered. |
| Discovered enjoyment in collaborative engineering (Images: possible authentic build-day photo or brief personal recollection) | 3 | User describes this as a formative memory; personal insight rather than performance metric. |

## Finding the road ahead

Evidence: original course repository and new reproducible portfolio demo, October2026.

| Potential point with imagery | Score | Evidence / scope |
|---|---|---|
| Turned road pixels into two visible lane boundaries (Images: existing `site/assets/lane-input.jpg` and `lane-overlay.jpg`; working reveal slider) | 3 | New single-image educational demonstration; distinguish from unfinished historical course notebook. |
| Reduced the search space before fitting a model (Images: possible road-region mask and selected-pixel intermediate, reproducible from script) | 3 | Colour selection,region restriction and line fitting in `tool/lane_demo.py`. |
| Made the result easy to inspect and reproduce (Images: existing source/output pair and short code excerpt) | 3 | Public implementation and comparison available; course image credited to Udacity materials. |
| Understood where simple visual assumptions break (Images: possible additional failure-case images, only after running and checking them) | 3 | No video,curved-road or poor-weather validation; failure analysis is a potential extension. |

## Building AI communities

Evidence: Samuel's founder/president confirmation and linked AI Society/AI-squared public resources.

| Potential point with imagery | Score | Evidence / scope |
|---|---|---|
| Founded and led the AI Society (Images: existing `site/assets/community.png` logo; authentic committee/event photo to select) | 5 | Founder and President confirmed by Samuel; avoid invented membership or attendance figures. |
| Created opportunities for people across disciplines to learn together (Images: possible public workshop poster or event photo with permission) | 4 | Community activities and public workshop resources; confirm individual-event attribution. |
| Made practical learning resources available (Images: possible existing workshop material or society-site screenshot) | 3 | Public resources include workshops and committee information; select an authored or accurately credited example. |
| Connected the society story with a wider AI forum (Images: possible AI-squared archive screenshot or event programme) | 3 | Forum exists; Samuel's precise AI-squared role and chronology remain to confirm. |

## Music Note Rain

Evidence: local `music_note_rain_2` prototype and current playable browser excerpt.

| Potential point with imagery | Score | Evidence / scope |
|---|---|---|
| Made musical timing visible as falling notes (Images: existing live piano waterfall; screenshot/short recording to capture) | 4 | Working public24-second composed demo with synthesised playback. |
| Explored arrangements that adapt to a player's level (Images: possible actual local lead/accompaniment/combined views at different difficulties) | 4 | Prototype supports three arrangements and five complexity levels; no learning-outcome claim. |
| Connected audio analysis with a playable visual interface (Images: possible real local import-to-arrangement sequence) | 3 | Imported-recording analysis exists locally and remains experimental; browser excerpt does not transcribe uploads. |
| Preserved musical phrases while reducing playing complexity (Images: possible same passage at two verified arrangement levels) | 3 | Design aim; demonstrate with genuine output rather than inventing transcription accuracy. |

## From echoes to shapes

Evidence: local FieldII/PyTorch experiments, saved figure and Samuel's aim clarification.

| Potential point with imagery | Score | Evidence / scope |
|---|---|---|
| Investigated reconstructing shapes directly from ultrasound waveforms (Images: existing `site/assets/ultrasound.png`; possible simulator-object/waveform/reconstruction diagram) | 4 | Experimental neural reconstruction of a known simulated phantom; no demonstrated superiority over conventional reconstruction. |
| Used simulation to connect known objects with received signals (Images: possible original FieldII phantom and waveform plots from scripts) | 4 | Useful controlled experimental setup; credit FieldII and Jensen examples. |
| Combined physical simulation,signal processing and neural networks (Images: possible actual processing stages with one real saved output) | 4 | Scripts,RF files,notebook and checkpoints exist. |
| Identified unseen-object testing as the decisive next question (Images: possible future target/prediction/baseline comparison; not yet an established result) | 3 | Current saved figure concerns training; held-out generalisation remains unverified. |

## Incidental AI

Evidence: four-person medical-education hackathon source and September2023 recorded demonstration.

| Potential point with imagery | Score | Evidence / scope |
|---|---|---|
| Built a medical-teaching concept with a four-person team (Images: existing recorded Streamlit demo; clean still to extract; `site/assets/medicine.webp` is illustrative) | 4 | Samuel confirms collaborative work without AI-assisted coding; product itself uses generative AI. |
| Turned simulated cases into an interactive reasoning conversation (Images: possible scenario/question/feedback sequence from actual recording) | 4 | Generated scenarios,images and chat component; no clinical correctness or educational efficacy established. |
| Integrated several services into a demonstrable prototype (Images: possible simplified Streamlit/service flow paired with a real screen) | 3 | Source and recording exist; unfinished and fallback paths remain. |
| Recognised the importance of reliable,reviewed teaching material (Images: possible clearly marked example-review checklist next to a demo case) | 3 | A product lesson and future requirement, not evidence of clinician validation. |

## Selection rule

Use roughly four strong points per public page. Prefer a real output or interaction over generic decorative imagery. Keep illustrations labelled, use fictional product entries, and keep patient material private unless a specific image is cleared for publication. Ratings and possible future visuals belong in this evidence bank, not in the visitor experience.
