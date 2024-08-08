import subprocess
import argparse
import os

def run_ffmpeg_kvazaar(input_file, input_res, input_fps, low_qp, high_qp,tile_size):
    # Step 1: Format the generated mask values to the one required for running into kvazaar
    roi_output=input_file.replace(".mp4","_roi.hevc")
    mask_file_name=input_file.replace(".mp4","_mask_values.txt")
    if(os.path.exists(mask_file_name)):
        python_command = [
                "python", "mask_gen_formatter.py",
                mask_file_name,
                "--input_res", input_res,
                "--high_qp", str(high_qp),
                "--low_qp", str(low_qp),
                "--tile_size", str(tile_size)
        ]
        subprocess.run(python_command, check=True)
    else:
        print("Missing mask values in given folder of videos "+input_file)
        return

    # Step 2: Convert input file to YUV format using ffmpeg
    yuv_output = input_file.replace('.mp4', '_yuv.yuv')
    if(not os.path.exists(yuv_output)):
        ffmpeg_command_1 = ['ffmpeg', '-i', input_file, '-c:v', 'rawvideo', '-pix_fmt', 'yuv420p', yuv_output]
        subprocess.run(ffmpeg_command_1, check=True)
    
    # Step 3: Encode YUV to HEVC with Kvazaar using the msk_values generated
    # roi_output=input_file.replace(".mp4","_roi.hevc")
    mask_file_formatted_name=mask_file_name.replace(".txt",'_formatted.txt')
    kvazaar_command=['kvazaar', '-i', yuv_output, '--input-res', input_res, '--input-fps', input_fps,'-q',str(low_qp),'--roi',mask_file_formatted_name,'-o' ,roi_output]
    subprocess.run(kvazaar_command, check=True)
    
    # Step 4: Convert HEVC to MP4 using ffmpeg
    mp4_output = roi_output.replace('.hevc', '.mp4')
    ffmpeg_command_2 = ['ffmpeg', '-i',roi_output, '-c:v', 'copy', mp4_output]
    subprocess.run(ffmpeg_command_2, check=True) 
    

def process_directory(directory, input_res, input_fps, low_qp, high_qp,tile_size):
    for filename in os.listdir(directory):
        #Use if only source files are avvaible in the folder
        if filename.endswith('.mp4') and not filename.endswith('qp_30.mp4') and not filename.endswith("qp_40.mp4") and not filename.endswith("_h264.mp4"):
        #Use if yuv file already exists
        #if filename.endswith('.yuv'):
            input_file = os.path.join(directory, filename)
            run_ffmpeg_kvazaar(input_file, input_res, input_fps, low_qp, high_qp,tile_size) 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run ffmpeg and kvazaar commands with user-defined parameters.')
    parser.add_argument('directory', type=str, help='Directory containing input files')
    parser.add_argument('--input_res', type=str, default='1280x720', help='Input resolution (default: 1280x720)')
    parser.add_argument('--input_fps', type=str, default='30', help='Input frame rate (default: 30)')
    parser.add_argument('--low_qp', type=int, default=30, help='Lower Value of QP (default: 30)')
    parser.add_argument('--high_qp', type=int, default=40, help='Higher Value of QP (default: 40)')
    parser.add_argument('--tile_size', type=int, default=16, help='Size of each tile in a single frame (default: 16)')
        
    args = parser.parse_args()
    
    process_directory(args.directory, args.input_res, args.input_fps, args.low_qp, args.high_qp,args.tile_size)
