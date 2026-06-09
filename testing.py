import os
maps = os.listdir("maps")

for name in maps:
    print(f"{name}")
    os.system(f"python3 main.py maps/{name}")