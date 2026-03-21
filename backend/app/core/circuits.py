# SVG Paths for major F1 circuits
# Note: These are simplified but recognizable approximations

CIRCUITS = {
    "Bahrain": {
        "id": "bahrain",
        "name": "Bahrain International Circuit",
        "path": "M 160 320 L 40 320 L 80 160 L 160 40 L 240 120 L 320 160 L 360 280 L 280 360 Z",
        "viewBox": "0 0 400 400"
    },
    "Monza": {
        "id": "monza",
        "name": "Autodromo Nazionale di Monza",
        "path": "M 50 300 L 350 300 Q 380 300 380 270 L 380 100 Q 380 70 350 70 L 150 70 Q 120 70 120 100 L 120 150 L 80 150 L 80 180 L 120 180 L 120 230 Q 120 260 90 260 L 50 260 Z",
        "viewBox": "0 0 430 350"
    },
    "Suzuka": {
        "id": "suzuka",
        "name": "Suzuka International Racing Course",
        "path": "M 100 300 C 50 300, 50 200, 150 150 C 250 100, 350 100, 350 200 C 350 300, 250 300, 150 250 C 50 200, 50 100, 100 50 C 150 0, 250 0, 300 100 L 350 150 L 300 200 L 100 300",
        "viewBox": "0 0 400 350"
    }
}

def get_circuit_for_session(year: int, race_round: int):
    # For now, let's map rounds to circuits to show variety
    if race_round == 1:
        return CIRCUITS["Bahrain"]
    elif race_round == 2:
        return CIRCUITS["Monza"]
    else:
        return CIRCUITS["Suzuka"]
