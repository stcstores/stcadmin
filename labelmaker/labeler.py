import labels
from reportlab.graphics import shapes
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.graphics import renderPDF
from reportlab.pdfgen.canvas import Canvas


class PaperSize:
    def __init__(self, width, height):
        self.width = width
        self.height = height


class A4(PaperSize):
    width = 210
    height = 297


class LabelSize:
    def __init__(self, width, height):
        self.width = width
        self.height = height


class DefaultLabelSize:
    width = 45.7
    height = 25.4


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

    def __init__(
            self, paper_size, label_size, columns=4, rows=10):
            self.paper_size = paper_size
            self.label_size = label_size
            self.columns = columns
            self.rows = rows

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
            center = width / 2
            font = 'Helvetica-Bold'
            max_font_size = 16
            gap = height - (max_font_size * len(lines))
            from_bottom = height - 15
            for line in lines:
                max_width = width - 10
                font_size = max_font_size
                string_width = stringWidth(line, font, font_size)
                while string_width > max_width:
                    font_size *= 0.8
                    string_width = stringWidth(line, font, font_size)
                label.add(shapes.String(
                    center, from_bottom, line, fontName=font,
                    textAnchor='middle', fontSize=font_size))
                from_bottom -= gap

        sheet = labels.Sheet(specs, draw_label, border=False)
        for item in data:
            sheet.add_label(item)
        canvas = Canvas(None, pagesize=sheet._pagesize)
        for page in sheet._pages:
            renderPDF.draw(page, canvas, 0, 0)
            canvas.showPage()
        return canvas


class STW046025PO(LabelSheet):
    paper_size = A4
    label_size = LabelSize(48, 26)
    columns = 4
    rows = 10
    left_margin = 5
    right_margin = 3
    top_margin = 18
    bottom_margin = 13
    corner_radius = 2
    left_padding = 0
    right_padding = 0
    padding_top = 0
    padding_bottom = 0

    def __init__(self):
        pass
