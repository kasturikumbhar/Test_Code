import pandas as pd
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import os
import pdfkit

# Load your CSV file
df = pd.read_csv('your_data.csv')  # Replace with actual file path

amount_cols = ['amount_1', 'amount_2']  # Adjust as per your columns
group_cols = ['settlement_currency', 'presentment_currency']
group_unit_cols = ['unit_name', 'unit_id']

user_info = {
    'name': 'John Doe',
    'address': '123 Street Name, City, Country',
    'telephone': '+1234567890',
    'email': 'john.doe@example.com'
}

def insert_subtotals(df, amount_cols):
    df = df.copy()
    df['is_subtotal'] = False
    subtotal_row = {col: '' for col in df.columns}
    for col in amount_cols:
        subtotal_row[col] = df[col].sum()
    subtotal_row['is_subtotal'] = True
    return pd.concat([df, pd.DataFrame([subtotal_row])], ignore_index=True)

sections = []
max_col_count = 0
for (unit_name, unit_id), unit_df in df.groupby(group_unit_cols):
    currency_groups = []
    for (settlement, presentment), pair_df in unit_df.groupby(group_cols):
        table_df = pair_df.drop(columns=group_cols)
        subtotal_df = insert_subtotals(table_df, amount_cols)
        cols = [col for col in subtotal_df.columns if col != 'is_subtotal']
        max_col_count = max(max_col_count, len(cols))
        currency_groups.append({
            'currency_pair': f"{settlement} - {presentment}",
            'date_range': '2024-01-01 to 2024-12-31',  # Placeholder
            'columns': cols,
            'data': subtotal_df.fillna('').to_dict(orient='records')
        })
    sections.append({
        'unit_name': unit_name,
        'unit_id': unit_id,
        'report_name': 'Currency Pair Report',
        'report_date': datetime.now().strftime('%Y-%m-%d'),
        'currency_groups': currency_groups
    })

# Determine paper size
if max_col_count <= 10:
    paper_size = 'A4'
    orientation = 'Portrait'
elif max_col_count <= 18:
    paper_size = 'A3'
    orientation = 'Landscape'
else:
    paper_size = 'A3'
    orientation = 'Landscape'

# Render HTML
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('report_with_header_each_page.html')
rendered_html = template.render(sections=sections, user_info=user_info, generation_date=datetime.now().strftime('%Y-%m-%d'))

with open('rendered_currency_pair_report.html', 'w') as f:
    f.write(rendered_html)

# PDF Generation
config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')  # Adjust path as needed
options = {
    'page-size': paper_size,
    'orientation': orientation,
    'enable-local-file-access': '',
    'margin-top': '20mm',
    'margin-right': '10mm',
    'margin-bottom': '20mm',
    'margin-left': '10mm',
    'footer-right': 'Page [page] of [topage]',
    'footer-font-size': '8',
    'footer-spacing': '5'
}
pdfkit.from_file('rendered_currency_pair_report.html', 'currency_pair_report.pdf', configuration=config, options=options)
