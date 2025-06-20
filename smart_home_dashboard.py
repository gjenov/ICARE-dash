# Smart Home GUI Playback Streamlit App

#Usage:
#python -m streamlit run smart_home_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import cv2
from datetime import datetime, timedelta
from PIL import Image

import altair as alt

#not necessary, changes to wide
st.set_page_config(layout="wide", page_title="Smart Home GUI", initial_sidebar_state="collapsed")
# open sheet
filename = "Arveen_2_sheet.xlsx"
df = pd.read_excel(filename)
#df['Time'] = pd.to_datetime(df['Time'], format="%H:%M:%S")

#bathroom visits, move elsewhere
bathroom_visits = (df['Activity'].str.contains('Entered Bathroom')).sum()


#fix this, hard coded
st.sidebar.header("Patients: ")




# Draw the overlay (house map)
def draw_overlay(current_room, current_action, previous_action_overlay, time_str=None):
    overlay_width, overlay_height = 600, 400
    overlay = np.ones((overlay_height, overlay_width, 3), dtype=np.uint8) * 27  # white background

    # Define room areas
    rooms = {
        "Kitchen": (100, 200, 100, 160),
        "Bathroom": (100, 100, 100, 100),
        "Bedroom": (200, 100, 200, 100),
        "Living Room": (400, 100, 100, 260),
    }

    # Define action areas
    actions = {
        "Fridge": (101, 270, 25, 25),
        "Laying on Bed": (270, 101, 60, 60),
        "Sink": (169, 130, 30, 40),
        "Couch": (469, 200, 30, 80),
        "Drawer": (245, 101, 25, 25),
        "Dresser": (201, 101, 20, 50),
        "Cupboard": (120, 339, 60, 20),
        "Table": (160, 235, 40, 40),
    }

    # Draw rooms
    for room_name, (x, y, w, h) in rooms.items():
        color = (154, 205, 50)  # light green
        thickness = -1  
        if room_name == current_room:
            color = (0, 165, 255)  # orange 
            thickness = -1
        cv2.rectangle(overlay, (x, y), (x + w, y + h), color, thickness)
        if room_name == current_room:

            cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 0, 255), 3)  # red 
        cv2.putText(overlay, room_name, (x + 5, y + h - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (80, 80, 80), 1)

    # Draw actions
    for action_name, (x, y, w, h) in actions.items():
        color = (128, 128, 128)  # gray
        thickness = -1
        if action_name == current_action:
            color = (0, 255, 255)  # yellow
        if action_name == previous_action_overlay:
            color = (0, 120, 120) 
        cv2.rectangle(overlay, (x, y), (x + w, y + h), color, thickness)
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 0, 0), 1)  

    # time print
    if time_str:
        cv2.putText(overlay, f"Time: {time_str}", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

    return overlay
    
def timeSpent(filename):
    activityLog = {}
    df = pd.read_excel(filename)
    action_stack = {}
    total_duration = {}
    for rowindex, row in df.iterrows():
        action = row['Activity']
        duration = datetime.strptime(str(row['Time']), "%H:%M:%S")
        #We have room trans and Action
        if action.startswith("Entered"): #beginning of room trans
            name = action.replace("Entered ", "")
            action_stack[name] = duration

        elif action.startswith("Left"): #end of room trans
            #log time and clear stack of that action
            name = action.replace("Left ", "")
            if name in action_stack:
                duration = duration - action_stack[name]
                total_duration[name] = total_duration.get(name, timedelta()) + duration
                del action_stack[name]
        #coarse grain actions
        elif action.startswith("Started"):
            name = action.replace("Started ", "")
            action_stack[name] = duration
        elif action.startswith("Stopped"):
            name = action.replace("Stopped ", "")
            if name in action_stack:
                duration = duration - action_stack[name]
                total_duration[name] = total_duration.get(name, timedelta()) + duration
                del action_stack[name]

    for name, time in total_duration.items():
        minutes = int(time.total_seconds() // 60)
        seconds = int(time.total_seconds() % 60)
        activityLog[name] = f"{minutes:02}:{seconds:02}"

    return activityLog


# --- Streamlit Frontend ---

st.title("Smart Home Dashboard")

leftCol, rightCol = st.columns(2)

def highlight_selected_row(x):
    df = x.copy()
    df.loc[:, :] = ''
    df.loc[index, :] = 'background-color: #3a3a3a; font-weight: bold' #highlights in grey over idx
    return df

#df function
###

# ###{'Living': '03:37', 'Fridge': '00:19', 'Kitchen': '02:15', 'Sink': '00:19', 'Bathroom': '04:15', 'Bedroom': '00:13'}
def graphConvert(data, activityLog, name):

    for entries, times in activityLog.items():
        minutes, seconds = map(int, times.split(':'))
        totaltime = minutes * 60 + seconds
        data['Video'].append(name)
        data['Room'].append(entries)
        data['Seconds'].append(totaltime)

    return data



#default
if 'page' not in st.session_state:
    st.session_state.page = 'Arveen 2'  

#sidebard select
with st.sidebar:
    if st.button("Overview"):
        st.session_state.page = 'Overview'
    if st.button("Arveen 2"):
        st.session_state.page = 'Arveen 2'
    if st.button("Arveen 3"):
        st.session_state.page = 'Arveen 3'
    if st.button("Arveen 4"):
        st.session_state.page = 'Arveen 4'
    if st.button("Arveen 5"):
        st.session_state.page = 'Arveen 5'


#All pages, navigate on left bar
if st.session_state.page == 'Overview':
    data = {
        'Video' : [],
        'Room' : [],
        'Seconds' : []
    }
    filename = "Arveen_1_sheet.xlsx"
    name = filename.split("_sheet")[0]
    activityLog = timeSpent(filename)
    data = graphConvert(data, activityLog, "1")

    filename = "Arveen_2_sheet.xlsx"
    name = filename.split("_sheet")[0]
    activityLog = timeSpent(filename)
    data = graphConvert(data, activityLog, "2")

    filename = "Arveen_3_sheet.xlsx"
    name = filename.split("_sheet")[0]
    activityLog = timeSpent(filename)
    data = graphConvert(data, activityLog, "3")

    filename = "Arveen_4_sheet.xlsx"
    name = filename.split("_sheet")[0]
    activityLog = timeSpent(filename)
    data = graphConvert(data, activityLog, "4")

    filename = "Arveen_5_sheet.xlsx"
    name = filename.split("_sheet")[0]
    activityLog = timeSpent(filename)
    data = graphConvert(data, activityLog, "5")

    filename = "Arveen_6_sheet.xlsx"
    name = filename.split("_sheet")[0]
    activityLog = timeSpent(filename)
    data = graphConvert(data, activityLog, "6")

    filename = "Arveen_7_sheet.xlsx"
    name = filename.split("_sheet")[0]
    activityLog = timeSpent(filename)
    data = graphConvert(data, activityLog, "7")

    filename = "Arveen_8_sheet.xlsx"
    name = filename.split("_sheet")[0]
    activityLog = timeSpent(filename)
    data = graphConvert(data, activityLog, "8")

    df = pd.DataFrame(data)

    # Create a stacked bar chart
    chart = alt.Chart(df).mark_bar().encode(
        x='Video:N',                 # X-axis = Videos
        y='Seconds:Q',              # Y-axis = Seconds
        color='Room:N',             # Different colors by room
        tooltip=['Room', 'Seconds'] # Tooltip shows details on hover
    ).properties(
        width=600,
        height=400,
        title='Time Spent in Rooms Over Days'
    )

    #Display  graph in streamlit
    st.altair_chart(chart, use_container_width=False)

    text = timeSpent(filename)


    

if st.session_state.page == 'Arveen 2':
        
    with rightCol:
        # Scrollbar
        st.header("GUI")
        index = st.slider("", min_value=0, max_value=len(df)-1, value=0, step=1)

        current_room = None
        current_action = None
        previous_action = None

        # Current room logic
        for i in range(index + 1):
            action = df.loc[i, 'Activity']
            time_str = df.loc[i, 'Time']

            if action.startswith("Entered"):
                current_room = action.replace("Entered ", "")
            elif action.startswith("Left"):
                current_room = None
            elif action.startswith("started"):
                previous_action = current_action
                current_action = action.replace("started ", "")
            elif action.startswith("stopped"):
                previous_action = current_action
                current_action = None

        # GUI display
        frame = draw_overlay(current_room, current_action, previous_action, time_str)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        st.image(Image.fromarray(frame_rgb),  use_container_width=False)  # fixed warning

        st.subheader(f"Event: {action}")
    with leftCol:
        #snapshot of the data
        st.header("Activity Log")
        st.dataframe(df[['Time', 'Activity']].style.apply(highlight_selected_row, axis=None), use_container_width=True)

    st.divider()

    with st.container():
        st.header("Important Metrics")

        data = {
            'Day' : [],
            'Room' : [],
            'Minutes' : []
        }
        filename = "Arveen_2_sheet.xlsx"
        name = filename.split("_sheet")[0]
        activityLog = timeSpent(filename)
        data = graphConvert(data, activityLog, name)

        df = pd.DataFrame(data)

            # Create a stacked bar chart
        chart = alt.Chart(df).mark_bar().encode(
            x='Video:N',                 # X-axis = days (categorical)
            y='Seconds:Q',              # Y-axis = minutes (quantitative)
            color='Room:N',             # Different colors by room
            tooltip=['Room', 'Minutes'] # Tooltip shows details on hover
        ).properties(
            width=600,
            height=400,
            title='Time Spent in Rooms Over Days'
        )

        # Show it in Streamlit
        st.altair_chart(chart, use_container_width=False)

        text = timeSpent(filename)
        
        timedf = pd.DataFrame(list(text.items()), columns=["Location", "Time Spent"])
        st.dataframe(timedf)
        st.text(f"Bathroom Visits: {bathroom_visits}")

        #st.text(text)
    

#repeat for each additional page
elif st.session_state.page == "Arveen 3":
        # Streamlit page settings
    #st.set_page_config(layout="wide", page_title="Smart Home GUI", initial_sidebar_state="collapsed")

    # Load Data
    filename = "Arveen_3_sheet.xlsx"
    df = pd.read_excel(filename)
    #df['Time'] = pd.to_datetime(df['Time'], format="%H:%M:%S")

    # Calculate bathroom visits
    bathroom_visits = (df['Activity'].str.contains('Entered Bathroom')).sum()
    kitchen_visits = (df['Activity'].str.contains('Entered Kitchen')).sum()

    # Display on dashboard
    #fix this, hard coded
    #st.sidebar.header(filename.split("_s")[0])
    #st.sidebar.metric("Bathroom Visits", bathroom_visits)

    with rightCol:
        # Scrollbar to move through events
        st.header("GUI")
        index = st.slider("", min_value=0, max_value=len(df)-1, value=0, step=1)

        current_room = None
        current_action = None
        previous_action = None

        # Figure out what the current room/action is based on index
        for i in range(index + 1):
            action = df.loc[i, 'Activity']
            time_str = df.loc[i, 'Time']

            if action.startswith("Entered"):
                current_room = action.replace("Entered ", "")
            elif action.startswith("Left"):
                current_room = None
            elif action.startswith("started"):
                previous_action = current_action
                current_action = action.replace("started ", "")
            elif action.startswith("stopped"):
                previous_action = current_action
                current_action = None

        # Draw the current frame
        frame = draw_overlay(current_room, current_action, previous_action, time_str)

        # Convert BGR to RGB for Streamlit
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Show the image
        st.image(Image.fromarray(frame_rgb),  use_container_width=False)  # fixed warning

        # Add the Event Text Below
        st.subheader(f"Event: {action}")
    with leftCol:
        #snapshot of the data
        st.header("Activity Log")
        st.dataframe(df[['Time', 'Activity']].style.apply(highlight_selected_row, axis=None), use_container_width=True)

    st.divider()

    with st.container():
        st.header("Important Metrics")

        data = {
            'Video' : [],
            'Room' : [],
            'Seconds' : []
        }
        name = filename.split("_sheet")[0]
        activityLog = timeSpent(filename)
        data = graphConvert(data, activityLog, name)

        df = pd.DataFrame(data)

            # Create a stacked bar chart
        chart = alt.Chart(df).mark_bar().encode(
            x='Video:N',                 # X-axis = days (categorical)
            y='Seconds:Q',              # Y-axis = minutes (quantitative)
            color='Room:N',             # Different colors by room
            tooltip=['Room', 'Seconds'] # Tooltip shows details on hover
        ).properties(
            width=600,
            height=400,
            title='Time Spent in Rooms Over Days'
        )

        # Show it in Streamlit
        st.altair_chart(chart, use_container_width=False)

        text = timeSpent(filename)
        
        timedf = pd.DataFrame(list(text.items()), columns=["Location", "Time Spent"])
        st.dataframe(timedf)
        
        st.text(f"Kitchen Visits: {kitchen_visits}")
        st.text(f"Bathroom Visits: {bathroom_visits}")

        #st.text(text)

elif st.session_state.page == "Arveen 4":
        # Streamlit page settings
    #st.set_page_config(layout="wide", page_title="Smart Home GUI", initial_sidebar_state="collapsed")

    # Load Data
    filename = "Arveen_4_sheet.xlsx"
    df = pd.read_excel(filename)
    #df['Time'] = pd.to_datetime(df['Time'], format="%H:%M:%S")

    # Calculate bathroom visits
    bathroom_visits = (df['Activity'].str.contains('Entered Bathroom')).sum()

    # Display on dashboard
    #fix this, hard coded
    #st.sidebar.header(filename.split("_s")[0])
    #st.sidebar.metric("Bathroom Visits", bathroom_visits)

    with rightCol:
        # Scrollbar to move through events
        st.header("GUI")
        index = st.slider("", min_value=0, max_value=len(df)-1, value=0, step=1)

        current_room = None
        current_action = None
        previous_action = None

        # Figure out what the current room/action is based on index
        for i in range(index + 1):
            action = df.loc[i, 'Activity']
            time_str = df.loc[i, 'Time']

            if action.startswith("Entered"):
                current_room = action.replace("Entered ", "")
            elif action.startswith("Left"):
                current_room = None
            elif action.startswith("started"):
                previous_action = current_action
                current_action = action.replace("started ", "")
            elif action.startswith("stopped"):
                previous_action = current_action
                current_action = None

        # Draw the current frame
        frame = draw_overlay(current_room, current_action, previous_action, time_str)

        # Convert BGR to RGB for Streamlit
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Show the image
        st.image(Image.fromarray(frame_rgb),  use_container_width=False)  # fixed warning

        # Add the Event Text Below
        st.subheader(f"Event: {action}")
    with leftCol:
        #snapshot of the data
        st.header("Activity Log")
        st.dataframe(df[['Time', 'Activity']].style.apply(highlight_selected_row, axis=None), use_container_width=True)

    st.divider()

    with st.container():
        st.header("Important Metrics")

        data = {
            'Day' : [],
            'Room' : [],
            'Minutes' : []
        }
        name = filename.split("_sheet")[0]
        activityLog = timeSpent(filename)
        data = graphConvert(data, activityLog, name)

        df = pd.DataFrame(data)

            # Create a stacked bar chart
        chart = alt.Chart(df).mark_bar().encode(
            x='Day:N',                 # X-axis = days (categorical)
            y='Minutes:Q',              # Y-axis = minutes (quantitative)
            color='Room:N',             # Different colors by room
            tooltip=['Room', 'Minutes'] # Tooltip shows details on hover
        ).properties(
            width=600,
            height=400,
            title='Time Spent in Rooms Over Days'
        )

        # Show it in Streamlit
        st.altair_chart(chart, use_container_width=False)

        text = timeSpent(filename)
        
        timedf = pd.DataFrame(list(text.items()), columns=["Location", "Time Spent"])
        st.dataframe(timedf)
        st.text(f"Bathroom Visits: {bathroom_visits}")

        #st.text(text)


elif st.session_state.page == "Arveen 5":
        # Streamlit page settings
    #st.set_page_config(layout="wide", page_title="Smart Home GUI", initial_sidebar_state="collapsed")

    # Load Data
    filename = "Arveen_5_sheet.xlsx"
    df = pd.read_excel(filename)
    #df['Time'] = pd.to_datetime(df['Time'], format="%H:%M:%S")

    # Calculate bathroom visits
    bathroom_visits = (df['Activity'].str.contains('Entered Bathroom')).sum()

    # Display on dashboard
    #fix this, hard coded
    #st.sidebar.header(filename.split("_s")[0])
    #st.sidebar.metric("Bathroom Visits", bathroom_visits)

    with rightCol:
        # Scrollbar to move through events
        st.header("GUI")
        index = st.slider("", min_value=0, max_value=len(df)-1, value=0, step=1)

        current_room = None
        current_action = None
        previous_action = None

        # Figure out what the current room/action is based on index
        for i in range(index + 1):
            action = df.loc[i, 'Activity']
            time_str = df.loc[i, 'Time']

            if action.startswith("Entered"):
                current_room = action.replace("Entered ", "")
            elif action.startswith("Left"):
                current_room = None
            elif action.startswith("started"):
                previous_action = current_action
                current_action = action.replace("started ", "")
            elif action.startswith("stopped"):
                previous_action = current_action
                current_action = None

        # Draw the current frame
        frame = draw_overlay(current_room, current_action, previous_action, time_str)

        # Convert BGR to RGB for Streamlit
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Show the image
        st.image(Image.fromarray(frame_rgb),  use_container_width=False)  # fixed warning

        # Add the Event Text Below
        st.subheader(f"Event: {action}")
    with leftCol:
        #snapshot of the data
        st.header("Activity Log")
        st.dataframe(df[['Time', 'Activity']].style.apply(highlight_selected_row, axis=None), use_container_width=True)

    st.divider()

    with st.container():
        st.header("Important Metrics")

        data = {
            'Day' : [],
            'Room' : [],
            'Minutes' : []
        }
        name = filename.split("_sheet")[0]
        activityLog = timeSpent(filename)
        data = graphConvert(data, activityLog, name)

        df = pd.DataFrame(data)

            # Create a stacked bar chart
        chart = alt.Chart(df).mark_bar().encode(
            x='Day:N',                 # X-axis = days (categorical)
            y='Minutes:Q',              # Y-axis = minutes (quantitative)
            color='Room:N',             # Different colors by room
            tooltip=['Room', 'Minutes'] # Tooltip shows details on hover
        ).properties(
            width=600,
            height=400,
            title='Time Spent in Rooms Over Days'
        )

        # Show it in Streamlit
        st.altair_chart(chart, use_container_width=False)

        text = timeSpent(filename)
        
        timedf = pd.DataFrame(list(text.items()), columns=["Location", "Time Spent"])
        st.dataframe(timedf)
        st.text(f"Bathroom Visits: {bathroom_visits}")

        #st.text(text)