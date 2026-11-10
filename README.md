# BitRate API

BitRate is a small REST API for checking Python code and basic UI design details. You can create projects, run audits, review findings, and see a score report. It is a student project built with Python, FastAPI, and Pydantic.

The checks use simple rules. The API **does not run submitted Python code**. For design audits, it checks the element details you send in the request.

## Run the project

You need Python 3.10 or newer. Run these commands from the project folder.

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000/docs> to use Swagger UI. You can also open <http://127.0.0.1:8000/health> to check that the server is running.

## How it works

1. **Create a project.** Project names must be unique, even if the letter case is different.
2. **Run an audit.** Choose `code` for Python code or `design` for a list of UI elements. The audit creates findings when it detects problems.
3. **Review the findings.** Mark a finding as resolved, or reopen it. The report shows the original score and the score for findings that are still open.

One project can have many audits, and one audit can have many findings. You can run a new audit without deleting older ones. Deleting a project also deletes its audits and findings.

Data is stored **in memory**. It is cleared when the server restarts.

### Checks and scores

- **Code:** Python syntax errors, calls to `eval` or `exec`, possible hardcoded secrets, and functions longer than 30 lines.
- **Design:** missing labels on interactive elements, text contrast below 4.5:1, font size below 14 px, and provided interactive width or height below 44 px.
- **Score:** starts at 100. Each finding removes points: low = 5, medium = 10, high = 20, critical = 30. The score cannot go below 0.
- **Report:** `initial_score` includes all findings from the audit. `current_score` includes only open findings.

Marking a finding as resolved means that a user says it was fixed. To check the changed code or design again, run a new audit. These checks are for a class project; they are not a full security scan or a visual review of a real web page.

## API endpoints

All project, audit, and finding endpoints start with `/api/v1`.

| Method | Path | What it does |
|---|---|---|
| POST | `/projects` | Create a project |
| GET | `/projects` | List projects; supports `search`, `offset`, and `limit` |
| GET | `/projects/{project_id}` | Get one project |
| PATCH | `/projects/{project_id}` | Change a project's name or description |
| DELETE | `/projects/{project_id}` | Delete a project and its related data |
| POST | `/projects/{project_id}/audits` | Run a code or design audit |
| GET | `/projects/{project_id}/audits` | List audits; supports `kind`, `offset`, and `limit` |
| GET | `/audits/{audit_id}` | Get one audit |
| GET | `/audits/{audit_id}/findings` | List findings; supports `severity`, `status`, `offset`, and `limit` |
| PATCH | `/audits/{audit_id}/findings/{finding_id}` | Resolve or reopen a finding |
| GET | `/audits/{audit_id}/report` | Get scores and finding counts |

List endpoints use `offset=0` and `limit=20` by default. `offset` must be 0 or higher, and `limit` must be between 1 and 100. IDs use the UUID format.

## Try it in Swagger UI

In <http://127.0.0.1:8000/docs>, open an endpoint, click **Try it out**, enter the data, and click **Execute**.

**1. Create a project:** `POST /api/v1/projects`

```json
{"name": "Demo", "description": "My class project"}
```

The response has status **201**. Copy the project's `id` for the next request.

**2. Run a code audit:** `POST /api/v1/projects/{project_id}/audits`

```json
{"kind": "code", "source": "password = 'demo'\neval('2 + 2')"}
```

You can also run a design audit:

```json
{
  "kind": "design",
  "elements": [
    {
      "kind": "button",
      "label": "",
      "text_color": "#777777",
      "background_color": "#777777",
      "font_size": 12,
      "width": 30,
      "height": 30
    }
  ]
}
```

Copy the audit's `id`, then use `GET /api/v1/audits/{audit_id}/findings` to see its findings.

**3. Resolve a finding:** `PATCH /api/v1/audits/{audit_id}/findings/{finding_id}`

```json
{"status": "resolved", "resolution_note": "Removed the eval call"}
```

To reopen it, send `{"status": "open"}`. Use `GET /api/v1/audits/{audit_id}/report` to compare `initial_score` and `current_score`.

### Error responses

- **422:** invalid input, such as an empty name, a wrong UUID, an unknown audit type, or a missing resolution note. FastAPI returns a `detail` field.
- **404:** a project, audit, or finding does not exist, or a finding belongs to a different audit.
- **409:** a project name is already taken, or a finding already has the requested status.

Business errors use this JSON format: `{"error": {"code": "...", "message": "..."}}`.

## Project structure

```text
app/
  main.py                  creates the FastAPI app and data store
  api/routes/              API endpoints
  api/dependencies.py      gives routes access to the data store
  schemas/                 Pydantic request and response models
  services/                business rules and audit checks
  repositories/memory.py   in-memory data store
tests/test_api.py          API tests
docs/                     architecture notes and Swagger checklist
```

Routes receive HTTP requests and call services. Services apply the rules and work with the data store. Pydantic checks request data. One error handler turns business errors into HTTP responses.

## Run tests

```bash
python -m pytest -q
```

The tests cover successful requests, invalid input, conflicts, and deletion of related data. The [Swagger checklist](docs/swagger-checklist.md) gives steps for a manual demo of every endpoint.
