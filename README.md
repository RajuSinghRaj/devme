# DevTrack

A small black-and-white developer activity log with a Flask dashboard, SQLite storage, and a JSON API.

## Run locally

Install dependencies with `python -m pip install -r requirements.txt`, then start the app with `python run.py`. Open `http://127.0.0.1:5000`.

Set `DEVTRACK_SECRET_KEY` to a private random value before deployment. Set `DEVTRACK_DATABASE` to choose the SQLite database file.

## API

- `GET /health` reports service health.
- `GET /api/summary` returns event, category, monitor, and latest-event totals.
- `GET /api/events.csv` downloads entries as CSV.
- `GET /api/events/breakdown` groups totals by category and severity.
- `GET /api/events` lists entries. Optional `q`, `limit`, and `page` query parameters filter and paginate results.
- `POST /api/events` accepts a JSON object with `title` and optional `details`, `category`, and `severity` (`low`, `normal`, or `high`).
- `GET`, `PUT`, and `DELETE /api/events/<id>` retrieve, update, or remove an entry.

- `POST /api/monitors` creates an HTTP or HTTPS monitor.
- `GET /api/monitors` lists configured monitors.
- `POST /api/monitors/<id>/results` records a monitor check.
- `GET /api/monitors/<id>/results` lists check history with an optional `limit` parameter.
- `GET /api/monitors/<id>/summary` returns recorded uptime metrics.

## Commands

Use `flask --app run init-db` to initialize the configured database and `flask --app run count-events` to print the saved log count, or `flask --app run count-monitors` to print configured monitor totals.

Use `flask --app run export-events` to print event CSV, or pass `--output path/to/events.csv` to save it.

Create a consistent SQLite copy with `flask --app run backup-db --output backups/devtrack.sqlite`. To restore it, stop the app, replace the configured database file with the backup, then start the app again.

Prune monitor history with `flask --app run prune-checks --before "2025-01-01 00:00:00"`.

Run one monitor check with `flask --app run check-monitor 1`. Schedule `flask --app run check-due` with cron or a system scheduler to run checks whose interval has elapsed.

Prune old event entries with `flask --app run prune-events --before "2025-01-01 00:00:00"`.
