import glob
import os
import re
import shutil
from logging import getLogger
from pathlib import Path

from src.converter import FrameToVideoConverter, VideoToFrameConverter
from src.estimator import PoseEstimator
from src.logger import LoggingClass
from src.viewer import Vizualizer


class Executor(LoggingClass):

    def __init__(self, input_dir: str = './data_input', output_dir: str = './data_output', logger: getLogger = None, **kw_args):
        super().__init__(logger, **kw_args)
        self.input_dir = input_dir
        self.output_dir = output_dir

    def read_input(self, context):
        self.info('reading input file')
        valid_extensions = ['avi', 'mp4', 'MOV']
        list_of_files = glob.glob(f'{self.input_dir}/*')
        list_of_files = [f for f in list_of_files if f.split('.')[-1] in valid_extensions]
        if not list_of_files:
            message = f'no video file avaiable at {self.input_dir}'
            self.error(message)
            raise Exception(message)

        latest_file = max(list_of_files, key=os.path.getctime)
        self.info(f'latest file finded: {latest_file}')

        context['latest_file'] = latest_file

    def prepare(self, context):
        latest_file = context['latest_file']
        
        (filename, title), *_ = re.findall('.+\/((.+)\.\w{3})', latest_file)
        
        location = f'{self.output_dir}/{title}'

        self.info('creating output path')
        Path(location).mkdir(parents=True, exist_ok=True)
        for subfold in ['frames/raw', 'frames/processed']:
            Path(f'{location}/{subfold}').mkdir(parents=True, exist_ok=True)
        
        shutil.copy(latest_file, f'{location}/{filename}')

        context['location'] = location
        context['filename'] = filename

    def transform_to_frame(self, context):
        location = context['location']
        filename = context['filename']
        VideoToFrameConverter(f'{location}/{filename}', f'{location}/frames/raw')()

    def estimate_pose(self, context):
        location = context['location']

        frames = glob.glob(f'{location}/frames/raw/*.jpg')

        preds = []
        model = PoseEstimator()
        for image in sorted(frames, key=os.path.getctime):
            pred, edge = model.predict(image)
#            self._write_coord(pred['poses3d'].numpy(), edge, image, context)
            preds.append((pred, edge))
        context['preds'] = preds

    def _write_coord(self, pred, edges, filename, context):
        self.info(f'writing coord of pred: {type*pred}')
        name = filename.split('/')[-1].split('.')[0]
        poses3d = pred['poses3d'].numpy()
        for pose3d in poses3d:
            for i_start, i_end in edges:
                print(f'v', *zip(pose3d[i_start], pose3d[i_end]))

    def process_frames(self, context):
        location = context['location']
        preds = context['preds']

        frames = glob.glob(f'{location}/frames/raw/*.jpg')

        model = Vizualizer()
        for image, (pred, edge) in zip(sorted(frames, key=os.path.getctime), preds):
            self.info(f'visualizing image {image}')
            name = image.split('/')[-1]
            fig = model.vizualize(
                image,
                pred['boxes'].numpy(),
                pred['poses3d'].numpy(),
                pred['poses2d'].numpy(),
                edge.numpy()
            )
            fig.savefig(f'{location}/frames/processed/processed-{name}')
    
    def transform_to_video(self, context):
        location = context['location']
        FrameToVideoConverter(input=f'{location}/frames/processed/', output_dir=location)()