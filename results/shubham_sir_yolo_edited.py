from collections import Counter
from pathlib import Path
import numpy as np
import argparse
import os

class CalculateMetrics():
    def __init__(self):
        self.TP, self.TN, self.FP, self.FN = 0, 0, 0, 0  # True Positives, True Negatives, False Positives, False Negatives
        self.g_data, self.t_data = [], []
        self.f1 = 0
        self.precision = 0
        self.recall = 0

    def reset(self):
        self.TP, self.TN, self.FP, self.FN = 0, 0, 0, 0

    def calc_metrics_individual(self, groundtruth_file, test_file, frames_in_a_seg=15, total_buffered_segs=0):
        # Reading ground truth file
        with open(groundtruth_file, 'r') as fg:
            g_d = fg.read()
        self.g_data = [i.split(" ")[:-1] for i in g_d.split('\n')[0:-1]]

        # Reading test file
        with open(test_file, 'r') as ft:
            t_d = ft.read()
        self.t_data = [i.split(" ")[:-1] for i in t_d.split('\n')[0:-1]]

        accu, f1, prec, recal = [], [], [], []
        for frame_indx in range(len(self.t_data)):
            g_frame_objs = Counter(self.g_data[frame_indx + (total_buffered_segs * frames_in_a_seg)])  # number of occurrences of each object class
            t_frame_objs = Counter(self.t_data[frame_indx])

            for cls in range(8):  # loop for 0 to 7 unique classes
                cls_str = str(cls)
                if cls_str in g_frame_objs and cls_str in t_frame_objs:
                    if g_frame_objs[cls_str] > t_frame_objs[cls_str]:
                        self.TP += t_frame_objs[cls_str]
                        self.FN += g_frame_objs[cls_str] - t_frame_objs[cls_str]
                    elif g_frame_objs[cls_str] < t_frame_objs[cls_str]:
                        self.TP += g_frame_objs[cls_str]
                        self.FP += t_frame_objs[cls_str] - g_frame_objs[cls_str]
                    else:
                        self.TP += g_frame_objs[cls_str]
                elif cls_str not in g_frame_objs and cls_str not in t_frame_objs:
                    self.TN += 1
                elif cls_str not in g_frame_objs and cls_str in t_frame_objs:
                    self.FP += t_frame_objs[cls_str]
                elif cls_str in g_frame_objs and cls_str not in t_frame_objs:
                    self.FN += g_frame_objs[cls_str]

            if (frame_indx + 1) % frames_in_a_seg == 0:  # number of frames in a segment
                a, f, p, r = self.get_metric(self.TP, self.TN, self.FP, self.FN)
                accu.append(a)
                f1.append(f)
                prec.append(p)
                recal.append(r)
                self.reset()

        accu, f1, prec, recal = np.array(accu), np.array(f1), np.array(prec), np.array(recal)
        self.reset()
        return np.mean(accu), np.mean(f1), np.mean(prec), np.mean(recal), np.std(accu), np.std(f1), np.std(prec), np.std(recal)

    def get_metric(self, tp, tn, fp, fn):
        if tp != 0:
            precision = tp / (tp + fp)
            recall = tp / (tp + fn)
            f1_score = 2 * ((precision * recall) / (precision + recall))
        else:
            precision, recall = 0, 0
            f1_score = 0
        accu = (tp + tn) / (tp + tn + fp + fn)
        return accu, f1_score, precision, recall

# def main():
#     parser = argparse.ArgumentParser(description='Calculate metrics from ground truth and test files.')
#     parser.add_argument('groundtruth_file', type=str, help='Path to the ground truth file')
#     parser.add_argument('test_file', type=str, help='Path to the test file')

#     args = parser.parse_args()
#     groundtruth_file = args.groundtruth_file
#     test_file = args.test_file

#     metrics_calculator = CalculateMetrics()
#     mean_acc, mean_f1, mean_prec, mean_recall, std_acc, std_f1, std_prec, std_recall = metrics_calculator.calc_metrics_individual(
#         groundtruth_file, test_file)

#     print(f"Mean Accuracy: {mean_acc}")
#     print(f"Mean F1 Score: {mean_f1}")
#     print(f"Mean Precision: {mean_prec}")
#     print(f"Mean Recall: {mean_recall}")
#     print(f"Std Accuracy: {std_acc}")
#     print(f"Std F1 Score: {std_f1}")
#     print(f"Std Precision: {std_prec}")
#     print(f"Std Recall: {std_recall}")

