from PIL import Image
import os
from lib import config

blocks = {}

for file in os.listdir(config.TEXTURES_DIRECTORY):
    if file.endswith('.png'):
        image_raw = Image.open(os.path.join(config.TEXTURES_DIRECTORY, file)).crop((0, 0, 16, 16))
        scaled_image = image_raw.resize((config.BLOCK_WIDTH, config.BLOCK_HEIGHT))
        stripped_filename = file[:-4]
        if stripped_filename.endswith('_top'):
            stripped_filename = stripped_filename[:-4]
        elif stripped_filename.endswith('_flow'):
            stripped_filename = stripped_filename[:-5]
        elif stripped_filename == 'magma':
            stripped_filename +='_block'
        blocks['minecraft:'+stripped_filename] = scaled_image
print(f'loaded {len(blocks)} textures')