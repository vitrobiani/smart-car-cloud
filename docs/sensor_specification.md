# Sensor Specification – Phase 2 Demo

> **Purpose:** define the exact schema, units, update mode, and value ranges for every sensor used in the demo. This is the contract between the mock telemetry producer, the DB, and the cloud brain.
> **Scope:** Phase 2 uses **mocked** telemetry that mimics AAOS/VHAL and Android Sensor APIs. Field names and units mirror the real Android APIs so the same schema can be reused in Phase 3.
> **Status:** draft — align with team before locking DB schema.

---

## Conventions

- **Timestamp:** every event carries `ts_ms` – Unix time in milliseconds (int64).
- **Trip context:** every event carries `trip_id` (uuid) and `driver_id` (uuid).
- **Coordinates / units:** SI where possible (m/s, m, °C, kPa, kg, Wh). Convert to display units on the frontend.
- **Sample types:**
  - `CONTINUOUS` – emitted at a fixed rate.
  - `ON_CHANGE` – emitted only when the value changes.
  - `EVENT` – emitted once per discrete occurrence.
- **Availability field:** every payload carries `available: bool` and `status: enum` (`OK`, `UNAVAILABLE`, `ERROR`, `PERMISSION_DENIED`) – lets the brain reason about missing signals without crashing.
- **Envelope (all sensors share it):**

```json
{
  "sensor_id": "vehicle.speed",
  "ts_ms": 1734567890123,
  "trip_id": "…",
  "driver_id": "…",
  "status": "OK",
  "available": true,
  "payload": { … sensor-specific … }
}
```

---

## 1. Vehicle Speed (non-GPS)

- **Source (real):** VHAL `PERF_VEHICLE_SPEED`
- **Sample type:** `CONTINUOUS`
- **Rate:** 10 Hz (100 ms)
- **Payload:**

| Field | Type | Unit | Range | Notes |
|-------|------|------|-------|-------|
| `speed_mps` | float | m/s | -30 … 90 | negative = reverse |
| `speed_kmh` | float | km/h | derived, for convenience |

- **Mock strategy:** driven by scenario script; smooth interpolation between waypoints; injectable noise.

---

## 2. Accelerometer

- **Source (real):** `Sensor.TYPE_ACCELEROMETER` (includes gravity) + `TYPE_LINEAR_ACCELERATION` (gravity-free)
- **Sample type:** `CONTINUOUS`
- **Rate:** 50 Hz (20 ms) – tune down to 20 Hz if too noisy for demo
- **Payload:**

| Field | Type | Unit | Range | Notes |
|-------|------|------|-------|-------|
| `ax` | float | m/s² | -20 … 20 | lateral (vehicle X) |
| `ay` | float | m/s² | -20 … 20 | longitudinal (vehicle Y) |
| `az` | float | m/s² | -20 … 20 | vertical (vehicle Z) |
| `linear_ax` | float | m/s² | -20 … 20 | gravity removed |
| `linear_ay` | float | m/s² | -20 … 20 | gravity removed |
| `linear_az` | float | m/s² | -20 … 20 | gravity removed |
| `magnitude` | float | m/s² | 0 … 30 | precomputed for convenience |

- **Derived events (produced by chronic processor, not the sensor):** `HARSH_BRAKE` (linear_ay < −4 m/s² for ≥250 ms), `HARSH_ACCEL` (linear_ay > 3.5 m/s²), `HARSH_CORNER` (|linear_ax| > 3.5 m/s²), `POTHOLE` (|linear_az| > 6 m/s² spike).
- **Mock strategy:** scenario waypoints emit shock profiles; base noise ±0.2 m/s².

---

## 3. Rotation Vector

- **Source (real):** `Sensor.TYPE_ROTATION_VECTOR` (device orientation quaternion) + `TYPE_GYROSCOPE` (angular velocity)
- **Sample type:** `CONTINUOUS`
- **Rate:** 50 Hz
- **Payload:**

| Field | Type | Unit | Range | Notes |
|-------|------|------|-------|-------|
| `qx` | float | – | -1 … 1 | quaternion x |
| `qy` | float | – | -1 … 1 | quaternion y |
| `qz` | float | – | -1 … 1 | quaternion z |
| `qw` | float | – | -1 … 1 | quaternion w |
| `heading_deg` | float | ° | 0 … 360 | derived, compass heading |
| `pitch_deg` | float | ° | -90 … 90 | derived |
| `roll_deg` | float | ° | -180 … 180 | derived |
| `gyro_x` | float | rad/s | -10 … 10 | pitch rate |
| `gyro_y` | float | rad/s | -10 … 10 | roll rate |
| `gyro_z` | float | rad/s | -10 … 10 | yaw rate (turning) |

