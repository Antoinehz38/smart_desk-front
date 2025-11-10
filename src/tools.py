from typing import Any, Dict
from nicegui import ui
import requests

from src.params.ROOMS import ROOM_TABLE
from src.quality_calculation import well_being_score


def set_color(el, name: str):
    el.style(f'color: {name}')


def color_air(q):
    return 'green' if q >= 75 else 'orange' if q >= 50 else 'red'


def color_temp(t):
    return 'green' if 20 <= t <= 24 else 'orange' if 15 <= t <= 29 else 'red'


def color_press(p):
    return 'green' if 1005 <= p <= 1018 else 'orange' if 990 <= p <= 1030 else 'red'


def color_hum(h):
    return 'green' if 30 <= h <= 60 else 'orange' if 20 <= h <= 70 else 'red'


def color_lux(x):
    return 'green' if 60 <= x <= 80 else 'orange' if 40 <= x <= 90 else 'red'


def color_noise(db):
    return 'green' if db < 25 else 'orange' if db <= 70 else 'red'


class RoomInfo:
    def __init__(self, room_number: str):
        self.room_number = room_number
        self.room_url_id = ROOM_TABLE[room_number]

        with ui.card().classes('w-full rounded-2xl shadow-md p-4 bg-white'):
            with ui.row().classes('items-center justify-between'):
                ui.label(f"Salle {self.room_number}").classes('text-xl font-semibold')
                self.badge = ui.badge('Qualité: --', color='grey') \
                    .classes('text-lg px-3 py-2')

            ui.separator()
            with ui.row().classes('justify-between'):
                ui.icon('thermostat').classes('opacity-70')
                ui.label("Température:").classes('font-medium')
                self.temp_value = ui.label("0 °C").classes('font-medium')

            with ui.row().classes('justify-between'):
                ui.icon('speed').classes('opacity-70')
                ui.label("Pression:").classes('font-medium')
                self.press_value = ui.label("0 hPa").classes('font-medium')

            with ui.row().classes('justify-between'):
                ui.icon('water_drop').classes('opacity-70')
                ui.label("Humidité:").classes('font-medium')
                self.hum_value = ui.label("0 %").classes('font-medium')

            with ui.row().classes('justify-between'):
                ui.icon('light_mode').classes('opacity-70')
                ui.label("Luminosité:").classes('font-medium')
                self.lum_value = ui.label("0 lx").classes('font-medium')

            with ui.row().classes('justify-between'):
                ui.icon('graphic_eq').classes('opacity-70')
                ui.label("Bruit:").classes('font-medium')
                self.noise_value = ui.label("0 dB").classes('font-medium')

    def update(self):
        url = f"https://api.thingspeak.com/channels/{self.room_url_id}/feeds.json"
        params = {"results": 1}
        response = requests.get(url, params)

        Temperature = float(response.json()["feeds"][0]["field1"])
        pressure = float(response.json()["feeds"][0]["field2"])
        hum = float(response.json()['feeds'][0]['field3'])
        if self.room_number == "2":
            lux = float(response.json()["feeds"][0]["field4"]) - 20 # HARDCODED
            noise = float(response.json()["feeds"][0]["field5"]) * 6
        else:
            lux = 54
            noise = 50

        score = well_being_score(temp_c=Temperature, press_hpa=pressure, hum=hum, lux=lux, sound=noise)

        self.temp_value.text = f"{Temperature:.1f} °C"
        self.press_value.text = f"{pressure:.2f} hPa"
        self.hum_value.text = f"{hum:.1f} %"
        self.lum_value.text = f"{lux:.0f} %"
        self.noise_value.text = f"{noise:.0f} %"
        self.badge.text = f"Score : {score}"

        set_color(self.temp_value, color_temp(Temperature))
        set_color(self.press_value, color_press(pressure))
        set_color(self.hum_value, color_hum(hum))
        set_color(self.lum_value, color_lux(lux))
        set_color(self.noise_value, color_noise(noise))
        self.badge.props(f'color={color_air(score)}')  # badge supporte bien color
