from lib import config
from PIL import Image

grass_palette = Image.open(config.GRASS_PALETTE)
foliage_palette = Image.open(config.FOLIAGE_PALETTE)

class Biome:
    def __init__(self, name, temperature, rainfall = None, water_colour = (25, 46, 89), grass_override=None):
        self.temperature = temperature
        self.name = name
        self.rainfall = rainfall if rainfall is not None else temperature
        self.water_colour = water_colour
        self.grass_override = grass_override

    @property
    def adjusted_temperature(self):
        return max(0, min(1, self.temperature))

    @property
    def adjusted_rainfall(self):
        return max(0, min(1, self.rainfall)) * self.adjusted_temperature

    @property
    def grass_colour(self):
        if self.grass_override is not None:
            return self.grass_override
        x = int((1 - self.adjusted_temperature) * (grass_palette.width-1))
        y = int((1 - self.adjusted_rainfall) * (grass_palette.height-1))
        return grass_palette.getpixel((x, y))

    @property
    def foliage_colour(self):
        x = int((1 - self.adjusted_temperature) * (foliage_palette.width-1))
        y = int((1 - self.adjusted_rainfall) * (foliage_palette.height-1))
        return foliage_palette.getpixel((x, y))

biomes = {
    #snowy
    12:Biome("Snowy Tundra", 0.0),
    140:Biome("Ice Spikes", 0.0),
    30:Biome("Snowy Taiga", -0.5),
    158:Biome("Snowy Taiga Mountains", -0.5),
    18:Biome("Snowy Taiga Hills", -0.5),
    11:Biome("Frozen River", 0.0, water_colour=(57,56,201)),
    26:Biome("Snowy Beach", 0.05),
    #cold
    3:Biome("Mountains", 0.2),
    131:Biome("Gravelly Mountains", 0.2),
    34:Biome("Wooded Mountains", 0.2),
    13:Biome("Wooded Hills", 0.2),
    162:Biome("Gravelly Mountains+", 0.2),
    5:Biome("Taiga", 0.25),
    133:Biome("Taiga Mountains", 0.25),
    17:Biome("Taiga Hills", 0.25),
    32:Biome("Giant Tree Taiga", 0.3),
    33:Biome("Giant Tree Taiga Hills", 0.3),
    160:Biome("Giant Spruce Taiga", 0.25),
    161:Biome("Giant Spruce Taiga Hills", 0.25),
    25:Biome("Stone Shore", 0.2),
    #Temperate/Lush
    1:Biome("Plains", 0.8),
    129:Biome("Sunflower Plains", 0.8),
    4:Biome("Forest", 0.7),
    132:Biome("Flower Forest", 0.7),
    27:Biome("Birch Forest", 0.6),
    28:Biome("Birch Forest Hills", 0.6),
    155:Biome("Tall Birch Forest", 0.7),
    156:Biome("Tall Birch Hills", 0.7),
    29:Biome("Dark Forest", 0.7),
    157:Biome("Dark Forest Hills", 0.7),
    6:Biome("Swamp", 0.8, water_colour=(97,123,100), grass_override=(76,118,60)),
    134:Biome("Swamp Hills", 0.8, water_colour=(97,123,100), grass_override=(76,118,60)),
    21:Biome("Jungle", 0.95),
    19:Biome("Jungle Hills", 0.95),
    149:Biome("Modified Jungle", 0.95),
    23:Biome("Jungle Edge", 0.95),
    151:Biome("Modified Jungle Edge", 0.95),
    168:Biome("Bamboo Jungle", 0.95),
    7:Biome("River", 0.5, water_colour=(63,118,228)),
    16:Biome("Beach", 0.8),
    14:Biome("Mushroom Fields", 0.9),
    15:Biome("Mushroom Field Shore", 0.9),
    # Dry/Warm Biomes
    2:Biome("Desert", 2.0),
    22:Biome("Desert Hills", 2.0),
    130:Biome("Desert Lakes", 2.0),
    35:Biome("Savanna", 1.2),
    163:Biome("Shattered Savanna", 1.1),
    37:Biome("Bandlands", 2.0, grass_override=(144,129,77)),
    165:Biome("Eroded Badlands", 2.0, grass_override=(144,129,77)),
    38:Biome("Wooded Badlands Plateau", 2.0, grass_override=(144,129,77)),
    166:Biome("Modified Wooded Badlands Plateau", 2.0, grass_override=(144,129,77)),
    36:Biome("Badlands Plateau", 2.0, grass_override=(144,129,77)),
    39:Biome("Savanna Pleateau", 1.0),
    164:Biome("Modified Badlands Plateau", 2.0, grass_override=(144,129,77)),
    167:Biome("Shattered Savanna Plateau", 1.0),

    #Ocean Biomes
    44:Biome("Warm Ocean", 0.5, water_colour=(67,213,238)),
    45:Biome("Lukewarm Ocean", 0.5, water_colour=(69,173,242)),
    48:Biome("Deep Lukewarm Ocean", 0.5),
    0:Biome("Ocean", 0.5, water_colour=(63,118,228)),
    24:Biome("Deep Ocean", 0.5),
    46:Biome("Cold Ocean", 0.5, water_colour=(61,87,214)),
    49:Biome("Deep Cold Ocean", 0.5),
    10:Biome("Frozen Ocean", 0.0),
    50:Biome("Deep Frozen Ocean", 0.5, water_colour=(57,56,201)),

    #Other
    127:Biome("The Void", 0.5)

}