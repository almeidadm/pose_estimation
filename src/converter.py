import subprocess
from abc import ABC
from logging import getLogger

from src.logger import LoggingClass

import cv2


class Converter(ABC, LoggingClass):
    def __init__(
            self, 
            input: str, 
            output_dir:str, 
            logger: getLogger = None, 
            **kw_args,
    ):
        super().__init__(logger, **kw_args)
        self.input = input
        self.output = output_dir


class VideoToFrameConverter(Converter):
    def __init__(self, input: str, output_dir: str, logger: getLogger = None, **kw_args):
        super().__init__(input, output_dir, logger, **kw_args)

    def __call__(self) -> None:
        subprocess.call(
            ['ffmpeg', '-i', self.input, '-f', 'image2', '-qscale:v', '0', f'{self.output}/video-frame%05d.jpg']
        )
"""     
        capture = cv2.VideoCapture(self.input)

        frame_number = 0
        
        while True:
            sucess, frame = capture.read()

            if not sucess:
                self.error(f'read failed {frame_number}')
                break

            cv2.imwrite(f'{self.output}/frame_{frame_number}.jpg', frame)
            frame_number += 1
        capture.release()
"""


class FrameToVideoConverter(Converter):
    frame_rate = '30'
    def __call__(self) -> None:
        subprocess.call(
            [
                'ffmpeg', 
                '-framerate', 
                self.frame_rate, 
                '-i',
                f'{self.input}/processed-video-frame%05d.jpg',
                '-vf',
                'format=yuv420p', 
                f'{self.output}/video.mp4',
            ]
        )
"""
        frames = []
        for filename in self.input:
            frames.append(cv2.imread(filename))

        height, width, _ = frames[0].shape

        video = cv2.VideoWriter(f'{self.output}/video.avi', -1, 1, (width, height))

        for frame in frames:
            video.write(frame)

        cv2.destroyAllWindows()
        video.release()
"""