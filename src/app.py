from nicegui import ui

from src.tools import  RoomInfo
# données d'exemple
rooms = [ '1', '2', '3']
Rooms_widget:list[RoomInfo]= []



ui.label('SmartDesk — Salles').classes('text-2xl font-bold mb-4')

# grille responsive: 1 colonne mobile, 3 colonnes ≥ md
with ui.element('div').classes(
    'grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-7xl'
):
    for r in rooms:
        Rooms_widget.append(RoomInfo(r))

def update():
    global Rooms_widget
    for room in Rooms_widget:
        room.update()
    return None

update()
ui.timer(5.0, update, active=True)
ui.run(title='SmartDesk')
