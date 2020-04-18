from multiprocessing import Pool

from PIL import Image
from nbt import world, nbt

from lib import config, block_colours, biome_stats
import time


def nbt_to_dict(nbt_in):
    out = {}
    #print(dir(nbt_in), nbt_in.tag_info())
    if isinstance(nbt_in, nbt.TAG_Compound):
        for k in nbt_in:
            out[k] = nbt_to_dict(nbt_in[k])
        return out
    elif isinstance(nbt_in, (nbt.TAG_List, nbt.TAG_Byte_Array, nbt.TAG_Int_Array, nbt.TAG_Long_Array)):
        return [nbt_to_dict(obj) for obj in nbt_in]
    elif isinstance(nbt_in, (nbt.TAG_Int, nbt.TAG_String, nbt.TAG_Long, nbt.TAG_Byte)):
        try:
            return nbt_in.value
        except AttributeError:
            raise
    else:
        return nbt_in

def render_chunk(chunk_data):
    chunk_levels = [Image.new('RGBA', (16 * config.BLOCK_WIDTH, 16 * config.BLOCK_HEIGHT), (0, 0, 0, 0)) for i in
                    range(256)]
    drawn = 0
    chunk_sections = chunk_data['Sections']
    chunk_x = chunk_data['xPos']
    chunk_z = chunk_data['zPos']
    problem_chunk = False
    biomes = chunk_data.get('Biomes')
    #print(biomes)
    for section in chunk_sections:
        palette = section.get('Palette')
        section_y = section['Y']
        if palette is not None:
            super_long = 0
            block_states = section['BlockStates']
            bitsPerBlock = len(block_states) * 64 // 4096
            #print('there are',bitsPerBlock,'bits per block with',len(palette),'different blocks')
            num_longs = 0
            block_states.reverse()
            for long in block_states:
                long = int.from_bytes(long.to_bytes(8, byteorder='big', signed=True), byteorder='big', signed=False)
                super_long <<= 64
                super_long+=long
                num_longs += 1


            for rel_y in range(16):
                for rel_z in range(16):
                    for rel_x in range(16):
                        palette_index = (super_long >> (((rel_y * 16 + rel_z) * 16 + rel_x) * bitsPerBlock)) & (2**bitsPerBlock-1)
                        # super_long >>= bitsPerBlock
                        world_y = section_y * 16 + rel_y

                        surrounding_biomes = []
                        normal_biome = None

                        for block_biome_x in range(-1, 2):
                            for block_biome_z in range(-1, 2):
                                biome_x = (rel_x + block_biome_x) // 4
                                biome_y = world_y // 4
                                biome_z = (rel_z + block_biome_z)//4
                                if not (0 <= biome_x <= 4 and 0<= biome_z <=4):
                                    continue
                                biome_index = ((biome_z*4)+biome_x)*4 + biome_y
                                biome_data = biome_stats.biomes[biomes[biome_index]]
                                if block_biome_x == 0 and block_biome_z == 0:
                                    normal_biome = biome_data
                                    continue
                                surrounding_biomes.append(biome_data)
                        # print(bitsPerBlock, palette_index, len(palette),len(block_states), rel_x, rel_y, rel_z,palette_index.to_bytes(bitsPerBlock, 'big'))
                        try:
                            block_state = palette[palette_index]
                        except IndexError:
                            print('blegh', palette_index, len(palette))
                            continue
                        block_name = block_state.get('Name')
                        # print(block_state.get('Name'))
                        if block_name not in config.BLACKLIST_BLOCKS:
                            translated_name = config.TRANSLATE_BLOCK_TO_TEXTURE.get(block_name)
                            if translated_name is not None:
                                block_name = translated_name
                            try:
                                texture = block_colours.blocks[block_name]
                                #print(palette_index)
                                # chunk_levels[y].paste(, (actual_x * config.BLOCK_WIDTH, actual_z * config.BLOCK_HEIGHT))

                                if block_name.endswith('grass_block'):
                                    if config.BIOME_BLENDING:
                                        grass_colour = [0 ,0 , 0]
                                        for grass in surrounding_biomes:
                                            for i in range(3):
                                                grass_colour[i] += grass.grass_colour[i]
                                        grass_colour[0] //= len(surrounding_biomes)
                                        grass_colour[1] //= len(surrounding_biomes)
                                        grass_colour[2] //= len(surrounding_biomes)
                                    else:
                                        grass_colour = normal_biome.grass_colour

                                    texture = Image.blend(texture, Image.new('RGBA', (
                                    config.BLOCK_WIDTH, config.BLOCK_HEIGHT), tuple(grass_colour)), 0.5)
                                elif block_name.endswith('leaves') or block_name in config.FOLIAGE:
                                    if config.BIOME_BLENDING:
                                        foliage_colour = [0, 0, 0]
                                        for foliage in surrounding_biomes:
                                            for i in range(3):
                                                foliage_colour[i] += foliage.foliage_colour[i]
                                        foliage_colour[0] //= len(surrounding_biomes)
                                        foliage_colour[1] //= len(surrounding_biomes)
                                        foliage_colour[2] //= len(surrounding_biomes)
                                    else:
                                        foliage_colour = normal_biome.foliage_colour

                                    texture = Image.blend(texture,
                                                           Image.new('RGBA', (config.BLOCK_WIDTH, config.BLOCK_HEIGHT),
                                                                     tuple(foliage_colour)), 0.5)
                                elif block_name.endswith('water'):
                                    if config.BIOME_BLENDING:
                                        water_colour = [0, 0, 0]
                                        for water in surrounding_biomes:
                                            for i in range(3):
                                                water_colour[i] += water.water_colour[i]
                                        water_colour[0] //= len(surrounding_biomes)
                                        water_colour[1] //= len(surrounding_biomes)
                                        water_colour[2] //= len(surrounding_biomes)
                                    else:
                                        water_colour = normal_biome.water_colour

                                    texture = Image.blend(texture,
                                        Image.new('RGBA', (config.BLOCK_WIDTH, config.BLOCK_HEIGHT),
                                                  tuple(water_colour)), 0.5)
                                drawn += 1
                                block_data = block_state.get('Properties')
                                if block_data is not None:
                                    for key in block_data:
                                        if key == 'facing':
                                            facing = block_data[key]
                                            if facing == 'north':
                                                direction = 180
                                            elif facing == 'east':
                                                direction = 90
                                            elif facing == 'south':
                                                direction = 0
                                            elif facing == 'west':
                                                direction = 270
                                            elif facing == 'up':
                                                continue
                                            elif facing == 'down':
                                                continue
                                            else:
                                                raise Exception(f"Unknown direction {facing}")
                                            texture = texture.rotate(direction)
                                chunk_levels[world_y].paste(texture,
                                                            (rel_x * config.BLOCK_WIDTH, rel_z * config.BLOCK_HEIGHT))
                                assert 0 <= rel_x * config.BLOCK_WIDTH <= chunk_levels[world_y].width - config.BLOCK_WIDTH and 0 <= rel_z * config.BLOCK_HEIGHT <= chunk_levels[world_y].height - config.BLOCK_HEIGHT
                            except KeyError:
                                print(f'{block_name} not found')
    out = chunk_levels[0]
    #out.save(os.path.join(config.OUTPUT_DIRECTORY, f'{chunk_x}.{chunk_z}.0.png'))
    if drawn > 0:
        for l_num, level in enumerate(chunk_levels):
            # level.save(os.path.join(config.OUTPUT_DIRECTORY, f'level {l_num}.png'))
            out.alpha_composite(level)
    return ((chunk_x, chunk_z), out)

