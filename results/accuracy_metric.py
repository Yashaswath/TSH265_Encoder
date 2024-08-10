import os
import argparse
import subprocess
from shubham_sir_yolo_edited import process_folders

def get_all_folders(root_folder):
    try:
        # List directories in the given root_folder
        return [d for d in os.listdir(root_folder) if os.path.isdir(os.path.join(root_folder, d))]
    except FileNotFoundError:
        print(f"The directory '{root_folder}' does not exist.")
        return []
    except PermissionError:
        print(f"Permission denied for accessing '{root_folder}'.")
        return []
    except Exception as e:
        print(f"An error occurred while accessing '{root_folder}': {e}")
        return []

def process_directory(directory):
    v_list = []
    for filename in os.listdir(directory):
        if filename.endswith('_FPN.mp4'):
            input_file = os.path.join(directory, filename)
            v_list.append(input_file.replace('_roi_bound_0.2_conv_1_hq_30_lq_40_app_FPN.mp4', ''))
    return v_list

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="List all folders in the specified directory.")
    parser.add_argument('directory', type=str, help='The directory to list folders from.')
    args = parser.parse_args()
    
    directory = args.directory
    
    # Check if the provided directory exists
    if not os.path.exists(directory):
        print(f"The directory '{directory}' does not exist.")
        return
    
    # Get and print all folders
    folders = get_all_folders(directory)
    print(folders)
    if folders:
        for folder in folders:
            folder_path = os.path.join(directory, folder)
            v_list = process_directory(folder_path)
            print(v_list)
            
            ext_list = [".mp4", "_roi_bound_0.2_conv_1_hq_30_lq_40_app_FPN.mp4"]
            for video in v_list:
                for ext in ext_list:
                    video1 = video + ext
                    command = [
                        "python3", "h265_detect_for_groundtruth.py",
                        "--source", video1,
                        "--save-txt",
                        "--save-labelfile-name", video1.replace(".mp4", ".txt"),
                        "--classes", "0", "1", "2", "3", "4", "5", "6", "7",
                        "--nosave"
                    ]
                    try:
                        result = subprocess.run(command, check=True, capture_output=True, text=True)
                        print("Command Output:", result.stdout)
                        print("Command Error:", result.stderr)
                    except subprocess.CalledProcessError as e:
                        print(f"Error running detection command: {e}")
                        print("Command Output:", e.stdout)
                        print("Command Error:", e.stderr)
        
        # Execute shubham_sir_yolo_edited.py with v_list
            v_list_str = " ".join(v_list)  # Convert list to space-separated string
            yolo_command = [
                "python3", "shubham_sir_yolo_edited.py",
                "--folder", folder,
                "--v_list", v_list_str
            ]
            try:
                yolo_result = subprocess.run(yolo_command, check=True, capture_output=True, text=True)
                print("YOLO Command Output:", yolo_result.stdout)
                print("YOLO Command Error:", yolo_result.stderr)
            except subprocess.CalledProcessError as e:
                print(f"Error running YOLO command: {e}")
                print("YOLO Command Output:", e.stdout)
                print("YOLO Command Error:", e.stderr)
    else:
        print(f"No folders found in '{directory}' or unable to access the directory.")

if __name__ == "__main__":
    main()
