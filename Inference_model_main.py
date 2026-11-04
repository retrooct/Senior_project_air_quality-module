
# ==========================================
# Environmental Inference Model
# ==========================================

def calculate_index(
    temperature_c: float,
    humidity: float,
    pm1_0: float,
    pm2_5: float,
    pm10: float,
    voc_index: float | None,
    nox_index: float | None
) -> dict:
    """
    Rule-based environmental inference model.

    Uses measurements from:
        PMS5003: PM1.0, PM2.5, PM10
        SGP41: VOC Index, NOx Index

    Estimates possible:
        - Smoke-related pollution
        - Dust/coarse particle pollution
        - Urban/combustion pollution

    Scores are custom heuristics, not validated
    health-risk levels or event probabilities.
    """

    # --------------------------------------
    # Initialize scores
    # --------------------------------------

    smoke_score = 0
    dust_score = 0
    urban_pollution_score = 0
    general_danger_score = 0

    particle_pollution_score = 0
    coarse_particle_score = 0
    voc_event_score = 0
    nox_event_score = 0

    results = []

    # --------------------------------------
    # Gas sensor readiness
    # --------------------------------------

    voc_ready = voc_index is not None
    nox_ready = nox_index is not None

    if not voc_ready:
        results.append(
            "VOC Index unavailable or warming up"
        )

    if not nox_ready:
        results.append(
            "NOx Index unavailable or warming up"
        )

    # --------------------------------------
    # VOC evidence
    # --------------------------------------

    # VOC Index baseline is approximately 100.
    # 150 is a custom event-detection threshold.

    if voc_ready and voc_index > 150:
        voc_event_score += 1
        smoke_score += 1
        urban_pollution_score += 1
        general_danger_score += 1

        results.append(
            "VOC Index is elevated relative to "
            "its recent baseline"
        )

    # --------------------------------------
    # NOx evidence
    # --------------------------------------

    # NOx Index baseline is approximately 1.
    # A value of 1 is not an elevated NOx event.

    if nox_ready and nox_index > 100:
        nox_event_score += 1
        urban_pollution_score += 2
        general_danger_score += 1

        results.append(
            "NOx Index is elevated relative to "
            "its recent baseline"
        )

    if nox_ready and nox_index > 200:
        nox_event_score += 1
        urban_pollution_score += 2
        general_danger_score += 1

        results.append(
            "NOx Index shows substantial "
            "relative deterioration"
        )

    # --------------------------------------
    # PM2.5 / Fine Particle Evidence
    # --------------------------------------

    if pm2_5 > 35:
        smoke_score += 2
        particle_pollution_score += 2
        general_danger_score += 1

        results.append(
            "PM2.5 concentration is elevated"
        )

    if pm2_5 > 55:
        smoke_score += 2
        particle_pollution_score += 2
        general_danger_score += 2

        results.append(
            "PM2.5 concentration is very high"
        )

    # --------------------------------------
    # PM10 / Coarse Particle Evidence
    # --------------------------------------

    if pm10 > 50:
        dust_score += 2
        coarse_particle_score += 1
        particle_pollution_score += 2
        general_danger_score += 1

        results.append(
            "PM10 concentration is elevated"
        )

    if pm10 > 100:
        dust_score += 2
        coarse_particle_score += 1
        particle_pollution_score += 2
        general_danger_score += 2

        results.append(
            "PM10 concentration is very high"
        )

    # --------------------------------------
    # PM10 / PM2.5 Ratio
    # --------------------------------------

    if pm2_5 > 0:
        pm10_pm25_ratio = pm10 / pm2_5
    else:
        pm10_pm25_ratio = 0.0

    if pm10_pm25_ratio > 3 and pm10 > 50:
        dust_score += 1
        coarse_particle_score += 1

        results.append(
            "PM10 is substantially higher than "
            "PM2.5, suggesting coarse particles"
        )

    # --------------------------------------
    # Combined Pollution Evidence
    # --------------------------------------

    # Fine particles together with elevated VOC

    if (
        voc_ready
        and voc_index > 150
        and pm2_5 > 35
    ):
        smoke_score += 2
        general_danger_score += 1

        results.append(
            "Elevated VOC Index and PM2.5 "
            "suggest a possible smoke or "
            "pollution event"
        )

    # Fine particles together with elevated NOx

    if (
        nox_ready
        and nox_index > 100
        and pm2_5 > 35
    ):
        urban_pollution_score += 2
        general_danger_score += 1

        results.append(
            "Elevated NOx Index and PM2.5 "
            "suggest possible combustion-related "
            "pollution"
        )

    # Both gas indices elevated

    if (
        voc_ready
        and nox_ready
        and voc_index > 150
        and nox_index > 100
    ):
        urban_pollution_score += 1

        results.append(
            "Both VOC and NOx indices show "
            "relative deterioration"
        )

    # --------------------------------------
    # Humidity Caution
    # --------------------------------------

    if humidity is not None and humidity > 85:
        results.append(
            "High humidity may affect optical "
            "particulate matter measurements"
        )

    # --------------------------------------
    # General Concern Classification
    # --------------------------------------

    if general_danger_score >= 5:
        danger_level = "dangerous"

    elif general_danger_score >= 3:
        danger_level = "unhealthy"

    elif general_danger_score >= 1:
        danger_level = "moderate concern"

    else:
        danger_level = "normal"

    # --------------------------------------
    # Event Classification
    # --------------------------------------

    event_scores = {
        "possible smoke event": smoke_score,
        "possible dust/coarse particle event": dust_score,
        "possible urban/combustion pollution event":
            urban_pollution_score
    }

    strongest_event = max(
        event_scores,
        key=event_scores.get
    )

    if event_scores[strongest_event] >= 4:
        event = strongest_event
    else:
        event = "no major event detected"

    # --------------------------------------
    # Default Explanation
    # --------------------------------------

    if not results:
        results.append(
            "No major environmental warning "
            "signs detected"
        )

    # --------------------------------------
    # Return Results
    # --------------------------------------

    return {
        "smoke_score": smoke_score,
        "dust_score": dust_score,
        "urban_pollution_score": urban_pollution_score,
        "general_danger_score": general_danger_score,

        "particle_pollution_score":
            particle_pollution_score,

        "coarse_particle_score":
            coarse_particle_score,

        "voc_event_score": voc_event_score,
        "nox_event_score": nox_event_score,

        "danger_level": danger_level,
        "event": event,
        "results": results,

        "pm10_pm25_ratio": pm10_pm25_ratio
    }
