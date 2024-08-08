import argparse
import gc
import importlib
import logging

import coloredlogs
import enlighten
import seaborn as sns
import torch
import torch.nn.functional as F
import torchvision.transforms as T
from torch.utils.tensorboard import SummaryWriter
from torchvision import io
from tqdm import tqdm

from AccMPEG.dnn.dnn_factory import DNN_Factory
from AccMPEG.utilities.mask_utils import *
from AccMPEG.utilities.timer import Timer
from AccMPEG.utilities.video_utils import get_qp_from_name, read_videos
from AccMPEG.utilities.visualize_utils import (
    visualize_dist_by_summarywriter,
    visualize_heat_by_summarywriter,
)

thresh_list = [0.01, 0.02, 0.05, 0.1, 0.2, 0.4, 0.8]

sns.set()


def main(args):

    gc.enable()

    # initialize
    logger = logging.getLogger("blackgen")
    logger.addHandler(logging.FileHandler("blackgen.log"))
    torch.set_default_tensor_type(torch.FloatTensor)

    # read the video frames (will use the largest video as ground truth)
    videos, bws, video_names = read_videos(args.inputs, logger, sort=True)
    videos = videos
    bws = [0, 1]
    qps = [get_qp_from_name(video_name) for video_name in video_names]

    # construct applications
    app = DNN_Factory().get_model(args.app)
    print(len(videos), video_names, args.inputs)

    maskgen_spec = importlib.util.spec_from_file_location(
        "maskgen", args.maskgen_file
    )
    maskgen = importlib.util.module_from_spec(maskgen_spec)
    maskgen_spec.loader.exec_module(maskgen)
    mask_generator = maskgen.FCN()
    mask_generator.load(args.path)
    mask_generator.cuda()

    cached_images = []

    height_res=args.input_res.split('x')[1]
    width_res=args.input_res.split('x')[0]
    # construct the mask
    mask_shape = [
        len(videos[-1]),
        1,
        height_res // args.tile_size,
        width_res // args.tile_size,
    ]
    mask = torch.ones(mask_shape).float()

    # construct the writer for writing the result
    writer = SummaryWriter(f"runs/{args.app}/{args.output}")

    for temp in range(1):

        logger.info(f"Processing application")
        progress_bar = enlighten.get_manager().counter(
            total=len(videos[-1]), desc=f"{app.name}", unit="frames"
        )

        losses = []
        f1s = []

        for fid, (video_slices, mask_slice) in enumerate(
            zip(zip(*videos), mask.split(1))
        ):
            
            progress_bar.update()
            lq_image, hq_image = video_slices[0], video_slices[1]

            with torch.no_grad():
                hq_image = hq_image.cuda()
                mask_gen = mask_generator(hq_image)
                mask_gen = mask_gen.softmax(dim=1)[:, 1:2, :, :]

                # Debugging: print shapes
                print(f"hq_image shape: {hq_image.shape}")
                print(f"mask_gen shape: {mask_gen.shape}")
                print(f"mask_slice shape: {mask_slice.shape}")

                # Resize mask_gen to match mask_slice shape if necessary
                if mask_gen.shape[2:] != mask_slice.shape[2:]:
                    mask_gen = F.interpolate(mask_gen, size=mask_slice.shape[2:], mode='bilinear', align_corners=False)
                
                mask_slice[:, :, :, :] = mask_gen

            if fid % args.visualize_step_size == 0:

                image = T.ToPILImage()(video_slices[-1][0, :, :, :])
                cached_images.append(image)

                mask_slice = mask_slice.detach().cpu()

                writer.add_image("raw_frame", video_slices[-1][0, :, :, :], fid)

                visualize_heat_by_summarywriter(
                    image, mask_slice, "inferred_saliency", writer, fid, args,
                )

                visualize_dist_by_summarywriter(
                    mask_slice, "saliency_dist", writer, fid,
                )

                mask_slice = sum(
                    [(mask_slice > thresh).float() for thresh in thresh_list]
                )

                visualize_heat_by_summarywriter(
                    image, mask_slice, "binarized_saliency", writer, fid, args,
                )

        logger.info("In video %s", args.output)
        logger.info("The average loss is %.3f" % torch.tensor(losses).mean())

    mask.requires_grad = False

    for mask_slice in tqdm(mask.split(args.smooth_frames)):

        num = mask_slice.shape[0]

        mask_slice[:, :, :, :] = (
            mask_slice[0:1, :, :, :] + mask_slice[num - 1 : num, :, :, :]
        ) / 2

    if args.bound is not None:
        mask = (mask > args.bound).float()
    else:
        mask = (mask > percentile(mask, args.perc)).float()

    mask = dilate_binarize(mask, 0.5, args.conv_size, cuda=False)

    mask = postprocess_mask(mask)

    logger.info("logging actual quality assignment...")

    for fid, mask_slice in enumerate(tqdm(mask.split(1))):

        if fid % args.visualize_step_size == 0:

            image = cached_images[0]

            cached_images = cached_images[1:]
            visualize_heat_by_summarywriter(
                image,
                mask_slice.cpu().detach().float(),
                "quality_assignment",
                writer,
                fid,
                args,
            )

    assert args.hq != -1 and args.lq != -1
    assert "blackgen" not in args.output and "dual" not in args.output

    mask = (mask > 0.5).int()
    mask = torch.where(
        mask == 1,
        args.hq * torch.ones_like(mask),
        args.lq * torch.ones_like(mask),
    )

    # Assuming mask is your 4D tensor (e.g., torch.Size([batch_size, channels, height, width]))
    print(mask.size())
    print(mask[0, 0, 10, :])

    # Convert the tensor to a numpy array
    mask_np = mask.cpu().numpy()

    # Set numpy print options to avoid truncation
    import numpy as np
    np.set_printoptions(threshold=np.inf)

    # Define the file path where you want to save the values
    output_file_path = str(args.source)+"_mask_values.txt"

    # Open the file in write mode and write the values frame by frame
    with open(output_file_path, 'w') as f:
        for b in range(mask_np.shape[0]):
            for c in range(mask_np.shape[1]):
                np.savetxt(f, mask_np[b, c, :, :], fmt='%d')

    # Optionally, print the file path to confirm
    print(f"Mask values saved to {output_file_path}")

    #h264_roi_compressor_segment(mask, args, logger)

    #masked_video = generate_masked_video(mask, videos, bws, args)
    #SSwrite_video(masked_video, args.output, logger)