- **Derived events:** `LANE_CHANGE` (yaw-rate signature over ~1.5 s), `SHARP_TURN` (|gyro_z| > 0.4 rad/s sustained).
- **Mock strategy:** scenario supplies heading trajectory; quaternion computed from it.

---

## 4. Accelerator & Brake Pedals

- **Source (real):** VHAL `ACCELERATOR_PEDAL_COMPRESSION_PERCENTAGE`, `BRAKE_PEDAL_COMPRESSION_PERCENTAGE` (privileged; may fall back to boolean brake light on some builds)
- **Sample type:** `CONTINUOUS` (compression) + `EVENT` (transitions)
- **Rate:** 20 Hz
- **Payload:**

| Field | Type | Unit | Range | Notes |
|-------|------|------|-------|-------|
| `accelerator_pct` | float | % | 0 … 100 | 0 = released |
| `brake_pct` | float | % | 0 … 100 | 0 = released |
| `brake_light_on` | bool | – | – | fallback if % not available |
| `accelerator_available` | bool | – | – | signal availability |
| `brake_available` | bool | – | – | signal availability |

- **Derived events:** `BRAKE_PRESSED`, `BRAKE_RELEASED`, `ACCEL_PRESSED`, `ACCEL_RELEASED`, `COAST_START/END` (both pedals released for ≥500 ms).
- **Mock strategy:** scenario-driven; noise ±1 %.

---

## 5. Fuel / Battery

- **Source (real):** VHAL `FUEL_LEVEL`, `FUEL_LEVEL_LOW`, `EV_BATTERY_LEVEL`, `EV_CHARGE_STATE`, `RANGE_REMAINING`
- **Sample type:** `ON_CHANGE` + heartbeat every 30 s
- **Payload:**

| Field | Type | Unit | Range | Notes |
|-------|------|------|-------|-------|
| `powertrain` | enum | – | `ICE` / `EV` / `HYBRID` | per-vehicle constant |
| `fuel_level_l` | float | liters | 0 … tank_capacity | ICE / hybrid |
| `fuel_level_pct` | float | % | 0 … 100 | derived |
| `fuel_low` | bool | – | – | VHAL flag |
| `battery_level_wh` | float | Wh | 0 … pack_capacity | EV / hybrid |
| `battery_level_pct` | float | % | 0 … 100 | derived |
| `charging` | bool | – | – | EV |
| `charge_state` | enum | – | `NOT_CHARGING` / `CHARGING` / `FULL` / `FAULT` | EV |
| `range_remaining_m` | float | meters | 0 … 1_000_000 | combined range |

- **Derived events:** `FUEL_LOW_THRESHOLD_CROSSED`, `BATTERY_LOW_THRESHOLD_CROSSED`, `RANGE_INSUFFICIENT_FOR_DESTINATION` (needs route module).
- **Mock strategy:** decay linearly per km driven; jitter ±0.1 %; scenario can spike consumption.

---

## 6. Gears

- **Source (real):** VHAL `CURRENT_GEAR` (engaged), `GEAR_SELECTION` (driver-selected)
- **Sample type:** `ON_CHANGE`
- **Payload:**

| Field | Type | Unit | Range | Notes |
|-------|------|------|-------|-------|
| `gear_selected` | enum | – | `P` / `R` / `N` / `D` / `S` / `M` / `1`…`8` | what the driver picked |
| `gear_engaged` | enum | – | same | what the transmission is actually in |
| `is_shift` | bool | – | – | true on the event where engaged changed |
| `previous_gear` | enum | – | – | populated on shift events |

- **Derived events:** `SHIFT_UP`, `SHIFT_DOWN`, `SHIFT_TO_REVERSE`, `SHIFT_TO_PARK`, `MANUAL_MODE_ENTERED`.
- **Mock strategy:** driven by scenario or auto-shift logic tied to `speed_mps` and load.

---

## 7. Day / Night & Ambient Light

- **Sources (real):**
  - VHAL `NIGHT_MODE` (bool) – vehicle's own day/night state.
  - Android `UiModeManager.getNightMode()` – UI-level.
  - `Sensor.TYPE_LIGHT` – ambient light (lux).
- **Sample type:** `ON_CHANGE` for mode; `CONTINUOUS` (1 Hz) for lux.
- **Payload:**

