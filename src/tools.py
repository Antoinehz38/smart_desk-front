from typing import Any, Dict
from nicegui import ui
import requests

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


class Air_Quality_Widget:
    def __init__(self,title: str = "Qualité de l'air"):
        with ui.card().classes('w-64 p-4 rounded-2xl shadow-lg border border-gray-100'):
            ui.label(title).classes('text-sm font-medium opacity-70 mb-1')

            # ligne nombre + /100 (alignés sur la ligne de base)
            with ui.row().classes('items-baseline gap-1'):
                self.value = ui.label('—').classes('text-6xl font-extrabold leading-none') \
                                     .style('line-height:1;')
                self.unit  = ui.label('/100').classes('text-base opacity-50')

            # badge d’état (point coloré + libellé)
            with ui.row().classes('items-center gap-2 mt-2'):
                self.dot = ui.element('div').classes('w-2.5 h-2.5 rounded-full bg-gray-300')
                self.tag = ui.label('—').classes('text-sm font-semibold')

    def update(self, score: float):
        s = max(0, min(100, float(score)))
        self.value.set_text(f'{s:.0f}')

        # mapping couleurs & libellés
        if s >= 80:
            label = 'Excellent'
            dot_cls = 'bg-green-500'
            grad = 'linear-gradient(90deg,#34d399,#16a34a)'   # vert
            text_color = '#059669'
        elif s >= 50:
            label = 'Moyen'
            dot_cls = 'bg-amber-500'
            grad = 'linear-gradient(90deg,#fbbf24,#d97706)'   # orange
            text_color = '#d97706'
        else:
            label = 'Mauvais'
            dot_cls = 'bg-red-500'
            grad = 'linear-gradient(90deg,#f87171,#dc2626)'   # rouge
            text_color = '#dc2626'

        # nombre en dégradé
        self.value.style(f'background:{grad}; -webkit-background-clip:text; -webkit-text-fill-color:transparent; line-height:1;')
        # badge
        self.dot.classes(replace=f'w-2.5 h-2.5 rounded-full {dot_cls}')
        self.tag.set_text(label)
        self.tag.style(f'color:{text_color}')


class Room_choice_field:
    def __init__(self):
        with ui.card().classes('w-96 p-4 rounded-2xl shadow-md border border-gray-100'):
            ui.label("Choix de la salle").classes('text-lg font-semibold mb-2')

            # champ de texte
            message_input = ui.input(
                label="Numero de salle",
            ).classes('w-full mb-3')

            # zone d’affichage de la réponse
            response_label = ui.label('').classes('text-sm text-gray-600 mt-2')

            async def on_send():
                text = message_input.value.strip()
                if not text:
                    response_label.set_text("⚠️ Écris quelque chose avant d'envoyer.")
                    response_label.classes(replace='text-sm text-red-600 mt-2')
                    return

                ### TODO mettre un await
                response = requests.put("http://127.0.0.1:8085/room/change", json= {"room_number":str(text)})

                if response.status_code == 200:
                    response_label.set_text(response.json()["message"])
                    response_label.classes(replace='text-sm text-green-600 mt-2')
                    message_input.value = ""  # reset
                else:
                    response_label.set_text(f"erreur while contacting back")
                    response_label.classes(replace='text-sm text-green-600 mt-2')
                    message_input.value = ""  # reset

            ui.button("valider", on_click=on_send).classes(
                'bg-blue-500 hover:bg-blue-600 text-white font-semibold px-4 py-2 rounded-lg'
            )
