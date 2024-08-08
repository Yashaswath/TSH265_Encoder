import os
from itertools import product
import logging
import argparse

parser = argparse.ArgumentParser(description='Run ffmpeg and kvazaar commands with user-defined parameters.')
parser.add_argument('directory', type=str, help='Directory containing input files')
parser.add_argument('--input_res', type=str, default='1280x720', help='Input resolution (default: 1280x720)')
parser.add_argument('--input_fps', type=str, default='30', help='Input frame rate (default: 30)')
parser.add_argument('--low_qp', type=int, default=30, help='Lower Value of QP (default: 30)')
parser.add_argument('--high_qp', type=int, default=40, help='Higher Value of QP (default: 40)')
parser.add_argument('--tile_size', type=int, default=16, help='Size of a tile in a frame')

    
args = parser.parse_args()


v_list = []
# Video list
def process_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.mp4') and not filename.endswith('qp_30.mp4') and not filename.endswith('qp_40.mp4') and not filename.endswith('h264.mp4'):
            input_file = os.path.join(directory, filename)
            v_list.append(input_file.replace('.mp4',''))
    return v_list
v_list=process_directory(args.directory)
print(v_list)

# Parameters
high = args.low_qp
tile = args.tile_size
conv_list = [1]
bound_list = [0.2]
base_list = [args.high_qp]

# Model settings
model_app = "FPN"
model_name = f"COCO_detection_{model_app}_SSD_withconfidence_allclasses_new_unfreezebackbone_withoutclasscheck"

# Inference settings
stats = "artifact/stats_QP30_thresh7_segmented_FPN"
conf_thresh = 0.7
gt_conf_thresh = 0.7
app_name = "COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"

# Visualization step size
visualize_step_size = 10000

# Log settings
logging.basicConfig(level=logging.INFO)

# Define the filename for maskgen_file
filename = "SSD/accmpegmodel"

# Function to run shell commands
def run_shell_command(command):
    logging.info(f"Running command: {command}")
    os.system(command)

# Main loop
for conv, bound, base, v in product(conv_list, bound_list, base_list, v_list):
    logging.info(f"Processing video: {v} with conv: {conv}, bound: {bound}, base: {base}")

    output = f"{v}_roi_bound_{bound}_conv_{conv}_hq_{high}_lq_{base}_app_{model_app}.mp4"

    # Compress the video with specific parameters
    if not os.path.exists(output):
        compress_command = (
            f"python h265_compress_blackgen_roi.py -i {v}_qp_{high}.mp4 "
            f"{v}_qp_{base}.mp4 -s {v} -o {output} --tile_size {tile}  -p maskgen_pths/{model_name}.pth.best "
            f"--conv_size {conv} "
            f"-g {v}_qp_{high}.mp4 --bound {bound} --hq {high} --lq {base} --smooth_frames 10 --app {app_name} "
            f"--maskgen_file maskgen/{filename}.py --visualize_step_size {visualize_step_size}",
            f"--input_res {args.input_res}"
        )
        run_shell_command(compress_command)

logging.info("Script completed.")

