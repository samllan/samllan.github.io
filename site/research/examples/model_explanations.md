# Reading model explanations

An explanation map asks what in an image contributed to a particular model output. A useful inspection starts with the original image, shows the explanation next to it and makes clear which prediction the explanation refers to.

The thesis also explored Spectral Dream Dimming. Starting from the same input, it fits a separate brightness mask for each class, seeking to increase that class's score while keeping the model fixed. Comparing the masks shows which regions the model retains when favouring each class.

The runnable example uses four invented regions and a linear scoring rule. It isolates the idea of fitting one bounded mask per class. The thesis analysis applied the idea to trained models and displayed the masks as overlays.

To interpret a highlighted area, ask whether the signal repeats across examples, changes when the input is perturbed, or corresponds to something an expert recognises. A feature may matter to the model because of a biological pattern, a preparation artefact, or another correlation in the data. Those explanations require separate evidence.

Source — Samuel Llanwarne, *Multi-Scale and Multi-Stage Deep Learning for the Classification of Diffuse Large B-cell Lymphoma Histology*, University of Leeds, 2026, Chapter 4.
