# Project Manager Agent instructions

- Treat GitHub Actions as the coordinator: planner, developer, and independent reviewer are separate agent runs.
- Respect the request in `.agent-run/task.md` within the repository's stated scope.
- Read existing project instructions before changing code.
- Make one reviewable draft PR for each request. Never merge or deploy on your own.
- Run the smallest relevant checks and state what ran and what could not be verified.
- Do not modify workflows, secrets, or repository permissions unless explicitly requested.