| Field | Type | Unit | Range | Notes |
|-------|------|------|-------|-------|
| `night_mode` | bool | – | – | VHAL `NIGHT_MODE` (authoritative if available) |
| `night_mode_source` | enum | – | `VHAL` / `UI_MODE_MANAGER` / `LIGHT_SENSOR_INFERRED` / `UNAVAILABLE` | provenance |
| `ambient_light_lux` | float | lux | 0 … 40000 | 0 = pitch dark, >10000 = bright daylight |
| `light_sensor_available` | bool | – | – | – |
| `sun_state` | enum | – | `DAY` / `TWILIGHT` / `NIGHT` | derived from time + location + lux |

- **Derived events:** `SUNSET_APPROACHING`, `TUNNEL_ENTER`/`TUNNEL_EXIT` (rapid lux drop/rise), `HEADLIGHTS_RECOMMENDED`.
- **Mock strategy:** driven by scenario clock; can inject tunnel/sunset patterns.

---

## 8. Vehicle Lights (Headlights, Fog, High-Beam, etc.)

- **Source (real):** VHAL `HEADLIGHTS_STATE`, `HIGH_BEAM_LIGHTS_STATE`, `FOG_LIGHTS_STATE`, `HAZARD_LIGHTS_STATE`, `CABIN_LIGHTS_STATE` (plus corresponding `*_SWITCH` for driver intent).
- **Sample type:** `ON_CHANGE`
- **Payload:**

| Field | Type | Unit | Range | Notes |
|-------|------|------|-------|-------|
| `headlights` | enum | – | `OFF` / `ON` / `DAYTIME_RUNNING` / `AUTOMATIC` | – |
| `high_beam` | enum | – | `OFF` / `ON` / `AUTOMATIC` | – |
| `fog_lights_front` | enum | – | `OFF` / `ON` / `UNAVAILABLE` | – |
| `fog_lights_rear` | enum | – | `OFF` / `ON` / `UNAVAILABLE` | – |
| `hazard_lights` | enum | – | `OFF` / `ON` | – |
| `cabin_lights` | enum | – | `OFF` / `ON` / `AUTOMATIC` | – |
| `driver_intent_matches_actual` | bool | – | – | true if switch state == actual state |

- **Derived events:** `LIGHTS_ON`, `LIGHTS_OFF`, `HIGH_BEAM_TOGGLE`, `HAZARDS_ACTIVATED`, `FOG_LIGHTS_ON_IN_CLEAR_WEATHER` (needs weather API).
- **Mock strategy:** scenario-driven; auto-headlights can be inferred from `sun_state` for realism.

---

## 9. Surrounding Vehicles

- **Source (real):** No standard VHAL surface. In production this is OEM sensor-fusion / ADAS. For Phase 2 we mock it as if fused output were available.
- **Sample type:** `CONTINUOUS`
- **Rate:** 5 Hz
- **Payload:** `objects[]` array; up to N objects (limit ~16 for demo).

| Field | Type | Unit | Range | Notes |
|-------|------|------|-------|-------|
| `object_id` | int | – | – | stable across frames |
| `type` | enum | – | `CAR` / `TRUCK` / `MOTORCYCLE` / `PEDESTRIAN` / `CYCLIST` / `ANIMAL` / `UNKNOWN` | – |
| `relative_position_m` | {x,y} | meters | -100 … 100 | +y = ahead, +x = right |
| `relative_velocity_mps` | {vx,vy} | m/s | -50 … 50 | – |
| `distance_m` | float | meters | 0 … 200 | derived, straight-line |
| `bearing_deg` | float | ° | -180 … 180 | 0 = directly ahead |
| `lane_relative` | enum | – | `SAME` / `LEFT` / `RIGHT` / `UNKNOWN` | – |
| `time_to_collision_s` | float | s | 0 … 30 | derived; null if not converging |
| `confidence` | float | – | 0 … 1 | fusion confidence |

- **Also emitted (envelope-level):**
  - `following_distance_m` – to the object directly ahead in the same lane.
  - `following_time_s` – headway (distance / own speed).
- **Derived events:** `TAILGATING` (headway < 1.5 s for ≥3 s), `CUT_IN_DETECTED`, `PEDESTRIAN_NEAR_ROAD`, `EMERGENCY_BRAKE_RECOMMENDED` (TTC < 2 s).
- **Mock strategy:** scenario spawns objects along a track; simple kinematics; can inject aggressive drivers/pedestrians.

---

## 10. ADAS Sensors (radar / camera / ultrasonic) – Investigation