# if __name__ == "__main__":
#     main()

# from collections import Counter
# from pathlib import Path
# import numpy as np
# import os

# class CalculateMetrics:
#     def __init__(self):
#         self.TP, self.TN, self.FP, self.FN = 0, 0, 0, 0  # True Positives, True Negatives, False Positives, False Negatives
#         self.g_data = []
#         self.t_data = []
#         self.f1 = 0
#         self.precision = 0
#         self.recall = 0

#     def reset(self):
#         self.TP, self.TN, self.FP, self.FN = 0, 0, 0, 0

#     def calc_metrics_individual(self, groundtruth_file, test_file, frames_in_a_seg=15, total_buffered_segs=0):
#     # Reading ground truth file
#         with open(groundtruth_file, 'r') as fg:
#             g_d = fg.read()
#         self.g_data = [i.split(" ")[:-1] for i in g_d.split('\n') if i]

#         # Reading test file
#         with open(test_file, 'r') as ft:
#             t_d = ft.read()
#         self.t_data = [i.split(" ")[:-1] for i in t_d.split('\n') if i]

#         accu, f1, prec, recal = [], [], [], []
#         num_frames = len(self.t_data)
#         print(num_frames)
#         print(len(self.g_data))
#         for frame_indx in range(num_frames):
#             # Adjust index with total buffered segments
#             g_frame_objs = Counter(self.g_data[frame_indx])  
#             t_frame_objs = Counter(self.t_data[frame_indx])

#             for cls in range(8):  # Assuming there are 8 classes
#                 cls_str = str(cls)
#                 g_count = g_frame_objs[cls_str]
#                 t_count = t_frame_objs[cls_str]

#                 if g_count > 0 and t_count > 0:
#                     self.TP += min(g_count, t_count)
#                     self.FP += max(0, t_count - g_count)
#                     self.FN += max(0, g_count - t_count)
#                 elif g_count == 0 and t_count > 0:
#                     self.FP += t_count
#                 elif g_count > 0 and t_count == 0:
#                     self.FN += g_count
#                 elif g_count == 0 and t_count == 0:
#                     self.TN += 1

#             if (frame_indx + 1) % frames_in_a_seg == 0:
#                 a, f, p, r = self.get_metric(self.TP, self.TN, self.FP, self.FN)
#                 accu.append(a)
#                 f1.append(f)
#                 prec.append(p)
#                 recal.append(r)
#                 self.reset()

#         # Compute metrics for remaining frames
#         if (num_frames % frames_in_a_seg) != 0:
#             a, f, p, r = self.get_metric(self.TP, self.TN, self.FP, self.FN)
#             accu.append(a)
#             f1.append(f)
#             prec.append(p)
#             recal.append(r)

#         accu, f1, prec, recal = np.array(accu), np.array(f1), np.array(prec), np.array(recal)
#         self.reset()
#         return np.mean(accu), np.mean(f1), np.mean(prec), np.mean(recal), np.std(accu), np.std(f1), np.std(prec), np.std(recal)


#     def get_metric(self, tp, tn, fp, fn):
#         if tp != 0:
#             precision = tp / (tp + fp)
#             recall = tp / (tp + fn)
#             f1_score = 2 * ((precision * recall) / (precision + recall))
#         else:
#             precision, recall = 0, 0
#             f1_score = 0
#         accu = (tp + tn) / (tp + tn + fp + fn)
#         return accu, f1_score, precision, recall


#def process_directory(directory):
    #v_list=[]
    #print(os.listdir(directory))
    #for filename in os.listdir(directory):
       # if filename.endswith('_roi_bound_0.2_conv_1_hq_30_lq_40_app_FPN.txt') :
      #      input_file = os.path.join(directory, filename)
     #       v_list.append(input_file.replace('_roi_bound_0.2_conv_1_hq_30_lq_40_app_FPN.txt',''))
    #print(v_list)
   # return v_list

