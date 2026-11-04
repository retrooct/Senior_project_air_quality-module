
# inference.py

import math


# ==========================================
# PM2.5 AQI-LIKE CALCULATION
# ==========================================

def calculate_pm25_aqi(concentration):
    """
    Convert a PM2.5 concentration to an AQI-like
    indicator using EPA's 2024 PM2.5 breakpoints.

    An individual reading is NOT an official AQI.
    Official AQI requires the appropriate averaging
    method (24-hour or NowCast).
    """

    if concentration is None:
        return None

    concentration = float(concentration)

    if not math.isfinite(concentration) or concentration < 0:
        return None

    # EPA truncates PM2.5 concentrations to 0.1 ug/m3.
    concentration = math.floor(concentration * 10) / 10

    breakpoints = [
        (0.0, 9.0, 0, 50),
        (9.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 125.4, 151, 200),
        (125.5, 225.4, 201, 300),
        (225.5, 325.4, 301, 500)
    ]

    for c_low, c_high, i_low, i_high in breakpoints:

        if c_low <= concentration <= c_high:

            aqi = (
                (i_high - i_low)
                / (c_high - c_low)
                * (concentration - c_low)
                + i_low
            )

            return int(aqi + 0.5)

    # Display capped at 500 for this prototype.
    return 500


def get_aqi_category(aqi):

    if aqi is None:
        return "Unavailable"
    elif aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"


# ==========================================
# VOC STATE CLASSIFICATION
# ==========================================

def get_voc_state(voc_index):

    if voc_index is None or voc_index == 0:
        return "Warming Up / Unavailable"

    if voc_index <= 100:
        return "Stable or Below Baseline"
    elif voc_index <= 250:
        return "Slight Deterioration"
    elif voc_index <= 400:
        return "Distinct Deterioration"
    else:
        return "Intense Deterioration"


# ==========================================
# NOx STATE CLASSIFICATION
# ==========================================

def get_nox_state(nox_index):

    if nox_index is None or nox_index == 0:
        return "Warming Up / Unavailable"

    if nox_index <= 1:
        return "At Baseline"
    elif nox_index <= 20:
        return "Minimal Relative Increase"
    elif nox_index <= 150:
        return "Slight Relative Increase"
    elif nox_index <= 300:
        return "Distinct Relative Increase"
    else:
        return "Intense Relative Increase"


# ==========================================
# ENVIRONMENTAL INFERENCE MODEL
# ==========================================

def calculate_index(
    temperature_c: float | None,
    humidity: float | None,
    pm1_0: float,
    pm2_5: float,
    pm10: float,
    voc_index: float | None,
    nox_index: float | None
) -> dict:
    """
    Experimental rule-based environmental assessment.

    It identifies possible pollution patterns.
    It does NOT confirm a pollution source or
    provide a validated health-risk classification.
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
    # AQI-like assessment
    # --------------------------------------

    pm25_aqi = calculate_pm25_aqi(pm2_5)
    pm25_aqi_category = get_aqi_category(pm25_aqi)

    # --------------------------------------
    # Gas state classifications
    # --------------------------------------

    voc_state = get_voc_state(voc_index)
    nox_state = get_nox_state(nox_index)

    voc_ready = voc_index is not None and voc_index > 0
    nox_ready = nox_index is not None and nox_index > 0

    if not voc_ready:
        results.append("VOC Index warming up or unavailable")

    if not nox_ready:
        results.append("NOx Index warming up or unavailable")

    # --------------------------------------
    # VOC evidence
    # --------------------------------------

    if voc_ready and voc_index > 150:

        voc_event_score += 1
        smoke_score += 1
        urban_pollution_score += 1
        general_danger_score += 1

        results.append(
            "VOC Index elevated relative to its baseline"
        )

    # --------------------------------------
    # NOx evidence
    # --------------------------------------

    if nox_ready and nox_index > 100:

        nox_event_score += 1
        urban_pollution_score += 2
        general_danger_score += 1

        results.append(
            "NOx Index elevated relative to its baseline"
        )

    if nox_ready and nox_index > 200:

        nox_event_score += 1
        urban_pollution_score += 2
        general_danger_score += 1

        results.append(
            "NOx Index shows substantial deterioration"
        )

    # --------------------------------------
    # PM2.5 evidence
    # --------------------------------------

    if pm2_5 > 35:

        smoke_score += 2
        particle_pollution_score += 2
        general_danger_score += 1

        results.append("PM2.5 concentration is elevated")

    if pm2_5 > 55:

        smoke_score += 2
        particle_pollution_score += 2
        general_danger_score += 2

        results.append("PM2.5 concentration is very high")

    # --------------------------------------
    # PM10 evidence
    # --------------------------------------

    if pm10 > 50:

        dust_score += 2
        coarse_particle_score += 1
        particle_pollution_score += 2
        general_danger_score += 1

        results.append("PM10 concentration is elevated")

    if pm10 > 100:

        dust_score += 2
        coarse_particle_score += 1
        particle_pollution_score += 2
        general_danger_score += 2

        results.append("PM10 concentration is very high")

    # --------------------------------------
    # PM10 / PM2.5 ratio
    # --------------------------------------

    if pm2_5 > 0:
        pm10_pm25_ratio = pm10 / pm2_5
    else:
        pm10_pm25_ratio = 0.0

    if pm10_pm25_ratio > 3 and pm10 > 50:

        dust_score += 1
        coarse_particle_score += 1

        results.append(
            "PM10 is substantially higher than PM2.5, "
            "suggesting coarse particle pollution"
        )

    # --------------------------------------
    # Combined smoke-like evidence
    # --------------------------------------

    if (
        voc_ready
        and voc_index > 150
        and pm2_5 > 35
    ):

        smoke_score += 2
        general_danger_score += 1

        results.append(
            "Elevated VOC Index and PM2.5 suggest "
            "a possible smoke or pollution event"
        )

    # --------------------------------------
    # Combined combustion-like evidence
    # --------------------------------------

    if (
        nox_ready
        and nox_index > 100
        and pm2_5 > 35
    ):

        urban_pollution_score += 2
        general_danger_score += 1

        results.append(
            "Elevated NOx Index and PM2.5 suggest "
            "possible combustion-related pollution"
        )

    if (
        voc_ready
        and nox_ready
        and voc_index > 150
        and nox_index > 100
    ):

        urban_pollution_score += 1

        results.append(
            "VOC and NOx indices both show deterioration"
        )

    # --------------------------------------
    # Humidity caution
    # --------------------------------------

    if humidity is not None and humidity > 85:

        results.append(
            "High humidity may affect optical PM readings"
        )

    # --------------------------------------
    # Overall concern level
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
    # Select strongest possible event
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
    # Default explanation
    # --------------------------------------

    if not results:
        results.append(
            "No major environmental warning signs detected"
        )

    # --------------------------------------
    # Return all inference results
    # --------------------------------------

    return {
        "smoke_score": smoke_score,
        "dust_score": dust_score,
        "urban_pollution_score": urban_pollution_score,
        "general_danger_score": general_danger_score,

        "particle_pollution_score": particle_pollution_score,
        "coarse_particle_score": coarse_particle_score,
        "voc_event_score": voc_event_score,
        "nox_event_score": nox_event_score,

        "voc_state": voc_state,
        "nox_state": nox_state,

        "pm25_aqi": pm25_aqi,
        "pm25_aqi_category": pm25_aqi_category,

        "pm10_pm25_ratio": pm10_pm25_ratio,

        "danger_level": danger_level,
        "event": event,
        "results": results
    }
