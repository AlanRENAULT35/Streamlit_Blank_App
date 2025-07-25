import streamlit as st
import numpy as np
from typing import Any

st.write("Animation Page for Streamlit")

# Interactive Streamlit elements, like these sliders, return their value.
# This gives you an extremely simple interaction model.
iterations = st.sidebar.slider("Level of detail", 2, 20, 10, 1)
separation = st.sidebar.slider("Separation", 0.7, 2.0, 0.7885)

# Non-interactive elements return a placeholder to their location
# in the app. Here we're storing progress_bar to update it later.
progress_bar = st.sidebar.progress(0)

# These two elements will be filled in later, so we create a placeholder
# for them using st.empty()
frame_text = st.sidebar.empty()
image = st.empty()

m, n, s = 960, 640, 400
x = np.linspace(-m / s, m / s, num=m).reshape((1, m))
y = np.linspace(-n / s, n / s, num=n).reshape((n, 1))

for frame_num, a in enumerate(np.linspace(0.0, 4 * np.pi, 100)):
    # Here were setting value for these two elements.
    progress_bar.progress(frame_num)
    frame_text.text(f"Frame {frame_num + 1}/100")

    # Performing some fractal wizardry.
    c = separation * np.exp(1j * a)
    z = np.tile(x, (n, 1)) + 1j * np.tile(y, (1, m))
    c_matrix = np.full((n, m), c)
    m_matrix: Any = np.full((n, m), True, dtype=bool)
    n_matrix = np.zeros((n, m))

    for i in range(iterations):
        z[m_matrix] = z[m_matrix] * z[m_matrix] + c_matrix[m_matrix]
        m_matrix[np.abs(z) > 2] = False
        n_matrix[m_matrix] = i

    # Update the image placeholder by calling the image() function on it.
    image.image(1.0 - (n_matrix / n_matrix.max()), use_container_width=True)

# We clear elements by calling empty on them.
progress_bar.empty()
frame_text.empty()

# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Rerun")