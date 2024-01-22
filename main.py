import logging
from src.executor import Executor

logging.basicConfig(
    filename='log_pose_estimation.txt',
    filemode='a',
    format='[%(asctime)s,%(msecs)d] %(name)s %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO,
)

logging.info("Running pose estimation pipeline")

context = {}
executor = Executor(logger=logging.getLogger('pose-estimatior-pipeline'))

executor.read_input(context)
executor.prepare(context)
executor.transform_to_frame(context)
executor.estimate_pose(context)
executor.process_frames(context)
executor.transform_to_video(context)