if __name__ == '__main__':
    thread_pool = Pool(14)
    #w = world.AnvilWorldFolder(r'C:\Users\dumpl\AppData\Roaming\.minecraft\saves\contraptions')
    w = world.AnvilWorldFolder(r'UWO_World')
    #w = world.AnvilWorldFolder(r'C:\Users\dumpl\AppData\Roaming\.minecraft\saves\Glitch Research')
    #w = world.AnvilWorldFolder(r'C:\Users\dumpl\AppData\Roaming\.minecraft\saves\New World (1)')
    #w = world.AnvilWorldFolder(r'Y:\iocage\jails\MineOS\root\var\games\minecraft\servers\UWO_Nerds\UWO_World')
    box = w.get_boundingbox()
    min_x = box.minx
    max_x = box.maxx
    min_z = box.minz
    max_z = box.maxz
    world_width = (max_x - min_x) * 16 * config.BLOCK_WIDTH
    world_height = (max_z - min_z) * 16 * config.BLOCK_HEIGHT

    out_image = Image.new('RGBA', (world_width, world_height))
    print('output image has size', (world_width, world_height))

    for i, r in enumerate(w.iter_regions()):
        region_position = (r.loc.x, r.loc.z)
        print(f'{i/len(w.regionfiles) * 100 :.2f}')
        cases = (nbt_to_dict(c.get('Level')) for c in r.iter_chunks())
        #print(next(cases))
        for chunk_pos, out in thread_pool.imap(render_chunk, cases):

                chunk_x, chunk_z = chunk_pos

                canvas_position = ((chunk_x - min_x) * 16 * config.BLOCK_WIDTH, (chunk_z - min_z) * 16 * config.BLOCK_HEIGHT)
                out_image.paste(out, canvas_position)
                #out.save(os.path.join(config.OUTPUT_DIRECTORY, f'{chunk_x}.{chunk_z}.png'))
                #chunk_levels[0].save(os.path.join(config.OUTPUT_DIRECTORY, f'{region_position[0]}.{region_position[1]}.{chunk_x}.{chunk_z}.png'))
                #print(f'region {region_position} chunk ({chunk_x}, {chunk_z}) drawn to {canvas_position} min_vals = {(min_x, min_z)}')
    out_image.save(f'out{int(time.time())}.png')
    out_image.convert(mode='P', palette=Image.ADAPTIVE).save(f'out_palletized{int(time.time())}.png')
    thread_pool.close()