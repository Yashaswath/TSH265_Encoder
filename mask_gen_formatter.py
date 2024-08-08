import numpy as np
import argparse

def read_and_parse_file(file_path,input_res,tile_size):
    matrices = []
    n_rows=int(int(input_res.split('x')[1])/tile_size)
    with open(file_path, 'r') as f:
        matrix = []
        for line in f:
            row = np.fromstring(line.strip(), sep=' ')
            matrix.append(row)
            if len(matrix) == n_rows:  # One complete matrix is 60 rows
                matrices.append(np.array(matrix))
                matrix = []
    return matrices

def flatten_matrix_raster_order(matrix):
    return [element for row in matrix for element in row]

def convert_value(x,low_qp,high_qp):
    if x == low_qp:
        return "0"
    elif x == high_qp:
        return str(high_qp-low_qp)
    else:
        return str(x)

def process_matrices(matrices):
    flatten_matrices = []
    for matrix in matrices:
        flatten_matrix = flatten_matrix_raster_order(matrix)
        flatten_matrices.append(flatten_matrix)
    return flatten_matrices

def write_flattened_matrices(input_path,flatten_matrices,input_res, tile_size,low_qp,high_qp):
    output_path=input_path.replace('.txt','_formatted.txt')
    input_res=input_res.split('x')
    header = str(int(int(input_res[0])/tile_size))+" "+str(int(int(input_res[1])/tile_size))
    with open(output_path, "w") as file:
        for frame in flatten_matrices:
            file.write(header)
            file.write("\n")
            numbers = " ".join(convert_value(num,low_qp,high_qp) for num in frame)
            file.write(numbers)
            file.write("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process and flatten matrices from a file.')
    parser.add_argument('directory', type=str, help='Directory containing input files')
    parser.add_argument('--input_res', type=str, default='1280x720', help='Input resolution (default: 1280x720)')
    parser.add_argument('--low_qp', type=int, default=30, help='Lower Value of QP (default: 30)')
    parser.add_argument('--high_qp', type=int, default=40, help='Higher Value of QP (default: 40)')
    parser.add_argument('--tile_size', type=int, default=16, help='Size of each tile in a single frame (default: 16)')

    args = parser.parse_args()

    matrices = read_and_parse_file(args.directory,args.input_res,args.tile_size)
    flatten_matrices = process_matrices(matrices)
    write_flattened_matrices(args.directory,flatten_matrices,args.input_res,args.tile_size,args.low_qp,args.high_qp)

