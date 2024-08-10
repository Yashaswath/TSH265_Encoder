# TSH265_Encoder
A camera side encoder using H265 encoder for traffic surveillance videos.

## How to setup the repository

```
git clone https://github.com/Yashaswath/TSH265_Encoder.git
```
```
cd TSH265_Encoder
```
```
git submodule update --init --recursive
```
This installs the all the required repositories.

# Set-up environment

## Build ffmpeg from source

After that, ```cd``` into the repo and run ```build.sh```. It takes time to compile. If you compiled the code successfully, you should see something like
```
INSTALL libavutil/libavutil.pc
```
at the end.

Then, inside x264/encoder/encoder.c, search for ```/tank```, and you'll see
```C++
    // Qizheng: add qp matrix file here
    h->operation_mode_file = x264_fopen("/tank/kuntai/code/operation_mode_file", "r");
    fscanf(h->operation_mode_file, "%d,", &h->operation_mode_flag);
    h->qp_matrix_file = x264_fopen("/tank/kuntai/code/qp_matrix_file", "r");
```
change the two hard-coded paths (/tank/kuntai/code/...) to $DIR/myh264/... (the path must be absolute path), and rerun build.sh (the compilation will take much less time this time, don't worry.)

## Set up conda environment

Then, install the conda environment through the ```conda_env.yml```:
```bash
conda env create -f h265_env.yml
```

Then, activate the installed environment:
```bash
conda activate accmpeg
```

To finish configuring the environment, you have to install `pytorch` and `torchvision` (Check https://pytorch.org/get-started/locally/ for the installation command; we used `pytorch=1.8.2` with `cuda 11.1` to replicate the results) and `detectron2` (check https://github.com/facebookresearch/detectron2/blob/main/INSTALL.md to find a version that matches pytorch and cuda). **PLease install them THROUGH `pip`** rather than `conda` (since `conda will` install an ancient version of torchvision that triggers wierd bugs).

The procedure above will automatically install a old version ```ffmpeg```. We need to renew it. Please download the static version of ffmpeg through https://johnvansickle.com/ffmpeg/ and use the ffmpeg binary inside to replace previous ffmpeg binary (you can check the location of it thorugh ```which ffmpeg```.)
Now go to the AccMPEG folder using ```cd AccMPEG```

## Edit the config file

Then, ```cd ..``` and open ```settings.toml```:
```bash
vim settings.toml
```
and edit the value of ```x264_dir``` to $DIR/myh264/

following this add your

update the path used in ```batch_blackgen_roi.py``` where ```compress_blackgen_roi.py``` is called
```
f"--maskgen_file {x264_dir}/../video-compression/maskgen/{filename}.py --visualize_step_size {visualize_step_size}"
```
replace ```{x264_dir}/../video-compression/maskgen/{filename}.py``` to ```maskgen/{filename}.py```
after installing add this to batch_blackgen_roi.py
Now to the top of the ```batch_blackgen_roi.py``` add in 
```
import argparse

parser = argparse.ArgumentParser(description='Generate an H264 encoded video by AccMPEG technique')
parser.add_argument('directory', type=str, help='Directory containing input files')

args = parser.parse_args()
```
Following which replace this line 
```
v_list = ["artifact/dashcamcropped_%d" % i for i in range(1, 2)]
```
with 
```
def process_directory(directory):
    v_list=[]
    for filename in os.listdir(directory):
        if filename.endswith('.mp4') and not filename.endswith('qp_30.mp4') and not filename.endswith('qp_40.mp4') and not filename.endswith('FPN.mp4') and not filename.endswith('_roi.mp4'):
            input_file = os.path.join(directory, filename)
            v_list.append(input_file.replace('.mp4',''))
    return v_list
v_list = process_directory(args.directory) in place of v_list=[]
```
If the resolution of the video changes you will need to update mask dimension in the `mask_gen.py` and `compress_blackgen_roi.py` files.
```
mask_shape = [
        len(videos[-1]),
        1,
        720 // args.tile_size,
        1280 // args.tile_size,
    ]
```

following this install kvazaar using their steps need to install the required packages

## Compiling Kvazaar
If you have trouble regarding compiling the source code, please make an
[issue](https://github.com/ultravideo/kvazaar/issues) about in Github.
Others might encounter the same problem and there is probably much to
improve in the build process. We want to make this as simple as
possible.

### Autotools
Depending on the platform, some additional tools are required for compiling Kvazaar with autotools.
For Ubuntu, the required packages are `automake autoconf libtool m4 build-essential`.


Run the following commands to compile and install Kvazaar.

    ./autogen.sh
    ./configure
    make
    sudo make install
    sudo ldconfig

See `./configure --help` for more options.
**When building shared library with visual studio the tests will fail to link, the main binary will still work**


Move all the python files from the home directory to inside the `AccMPEG` folder
Then just call on the video_encoder.py file with the required parameters to get a H.265 encoded .mp4 file.
```
python video_encoder.py /path/to/videos_folder
```
This command will search for the all the files in that directory and apply the encoding on them as per the parameters specified.
If you want to use the AccMPEG H.264 encoding you will need to sen the `--encoder` flag with the above command


## Result Directory
To generate results we call upon neet to create a new enviorment present inside the `result` folder
Then, install the conda environment through the ```conda_env.yml```:
```bash
conda env create -f yolov5_env.yml
```

Then, activate the installed environment:
```bash
conda activate yolov5_env
```
This is used to compare the two original video with the encode for object detection.

The video directory shoul dbe of the format where we have ```videos``` folder is present and inside it there are multiple dataset folder inside the and within each dataset folder thier will be a `_roi.mp4` videos and `.mp4`.
```
python accuracy_metrics.py /path/to/folder_containing_dataset_folder.
```
Using this command we can generate the comparison graphs.
