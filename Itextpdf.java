


void addSubtotalRow(Table table, Map<String, String> row, List<String> columnOrder, Set<String> totalColumns) throws IOException {
    PdfFont font = PdfFontFactory.createFont(StandardFonts.HELVETICA_BOLD);

    boolean first = true;
    for (String col : columnOrder) {
        String cellText = "";

        if (first) {
            cellText = "Totals";
            first = false;
        } else if (totalColumns.contains(col)) {
            try {
                double value = Double.parseDouble(row.get(col));
                if (value < 0) {
                    cellText = "(" + String.format("%.2f", Math.abs(value)) + ")";
                } else {
                    cellText = String.format("%.2f", value);
                }
            } catch (NumberFormatException e) {
                cellText = "";
            }
        }

        Cell cell = new Cell().add(new Paragraph(cellText).setFont(font));
        cell.setBorder(Border.NO_BORDER);
        cell.setBackgroundColor(ColorConstants.LIGHT_GRAY);
        cell.setTextAlignment(TextAlignment.RIGHT);

        if (col.equals(columnOrder.get(0))) {
            cell.setTextAlignment(TextAlignment.LEFT);
        }

        table.addCell(cell);
    }
}