**Note:** in real AAOS these are almost never exposed to third-party apps directly. Access is OEM-privileged. For Phase 2 we treat ADAS as a **derived context source** rather than a raw sensor: the brain consumes the outputs listed below (which are what OEM ADAS would fuse), and we mock them.

- **Sample type:** `ON_CHANGE` for states; `CONTINUOUS` (10 Hz) for distances.
- **Payload:**

| Field | Type | Unit | Range | Notes |
|-------|------|------|-------|-------|
| `adas_available` | bool | – | – | master flag |
| `front_radar_distance_m` | float | m | 0 … 200 | nearest object ahead |
| `rear_radar_distance_m` | float | m | 0 … 100 | – |
| `ultrasonic_front_m` | float[8] | m | 0 … 5 | parking sensors |
| `ultrasonic_rear_m` | float[8] | m | 0 … 5 | parking sensors |
| `lane_departure_warning` | enum | – | `INACTIVE` / `LEFT` / `RIGHT` | – |
| `lane_keep_assist` | enum | – | `OFF` / `ON` / `INTERVENING` | – |
| `blind_spot_left` | bool | – | – | true = object in blind spot |
| `blind_spot_right` | bool | – | – | – |
| `forward_collision_warning` | enum | – | `INACTIVE` / `WARNING` / `EMERGENCY_BRAKE` | – |
| `adaptive_cruise_state` | enum | – | `OFF` / `STANDBY` / `ACTIVE` / `OVERRIDE` | – |
| `adaptive_cruise_set_speed_mps` | float | m/s | 0 … 55 | – |
| `traffic_sign_recognition` | array | – | – | detected signs (see below) |

- **Traffic sign object:** `{ type: 'SPEED_LIMIT'|'STOP'|'YIELD'|…, value?: int, confidence: float, distance_m: float }`
- **Team decision needed:** which of these do we consume in the demo? Recommended MVP subset: `front_radar_distance_m`, `blind_spot_left/right`, `forward_collision_warning`, `traffic_sign_recognition` (speed limit only).
- **Mock strategy:** derive from `Surrounding Vehicles` + scenario; TSR fed by geocoding lookup on route.

---

## 11. Tire Pressure

- **Source (real):** VHAL `TIRE_PRESSURE` (per-wheel area IDs: FL, FR, RL, RR), `CRITICALLY_LOW_TIRE_PRESSURE`, `TIRE_PRESSURE_DISPLAY_UNITS`
- **Sample type:** `ON_CHANGE` + heartbeat every 60 s
- **Payload:**

| Field | Type | Unit | Range | Notes |
|-------|------|------|-------|-------|
| `front_left_kpa` | float | kPa | 0 … 500 | – |
| `front_right_kpa` | float | kPa | 0 … 500 | – |
| `rear_left_kpa` | float | kPa | 0 … 500 | – |
| `rear_right_kpa` | float | kPa | 0 … 500 | – |
| `min_kpa` | float | kPa | – | derived, weakest wheel |
| `low_pressure_alert` | bool | – | – | any wheel < recommended |
| `critical_pressure_alert` | bool | – | – | any wheel below critical threshold |
| `recommended_kpa` | float | kPa | – | per-vehicle static |

- **Derived events:** `TIRE_PRESSURE_LOW`, `TIRE_PRESSURE_CRITICAL`, `SLOW_LEAK_DETECTED` (chronic downward trend on one wheel).
- **Mock strategy:** static baseline per wheel with small drift; scenario can inject leak.

---

## 12. Turn Signals

- **Source (real):** VHAL `TURN_SIGNAL_STATE` (actual lamps), `TURN_SIGNAL_LIGHT_STATE` / `TURN_SIGNAL_SWITCH` (driver intent)
- **Sample type:** `ON_CHANGE`
- **Payload:**

| Field | Type | Unit | Range | Notes |
|-------|------|------|-------|-------|
| `state` | enum | – | `NONE` / `LEFT` / `RIGHT` / `EMERGENCY` | actual lamps |
| `driver_intent` | enum | – | `NONE` / `LEFT` / `RIGHT` / `EMERGENCY` | switch position |
| `blink_count` | int | – | 0…∞ | since activation |
| `duration_ms` | int | ms | – | how long active |

- **Derived events:** `LANE_CHANGE_WITH_SIGNAL`, `LANE_CHANGE_WITHOUT_SIGNAL` (combined with rotation-vector yaw signature), `SIGNAL_LEFT_ON_TOO_LONG` (>30 s without lane change).
- **Mock strategy:** scenario-driven; coupled with lane-change scripts.

---

## 13. Parking Brake

