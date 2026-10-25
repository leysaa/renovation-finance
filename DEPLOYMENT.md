# Deploy on PythonAnywhere (free tier)

This app uses Flask, SQLite, and a single worker — a good fit for PythonAnywhere’s free account.

## 1. Upload the code

- Create a PythonAnywhere account and open the **Dashboard**.
- **Files** → under `/home/YOURUSERNAME/` upload or `git clone` the `building_app` folder (or the whole repo and use `building_app/` as the app directory).

Example with Git (if your code is on GitHub):

```bash
cd ~
git clone YOUR_REPO_URL RC_APP
cd RC_APP/building_app
```

## 2. Virtualenv and dependencies

In a **Bash console** on PythonAnywhere:

```bash
cd ~/RC_APP/building_app   # adjust path
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Web app configuration

- **Web** tab → **Add a new web app** → Manual configuration → Python 3.10.
- **Virtualenv**: `/home/YOURUSERNAME/RC_APP/building_app/.venv`
- Edit the **WSGI configuration file** (link on the Web tab). Replace the file contents with something like:

```python
import sys
import os

project_home = "/home/YOURUSERNAME/RC_APP/building_app"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ.setdefault("SECRET_KEY", "replace-with-a-long-random-string")

from app import create_app
application = create_app()
```

Use your real path and a strong `SECRET_KEY` (or set it only via the Web tab **Environment variables** section and read it in WSGI).

## 4. Static files

On the **Web** tab → **Static files**:

| URL           | Directory                                      |
|---------------|------------------------------------------------|
| `/static/`    | `/home/YOURUSERNAME/RC_APP/building_app/static` |

Reload the web app.

## 5. Database location and setup

SQLite lives in the **instance** folder (Flask default):

```text
/home/YOURUSERNAME/RC_APP/building_app/instance/building.db
```

In Bash (virtualenv active, same directory as `app.py`):

```bash
cd ~/RC_APP/building_app
export FLASK_APP=app:create_app
flask init-db
flask create-user YOURUSERNAME
```

Enter a password when prompted. Run `flask init-db` only once on an empty server (it will error if tables already exist).

## 6. Environment variables

In **Web** → **Environment variables** (or in WSGI):

| Variable     | Purpose                          |
|--------------|----------------------------------|
| `SECRET_KEY` | Session signing (required in prod) |

Optional for local-style debugging: do **not** enable Flask debug on PythonAnywhere.

## 7. Reload

**Web** tab → green **Reload** button after any code or WSGI change.

Visit `https://YOURUSERNAME.pythonanywhere.com/`, log in, and use the app.

## 8. Backup the database

Download periodically from **Files** → `instance/building.db` → download icon, or in Bash:

```bash
cp ~/RC_APP/building_app/instance/building.db ~/building-backup-$(date +%Y%m%d).db
```

## 9. Phone / home screen

The app includes `static/manifest.webmanifest`. After deployment, open the site in Safari on iPhone → **Share** → **Add to Home Screen**.

## Troublesureshooting

- **500 error**: check **Web** → **Error log** and **Server log**.
- **CSRF / session issues**: confirm `SECRET_KEY` is set and stable across reloads.
- **Database locked**: free tier has one worker; avoid long-running writes from multiple tabs at once.
