def well_being_score(temp_c: float, hum: float, press_hpa: float, sound: float, lux: float) -> float:
    """
    Score 0-100, plus indulgent sauf valeurs franchement aberrantes.
    Paramètres:
      - temp_c: °C
      - hum: % HR
      - press_hpa: hPa
      - sound: dB(A)
      - lux: lux
    """

    def score_three_zones(x, ideal, soft, hard):
        lo_i, hi_i = ideal
        lo_s, hi_s = soft
        lo_h, hi_h = hard

        # Récompense forte dans la zone idéale
        if lo_i <= x <= hi_i:
            return 100.0

        # Zone douce: décroissance légère -> min 70
        if lo_s <= x <= hi_s:
            # distance à la frontière idéale la plus proche, normalisée par la largeur de la zone douce hors idéal
            if x < lo_i:
                t = (lo_i - x) / (lo_i - lo_s + 1e-9)
            else:
                t = (x - hi_i) / (hi_s - hi_i + 1e-9)
            return 100.0 - 50.0 * max(0.0, min(1.0, t))

        # Zone dure: pénalité quadratique rapide vers 0
        if lo_h <= x <= hi_h:
            if x < lo_s:
                t = (lo_s - x) / (lo_s - lo_h + 1e-9)
            else:
                t = (x - hi_s) / (hi_h - hi_s + 1e-9)
            t = max(0.0, min(1.0, t))
            return max(0.0, 80.0 * (1.0 - t * t))

        # Hors bornes du raisonnable
        return -50

    def score_lower_better(x, ideal_max, soft_max, hard_max):
        # <= ideal_max: 100; (ideal_max, soft_max]: linéaire jusqu'à 70; (soft_max, hard_max]: quadratique jusqu'à 0; > hard_max: 0
        if x <= ideal_max:
            return 100.0
        if x <= soft_max:
            t = (x - ideal_max) / (soft_max - ideal_max + 1e-9)
            return 100.0 - 30.0 * max(0.0, min(1.0, t))
        if x <= hard_max:
            t = (x - soft_max) / (hard_max - soft_max + 1e-9)
            t = max(0.0, min(1.0, t))
            return max(0.0, 70.0 * (1.0 - t * t))
        return 0.0

    # Plages indulgentes mais réalistes
    temp_score = score_three_zones(
        temp_c,
        ideal=(20.0, 23.0),
        soft=(18.0, 26.0),
        hard=(15.0, 30.0),
    )

    hum_score = score_three_zones(
        hum,
        ideal=(40.0, 55.0),
        soft=(30.0, 70.0),
        hard=(20.0, 80.0),
    )

    press_score = score_three_zones(
        press_hpa,
        ideal=(1005.0, 1018.0),
        soft=(995.0, 1028.0),
        hard=(980.0, 1035.0),
    )

    sound_score = score_lower_better(
        sound,
        ideal_max=25.0,
        soft_max=50.0,
        hard_max=70.0,
    )

    lux_score = score_three_zones(
        lux,
        ideal=(60.0, 80.0),
        soft=(40.0, 90.0),
        hard=(0.0, 100.0),
    )

    # Pondérations indulgentes
    score = (
        0.30 * temp_score
        + 0.20 * hum_score
        + 0.05 * press_score
        + 0.30 * sound_score
        + 0.15 * lux_score
    )

    print(f'score temps = {temp_score}')

    return round(max(0.0, min(100.0, score)), 1)
