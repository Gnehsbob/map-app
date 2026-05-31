FUEL_PRICE_ZAR = 23.00
CONSUMPTION_RATES = {"sedan": 7.5, "suv": 9.5, "bakkie": 11.0}

def trip_label(trips):
    if trips == 1:   return "1 trip (one way)"
    if trips == 2:   return "2 trips (return)"
    r     = trips // 2
    extra = " + 1 one-way" if trips % 2 else ""
    return f"{trips} trips ({r}x return{extra})"

def calculate_transit_metrics(distance_meters, vehicle_type="sedan", trips=1):
    trips       = max(1, min(10, int(trips)))
    distance_km = (distance_meters / 1000) * trips
    rate        = CONSUMPTION_RATES.get(vehicle_type, 7.5)
    liters_used = (distance_km / 100) * rate
    cost_zar    = liters_used * FUEL_PRICE_ZAR
    return {
        "distance_km": round(distance_km, 2),
        "liters_used": round(liters_used, 2),
        "cost_zar":    round(cost_zar,    2),
        "trips":       trips,
        "trip_label":  trip_label(trips),
    }
