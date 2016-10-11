from reportlab.graphics import shapes
from reportlab.pdfbase.pdfmetrics import stringWidth


class LabelFormat:
    font = None
    vertical_margin = 0
    horizontal_margin = 0
    max_font_size = 0
    text_anchor = 'middle'

    def __init__(self, label, width, height, lines):
        self.width = width
        self.height = height
        self.lines = lines
        self.line_count = len(lines)

    def get_text_height(self):
        raise NotImplementedError

    def get_horizontal_location(self):
        raise NotImplementedError

    def get_usable_height(self):
        return self.height - (self.vertical_margin * 2)

    def get_usable_width(self):
        return self.width - (self.horizontal_margin * 2)

    def get_line_gap(self):
        return self.get_usable_height() - (
            self.get_text_height() * self.line_count)

    def calculate_max_font_size(self, text):
        font_size = self.max_font_size
        string_width = stringWidth(text, self.font, font_size)
        while string_width > self.get_usable_width():
            font_size *= 0.8
            string_width = stringWidth(text, self.font, font_size)
        return font_size

    def make_label(self, label, lines):
        horizontal_location = self.get_horizontal_location()
        vertical_location = self.vertical_margin
        for line in reversed(lines):
            font_size = self.calculate_max_font_size(line)
            label.add(shapes.String(
                horizontal_location, vertical_location, line,
                fontSize=font_size, fontName=self.font,
                textAnchor=self.text_anchor))
            vertical_location = vertical_location + self.get_line_gap()
