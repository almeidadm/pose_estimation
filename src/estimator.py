from logging import getLogger
from typing import Any
import os

import tensorflow as tf

from src.logger import LoggingClass


class PoseEstimator(LoggingClass):
    def __init__(
            self,
            model_type: str = 'metrabs_mob3l_y4t',
            logger: getLogger = None,
            **kw_args
    ):
        super().__init__(logger, **kw_args)
        self.model = self._load_model(model_type)

    def _download_model(self, model_type) -> str:
        server_prefix = 'https://omnomnom.vision.rwth-aachen.de/data/metrabs'
        self.info(f'downloading model {model_type} from {server_prefix}')
        model_zippath = tf.keras.utils.get_file(
            origin=f'{server_prefix}/{model_type}.zip',
            extract=True,
            cache_subdir='models',
        )
        model_path = os.path.join(os.path.dirname(model_zippath), model_type)
        self.info(f'modelpath - {model_path}')

        return model_path

    def _load_model(self, model_type):
        model_path = self._download_model(model_type)
        return tf.saved_model.load(model_path)

    def predict(self, filepath: str) -> Any:
        self.info(f'predicting image {filepath}')
        image = tf.image.decode_jpeg(tf.io.read_file(filepath))
        pred = self.model.detect_poses(image, skeleton='smpl_24')

        return pred, self.model.per_skeleton_joint_edges['smpl_24']