"""
Clean Streets LLC
by James Thompson
on 11/28/2020

BLUF: A monthly business update of Clean Streets built in Streamlit.
"""

import streamlit as st
import secrets_beta
from gsheetsdb import connect
import numpy as np
import pandas as pd

# beep beep beep beep
sheet = st.secrets["sheets_URL"]
conn = connect()
result = conn.execute(f"""
    SELECT
        month
      , cumulative_patrons
      , feet_serviced_weekly
      , total_pledged
      , operational_efficiency
      , patrons_pledge_less_than_10
      , patrons_pledge_between_10_and_24
      , patrons_pledge_25_or_more
    FROM
        "{sheet}"
    GROUP BY
        month
""", headers=1)

mile = 5280

months = []
patrons = []
weekly_miles = []
revenue = []
opperational_efficiency = []
patrons_pledge_distro = []

for row in result:
    months.append(row[0])
    patrons.append(row[1])
    weekly_miles.append(row[2]/mile)
    revenue.append(row[3])
    opperational_efficiency.append(row[4])
    patrons_pledge_distro.append([row[5], row[6], row[7]])

# Header
st.image("reports/jan2021_header.png", use_column_width=True)

# Introduction
st.title("Clean Streets — Jan 2021")
"""
**Our Mission:** To reshape San Francisco into the cleanest city in the world by organizing members of the community to sponsor recurring litter pickup on the blocks that need it most.
"""
"""
**How to Help:** Helping us grow our patrons is still the best way to support our work. Please become a patron and help others become patrons as well. More details at [www.cleanstreets.io](https://www.cleanstreets.io).
"""
"""
Happy New Year! I feel so happy to bring Clean Streets into its second (calendar year) and seventh month of operation. I have learned so much these last 7 months, and look forward to building on all that we have created together, to shape Clean Streets to be as effective and pro-worker as possible.
"""

st.header("Metrics")

# Patron contribution average and distro.
avg_payment = round(revenue[-1] / patrons[-1], 2)
st.write("### Our " + str(int(patrons[-1])) + " patrons contribute an average of $" + str(avg_payment) + " monthly.")
st.write("Number of patrons contributing at different levels:")
st.write("""
    - **A** - Less than $10
    - **B** - Between $10 and $24
    - **C** - $25 or more
""")

chart_data = pd.DataFrame(
     patrons_pledge_distro[-1],
     columns=['# Patrons'],
     index=['A', 'B', 'C'])

st.bar_chart(chart_data)

# Patron count
new_patrons = int(patrons[-1] - patrons[-2])

if new_patrons > 0:
    st.write("### Clean Streets gained another " + str(new_patrons) + " patrons last month!")
elif new_patrons < 0:
    st.write("### Clean Streets lost " + str(new_patrons) + " patrons last month.")
else:
    st.write("### Clean Streets still has " + str(new_patrons) + " patrons.")
st.write("The chart below shows our patron growth over time.")

chart_data = pd.DataFrame(
     patrons,
     columns=['# Patrons'],
     index=months)

st.area_chart(chart_data)

# Service area
st.write("### Clean Streets now services " + str(round(weekly_miles[-1],2)) + " miles of sidewalk each week.")
chart_data = pd.DataFrame(
     weekly_miles,
     columns=['Miles'],
     index=months)

st.area_chart(chart_data)

# Operational efficency
st.write("### Clean Streets continues to operate at " + str(int(opperational_efficiency[-1])) + "% efficiency.")
st.write("This means that " + str(int(opperational_efficiency[-1])) + "% of patrons' contributions funds litter pickup.")

chart_data = pd.DataFrame(
     opperational_efficiency,
     columns=['Efficiency'],
     index=months)

st.line_chart(chart_data)
