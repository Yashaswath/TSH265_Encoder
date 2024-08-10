import subprocess
import argparse
import os

h264=False

def run_ffmpeg_kvazaar(input_file, input_res, input_fps, low_qp, high_qp):
    # Step 1: Convert input file to YUV format using ffmpeg
    yuv_output = input_file.replace('.mp4', '_yuv.yuv')
    if not os.path.exists(yuv_output):
        ffmpeg_command_1 = ['ffmpeg', '-i', input_file, '-c:v', 'rawvideo', '-pix_fmt', 'yuv420p', yuv_output]
        subprocess.run(ffmpeg_command_1, check=True)
    
    # Step 2: Encode YUV to HEVC with Kvazaar
    if h264:
        quality_output = input_file.replace('.mp4', '.hevc')
        if not os.path.exists(quality_output):
            kvazaar_command_1 = ['kvazaar', '-i', yuv_output, '--input-res', input_res, '--input-fps', input_fps, '-o', quality_output]
            subprocess.run(kvazaar_command_1, check=True)
    
    quality_L_output = input_file.replace('.mp4', '_L.hevc')
    if not os.path.exists(quality_L_output):
        kvazaar_command_2 = ['kvazaar', '-i', yuv_output, '--input-res', input_res, '--input-fps', input_fps, '-q', str(low_qp), '-o', quality_L_output]
        subprocess.run(kvazaar_command_2, check=True)
    
    quality_H_output = input_file.replace('.mp4', '_H.hevc')
    if not os.path.exists(quality_H_output):
        kvazaar_command_3 = ['kvazaar', '-i', yuv_output, '--input-res', input_res, '--input-fps', input_fps, '-q', str(high_qp), '-o', quality_H_output]
        subprocess.run(kvazaar_command_3, check=True)
    
    # Step 3: Convert HEVC to MP4 using ffmpeg
    if h264:
        os.rename(input_file,input_file.replace('.mp4','_h264.mp4'))
        mp4_output = quality_output.replace('.hevc', '.mp4')
        if not os.path.exists(mp4_output):
            ffmpeg_command_2 = ['ffmpeg', '-i', quality_output, '-c:v', 'copy', mp4_output]
            subprocess.run(ffmpeg_command_2, check=True)
    
    mp4_output_L = input_file.replace('.mp4', f'_qp_{low_qp}.mp4')
    if not os.path.exists(mp4_output_L):
        ffmpeg_command_3 = ['ffmpeg', '-i', quality_L_output, '-c:v', 'copy', mp4_output_L]
        subprocess.run(ffmpeg_command_3, check=True)
    
    mp4_output_H = input_file.replace('.mp4', f'_qp_{high_qp}.mp4')
    if not os.path.exists(mp4_output_H):
        ffmpeg_command_4 = ['ffmpeg', '-i', quality_H_output, '-c:v', 'copy', mp4_output_H]
        subprocess.run(ffmpeg_command_4, check=True)

    # Step 4: Create pngs folder for the original video
    pngs_folder=input_file.replace('.mp4','')
    if not os.path.exists(pngs_folder):
        os.system(f'mkdir {pngs_folder}')
        os.system(f'ffmpeg -i {input_file} -start_number 0 {pngs_folder}/%010d.png') 
    

def process_directory(directory, input_res, input_fps, low_qp, high_qp):
    for filename in os.listdir(directory):
        if filename.endswith('.mp4') and not filename.endswith('_qp_30.mp4') and not filename.endswith('_qp_40.mp4') and not filename.endswith('_roi.mp4') and not filename.endswith('_FPN.mp4') and not filename.endswith('_h264.mp4'):
            input_file = os.path.join(directory, filename)
            run_ffmpeg_kvazaar(input_file, input_res, input_fps, low_qp, high_qp)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run ffmpeg and kvazaar commands with user-defined parameters.')
    parser.add_argument('directory', type=str, help='Directory containing input files')
    parser.add_argument('--input_res', type=str, default='1280x720', help='Input resolution (default: 1280x720)')
    parser.add_argument('--input_fps', type=str, default='30', help='Input frame rate (default: 30)')
    parser.add_argument('--low_qp', type=int, default=30, help='Lower Value of QP (default: 30)')
    parser.add_argument('--high_qp', type=int, default=40, help='Higher Value of QP (default: 40)')
    parser.add_argument('--h264', action='store_true', help='Specifies if the video is encoded using H264')
    
    args = parser.parse_args()
    h264=args.h264
    process_directory(args.directory, args.input_res, args.input_fps, args.low_qp, args.high_qp)
