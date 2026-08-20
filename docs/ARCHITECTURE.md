# Car Brain — Cloud Interface Architecture

This document describes the cloud-side FastAPI service for Volkswagen's Phase-2 "Car Brain" prototype. It covers the shape of the code (what lives where and why), the data flow at runtime, and — importantly — the boundary between this repo and the sibling `smart_car_project/` package that owns the database.

## 1. Scope

**This repo owns:** the HTTP surface, sensor validation, the Redis-based event bus, the scheduler that runs periodic ("chronic") jobs, the async workers that consume sensor streams ("event" processors), the orchestrator/decision engine, the LLM integration seam, and the notification delivery layer.

**This repo does *not* own:** the database. All persistence goes through `smart_car_project/` (their `Driver`, `Trip`, `Telemetry` SQLAlchemy models). We touch that package through a single adapter (`app/adapters/carbrain_db.py`) — never elsewhere. If we need a column that isn't there, we ask them, not add it ourselves.

**Deliberately not implemented yet:** the *bodies* of chronic jobs, event handlers, orchestrator rules, LLM provider clients, and external-context providers (weather / road / geofence). They exist as interfaces so the wiring is proven and adding a body is a single-file drop-in.

## 2. Repository layout

```
smart-car-cloud/
├── main.py                       # uvicorn entrypoint
├── pyproject.toml                # uv-managed deps
├── docker-compose.yml            # Redis (Postgres is external — see §4)
├── Dockerfile                    # python:3.13-slim + uv sync
├── .env.example                  # copy → .env
│
├── app/
│   ├── api.py                    # FastAPI() instance, mounts every router
│   ├── config.py                 # pydantic-settings (Redis URL, LLM keys, log level)
│   ├── lifespan.py               # startup/shutdown: scheduler, event consumers, engine
│   │
│   ├── adapters/                 # single seam to smart_car_project
│   │   └── carbrain_db.py
│   │
│   ├── core/                     # cross-cutting infra
│   │   ├── bus.py                # Redis Streams publish/consume
│   │   ├── envelope.py           # SensorEnvelope + enums
│   │   ├── errors.py             # exception handlers
│   │   ├── logging.py            # basicConfig + APScheduler noise dampener
│   │   ├── redis.py              # singleton Redis client
│   │   └── scheduler.py          # singleton AsyncIOScheduler
│   │
│   ├── sensors/                  # 14 sensor payload schemas + ingest router
│   ├── chronic/                  # 11 periodic (APScheduler) jobs
│   ├── events/                   # 15 stream-driven async processors
│   ├── orchestrator/             # engine, rules, throttle, snapshot builder
│   ├── llm/                      # provider-agnostic client + 4 uses
│   ├── delivery/                 # notifications, channels, priority, approval
│   ├── drivers/                  # driver CRUD + persona + (stub) identity
│   ├── trips/                    # trip CRUD + summary read
│   ├── environment/              # weather/road/geofence (interface only)
│   └── scenarios/                # mock-vehicle replay of JSON scenarios
│
└── tests/
    ├── conftest.py
    ├── unit/{sensors,chronic,events,delivery,llm,orchestrator}/
    ├── integration/              # placeholder
    └── scenarios/                # placeholder
```

## 3. Runtime picture

```
┌─────────────────┐    POST /ingest/{sensor_id}    ┌────────────────┐
│  mock vehicle   │────────────────────────────────▶│  FastAPI app   │
└─────────────────┘         (JSON envelope)         └────────┬───────┘
                                                             │
                                     ┌───────────────────────┼───────────────────────┐
                                     ▼                       ▼                       ▼
                             ┌──────────────┐        ┌───────────────┐      ┌────────────────┐
                             │ smart_car_pj │        │ Redis Streams │      │  APScheduler   │
                             │  Postgres    │        │ telemetry.*   │      │  11 chronic    │
                             │  telemetry   │        │ events.derived│      │  jobs          │
                             └──────────────┘        └───────┬───────┘      └────────┬───────┘
                                                             │                       │
                                          ┌──────────────────┼───────────────────────┘
                                          ▼                  ▼
                                  ┌──────────────┐   ┌──────────────┐
                                  │ 15 event     │   │  orchestrator│
                                  │ processors   │──▶│  engine      │
                                  │ (async task) │   │  (rules +    │
                                  └──────────────┘   │   throttle)  │
                                                     └──────┬───────┘
                                                            ▼
                                                     ┌──────────────┐
                                                     │  delivery    │
                                                     │  WS + REST   │
                                                     └──────────────┘
```

