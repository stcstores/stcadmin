from . label_sheet import LabelSheet
from . label_size import LabelSize
from . paper_sizes import A4


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

    def __init__(self, label_format=None):
        self.label_format = label_format
