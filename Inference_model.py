# -----------------------
# inference model
# -----------------------

def calculate_index(
    temperature_c: float,
    humidity: float,
    pm1_0: float,
    pm2_5: float,
    pm10: float,
    voc_index: float,
    nox_index: float
) -> dict:
    """
    Rule-based environmental inference model.

    This does not prove a wildfire, dust storm, or pollution source.
    It estimates possible environmental conditions based on sensor patterns.
    """

    # Rule-based environmental risk scores
    smoke_score = 0
    dust_score = 0
    urban_pollution_score = 0
    general_danger_score = 0

    # Extra category scores
    particle_pollution_score = 0
    coarse_particle_score = 0
    voc_event_score = 0
    nox_event_score = 0

    # Output messages
    results = []

    # -------------------------------
    # VOC / NOx gas evidence
    # -------------------------------

    if voc_index < 100:
        voc_event_score = 0
        smoke_score -= 1
        results.append("VOC Index is in normal levels")

    if voc_index >= 100:
        voc_event_score += 1
        smoke_score += 1
        urban_pollution_score += 1
        general_danger_score += 1
        results.append("VOC Index indicates an elevated VOC event")

    if nox_index >= 1:
        nox_event_score += 1
        urban_pollution_score += 1
        general_danger_score += 1
        results.append("NOx Index indicates an elevated NOx event")

    if nox_index >= 1 and pm2_5 > 35:
        urban_pollution_score += 2
        general_danger_score += 1
        results.append("NOx and PM2.5 are both elevated, suggesting combustion-related pollution")

    if voc_index >= 100 and pm2_5 > 35:
        smoke_score += 2
        general_danger_score += 1
        results.append("VOC Index and PM2.5 are both elevated, suggesting smoke or indoor/outdoor pollution event")

    # -------------------------------
    # PM2.5 / smoke-like evidence
    # -------------------------------

    if pm2_5 > 35:
        smoke_score += 2
        particle_pollution_score += 2
        general_danger_score += 1
        results.append("PM2.5 is elevated")

    if pm2_5 > 55:
        smoke_score += 2
        particle_pollution_score += 2
        general_danger_score += 2
        results.append("PM2.5 is very high")

    # -------------------------------
    # PM10 / dust / coarse particle evidence
    # -------------------------------

    if pm10 > 50:
        dust_score += 2
        coarse_particle_score += 1
        particle_pollution_score += 2
        general_danger_score += 1
        results.append("PM10 is elevated")

    if pm10 > 100:
        dust_score += 2
        coarse_particle_score += 1
        particle_pollution_score += 2
        general_danger_score += 2
        results.append("PM10 is very high")

    if pm2_5 > 0:
        pm10_pm25_ratio = pm10 / pm2_5
    else:
        pm10_pm25_ratio = 0.0

    if pm10_pm25_ratio > 3:
        dust_score += 1
        coarse_particle_score += 1
        results.append("PM10 is much higher than PM2.5, suggesting coarse particle pollution")

    # -------------------------------
    # Urban / combustion pollution evidence
    # -------------------------------

    if nox_index > 100:
        urban_pollution_score += 2
        general_danger_score += 1
        results.append("NOx index is elevated")

    if nox_index > 200:
        urban_pollution_score += 2
        general_danger_score += 2
        results.append("NOx index is very high")

    if pm2_5 > 35 and nox_index > 100:
        urban_pollution_score += 1
        results.append("PM2.5 and NOx are both elevated")

    if voc_index > 150 and nox_index > 100:
        urban_pollution_score += 1
        results.append("VOC and NOx are both elevated")

    # -------------------------------
    # Humidity caution
    # -------------------------------

    if humidity > 85:
        results.append("High humidity may affect PM sensor readings")

    # -------------------------------
    # Risk classification
    # -------------------------------

    if general_danger_score >= 5:
        danger_level = "dangerous"
    elif general_danger_score >= 3:
        danger_level = "unhealthy"
    elif general_danger_score >= 1:
        danger_level = "moderate concern"
    else:
        danger_level = "normal"

    # -------------------------------
    # Event assessment
    # -------------------------------

    event = "no major event detected"

    if smoke_score >= 4 and smoke_score >= dust_score:
        event = "possible smoke event"

    if dust_score >= 4 and dust_score > smoke_score:
        event = "possible dust/coarse particle event"

    if urban_pollution_score >= 4:
        event = "possible urban/combustion pollution event"

    return {
        "smoke_score": smoke_score,
        "dust_score": dust_score,
        "urban_pollution_score": urban_pollution_score,
        "general_danger_score": general_danger_score,
        "particle_pollution_score": particle_pollution_score,
        "coarse_particle_score": coarse_particle_score,
        "voc_event_score": voc_event_score,
        "nox_event_score": nox_event_score,
        "danger_level": danger_level,
        "event": event,
        "results": results,
        "pm10_pm25_ratio": pm10_pm25_ratio
    }
