import streamlit as st
from datetime import datetime
from streamlit_calendar import calendar
import sqlite3
import pandas as pd


current_date = datetime.now()
formatted_date = current_date.strftime("%Y-%m-01")


user_id = st.session_state.user_id


st.set_page_config(page_title="Calendar", layout="wide", page_icon=":calendar:")


st.markdown(
    """
    <style>
    .header {
        text-align: center;
        color: #eaeaea;
        font-size: 40px !important;
        font-weight: bold;
        margin-bottom: 30px;}
    </style>
    """, unsafe_allow_html=True
)

st.markdown("<h1 class='header'>Calendar</h1>", unsafe_allow_html=True)


def fetch_calendar_events():
    """
    Retrieve calendar events from the database.

    Returns:
        events: A list of dictionaries containing calendar events.
    """
    conn = sqlite3.connect("BeAlive/data/database/BeAlive.db")
    query = """
   SELECT a.activity_name as activity,
          a.date_begin as start,
          a.date_finish as end,
          a.location as location
    FROM reservations r JOIN activities a
         ON
         a.activity_id = r.activity_id
    WHERE
        r.state = "confirmed" and
        r.user_id = ?

    UNION

    SELECT a.activity_name as activity,
           a.date_begin as start,
           a.date_finish as end,
           a.location as location
    FROM activities a
    WHERE a.host_id = ?
    """

    df = pd.read_sql_query(query, conn, params=(user_id, user_id))
    conn.close()

    # Format the events to match calendar expectations
    events = []
    for index, row in df.iterrows():
        event = {
            "title": row["activity"] + ", " + row["location"],  # This will display as the title of the event
            "start": row["start"],  # Event start date/time
            "end": row["end"],  # Event end date/time
        }
        events.append(event)

    return events


calendar_options = {
    "editable": "true",
    "navLinks": "true",
    "selectable": "true",
}


# Calendar options
calendar_options = {
    "initialView": "dayGridMonth",
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay"
    },
    "events": fetch_calendar_events(),
    "selectable": True,
}

mode = st.selectbox(
    "Calendar Mode:",
    (
        "daygrid",
        "timegrid",
        "timeline",
        "list",
        "multimonth",
    ), help="Select the calendar mode"
)

if mode == "daygrid":
    calendar_options = {
            **calendar_options,
            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "dayGridDay,dayGridWeek,dayGridMonth",
            },
            "initialDate": formatted_date,
            "initialView": "dayGridMonth",
        }

elif mode == "timegrid":
    calendar_options = {
            **calendar_options,
            "initialView": "timeGridWeek",
     }

elif mode == "timeline":
    calendar_options = {
            **calendar_options,
            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "timelineDay,timelineWeek,timelineMonth",
            },
            "initialDate": formatted_date,
            "initialView": "timelineMonth",
        }

elif mode == "list":
    calendar_options = {
            **calendar_options,
            "initialDate": formatted_date,
            "initialView": "listMonth",
        }
elif mode == "multimonth":
    calendar_options = {
            **calendar_options,
            "initialView": "multiMonthYear",
        }

state = calendar(
    events=st.session_state.get("events", fetch_calendar_events()),
    options=calendar_options)