def process_folders(folder, v_list):
    st_out = []    
    yerr_st = []
    st_out_dict = {}
    compare = CalculateMetrics()
    tmp = []
    st_tmp_dict = {}
    for video in v_list:
            groundtruth_file = Path(video + ".txt") 
            test_file = Path(video + "_roi_bound_0.2_conv_1_hq_30_lq_40_app_FPN.txt") 
            print(groundtruth_file,test_file)
            if groundtruth_file.exists() and test_file.exists():
               
                accu, f1, prec, recall, std_acc, std_f1, std_prec, std_recall = compare.calc_metrics_individual(groundtruth_file, test_file)
                st_tmp_dict[video] = [accu, f1, prec, recall, std_acc, std_f1, std_prec, std_recall]
            else:
                accu, f1, prec, recall, std_acc, std_f1, std_prec, std_recall = 1, 1, 1, 1, 0, 0, 0, 0
                st_tmp_dict[video] = [accu, f1, prec, recall, std_acc, std_f1, std_prec, std_recall]
            tmp.append([accu, f1, prec, recall, std_acc, std_f1, std_prec, std_recall])

    st_out_dict[folder] = st_tmp_dict
    tmp = np.array(tmp)

    yerr_st.append(np.std(tmp, axis=0))
    st_out.append(tmp.mean(axis=0))

    st_out = np.array(st_out)
    yerr_st = np.array(yerr_st)

    #if st_out.ndim == 2 and st_out.shape[0] > 1:
     #   _st_out = st_out.copy()
      #  _st_out[1, :] = (_st_out[0, :] + _st_out[1, :]) / 2
       # _st_out[0, :] = np.zeros(_st_out.shape[1])
    #else:
     #   _st_out = st_out.copy()  # If it's already 1-dimensional, don't modify it
      #  _st_out[0, :] = np.zeros(_st_out.shape[1])  # Assuming there are columns to reset

    return st_out, yerr_st, st_out_dict

def save_results(st_out, yerr_st, st_out_dict, output_file):
    with open(output_file, 'w') as f:
        f.write("Mean Metrics:\n")
        f.write(f"Accuracy: {st_out[:, 0]}\n")
        f.write(f"F1 Score: {st_out[:, 1]}\n")
        f.write(f"Precision: {st_out[:, 2]}\n")
        f.write(f"Recall: {st_out[:, 3]}\n")
        f.write(f"Standard Deviation of Accuracy: {yerr_st[:, 0]}\n")
        f.write(f"Standard Deviation of F1 Score: {yerr_st[:, 1]}\n")
        f.write(f"Standard Deviation of Precision: {yerr_st[:, 2]}\n")
        f.write(f"Standard Deviation of Recall: {yerr_st[:, 3]}\n\n")
        
        f.write("Detailed Metrics:\n")
        for folder, videos in st_out_dict.items():
            f.write(f"Folder: {folder}\n")
            for video, metrics in videos.items():
                f.write(f"  Video: {video}\n")
                f.write(f"    Accuracy: {metrics[0]}\n")
                f.write(f"    F1 Score: {metrics[1]}\n")
                f.write(f"    Precision: {metrics[2]}\n")
                f.write(f"    Recall: {metrics[3]}\n")
                f.write(f"    Standard Deviation of Accuracy: {metrics[4]}\n")
                f.write(f"    Standard Deviation of F1 Score: {metrics[5]}\n")
                f.write(f"    Standard Deviation of Precision: {metrics[6]}\n")
                f.write(f"    Standard Deviation of Recall: {metrics[7]}\n")
            f.write("\n")

def main():
    parser = argparse.ArgumentParser(description="Calculate metrics for YOLO model outputs.")
    parser.add_argument('--folder', type=str, required=True, help='Folder containing video files.')
    parser.add_argument('--v_list', type=str, required=True, help='List of video files.')

    args = parser.parse_args()
    folder = args.folder
    v_list = args.v_list.split()
    # results = process_folders(folder, v_list)
    # print(results)
    # path = "../yolov5/root"  # Hardcoded path to the data directory
    # folders = ["AccMPEG", "Sir_videos", "Secret"]  # Hardcoded list of folders
    output_file = v_list[0][:v_list[0].rfind("/")]+"/result.txt"  # Hardcoded output file path
    print(output_file)
    st_out, yerr_st, st_out_dict = process_folders(folder, v_list)
    save_results(st_out, yerr_st, st_out_dict, output_file)

    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--folder', type=str, default='', help='')
    # parser.add_argument('--v_list', type=list, default=[], help='')
    # main(parser.folder,parser.v_list)

# ['/mnt/d/IP/yolov5/root/AccMPEG/driving_3', '/mnt/d/IP/yolov5/root/AccMPEG/driving_4']
