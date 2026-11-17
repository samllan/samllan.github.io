# Reuse this logbook

Copy the example project folder to a new name inside site/research. Set the title, description, back link and source link in project.json. Leave the shared page, CSS and JavaScript in place.

- Add a question or goal to goals.json. Give it a stable ID and a single sentence about the question.
- Add what you tried, what you found and what followed under story. Cite the evidence and record when a later entry changes an earlier decision.
- Add a file to examples and list its filename, date and outcome under the goal. Capture the output of any runnable script in row_examples.json.
- Add a title and input description in leaf_details.json. Add framing or method when the experiment needs its own explanation. Link earlier entries with from and a goal ID followed by a slash and the filename.
- Use parent to nest a goal below an earlier goal in its group. Use default_file to choose the experiment readers open when they select a goal.

Use Edit on an experiment to draft question and notes in the browser. To share them, update the entry’s framing in leaf_details.json and rebuild.

Run python tool/build_site.py from the repository root. The build renders any project folder with project.json at research/ followed by the folder name.