The seam between "hot path" and "brain" is Redis Streams. The orchestrator only ever reads `events.derived`; nothing calls it directly. Chronic jobs and event processors publish to that stream when they detect something interesting.

## 4. Boot sequence & degraded modes

`app/lifespan.py` runs on FastAPI startup:

1. `configure_logging()`
2. `_try_redis()` — pings Redis. If it fails, sets `redis_up = False` and continues.
3. Starts APScheduler with all 11 chronic jobs (registered from `app/chronic/__init__.py`).
4. If Redis is up: spawns 15 event-consumer tasks and the orchestrator engine.
5. Yields (app serves traffic).
6. On shutdown: cancels engine, cancels consumers, `await gather(...)`, `shutdown_scheduler()`, `close_redis()`.

**States:**
- **All up (Redis + Postgres + smart_car_project on disk):** everything works.
- **Redis down:** app boots. REST endpoints work. Scheduler still fires (chronic bodies won't have streams to write to yet, so this is currently harmless). Event consumers + orchestrator stay off. Log line: `starting in degraded mode`.
- **Postgres down:** app boots. `/ingest/*` and driver/trip CRUD fail at `session.commit()` with a psycopg2 error.
- **`smart_car_project/` missing or not next to us:** hard boot failure at adapter import time.

**Where Postgres comes from:** `smart_car_project/` doesn't ship a compose file. Either bring it up yourself (`docker run -d --name carbrain-pg -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=carbrain -p 5432:5432 postgres:16-alpine`) or agree with the maintainer that we own the compose entry. Their `database.py` reads `DATABASE_URL` from env and defaults to `postgresql://postgres:postgres@localhost:5432/carbrain`.

Their migrations create the schema:
```bash
cd smart_car_project
uv run --with alembic --with sqlalchemy --with psycopg2-binary --with python-dotenv alembic upgrade head
```

## 5. File-by-file reference

### 5.1 Root

| File | Role |
|---|---|
| `main.py` | Entry point. Imports `app.api:app` for uvicorn. |
| `pyproject.toml` | uv-managed. Deps: fastapi, pydantic-settings, sqlalchemy (sync), psycopg2-binary, redis, apscheduler, httpx, python-dotenv. Dev: pytest, pytest-asyncio. |
| `docker-compose.yml` | Redis 7-alpine + the api service. No Postgres (owned by smart_car_project). |
| `Dockerfile` | python:3.13-slim, `uv sync`, `uvicorn main:app` on 8000. |
| `.env.example` | `DATABASE_URL`, `REDIS_URL`, LLM keys, `LOG_LEVEL`. |

### 5.2 `app/` top-level

| File | Role |
|---|---|
| `api.py` | FastAPI instance. Mounts routers: sensors, drivers, trips, environment, orchestrator, llm, delivery, scenarios. Exposes `GET /health`. Registers `SensorNotFound → 404`. |
| `config.py` | Pydantic `Settings`. Note: no `db_url` — that's smart_car_project's env, not ours. |
| `lifespan.py` | See §4. |

### 5.3 `app/adapters/`

| File | Role |
|---|---|
| `carbrain_db.py` | **The only file that imports from `smart_car_project/`.** Prepends the sibling package to `sys.path`, re-exports `SessionLocal`, `engine`, `Driver`, `Trip`, `Telemetry`, and provides a sync `get_session()` FastAPI dependency. |

### 5.4 `app/core/`

| File | Role |
|---|---|
| `bus.py` | `publish_envelope(env)` → `XADD telemetry.{sensor_id}`. `publish_derived_event(type, payload)` → `XADD events.derived`. `read_stream(streams, group, consumer, ...)` is a consumer-group iterator that auto-creates the group (`BUSYGROUP` swallowed on restart). |
| `envelope.py` | `SensorEnvelope`: `sensor_id`, `ts_ms`, `trip_id: UUID`, `driver_id: UUID`, `status: SensorStatus`, `available: bool`, `payload: dict`. Enums: `SensorStatus (OK/UNAVAILABLE/ERROR/PERMISSION_DENIED)`, `SampleType (CONTINUOUS/ON_CHANGE/EVENT)`. |
| `errors.py` | `SensorNotFound` + 404 handler. |
| `logging.py` | `basicConfig` at `settings.log_level`. Dampens `apscheduler.executors.default` + `apscheduler.scheduler` to WARNING (they log every job fire otherwise). |
| `redis.py` | Singleton `AsyncRedis` from `settings.redis_url`. `get_redis()`, `close_redis()`. |
| `scheduler.py` | Singleton `AsyncIOScheduler`. `get_scheduler()`, `shutdown_scheduler()`. |

### 5.5 `app/sensors/` — 14 sensors + base + router + registry

All 14 sensors share the envelope shape; each defines a typed `payload` model.

| File | `sensor_id` | Sample | Rate | Payload highlights |
|---|---|---|---|---|
| `speed.py` | `vehicle.speed` | CONTINUOUS | 10 Hz | `speed_mps`, `speed_kmh` |
| `accelerometer.py` | `vehicle.accelerometer` | CONTINUOUS | 50 Hz | 6-axis + magnitude |
| `rotation.py` | `vehicle.rotation` | CONTINUOUS | 50 Hz | quaternion + Euler + gyro |
| `pedals.py` | `vehicle.pedals` | CONTINUOUS | 20 Hz | accel/brake %, light flags |
| `energy.py` | `vehicle.energy` | ON_CHANGE | — | powertrain enum, fuel/battery, range |
| `gears.py` | `vehicle.gears` | ON_CHANGE | — | P/R/N/D/S/M/1-8, selected/engaged/is_shift |
| `lighting.py` | `env.lighting` | CONTINUOUS | 1 Hz | night_mode, lux, sun_state |
| `vehicle_lights.py` | `vehicle.lights` | ON_CHANGE | — | head/high/fog/hazard/cabin + intent match |
| `surroundings.py` | `env.surroundings` | CONTINUOUS | 5 Hz | list of objects (pos, vel, TTC, confidence) + following distance/time |
| `adas.py` | `vehicle.adas` | CONTINUOUS | 10 Hz | radar/ultrasonic, LDA/LKA, blind spot, FCW, ACC, signs |
| `tires.py` | `vehicle.tires` | ON_CHANGE | — | four pressures + alert flags |
| `turn_signals.py` | `vehicle.turn_signals` | ON_CHANGE | — | state + intent + blink count + duration |
| `parking_brake.py` | `vehicle.parking_brake` | ON_CHANGE | — | engaged, auto_apply, source |
| `odometer.py` | `vehicle.odometer` | CONTINUOUS | 0.2 Hz | total_km, trip_km, session_delta_km |

Supporting files:
- **`base.py`** — `Sensor` dataclass: `sensor_id`, `payload_model` (Pydantic), `sample_type`, `rate_hz`.
- **`__init__.py`** — imports all 14 modules, builds `SENSOR_REGISTRY: dict[str, Sensor]`, exports `get_sensor()`.
- **`router.py`** —
  - `GET /sensors` — list registered sensors.
  - `POST /ingest/{sensor_id}` — validates envelope + payload against the sensor's Pydantic model, writes `Telemetry(trip_id=NULL, timestamp, sensor_type, sensor_data)` (see §7 for the `trip_id=NULL` note), publishes to `telemetry.{sensor_id}`, returns `{stream_id}`. Uses `run_in_threadpool(session.commit)` because the DB session is sync.
  - `POST /ingest/batch` — same, list form.

### 5.6 `app/chronic/` — 11 periodic jobs

All jobs subclass `ChronicJob` (in `base.py`), which is an abstract with `name`, `interval_s`, and `async run(ctx: ChronicContext)`. `__init__.py` imports every module, builds `CHRONIC_REGISTRY`, and `register_all(scheduler)` adds each as an interval job.

**All 11 `run()` bodies are stubs** (debug log only). Intervals:

| File | Job | interval_s |
|---|---|---|
| `speed_check.py` | SpeedCheck | 1.0 |
| `alertness.py` | Alertness | 5.0 |
| `grip_quality.py` | GripQuality | 2.0 |
| `following_distance.py` | FollowingDistance | 1.0 |
| `speed_vs_limit.py` | SpeedVsLimit | 1.0 |
| `energy_range.py` | EnergyRange | 30.0 |
| `distraction.py` | Distraction | 5.0 |
| `fatigue_trend.py` | FatigueTrend | 30.0 |
| `eco_score.py` | EcoScore | 10.0 |
| `comfort_temp.py` | ComfortTemp | 60.0 |
| `known_places.py` | KnownPlaces | 15.0 |

### 5.7 `app/events/` — 15 stream consumers

All subclass `EventProcessor` (in `base.py`): `name`, `input_streams: list[str]`, `group='events'`, `async handle(stream, msg_id, fields, ctx)`. `__init__.py` builds `EVENT_REGISTRY` and `start_consumers()` spawns one asyncio task per processor. Each task reads its input streams via `bus.read_stream()` with the shared consumer group.

**All 15 `handle()` bodies are stubs.** Inputs:

| File | Processor | input_streams |
|---|---|---|
| `steering_release.py` | SteeringRelease | `telemetry.rotation`, `telemetry.pedals` |
| `harsh_brake.py` | HarshBrake | `telemetry.accelerometer`, `telemetry.pedals` |
| `harsh_accel.py` | HarshAccel | `telemetry.accelerometer`, `telemetry.pedals` |
| `lane_change.py` | LaneChange | `telemetry.rotation`, `telemetry.turn_signals` |
| `obstacle.py` | Obstacle | `telemetry.env.surroundings`, `telemetry.vehicle.adas` |
| `speed_threshold.py` | SpeedThreshold | `telemetry.vehicle.speed` |
| `geofence.py` | Geofence | `telemetry.vehicle.speed` (GPS sensor TBD) |
| `trip_lifecycle.py` | TripLifecycle | `telemetry.vehicle.gears`, `telemetry.vehicle.parking_brake` |
| `driver_identified.py` | DriverIdentified | `identity.bluetooth` (from `drivers/identity.py`) |
| `alertness_drop.py` | AlertnessDrop | `events.derived` (from chronic Alertness) |
| `weather_change.py` | WeatherChange | `environment.weather` |
| `energy_low.py` | EnergyLow | `telemetry.vehicle.energy` |
| `hotspot_approaching.py` | HotspotApproaching | `telemetry.vehicle.speed` |
| `parent_approval.py` | ParentApproval | `delivery.approval` |
| `llm_failure.py` | LlmFailure | `llm.failures` |

### 5.8 `app/orchestrator/`

| File | Role |
|---|---|
| `router.py` | `GET /orchestrator/context/{trip_id}` — returns a `ContextSnapshot`. |
| `engine.py` | Async engine that consumes `events.derived`, builds a snapshot, iterates `RULES`, throttles repeats (30s cooldown), logs matched actions. **TODO:** publish matched action to delivery. `start_engine()` returns the task. |
| `rules.py` | `Rule = Callable[[ContextSnapshot, dict], RuleResult | None]`. `RuleResult(action, priority, message)`. `RULES: list[Rule]` + `register_rule` decorator. |
| `policy.py` | `prompt_for(persona, use)` → `"{persona.lower()}.{use}"`. Trivial resolver the LLM layer uses to pick a prompt template. |
| `throttle.py` | `Throttle(cooldown_s=30)`. `allow(key)` returns True/False by tracking last-emission timestamp per key. |
| `context.py` | `ContextSnapshot(user, vehicle, environment, interaction)`. `build_snapshot(trip_id)` currently returns an empty snapshot — real Redis-backed builder is a TODO. |

### 5.9 `app/llm/`

| File | Role |
|---|---|
| `router.py` | `POST /llm/chat` and `POST /llm/trips/{trip_id}/summary`. Both catch `LlmUnavailable` → 503. |
| `client.py` | `LlmClient.complete()` raises `LlmUnavailable("no LLM provider configured")`. Real impl selects Anthropic/OpenAI based on `settings.*_api_key` and handles retries. |
| `guardrails.py` | `validate(text)` — trims whitespace, truncates to MAX_LEN=400 (appends "…"). |
| `prompts/__init__.py` | `PROMPTS: dict[str, str]` with templates for `chatbot.default`, `tips.default`, `summary.default`, `coaching.{new,sport,eco,experienced}`. `get(name, **kwargs)` formats. |
| `uses/chatbot.py` | `reply(question)` — chatbot.default template → client → guardrails. |
| `uses/tips.py` | `generate(context_desc)` — same pattern. |
| `uses/summary.py` | `summarize(events_desc)` — same pattern. |
| `uses/coaching.py` | `coach(persona, situation)` — maps persona string to prompt key `NEW/SPORT/ECO/EXPERIENCED`. |

### 5.10 `app/delivery/`

| File | Role |
|---|---|
| `router.py` | `GET /notifications/{trip_id}` (drain queue), `WS /notifications/{trip_id}/ws` (stream, 0.5s poll), `POST /approvals` (returns req id), `POST /approvals/{req_id}` (approve/deny). `emit(n)` publishes a `Notification` to the dashboard queue. |
| `channel.py` | `Notification(trip_id, channel, message, priority=5)`. Abstract `Channel`. `DashboardChannel` — in-memory per-trip queue. `TtsChannel` — logs. |
| `priority.py` | `choose(candidates)` — returns the notification with the lowest `priority` integer. |
| `approval.py` | `ApprovalRequest(id, trip_id, reason, status)`. `request(trip_id, reason)`, `resolve(req_id, approve)`. In-memory `_pending` dict. |

### 5.11 `app/drivers/`

| File | Role |
|---|---|
| `router.py` | `GET /drivers`, `POST /drivers`, `GET /drivers/{id}`, `PUT /drivers/{id}/persona`. |
| `service.py` | Sync CRUD using their `Driver` via the adapter. |
| `schemas.py` | `DriverCreate`, `DriverRead` (mirrors their columns), `PersonaUpdate`. |
| `identity.py` | `resolve_by_mac(session, mac)` raises `NotImplementedError`. The `drivers` table has no `bluetooth_mac` column — coordination item with smart_car_project. |

### 5.12 `app/trips/`

| File | Role |
|---|---|
| `router.py` | `GET /trips`, `GET /trips/{id}`, `GET /trips/{id}/summary`. |
| `service.py` | `start_trip(driver_id)` (sets `start_time = utcnow`), `end_trip(id)`, `list_trips()`, `get_trip(id)`. |
| `schemas.py` | `TripRead(id, driver_id, start_time, end_time, summary)`, `TripSummaryRead`. Summary JSON schema is owned by an external processor. |

### 5.13 `app/environment/`

| File | Role |
|---|---|
| `router.py` | `GET /environment/{lat}/{lon}` — currently raises 501. |
| `weather.py` | `fetch(lat, lon)` — `NotImplementedError`. Enum: `CLEAR/RAIN/SNOW/FOG`. |
| `road_type.py` | `classify(lat, lon)` — `NotImplementedError`. Enum: `URBAN/RURAL/HIGHWAY/SCHOOL_ZONE/UNKNOWN`. |
| `speed_limits.py` | `lookup(lat, lon)` — `NotImplementedError`. |
| `geofence.py` | `contains(lat, lon)` — `NotImplementedError`. No hardcoded fences by design — definitions pending a decision (DB / feature-flag / user profile). |

### 5.14 `app/scenarios/`

| File | Role |
|---|---|
| `router.py` | `GET /scenarios`, `POST /scenarios/{name}/start`, `POST /scenarios/{name}/stop`. |
| `runner.py` | `list_scenarios()` globs `library/*.json`. `_play(name, base_url)` replays frames by POSTing envelopes to `/ingest/{sensor_id}` at real rate. Tasks tracked in `_running`. |
| `library/` | Empty. Drop scenario JSONs here. |

### 5.15 `tests/`

| File | Covers |
|---|---|
| `conftest.py` | `sample_envelope()` fixture. |
| `unit/sensors/test_registry.py` | 14 sensor IDs registered. |
| `unit/sensors/test_speed_payload.py` | `SpeedPayload` range validation. |
| `unit/chronic/test_registry.py` | 11 chronic jobs registered, positive intervals. |
| `unit/events/test_registry.py` | 15 event processors registered, `input_streams` declared. |
| `unit/delivery/test_priority.py` | `choose()` picks lowest priority. |
| `unit/llm/test_guardrails.py` | `validate()` trims + truncates. |
| `unit/orchestrator/test_throttle.py` | Cooldown behavior. |
| `integration/test_placeholder.py` | Skipped stub. |
| `scenarios/test_placeholder.py` | Skipped stub. |

## 6. Data flow at runtime

1. **Ingest.** Mock vehicle → `POST /ingest/vehicle.speed` with a `SensorEnvelope`. Router validates envelope + payload, writes a `Telemetry` row, publishes JSON to `telemetry.vehicle.speed` in Redis. Returns `202 {stream_id}`.
2. **Chronic sample.** APScheduler fires `SpeedVsLimit.run()` every 1s. (Currently a stub. When implemented, it will read recent telemetry via the adapter or Redis and, on a threshold breach, `publish_derived_event("speed_limit_exceeded", {...})`.)
3. **Event sample.** The `SpeedThreshold` processor is blocking on `XREADGROUP telemetry.vehicle.speed`. When a message arrives, `handle()` runs. (Also a stub — same publish path when implemented.)
4. **Orchestrator.** The engine is blocking on `XREADGROUP events.derived`. On a matching rule, it consults `Throttle` (30s cooldown per key), and if allowed, dispatches an action.
5. **Delivery.** (TODO) Orchestrator emits a `Notification` via `delivery.emit()`. Any WebSocket client on `WS /notifications/{trip_id}/ws` receives it within 0.5s.

## 7. Known coordination items with `smart_car_project`

These are real friction points to raise with their maintainer — not bugs on our side, but places where the seam is provisional:

1. **`telemetry.trip_id` type mismatch.** Envelope carries `trip_id: UUID`; their column is `Integer` (32-bit). `int(UUID)` overflows, so the router currently writes `NULL`. Fix on their end: widen to `BIGINT` or switch to `UUID`. Alternative on our end: drop UUIDs from the envelope.
2. **No `bluetooth_mac` column on `drivers`.** `drivers/identity.py::resolve_by_mac` raises `NotImplementedError` until they add it.
3. **No `docker-compose.yml` in their repo.** We currently bootstrap Postgres with a raw `docker run`. They should either ship a compose file or agree that we own the compose entry.
4. **Trip summary JSON schema.** `trips/schemas.py::TripSummaryRead` accepts `dict[str, Any]`. Owner and shape TBD.
5. **Migrations invocation.** Their repo has `requirements.txt` but no `pyproject.toml`, so `uv run alembic` needs `--with alembic --with sqlalchemy --with psycopg2-binary --with python-dotenv`. Ideally they publish a `pyproject.toml` so `uv run alembic upgrade head` just works.

## 8. Extension recipes

- **New sensor.** Drop `app/sensors/<name>.py` with a Pydantic `payload_model` + `SENSOR = Sensor(...)`. Add one import to `sensors/__init__.py`. Ingest, validation, DB write, and stream publish come for free.
- **New chronic job.** Drop `app/chronic/<name>.py` subclassing `ChronicJob` with `interval_s` and `async def run(ctx)`. Add one import to `chronic/__init__.py`. Scheduler picks it up on next boot.
- **New event processor.** Drop `app/events/<name>.py` subclassing `EventProcessor` with `input_streams` + `async def handle(...)`. Add one import to `events/__init__.py`. `start_consumers()` spawns a task on next boot.
- **New orchestrator rule.** In any imported module, define a `Rule` and call `@register_rule`. The engine picks it up.
- **New LLM use.** Drop `app/llm/uses/<name>.py` + a template in `llm/prompts/__init__.py`. Expose via `llm/router.py` if user-facing.
- **New scenario.** Drop a JSON file in `app/scenarios/library/`. `GET /scenarios` will list it.

## 9. Design principles

1. **One file per sensor, per chronic job, per event handler.** Small, self-contained, individually testable. 40 domain files that need to grow independently anyway.
2. **Registry pattern per domain.** Each `__init__.py` builds a dict. Adding a member = drop a file + one import.
3. **Base class per domain.** `sensors/base.py`, `chronic/base.py`, `events/base.py` fix the contract. Subclassing gets you scheduled / consumed / registered automatically.
4. **Router per domain.** Each package exposes an `APIRouter`; `app/api.py` mounts them. OpenAPI stays organized.
5. **Redis Streams is the seam.** Nothing calls the orchestrator directly — chronic and event processors publish to `events.derived`, orchestrator subscribes there.
6. **One adapter for their DB.** `app/adapters/carbrain_db.py` is the *only* file that reaches into `smart_car_project/`. If a second file needs to, add the re-export to the adapter instead of importing directly.
