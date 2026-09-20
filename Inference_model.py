#-----------------------
# inferencce model
#----------------------

# Sensor data dictionary
def calculate_index(
    temperature_c: float,
    humidity: float,
    pm1_0: float,
    pm2_5: float,
    pm10: float,
    voc_index: float,
    nox_index: float,
    co_ppm: float = 0.0
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
    
    # empty string for output results
    results = []

     # -------------------------------
    # VOC / NOx gas evidence
    # -------------------------------

    if voc_index >= 150:
        smoke_score += 1
        urban_pollution_score += 1
        general_danger_score += 1
        results.append("VOC Index indicates an elevated VOC event")

    if nox_index >= 20:
        urban_pollution_score += 1
        general_danger_score += 1
        results.append("NOx Index indicates an elevated NOx event")

    if nox_index >= 20 and pm2_5 > 35:
        urban_pollution_score += 2
        general_danger_score += 1
        results.append("NOx and PM2.5 are both elevated, suggesting combustion-related pollution")

    if voc_index >= 150 and pm2_5 > 35:
        smoke_score += 2
        general_danger_score += 1
        evidence.append("VOC Index and PM2.5 are both elevated, suggesting smoke or indoor/outdoor pollution event")


    # -------------------------------
    # Smoke / wildfire-like evidence
    # -------------------------------
    # Smoke is usually more related to fine particles: PM2.5.
    if pm2_5 > 35:
        smoke_score += 2
        general_danger_score += 1
        evidence.append("PM2.5 is elevated")

    if pm2_5 > 55:
        smoke_score += 2
        general_danger_score += 2
        evidence.append("PM2.5 is very high")

    if voc_index > 150:
        smoke_score += 1
        general_danger_score += 1
        evidence.append("VOC index is elevated")

    if co_ppm > 1.0:
        smoke_score += 1
        urban_pollution_score += 1
        evidence.append("CO is elevated")

    # -------------------------------
    # Dust evidence
    # -------------------------------
    # Dust is often more related to coarse particles: PM10.
    if pm10 > 50:
        dust_score += 2
        general_danger_score += 1
        evidence.append("PM10 is elevated")

    if pm10 > 100:
        dust_score += 2
        general_danger_score += 2
        evidence.append("PM10 is very high")

    # PM10 much larger than PM2.5 can suggest coarse particles.
    if pm2_5 > 0:
        pm10_pm25_ratio = pm10 / pm2_5
    else:
        pm10_pm25_ratio = 0.0

    if pm10_pm25_ratio > 3:
        dust_score += 1
        evidence.append("PM10 is much higher than PM2.5")

    if wind_speed > 15:
        dust_score += 1
        evidence.append("Wind speed is elevated")

    # -------------------------------
    # Urban / combustion pollution evidence
    # -------------------------------
    if nox_index > 100:
        urban_pollution_score += 2
        general_danger_score += 1
        evidence.append("NOx index is elevated")

    if nox_index > 200:
        urban_pollution_score += 2
        general_danger_score += 2
        evidence.append("NOx index is very high")

    if pm2_5 > 35 and nox_index > 100:
        urban_pollution_score += 1
        evidence.append("PM2.5 and NOx are both elevated")

    if voc_index > 150 and nox_index > 100:
        urban_pollution_score += 1
        evidence.append("VOC and NOx are both elevated")

    # -------------------------------
    # Humidity correction / caution
    # -------------------------------
    # High humidity can affect optical PM readings.
    if humidity > 85:
        evidence.append("High humidity may affect PM sensor readings")

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
        event = "possible dust event"

    if urban_pollution_score >= 4:
        event = "possible urban/combustion pollution event"

    return {
        "smoke_score": smoke_score,
        "dust_score": dust_score,
        "urban_pollution_score": urban_pollution_score,
        "general_danger_score": general_danger_score,
        "danger_level": danger_level,
        "event": event,
        "evidence": evidence,
        "pm10_pm25_ratio": pm10_pm25_ratio
    }
