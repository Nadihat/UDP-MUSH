import random
import math

def generate_perlin_noise(width, height, scale=10.0):
    """
    Generates a 2D grid of Perlin noise values.
    Since we don't have an external library, we implement a simple value noise
    interpolated to look somewhat like Perlin noise for terrain generation.
    """
    grid = [[0.0 for _ in range(height)] for _ in range(width)]
    
    # Random gradient vectors
    vectors = {}

    def get_gradient(x, y):
        if (x, y) not in vectors:
            angle = random.uniform(0, 2 * math.pi)
            vectors[(x, y)] = (math.cos(angle), math.sin(angle))
        return vectors[(x, y)]

    def dot_grid_gradient(ix, iy, x, y):
        grad = get_gradient(ix, iy)
        dx = x - ix
        dy = y - iy
        return (dx * grad[0] + dy * grad[1])

    def smoothstep(w):
        if w <= 0: return 0
        if w >= 1: return 1
        return w * w * (3.0 - 2.0 * w) # Cubic interpolation

    def lerp(a0, a1, w):
        return (1.0 - w) * a0 + w * a1

    def perlin(x, y):
        x0 = int(x)
        x1 = x0 + 1
        y0 = int(y)
        y1 = y0 + 1

        sx = x - x0
        sy = y - y0

        # Interpolate dot product values at corners
        n0 = dot_grid_gradient(x0, y0, x, y)
        n1 = dot_grid_gradient(x1, y0, x, y)
        ix0 = lerp(n0, n1, smoothstep(sx))

        n0 = dot_grid_gradient(x0, y1, x, y)
        n1 = dot_grid_gradient(x1, y1, x, y)
        ix1 = lerp(n0, n1, smoothstep(sx))

        value = lerp(ix0, ix1, smoothstep(sy))
        return value

    for x in range(width):
        for y in range(height):
            # Normalize coordinates
            nx = x / scale
            ny = y / scale
            grid[x][y] = perlin(nx, ny)
            
    return grid

def generate_rooms(width=32, height=24):
    """
    Generates rooms based on a 32x24 grid using Perlin noise for biomes.
    """
    rooms = {}
    noise_map = generate_perlin_noise(width, height, scale=5.0)
    
    # Biome definitions based on noise value (-1.0 to 1.0 approx)
    # < -0.3: Water
    # -0.3 to 0.0: Sand/Beach
    # 0.0 to 0.4: Grass/Forest
    # > 0.4: Mountain/Snow
    
    for x in range(width):
        for y in range(height):
            val = noise_map[x][y]
            room_id = f"{x}_{y}"
            
            name = "Unknown"
            description = "A mysterious place."
            items = {}
            
            if val < -0.2:
                name = f"Dark Water ({x}, {y})"
                description = "You are treading in dark, cold water. The current is strong here."
                biome = "water"
            elif val < 0.0:
                name = f"Sandy Beach ({x}, {y})"
                description = "Warm sand shifts beneath your feet. The sound of waves is near."
                biome = "sand"
            elif val < 0.2:
                name = f"Open Grassland ({x}, {y})"
                description = "You are in an open grassland. A gentle breeze rustles the tall grass."
                items = {}
                biome = "grassland"
            elif val < 0.4:
                name = f"Dense Forest ({x}, {y})"
                description = "Tall trees block out most of the light. The air smells of pine and earth."
                items = {"a pinecone": "A sticky pinecone fallen from a tree."}
                biome = "forest"
            else:
                name = f"Rocky Peak ({x}, {y})"
                description = "The air is thin and cold up here. Jagged rocks surround you."
                biome = "mountain"
                
            rooms[room_id] = {
                'name': name,
                'description': description,
                'items': items,
                'sitting_users': {},
                'exits': {}
            }

    # Link exits
    for x in range(width):
        for y in range(height):
            current_id = f"{x}_{y}"
            
            # North (y - 1)
            if y > 0:
                rooms[current_id]['exits']['north'] = f"{x}_{y-1}"
            # South (y + 1)
            if y < height - 1:
                rooms[current_id]['exits']['south'] = f"{x}_{y+1}"
            # West (x - 1)
            if x > 0:
                rooms[current_id]['exits']['west'] = f"{x-1}_{y}"
            # East (x + 1)
            if x < width - 1:
                rooms[current_id]['exits']['east'] = f"{x+1}_{y}"
                
    return rooms
