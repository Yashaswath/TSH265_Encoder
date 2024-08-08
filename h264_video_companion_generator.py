import os
import subprocess
import argparse

def compress_videos_in_directory(directory_path, qps,fps):
    # Ensure the directory exists
    if not os.path.isdir(directory_path):
        raise ValueError(f"The provided path '{directory_path}' is not a valid directory.")

    # Get a list of all video files in the directory
    video_files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    
    # Filter only video files by extension if necessary
    # video_files = [f for f in video_files if f.endswith(('.mp4', '.mkv', '.avi'))]

    # Process each video file with the specified QP values
    for qp in qps:
        for video_file in video_files:
            input_name = os.path.join(directory_path, video_file)
            output_name = os.path.join(directory_path, f"{os.path.splitext(video_file)[0]}_qp_{qp}.mp4")
            if os.path.exists(output_name):
                continue
            try:
                ffmpeg_command = [
                                    'ffmpeg', '-i', input_name,
                                    '-c:v', 'libx264', '-crf', str(qp),
                                    '-r', str(fps), '-c:a', 'copy', output_name
                                ]
                subprocess.run(ffmpeg_command, check=True)
                print(f"Successfully processed {video_file} with qp={qp}. Output saved as {output_name}.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to process {video_file} with qp={qp}. Error: {e}")
    for video_file in video_files:
        pngs_folder=video_file.replace('.mp4','')
        os.system(f'mkdir {pngs_folder}')
        os.system(f'ffmpeg -i {video_file} -start_number 0 {pngs_folder}/%010d.png')

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Compress videos in a directory using specified QP values.")
    parser.add_argument("directory_path", type=str, help="The path to the directory containing video files.")
    parser.add_argument(
        "--qps",
        type=int,
        nargs='+',
        default=[30, 40],
        help="List of QP values to use for compression (default: [30, 40])."
    )
    parser.add_argument("--input_fps", type=str,default="30", help="The path to the directory containing video files.")

    # Parse arguments
    args = parser.parse_args()

    # Call the function with the parsed arguments
    compress_videos_in_directory(args.directory_path, args.qps,args.input_fps)

