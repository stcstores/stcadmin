import labels

from reportlab.graphics import renderPDF
from reportlab.pdfgen.canvas import Canvas


class LabelSheet:
    left_margin = 0
    right_margin = 0
    top_margin = 0
    bottom_margin = 0
    left_padding = 0
    right_padding = 0
    top_padding = 0
    bottom_padding = 0
    corner_radius = 0
    border = False

    def __init__(
            self, paper_size, label_size, label_format, columns=4, rows=10):
            self.paper_size = paper_size
            self.label_size = label_size
            self.columns = columns
            self.rows = rows
            self.label_format = label_format

    def generate_PDF_from_data(self, data):
        specs = labels.Specification(
            self.paper_size.width, self.paper_size.height, self.columns,
            self.rows, self.label_size.width, self.label_size.height,
            left_margin=self.left_margin,
            right_margin=self.right_margin,
            top_margin=self.top_margin,
            bottom_margin=self.bottom_margin,
            left_padding=self.left_padding,
            right_padding=self.right_padding,
            top_padding=self.top_padding,
            bottom_padding=self.bottom_padding,
            corner_radius=self.corner_radius)

        def draw_label(label, width, height, lines):
            label_format = self.label_format(label, width, height, lines)
            label_format.make_label(label, lines)

        sheet = labels.Sheet(specs, draw_label, border=self.border)
        for item in data:
            sheet.add_label(item)
        canvas = Canvas(None, pagesize=sheet._pagesize)
        for page in sheet._pages:
            renderPDF.draw(page, canvas, 0, 0)
            canvas.showPage()
        return canvas
