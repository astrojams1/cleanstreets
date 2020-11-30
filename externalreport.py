"""
Clean Streets LLC
by James Thompson
on 11/28/2020

BLUF: A monthly business update of Clean Streets built in Streamlit.
"""

import streamlit as st
import numpy as np
import pandas as pd

"""
# 🧹 Clean Streets Monthly
### December 2020
Starting this month I'm providing more detailed reporting on Clean Streets' activities in the neighborhood. This is meant to provide you a clearer picture of our impact. Please let me know how I can make this information clearer!
#### Average Contribution:
"""

avg_contribution = 715/28
avg_contribution

"""
#### Operational Efficiency:
"""
operational_efficiency = 100
operational_efficiency

df = pd.DataFrame({
  'Month': ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'],
  'Miles Serviced Weekly': [5000/5280, 5000/5280, 5000/5280, 7250/5280, 9250/5280, 10750/5280],
  'Patrons': [6, 8, 11, 20, 25, 28],
  'Operational Efficiency': [100, 100, 100, 100, 100, 100],
})

df

st.write("### Amount Cleaned Per Week")
st.write("How many feet of sidewalk get cleaned by Clean Streets weekly?")

chart_data = pd.DataFrame(
     [[1,1,1],[2,2,2]],
     columns=['a', 'b', 'c'])

st.bar_chart(chart_data)

st.write("### Revenue v Expenses")
st.write("What percent of revenue is paid to workers to clean streets?")

chart_data = pd.DataFrame(
     np.random.randn(20, 3),
     columns=['a', 'b', 'c'])

st.line_chart(chart_data)

st.write("## Coverage")

col1, col2, col3 = st.beta_columns(3)

with col1:
    st.header("A cat")
    st.image("https://static.streamlit.io/examples/cat.jpg", use_column_width=True)

with col2:
    st.header("A dog")
    st.image("https://static.streamlit.io/examples/dog.jpg", use_column_width=True)

with col3:
    st.header("An owl")
    st.image("https://static.streamlit.io/examples/owl.jpg", use_column_width=True)

st.write("### Blob 1")

map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [5000, 5000] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.map(map_data)

st.write("### Blob 2")

map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [500, 500] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.map(map_data)

st.write("### Blob 3")

map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50000, 50000] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.map(map_data)
