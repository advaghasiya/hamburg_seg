# Copyright (c) OpenMMLab. All rights reserved.
from mmseg.datasets.builder import DATASETS
from mmseg.datasets.custom import CustomDataset

@DATASETS.register_module()
class HamburgMMSEGDataset(CustomDataset):
    """Hamburg dataset.

    In segmentation map annotation for Hamburg dataset, 0 is the ignore index.
    ``reduce_zero_label`` should be set to True. The ``img_suffix`` and
    ``seg_map_suffix`` are both fixed to '.png'.
    """
    CLASSES = ('road')

    PALETTE = [[255, 255, 255]]

    def __init__(self, **kwargs):
        super(HamburgMMSEGDataset, self).__init__(
            img_suffix='.png',
            seg_map_suffix='.png',
            reduce_zero_label=True,
            **kwargs)