import csv
import requests
from bs4 import BeautifulSoup
import io
from datetime import datetime
import pytz
import re

# URL of the published Google Sheet CSVs
SUPPORTERS_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSxt3SXANj2NU-2UHlFRHhJLVJOdx1HBVxekMcHtkhAMzwp5E4ftBJ1DPlx7LMelBYd7d800_PmShJi/pub?gid=1418573323&single=true&output=csv"
IMPACT_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSxt3SXANj2NU-2UHlFRHhJLVJOdx1HBVxekMcHtkhAMzwp5E4ftBJ1DPlx7LMelBYd7d800_PmShJi/pub?gid=1437133102&single=true&output=csv"

def fetch_csv(url):
    response = requests.get(url)
    response.raise_for_status()
    return csv.reader(io.StringIO(response.content.decode('utf-8')))

def update_supporters():
    # 1. Fetch and Parse Supporters Data
    csv_reader = fetch_csv(SUPPORTERS_CSV_URL)

    # Skip header
    next(csv_reader, None)

    top_supporters = []
    supporters = []

    for row in csv_reader:
        if not row:
            continue
        if len(row) < 1:
            continue
        name = row[0].strip()
        if not name:
            continue

        is_top = False
        if len(row) >= 2:
            is_top = row[1].strip().upper() == 'TRUE'

        if is_top:
            top_supporters.append(name)
        else:
            supporters.append(name)

    # 2. Fetch and Parse Impact Data
    impact_reader = fetch_csv(IMPACT_CSV_URL)

    # Skip header
    next(impact_reader, None)

    total_hours = 0.0
    total_pounds = 0.0
    total_miles = 0.0

    for row in impact_reader:
        if not row or len(row) < 4:
            continue
        try:
            # Columns: Date, Hours, Pounds, Miles
            total_hours += float(row[1].replace(',', ''))
            total_pounds += float(row[2].replace(',', ''))
            total_miles += float(row[3].replace(',', ''))
        except ValueError:
            continue

    # 3. Update index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Update Top Supporters
    top_list = soup.find('ul', id='top-supporters')
    if top_list:
        top_list.clear()
        for name in top_supporters:
            li = soup.new_tag('li')
            li.string = name
            top_list.append(li)

    # Update Supporters
    supporters_list = soup.find('ul', id='supporters')
    if supporters_list:
        supporters_list.clear()
        for name in supporters:
            li = soup.new_tag('li')
            li.string = name
            supporters_list.append(li)

    # Update Impact Metrics
    impact_hours_span = soup.find('span', id='impact-hours')
    if impact_hours_span:
        impact_hours_span.string = f"{int(total_hours):,}"

    impact_pounds_span = soup.find('span', id='impact-pounds')
    if impact_pounds_span:
        impact_pounds_span.string = f"{int(total_pounds):,}"

    impact_miles_span = soup.find('span', id='impact-miles')
    if impact_miles_span:
        impact_miles_span.string = f"{int(total_miles):,}"

    # Update Last Updated timestamp
    last_updated_p = soup.find('p', id='last-updated')
    if last_updated_p:
        pacific = pytz.timezone('US/Pacific')
        current_date = datetime.now(pacific).strftime("%B %d, %Y")
        last_updated_p.string = f"Last updated: {current_date}"

    # Update years operating
    years_operating_span = soup.find('span', id='years-operating')
    if years_operating_span:
        start_date = datetime(2020, 6, 18)
        years = (datetime.now() - start_date).days / 365.25
        years_operating_span.string = f"{int(years)} years"

    # Update Impact Header Years
    impact_years_span = soup.find('span', id='impact-years')
    if impact_years_span:
        start_date = datetime(2020, 6, 18)
        years = (datetime.now() - start_date).days / 365.25
        impact_years_span.string = f"{int(years)}+ Years"

    # 4. Save the file
    html_output = soup.prettify(formatter="html")
    html_output = html_output.replace('</meta>', '')

    # Post-process regex
    pattern = r'For over\s*<span id="years-operating">\s*(\d+ years)\s*</span>\s*,'
    replacement = r'For over <span id="years-operating">\1</span>,'
    html_output = re.sub(pattern, replacement, html_output)

    # Fix Impact Header spacing
    pattern_impact = r'Celebrating\s*<span id="impact-years">\s*(\d+\+ Years)\s*</span>\s*of Impact'
    replacement_impact = r'Celebrating <span id="impact-years">\1</span> of Impact'
    html_output = re.sub(pattern_impact, replacement_impact, html_output)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_output)

if __name__ == "__main__":
    update_supporters()
