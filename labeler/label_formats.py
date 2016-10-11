from . label_format import LabelFormat


class DefaultLabelFormat(LabelFormat):
    font = 'Helvetica-Bold'
    vertical_margin = 10
    horizontal_margin = 5
    max_font_size = 18

    def get_text_height(self):
        return int((self.height / 100) * 16)

    def get_horizontal_location(self):
        return self.width / 2
