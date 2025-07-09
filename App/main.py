import streamlit as st

# CHEMINS D'ACCÈS AUX PAGES
# This file is the main entry point for the Streamlit application.
basePath = "root/pages/"

demosPath = basePath + "demos/"
exercisesPath = basePath + "exercises/"

# NAVIGATION
# The navigation structure of the application is defined here.

pg = st.navigation({
    "Demos": [
        # DEMOS
        st.Page(demosPath + "animation.py", title="Animation", icon=":material/animation:"),
        st.Page(demosPath + "dataFrame.py", title="DataFrame", icon=":material/data_table:"),
        st.Page(demosPath + "mapping.py", title="Mapping", icon=":material/map:"),
        st.Page(demosPath + "plotting.py", title="Plotting", icon=":material/show_chart:"),
    ],
    "Exercises": [
        # BASE
        st.Page(exercisesPath + "base.py", title="Home", icon=":material/home:"),
        st.Page(exercisesPath + "openai-chatbot.py", title="openai-chatbot"),
        st.Page(exercisesPath + "openai-image.py", title="openai-image"),

        # st.Page(exercisesPath + "about.py", title="About", icon=":material/info:"),
        # st.Page(exercisesPath + "contact.py", title="Contact", icon=":material/contact_mail:"),
        
        # # SETTINGS
        # st.Page(exercisesPath + "settings.py", title="Settings", icon=":material/settings:"),
        
        # # HELP
        # st.Page(exercisesPath + "help.py", title="Help", icon=":material/help:"),
    ]
}) 

pg.run()
