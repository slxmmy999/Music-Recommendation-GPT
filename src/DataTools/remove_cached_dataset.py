import os

files_dir = "./dataset"
files = os.listdir(files_dir)

for file in files:
    if file.startswith("cached"):
        print(f"Removing {file}...")
        pathto = os.path.join(files_dir, file)
        os.remove(pathto)

print("Finished!")