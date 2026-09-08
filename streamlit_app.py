import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:8000/predict/"


# ============================================================
# INTERFACE
# ============================================================

st.set_page_config(
    page_title="ObRail Europe - Prédiction",
    page_icon="🚆",
    layout="centered"
)

st.title("🚆 ObRail Europe")
st.subheader("Prédiction de la durée théorique d'un trajet")

st.write(
    "Entrez les caractéristiques du trajet pour obtenir "
    "une estimation de sa durée."
)


# ============================================================
# FORMULAIRE
# ============================================================

with st.form("prediction_form"):

    route_id = st.text_input(
        "Route ID",
        value="FR:Line::19ea029b-6782-421a-8481-7470f5718e47:"
    )

    agency_id = st.text_input(
        "Agency ID",
        value="1187"
    )

    route_type = st.number_input(
        "Route type",
        min_value=0,
        step=1,
        value=2
    )

    direction_id = st.text_input(
        "Direction ID",
        value="0"
    )

    origin_stop_id = st.text_input(
        "Gare / arrêt de départ",
        value="StopPoint:OCECar TER-87141002"
    )

    destination_stop_id = st.text_input(
        "Gare / arrêt d'arrivée",
        value="StopPoint:OCECar TER-87613463"
    )

    n_stops = st.number_input(
        "Nombre d'arrêts",
        min_value=1,
        step=1,
        value=8
    )

    departure_hour = st.number_input(
        "Heure de départ",
        min_value=0,
        max_value=23,
        step=1,
        value=14
    )

    departure_minute = st.number_input(
        "Minute de départ",
        min_value=0,
        max_value=59,
        step=1,
        value=30
    )

    distance_km = st.number_input(
        "Distance (km)",
        min_value=0.0,
        step=0.1,
        value=75.9
    )

    submitted = st.form_submit_button(
        "🔮 Prédire la durée"
    )


# ============================================================
# APPEL DE L'API
# ============================================================

if submitted:

    payload = {
        "route_id": route_id,
        "agency_id": agency_id,
        "route_type": route_type,
        "direction_id": direction_id,
        "origin_stop_id": origin_stop_id,
        "destination_stop_id": destination_stop_id,
        "n_stops": n_stops,
        "departure_hour": departure_hour,
        "departure_minute": departure_minute,
        "distance_km": distance_km
    }

    try:

        response = requests.post(
            API_URL,
            json=payload,
            timeout=10
        )

        if response.status_code == 200:

            result = response.json()

            duration = result[
                "predicted_duration_minutes"
            ]

            hours = int(duration // 60)
            minutes = round(duration % 60)

            st.success("Prédiction réalisée avec succès !")

            st.metric(
                "Durée théorique prédite",
                f"{duration:.2f} min"
            )

            if hours > 0:
                st.info(
                    f"≈ {hours} h {minutes:02d}"
                )

        else:

            st.error(
                f"Erreur API ({response.status_code})"
            )

            st.json(response.json())

    except requests.exceptions.ConnectionError:

        st.error(
            "Impossible de contacter l'API FastAPI. "
            "Vérifiez qu'elle est bien démarrée."
        )

    except requests.exceptions.Timeout:

        st.error(
            "L'API n'a pas répondu dans le délai prévu."
        )

    except Exception as e:

        st.error(
            f"Une erreur est survenue : {str(e)}"
        )