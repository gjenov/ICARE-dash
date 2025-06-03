# ICARE-dash

```
This repo uses video and truth labels from the ICARE dataset at UC Davis Medical School, courtesy of Professor Weakley
```
## smart_home_dashboard.py
Streamlit Dashboard using annotated .xlsx sheets
Ensure your environment supports:
- Cv2
- Streamlit
- Altair
To add pages, modify after line 161 and add a st.session_state.page
Modify filename local to session state to access different .xlsx

Annotated sheets can be obtained from spread_annotation.ipynb


## spread_annotation.ipynb
This application uses Yolov11 and rule based activity recognition to annotate actions and populate a spreadsheet.

Modify video_path, excel_file and start time, specific to your current video.

test_boxes and room_names define location and name of rooms
action_boxes and action_names define action location and name

modify: room_buffer_threshold and buffer_frames_threshold to make the algorithm more or less sensitive. More frames on both decrease sensitivity. 60 frames is a good starting point

## spreadsheet_GUI.ipynb
Takes a .xlsx as an input to generate a historical GUI

Application runs in its own python window locally
