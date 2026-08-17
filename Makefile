# SpiceXplorer (public monorepo) — task front-door.
#
# Managed by the release infra — this Makefile is self-contained for THIS repo
# (analog-db/ + platform/ + ui/ as sibling directories; no submodules, no
# scripts/). Two ways to run the app:
#
#   * Docker           — `make up`      (api :8000 + ui :4000; no simulator) or
#                        `make up-live` (same, plus ngspice + three open PDKs
#                        vendored, so live SPICE works with nothing installed on
#                        the host). See docs/docker.md. Needs Docker.
#   * Native/no-Docker — `make api` (backend) and `make ui` (frontend) in two
#                        terminals. Needs uv (Python) + Node.
#
# First run, native:
#   make sync          # build the platform venv (uv) + borrow the analog-db corpus
#   make api           # backend  (http://localhost:8000)
#   make ui            # frontend (http://localhost:4000)  [separate terminal]
#
# Recipe lines are TAB-indented. Override any var: `make api BACKEND_PORT=8010`,
# `make logs S=api`.

# ---- Configuration (override on the command line) --------------------------
PLATFORM       ?= platform
UI             ?= ui
ANALOG_DB      ?= analog-db
BACKEND_PORT   ?= 8000
FRONTEND_PORT  ?= 4000
S              ?=
# `make up-live` rebuilds the api FROM this image (built by `make spice-base`).
SPICE_BASE     ?= spicexplorer-spice-base:release
# OSDI compact models for the base image: `vendor` reuses the committed prebuilt
# x86-64 binaries (fast); `compile` builds openvaf and compiles the Verilog-A for
# this machine's arch — slower, but the ONLY native route on arm64, where the
# vendored x86-64 .osdi cannot load. Default follows the machine so `make up-live`
# is correct out of the box on Apple silicon; override explicitly to force either.
export OSDI_MODE ?= $(if $(filter arm64 aarch64,$(shell uname -m)),compile,vendor)
# The api resolves the analog-db corpus (the /api/library routes) from this path.
ANALOG_DB_ABS  := $(CURDIR)/$(ANALOG_DB)

.DEFAULT_GOAL := help
.PHONY: help sync ui-install api ui up spice-base up-live down logs test lint \
        typecheck check build-ui gen-types clean

##@ General
help:  ## List the available targets
	@awk 'BEGIN {FS = ":.*##"} \
	  /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5); next } \
	  /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-13s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@printf "\nDocker: \033[36mmake up\033[0m  ·  Native: \033[36mmake sync && make api\033[0m (+ \033[36mmake ui\033[0m)\n"

##@ Setup (native, no Docker)
sync:  ## Build the platform venv (uv sync) + borrow the analog-db corpus editable
	cd $(PLATFORM) && uv sync
	cd $(PLATFORM) && uv pip install --no-deps -e ../$(ANALOG_DB)

ui-install:  ## Install the UI's Node deps from the lockfile
	cd $(UI) && npm ci

##@ Develop — native (no Docker)
api:  ## Backend only — uvicorn hot reload (:8000). Replay mode unless ngspice+PDK are on PATH
	cd $(PLATFORM) && SPICEXPLORER_ANALOG_DB=$(ANALOG_DB_ABS) \
	  uv run uvicorn spicexplorer_api.main:app --reload --port $(BACKEND_PORT)

ui:  ## Frontend only — Next dev server (:4000). Proxies /api → the backend
	@[ -d $(UI)/node_modules ] || $(MAKE) ui-install
	cd $(UI) && BACKEND_URL=http://127.0.0.1:$(BACKEND_PORT) \
	  npm run dev -- -p $(FRONTEND_PORT)

##@ Develop — Docker (see docs/docker.md)
up:  ## Build + run the stack (api :8000 + ui :4000). No live SPICE
	docker compose up --build

spice-base:  ## Build the EDA base image: ngspice + IHP/sky130/gf180 PDKs vendored
	@echo "OSDI_MODE=$(OSDI_MODE) (arch $(shell uname -m)) — 'compile' also builds a Rust/LLVM toolchain and takes considerably longer."
	docker compose --profile live build spice-base

up-live: spice-base  ## Build + run the stack WITH live SPICE (pdk_ok:true)
	SPICE_BASE=$(SPICE_BASE) docker compose up --build api ui

down:  ## Stop the stack
	docker compose down

logs:  ## Tail logs — all, or one service: make logs S=api | S=ui
	docker compose logs -f $(S)

##@ Quality
test:  ## Fast platform tests (no SPICE simulation)
	cd $(PLATFORM) && uv run pytest -m 'not slow'

lint:  ## Lint Python (ruff) + UI (eslint)
	cd $(PLATFORM) && uv run ruff check .
	cd $(UI) && npm run lint

typecheck:  ## Typecheck the UI (tsc)
	cd $(UI) && npm run typecheck

check: lint typecheck test  ## Lint + typecheck + fast tests

##@ Build / codegen
build-ui:  ## Production UI bundle (next build)
	cd $(UI) && npm run build

gen-types:  ## Regenerate the UI TypeScript types from the API OpenAPI spec
	cd $(UI) && npm run gen:types

##@ Maintenance
clean:  ## Remove Python/UI caches and build outputs
	@find . -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type d \( -name ".pytest_cache" -o -name ".ruff_cache" -o -name ".next" \) -prune -exec rm -rf {} + 2>/dev/null || true
	@echo "Done."
