# start.sh

#!/usr/bin/env bash
# Explicitly use the virtual environment's python executable
/opt/render/project/src/.venv/bin/gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT