def well_being_score(temp_c: float, hum: float, press_hpa: float) -> float:
    """
    Calcule un score de bien-être (0 à 100) à partir de :
    - température en °C
    - humidité en %
    - pression en hPa
    """
    temp_score = max(0, 100 - abs(temp_c - 22) * 10)

    if hum < 40:
        hum_score = max(0, 100 - (40 - hum) * 2)
    elif hum > 60:
        hum_score = max(0, 100 - (hum - 60) * 2)
    else:
        hum_score = 100

    press_score = max(0, 100 - abs(press_hpa - 1013) * 2)

    score = 0.5 * temp_score + 0.3 * hum_score + 0.2 * press_score

    return round(score, 1)