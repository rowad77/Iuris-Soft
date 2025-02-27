# Variables
DJANGO_MANAGE=./manage.py
CELERY_APP=core.celery
CELERY_BIN=celery

# Environment file (if needed for env vars)
ENV_FILE=.env

# Load environment variables (optional if using direnv or other tools)
include $(ENV_FILE)
export $(shell sed 's/=.*//' $(ENV_FILE))

# Commands
runserver:
	python $(DJANGO_MANAGE) runserver

migrate:
	python $(DJANGO_MANAGE) migrate

celery-worker:
	$(CELERY_BIN) -A $(CELERY_APP) worker --loglevel=info

celery-beat:
	$(CELERY_BIN) -A $(CELERY_APP) beat --loglevel=info

send-due-cases:
	python $(DJANGO_MANAGE) send_due_cases

start-all:
	@echo "Starting Django, Celery Worker & Beat..."
	@tmux new-session -d -s dev "make runserver"
	@tmux split-window -h "make celery-worker"
	@tmux split-window -v "make celery-beat"
	@tmux select-layout tiled
	@tmux attach-session -t dev

stop-all:
	@tmux kill-session -t dev || true

help:
	@echo "Available commands:"
	@echo "  make runserver        - Start Django server"
	@echo "  make migrate          - Run migrations"
	@echo "  make celery-worker    - Start Celery worker"
	@echo "  make celery-beat      - Start Celery beat"
	@echo "  make send-due-cases   - Run management command"
	@echo "  make start-all        - Start server, worker, beat in Tmux"
	@echo "  make stop-all         - Kill Tmux session"

# # Variables
# DJANGO_MANAGE=./manage.py
# CELERY_APP=core
# CELERY_BIN=celery

# # Environment file (if needed for env vars)
# ENV_FILE=.env

# # Load environment variables (optional if using direnv or other tools)
# include $(ENV_FILE)
# export $(shell sed 's/=.*//' $(ENV_FILE))

# # Commands
# runserver:
# 	python $(DJANGO_MANAGE) runserver

# migrate:
# 	python $(DJANGO_MANAGE) migrate

# celery-worker:
# 	$(CELERY_BIN) -A $(CELERY_APP) worker --loglevel=info

# celery-beat:
# 	$(CELERY_BIN) -A $(CELERY_APP) beat --loglevel=info

# send-due-cases:
# 	python $(DJANGO_MANAGE) send_due_cases

# start-all:
# 	@echo "Starting Django, Celery Worker & Beat..."
# 	@tmux new-session -d -s dev "make runserver"
# 	@tmux split-window -h "make celery-worker"
# 	@tmux split-window -v "make celery-beat"
# 	@tmux select-layout tiled
# 	@tmux attach-session -t dev

# stop-all:
# 	@tmux kill-session -t dev || true

# help:
# 	@echo "Available commands:"
# 	@echo "  make runserver        - Start Django server"
# 	@echo "  make migrate          - Run migrations"
# 	@echo "  make celery-worker    - Start Celery worker"
# 	@echo "  make celery-beat      - Start Celery beat"
# 	@echo "  make send-due-cases   - Run management command"
# 	@echo "  make start-all        - Start server, worker, beat in Tmux"
# 	@echo "  make stop-all         - Kill Tmux session"

