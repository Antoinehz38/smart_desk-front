
import asyncio, json, time
from nicegui import ui
import aiomqtt

BROKER = 'localhost'
TOPIC  = 'smartdesk/+/metrics'

ui.label('Smart Desk • Live Metrics').classes('text-xl font-semibold')
status = ui.label('MQTT: connecting…').classes('text-sm opacity-70')

# 3 séries: Temp / Pression / Humidité
line = ui.line_plot(n=3, limit=200, update_every=1).with_legend(
    ['Temp (°C)', 'Press (hPa)', 'Humidité (%)'], loc='upper center', ncol=3
).classes('w-full h-80')

latest = ui.label('—')

async def handle_payload(payload: bytes):
    data = json.loads(payload.decode())
    t = float(data.get('temp_c', 0.0))
    p = float(data.get('pressure_hpa', 0.0))
    h = float(data.get('humidity_pct', 0.0))
    x = time.time()
    line.push([x], [[t], [p], [h]])
    latest.text = f'{time.strftime("%H:%M:%S")} • {t:.2f}°C, {p:.1f} hPa, {h:.1f}%'

async def mqtt_consumer():
    try:
        status.text = f'MQTT: connexion à {BROKER}…'
        async with aiomqtt.Client(BROKER) as client:
            async with client.messages() as messages:
                await client.subscribe(TOPIC)
                status.text = f'MQTT: connecté ({BROKER})'
                async for msg in messages:
                    await handle_payload(msg.payload)
    except Exception as e:
        status.text = f'MQTT: erreur ({e}) — retry…'
        await asyncio.sleep(2)
        asyncio.create_task(mqtt_consumer())  # retry


def start_mqtt_once():

    if not getattr(start_mqtt_once, 'started', False):
        start_mqtt_once.started = True
        asyncio.create_task(mqtt_consumer())

ui.timer(0.1, start_mqtt_once, once=True)

ui.run(title='Smart Desk', reload=False,host = "127.0.0.0", port=8081 )
