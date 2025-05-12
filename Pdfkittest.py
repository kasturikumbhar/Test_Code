import pandas as pd
from jinja2 import Environment, FileSystemLoader
import pdfkit
from datetime import datetime
import os

# Sample data
data = [
    {'settlement_currency': 'USD', 'presentment_currency': 'EUR', 'amount_1': 100, 'amount_2': 200, 'transaction_type': 'Refund', 'region': 'North America', 'unit_name': 'Unit A', 'unit_id': 'UA001'},
    {'settlement_currency': 'USD', 'presentment_currency': 'EUR', 'amount_1': 150, 'amount_2': 100, 'transaction_type': 'Purchase', 'region': 'Europe', 'unit_name': 'Unit A', 'unit_id': 'UA001'},
    {'settlement_currency': 'GBP', 'presentment_currency': 'INR', 'amount_1': 80, 'amount_2': 60, 'transaction_type': 'Chargeback', 'region': 'Europe', 'unit_name': 'Unit B', 'unit_id': 'UB002'},
    {'settlement_currency': 'GBP', 'presentment_currency': 'INR', 'amount_1': 70, 'amount_2': 40, 'transaction_type': 'Purchase', 'region': 'Asia', 'unit_name': 'Unit B', 'unit_id': 'UB002'}
]
df = pd.DataFrame(data)

# Insert subtotals
def insert_subtotals(df, group_cols, amount_cols):
    df = df.sort_values(by=group_cols)
    result_rows = []

    for _, group in df.groupby(group_cols):
        group['is_subtotal'] = False
        result_rows.append(group)

        subtotal_row = {col: '' for col in df.columns}
        for col in amount_cols:
            subtotal_row[col] = group[col].sum()
        subtotal_row['is_subtotal'] = True
        result_rows.append(pd.DataFrame([subtotal_row]))

    return pd.concat(result_rows, ignore_index=True)

# Group by unit and process
amount_cols = ['amount_1', 'amount_2']
group_cols = ['settlement_currency', 'presentment_currency']
group_unit_cols = ['unit_name', 'unit_id']

sections = []
for (unit_name, unit_id), group_df in df.groupby(group_unit_cols):
    subtotal_df = insert_subtotals(group_df, group_cols, amount_cols)
    sections.append({
        'unit_name': unit_name,
        'unit_id': unit_id,
        'report_name': 'Currency Pair Report',
        'report_date': datetime.now().strftime('%Y-%m-%d'),
        'columns': [col for col in subtotal_df.columns if col != 'is_subtotal'],
        'data': subtotal_df.fillna('').to_dict(orient='records')
    })

# Setup Jinja2
template_dir = '/mnt/data/templates_pdfkit'
os.makedirs(template_dir, exist_ok=True)
html_path = os.path.join(template_dir, 'report.html')

html_template = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body { font-family: Arial, sans-serif; font-size: 12px; margin: 20px; }
    .header { text-align: center; margin-bottom: 10px; page-break-before: always; }
    .header img { height: 40px; }
    .report-title { font-size: 18px; font-weight: bold; margin-top: 5px; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th, td { border: 1px solid #999; padding: 6px; text-align: left; }
    tr:nth-child(even) { background-color: #f2f2f2; }
    .subtotal-row { font-weight: bold; background-color: #d9edf7; }
    .page-break { page-break-before: always; }
  </style>
</head>
<body>

{% for section in sections %}
  <div class="header">
    <img src="https://via.placeholder.com/120x40?text=LOGO">
    <div class="report-title">{{ section.report_name }}</div>
    <div>Unit: {{ section.unit_name }} ({{ section.unit_id }})</div>
    <div>Date: {{ section.report_date }}</div>
  </div>

  <table>
    <thead>
      <tr>
        {% for col in section.columns %}
        <th>{{ col }}</th>
        {% endfor %}
      </tr>
    </thead>
    <tbody>
      {% for row in section.data %}
      <tr class="{{ 'subtotal-row' if row.is_subtotal else '' }}">
        {% for col in section.columns %}
        <td>{{ row[col] }}</td>
        {% endfor %}
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <div class="page-break"></div>
{% endfor %}

</body>
</html>
"""

# Save template
with open(html_path, 'w') as f:
    f.write(html_template)

# Render HTML
env = Environment(loader=FileSystemLoader(template_dir))
template = env.get_template('report.html')
rendered_html = template.render(sections=sections)

# Save HTML for reference
rendered_html_path = '/mnt/data/rendered_report.html'
with open(rendered_html_path, 'w') as f:
    f.write(rendered_html)

# Generate PDF
pdf_path = '/mnt/data/final_report_pdfkit.pdf'
pdfkit.from_file(rendered_html_path, pdf_path)

pdf_path  # This is your output PDF path
