import requests
from nicegui import ui

from src.tools import make_gauge,  to_float_list, Air_Quality_Widget, Room_choice_field
from src.params.gauge_params import temp_gauge_params, humidity_gauge_params, pressure_gauge_params


ui.label('📈 SmartDesk — Mesures récentes').classes('text-2xl font-semibold mb-4')


room_choice_field = Room_choice_field()


air_quality_widget = Air_Quality_Widget()

with ui.row().classes('gap-4 flex-wrap items-start'):
    temp_gauge = make_gauge('Température', temp_gauge_params)
    humidity_gauge = make_gauge('Humidity', humidity_gauge_params)
    pressure_gauge = make_gauge('Pression', pressure_gauge_params)

status = ui.label('Chargement des données...').classes('mt-2 text-sm opacity-70')


def update():
    try:
        r_data_all= requests.get("http://127.0.0.1:8085/data/all", timeout=3)
        if r_data_all.status_code != 200:
            status.set_text(f"Erreur HTTP {r_data_all.status_code}")
            return

        data = r_data_all.json()
        times = data['time']  # ex: "2025-10-16T14:05:55Z"
        temp  = to_float_list(data['temperature'])
        press = to_float_list(data['pressure'])
        hum   = to_float_list(data['humidity'])

        # ECharts accepte directement [time_iso, value]
        temp_gauge.options['series'][0]['data'][0]['value'] = float(temp[-1])
        humidity_gauge.options['series'][0]['data'][0]['value'] = float(hum[-1])
        pressure_gauge.options['series'][0]['data'][0]['value'] = float(press[-1])
        #temp_chart.options['series'][0]['data']  = [[t, y] for t, y in zip(times, temp)]

        r_data_wb_score = requests.get("http://127.0.0.1:8085/data/well-being-score", timeout=3)
        if r_data_wb_score.status_code != 200:
            status.set_text(f"Erreur HTTP {r_data_wb_score.status_code}")
            return
        data_wb = r_data_wb_score.json()

        score = data_wb.get("well_being_score", 50)

        air_quality_widget.update(score)
        temp_gauge.update()
        humidity_gauge.update()
        pressure_gauge.update()
        #temp_chart.update()


        status.set_text('Dernière mise à jour : OK ✅')

    except Exception as e:
        status.set_text(f'Erreur de connexion : {e}')

# Premier rendu + refresh toutes les 5 s
update()
ui.timer(5.0, update, active=True)

ui.run(title='SmartDesk Live Dashboard')
