from typing import Any, Dict
from nicegui import ui

def make_gauge(title, params):
    MIN, IDEAL, MAX = params['MIN'], params['IDEAL'], params['MAX']  # ← bornes et valeur idéale au centre
    ideal_ratio = (IDEAL - MIN) / (MAX - MIN)
    band = 0.05  # largeur de la bande "idéale" (2% de l'échelle)
    segments = [
        [max(0, ideal_ratio - band), '#10b981'],  # en-dessous
        [min(1, ideal_ratio + band), '#3b82f6'],  # bande idéale (étroite)
        [1, '#ef4444'],  # au-dessus
    ]

    gauge = ui.echart({
        'series': [{
            'type': 'gauge',
            'min': MIN, 'max': MAX,
            'startAngle': 210, 'endAngle': -30,
            'pointer': {'show': True, 'length': '70%'},
            'anchor': {'show': True, 'size': 8},
            'axisLine': {'lineStyle': {'width': 14, 'color': segments}},
            'axisTick': {'distance': -15, 'length': 6, 'splitNumber': 4},
            'splitLine': {'distance': -18, 'length': 14},
            # 👇 labels plus petits, toujours en couleur noire pour contraste
            'axisLabel': {'distance': -28, 'formatter': '{value}', 'color': '#000', 'fontSize': 10},
            #'axisLabel': {'distance': -30, 'formatter': '{value}°C'},
            'detail': {'fontSize': 22, 'offsetCenter': [0, '60%'], 'formatter': params['formateur']},
            'title': {'show': True, 'offsetCenter': [0, '85%'], 'textStyle': {'fontSize': 14}},
            'data': [{'value': IDEAL, 'name': title}],
        }]
    }).classes('w-70 h-70')

    return gauge


def make_chart(title: str):
    return ui.echart({
        'title': {'text': title, 'left': 'center', 'textStyle': {'fontSize': 14}},
        'grid': {'left': 50, 'right': 20, 'top': 40, 'bottom': 40},
        'tooltip': {'trigger': 'axis'},
        'xAxis': {'type': 'time', 'axisLabel': {'formatter': '{HH}:{mm}:{ss}'}},
        'yAxis': {'type': 'value'},
        'series': [{'type': 'line', 'showSymbol': True, 'data': []}],
    }).classes('w-full h-60 my-3')


def to_float_list(lst):
    out = []
    for v in lst:
        try:
            out.append(float(v))
        except Exception:
            out.append(None)
    return out