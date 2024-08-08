import subprocess
import argparse


def prepare_videos(directory, input_res, input_fps, low_qp, high_qp,h264):
    #Calls prepare_videos.py
    python_command=[
        'python','prepare_videos.py',
        directory,
        f'--input_res {input_res}',
        f'--input_fps {input_fps}',
        f'--low_qp {low_qp}',
        f'--high_qp {high_qp}',
        f'--h264 {h264}'
    ]
    subprocess.run(python_command,check=True)

def generate_mask_values(directory, input_res, input_fps, low_qp, high_qp,tile):
    python_command=[
        'python h265_batch_blackgen.py',
        directory,
        f'--input_res {input_res}',
        f'--input_fps {input_fps}',
        f'--low_qp {low_qp}',
        f'--high_qp {high_qp}',
        f'--tile_size {tile}'
    ]
    subprocess.run(python_command,check=True)

def generate_encoded_video(directory, input_res, input_fps, low_qp, high_qp,tile_size):
    python_command=[
        'python generate_encoded_video.py',
        directory,
        f'--input_res {input_res}',
        f'--input_fps {input_fps}',
        f'--low_qp {low_qp}',
        f'--high_qp {high_qp}',
        f'--tile_size {tile_size}'
    ]
    subprocess.run(python_command,check=True)

def prepare_h264_videos(directory, input_fps, low_qp, high_qp):
    python_command=[
        'python','h264_video_companion_generator.py',
        directory,
        f'--input_fps {input_fps}'
        f'--qps [{low_qp},{high_qp}]'
    ]
    subprocess.run(python_command,check=True)

def generate_encoded_h264_video(directory):
    python_command=[
        'python AccMPEG/batch_blackgen_roi.py',
        directory,
    ]
    subprocess.run(python_command,check=True)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate an H265 encoded video by AccMPEG technique')
    parser.add_argument('directory', type=str, help='Directory containing input files')
    parser.add_argument('--input_res', type=str, default='1280x720', help='Input resolution (default: 1280x720)')
    parser.add_argument('--input_fps', type=str, default='30', help='Input frame rate (default: 30)')
    parser.add_argument('--low_qp', type=int, default=30, help='Lower Value of QP (default: 30)')
    parser.add_argument('--high_qp', type=int, default=40, help='Higher Value of QP (default: 40)')
    parser.add_argument('--h264', type=bool, default=False, help='Specifies if the source video is encoded using H264')
    parser.add_argument('--encoder',type=bool, default=True, help='True if you need to encode the video in H.265 else False in H.264')
    parser.add_argument('--tile_size', type=int, default=16, help='Size of a tile in a frame')
    
    args = parser.parse_args()

    if args.encoder:
        prepare_videos(args.directory, args.input_res, args.input_fps, args.low_qp, args.high_qp,args.h264)
        generate_mask_values(args.directory, args.input_res, args.input_fps, args.low_qp, args.high_qp,args.tile_size)
        generate_encoded_video(args.directory, args.input_res, args.input_fps, args.low_qp, args.high_qp,args.tile_size)
    else:
        prepare_h264_videos(args.directory, args.input_fps, args.low_qp,args.high_qp)
        generate_encoded_h264_video(args.directory)

