# DevTrack

A small black-and-white developer activity log with a Flask dashboard, SQLite storage, and a JSON API.

## Run locally

Install dependencies with `python -m pip install -r requirements.txt`, then start the app with `python run.py`. Open `http://127.0.0.1:5000`.

Set `DEVTRACK_SECRET_KEY` to a private random value before deployment. Set `DEVTRACK_DATABASE` to choose the SQLite database file.

## API

- `GET /health` reports service health.
- `GET /api/events.csv` downloads entries as CSV.
- `GET /api/events` lists entries. Optional `q`, `limit`, and `page` query parameters filter and paginate results.
- `POST /api/events` accepts a JSON object with `title` and optional `details`, `category`, and `severity` (`low`, `normal`, or `high`).
- `GET`, `PUT`, and `DELETE /api/events/<id>` retrieve, update, or remove an entry.

- `POST /api/monitors` creates an HTTP or HTTPS monitor.
- `GET /api/monitors` lists configured monitors.
- `POST /api/monitors/<id>/results` records a monitor check.
- `GET /api/monitors/<id>/results` lists check history.
- `GET /api/monitors/<id>/summary` returns recorded uptime metrics.