- **Source (real):** VHAL `PARKING_BRAKE_ON`, `PARKING_BRAKE_AUTO_APPLY`
- **Sample type:** `ON_CHANGE`
- **Payload:**

| Field | Type | Unit | Range | Notes |
|-------|------|------|-------|-------|
| `engaged` | bool | – | – | – |
| `auto_apply_enabled` | bool | – | – | – |
| `engaged_source` | enum | – | `DRIVER` / `AUTO` / `UNKNOWN` | – |

- **Derived events:** `PARKING_BRAKE_ENGAGED`, `PARKING_BRAKE_RELEASED`, `MOVING_WITH_PARKING_BRAKE` (speed > 5 km/h AND engaged – fault condition).
- **Mock strategy:** state machine tied to `gear_selected == P`.

---

## 14. Odometer

- **Source (real):** VHAL `PERF_ODOMETER`
- **Sample type:** `CONTINUOUS` (low rate) – 0.2 Hz (every 5 s) + `ON_CHANGE` on trip end
- **Payload:**

| Field | Type | Unit | Range | Notes |
|-------|------|------|-------|-------|
| `total_km` | float | km | 0 … 999_999 | vehicle lifetime |
| `trip_km` | float | km | 0 … ∞ | since trip start (derived by brain) |
| `session_delta_km` | float | km | – | since last message |

- **Derived events:** `SERVICE_INTERVAL_APPROACHING` (needs vehicle config), `LONG_TRIP_MILESTONE` (every 100 km within a trip → rest suggestion).
- **Mock strategy:** integrate speed over time; persist last value across restarts.

---

## Cross-cutting: Envelope + Message Bus Topics

Suggested Redis Streams / Kafka topics – one per sensor plus one aggregate:

| Topic | Producer | Consumers |
|-------|----------|-----------|
| `telemetry.speed` | mock vehicle | chronic-speed, orchestrator, dashboard |
| `telemetry.accel` | mock vehicle | harsh-event detector, comfort scorer |
| `telemetry.rotation` | mock vehicle | lane-change detector, cornering scorer |
| `telemetry.pedals` | mock vehicle | eco scorer, harsh-event detector |
| `telemetry.energy` | mock vehicle | range planner, eco advisor |
| `telemetry.gears` | mock vehicle | eco scorer, sport coach |
| `telemetry.lighting` | mock vehicle | env classifier |
| `telemetry.vehicle_lights` | mock vehicle | env classifier, safety advisor |
| `telemetry.surroundings` | mock vehicle | following-distance, hazard detector |
| `telemetry.adas` | mock vehicle | safety advisor, sport coach |
| `telemetry.tires` | mock vehicle | maintenance advisor |
| `telemetry.signals` | mock vehicle | lane-change detector |
| `telemetry.parking_brake` | mock vehicle | trip lifecycle |
| `telemetry.odometer` | mock vehicle | trip lifecycle, milestone advisor |
| `events.derived` | processors | orchestrator, event log |
| `context.snapshot` | context builder | orchestrator, chatbot |

---

## DB Modeling Notes

Two-tier storage recommendation:

1. **Hot store (Redis):** last-N samples per sensor per trip, current context snapshot, active event list. TTL 24 h.
2. **Cold store (Postgres):**
   - `telemetry_raw` – append-only, partitioned by day + `trip_id`. High-volume signals may be downsampled before insert (e.g., 10 Hz → 1 Hz).
   - `events_derived` – all derived events with type, ts, trip_id, payload jsonb.
   - `trip_summary` – one row per trip with aggregates (distance, harsh events count, eco score, coaching messages count, …).
   - `sensor_availability` – per trip, which sensors were available/degraded/unavailable (feeds "known limitations" narrative for VW).

A single `telemetry_raw(sensor_id, ts_ms, trip_id, driver_id, payload jsonb)` table keeps modeling simple; add per-sensor materialized views if we need query speed for the dashboard.

---

## Open Questions for the Team

- [ ] Do we downsample high-rate sensors (accel, rotation) before writing to Postgres, or store everything and let queries aggregate?
- [ ] Do we model the vehicle as ICE, EV, or make it configurable per scenario? (Recommended: **EV** – matches VW ID.-family focus and simplifies fuel/energy modeling.)
- [ ] Which ADAS subset do we actually consume in the demo? (Recommend MVP subset from §10.)
- [ ] For surrounding vehicles, do we mock a full 360° object list or only "vehicle directly ahead"? (Recommend full list – small extra effort, big demo payoff.)
- [ ] Do we need a persistent `driver_id`↔`bluetooth_mac` table, or hardcode a single demo driver?