if __name__ == "__main__":

    # set the format of the logger
    coloredlogs.install(
        fmt="%(asctime)s [%(levelname)s] %(name)s:%(funcName)s[%(lineno)s] -- %(message)s",
        level="INFO",
    )

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--app", type=str, help="The name of the model.", required=True,
    )

    parser.add_argument(
        "-i",
        "--inputs",
        nargs="+",
        help="The video file names. The largest video file will be the ground truth.",
        required=True,
    )
    parser.add_argument(
        "-g",
        "--ground_truth",
        help="The video file names. The largest video file will be the ground truth.",
        type=str,
        required=True,
    )
    parser.add_argument("--batch_size", type=int, default=1)
    parser.add_argument(
        "-s",
        "--source",
        type=str,
        help="The original video source.",
        required=True,
    )
    parser.add_argument(
        "-o", "--output", type=str, help="The output name.", required=True
    )
    parser.add_argument(
        "--confidence_threshold",
        type=float,
        help="The confidence score threshold for calculating accuracy.",
        default=0.7,
    )
    parser.add_argument(
        "--iou_threshold",
        type=float,
        help="The IoU threshold for calculating accuracy in object detection.",
        default=0.5,
    )
    parser.add_argument(
        "--tile_size", type=int, help="The tile size of the mask.", default=8
    )
    parser.add_argument(
        "--maskgen_file",
        type=str,
        help="The file that defines the neural network.",
        required=True,
    )
    parser.add_argument(
        "-p",
        "--path",
        type=str,
        help="The path of pth file that stores the generator parameters.",
        required=True,
    )

    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "--bound", type=float, help="The lower bound for the mask",
    )
    action.add_argument(
        "--perc", type=float, help="The percentage of modules to be encoded."
    )
    parser.add_argument(
        "--smooth_frames",
        type=int,
        help="Proposing one single mask for smooth_frames many frames",
        default=10,
    )
    parser.add_argument(
        "--visualize_step_size",
        type=int,
        help="Proposing one single mask for smooth_frames many frames",
        default=100,
    )
    parser.add_argument("--conv_size", type=int, default=1)
    parser.add_argument("--hq", type=int, default=-1)
    parser.add_argument("--lq", type=int, default=-1)
    parser.add_argument('--input_res', type=str, default="1280x720", help='Input Resolution of video')


    # parser.add_argument('--mask', type=str,
    #                     help='The path of the ground truth video, for loss calculation purpose.', required=True)

    args = parser.parse_args()

    main(args)

