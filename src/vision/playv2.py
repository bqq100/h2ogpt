import os

import filelock
from diffusers import DiffusionPipeline
import torch

from src.utils import makedirs
from src.vision.sdxl import get_device


def get_pipe_make_image(gpu_id):
    device = get_device(gpu_id)

    pipe = DiffusionPipeline.from_pretrained(
        # "playgroundai/playground-v2-1024px-aesthetic",
        "playgroundai/playground-v2.5-1024px-aesthetic",
        torch_dtype=torch.float16,
        use_safetensors=True,
        add_watermarker=False,
        variant="fp16"
    ).to(device)

    return pipe


def make_image(prompt, filename=None, gpu_id='auto', pipe=None,
               image_guidance_scale=5.0,  # 5 is optimal for playv2.5
               image_size=(1024, 1024),
               image_quality='standard',
               image_num_inference_steps=50,
               max_sequence_length=512):
    if pipe is None:
        pipe = get_pipe_make_image(gpu_id=gpu_id)

    if image_quality == 'manual':
        # listen to guidance_scale and num_inference_steps passed in
        pass
    else:
        if image_quality == 'quick':
            image_num_inference_steps = 10
            image_size = (512, 512)
        elif image_quality == 'standard':
            image_num_inference_steps = 20
        elif image_quality == 'quality':
            image_num_inference_steps = 50

    lock_type = 'image'
    base_path = os.path.join('locks', 'image_locks')
    base_path = makedirs(base_path, exist_ok=True, tmp_ok=True, use_base=True)
    lock_file = os.path.join(base_path, "%s.lock" % lock_type)
    makedirs(os.path.dirname(lock_file))  # ensure made
    with filelock.FileLock(lock_file):
        image = pipe(prompt=prompt,
                     height=image_size[0],
                     width=image_size[1],
                     num_inference_steps=image_num_inference_steps,
                     max_sequence_length=max_sequence_length,
                     guidance_scale=image_guidance_scale,
                     ).images[0]
    if filename:
        image.save(filename)
        return filename
    return image
