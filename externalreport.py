"""
Clean Streets LLC
by James Thompson
on 11/28/2020

BLUF: A monthly business update of Clean Streets built in Streamlit.
"""

import streamlit as st
import numpy as np
import pandas as pd

mile = 5280
patrons = 28
revenue = 715
patrons_6mo = [6, 8, 11, 20, 25, 28]
opp_eff_6mo = [100, 100, 100, 100, 100, 100]
monthly_miles_6mo = np.divide([5000, 5000, 5000, 7250, 9250, 10750], mile)
months = ['1: Jun 2020', '2: Jul 2020', '3: Aug 2020', '4: Sep 2020', '5: Oct 2020', '6: Nov 2020']

st.image("reportheader.png", use_column_width=True)
st.title("Clean Streets — Dec 2020")
"""
**Our Mission:** To reshape San Francisco into the cleanest city in the world by organizing members of the community to sponsor recurring litter pickup on the blocks that need it most.
"""
"""
**How to Help:** Helping us grow our patrons is still the best way to support our work. Please become a patron and help others become patrons as well. More details at [www.cleanstreets.io](https://www.cleanstreets.io).
"""
"""
**🌟 Special Note:** Moving forward, Clean Streets will provide monthly updates on its activities using a new tool that lets me easily assemble data and visualizations to better communicate important changes and trends with the project. I am excited to provide you richer information moving forward, and I look forward to your feedback on this report!
"""

st.header("Metrics")

avg_payment = round(revenue / patrons, 2)
st.write("### Our " + str(patrons) + " patrons each contribute an average of $" + str(avg_payment) + " monthly.")
"""
Number of patrons contributing at different levels:
- **A** - Less than $10
- **B** - Between $10 and $24
- **C** - More than $25
"""

chart_data = pd.DataFrame(
     [4, 15, 9],
     columns=['# Patrons'],
     index=['A', 'B', 'C'])

st.bar_chart(chart_data)

"""
### Clean Streets gained another 3 patrons last month!
The chart below shows our patron growth over time.
"""

chart_data = pd.DataFrame(
     patrons_6mo,
     columns=['# Patrons'],
     index=months)

st.area_chart(chart_data)

"""
### Clean Streets now services over 2 miles of sidewalk each week.
"""
chart_data = pd.DataFrame(
     monthly_miles_6mo,
     columns=['Miles'],
     index=months)

st.area_chart(chart_data)

"""
### Clean Streets continues to operate at 100% efficiency.
This means that 100% of patrons' contributions funds litter pickup.
"""
chart_data = pd.DataFrame(
     opp_eff_6mo,
     columns=['Efficiency'],
     index=months)

st.line_chart(chart_data)
