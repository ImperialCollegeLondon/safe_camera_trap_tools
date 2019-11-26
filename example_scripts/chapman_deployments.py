import os
import re
from itertools import groupby
import safe_camera_trap_tools as sctt

# Phil's folders are arranged as:
# /201X/Block/Loc
# /201X/Block/Loc Calib

copy = False

paths = []

year_folders = ['Chapman_camera_traps/2015', 
                'Chapman_camera_traps/2016', 
                'Chapman_camera_traps/2017']

for yrf in year_folders:
    for path, _, _ in os.walk(yrf):
        paths.append(path)

# Reduce to the image folders - anything with a directory after Block
regex = re.compile('[0-9]{4}/[-0-9A-Z]+/')
image_folders = [p for p in paths if regex.search(p) is not None]

# Remove some problem folders:
bad = []
# Mangled date and time stamps - no species present
bad.append('Chapman_camera_traps/2015/D100-2/D100-2-33 (1)')
# Empty directory
bad.append('Chapman_camera_traps/2016/D100-1/D100-1-22/')

image_folders = [p for p in image_folders if p not in bad]

# Group them by year/block/location
image_folders.sort()
regex = re.compile('[0-9]{4}/[-0-9A-Z]+/[-0-9A-Z]+')
image_group = [regex.search(p).group() for p in image_folders]

groups = {}
for ky, gp in groupby(zip(image_group, image_folders), key=lambda x: x[0]):
    groups[ky] = [g[1] for g in list(gp)]

# Now process each group
for ky, dirs in groups.items():
    
    # separate in image and calib directories
    image_dirs, calib_dirs = [], []
    for d in dirs:
        if d.endswith('CALIB'):
            calib_dirs.append(d)
        else:
            image_dirs.append(d)
    
    # process the deployment
    location = os.path.basename(ky)
    year = re.search('^[0-9]{4}', ky).group()
    outdir = os.path.join('deployments', year)
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    
    gathered = sctt.gather_deployment_files(image_dirs, location, calib_dirs=calib_dirs)
    deployment_dir = sctt.create_deployment(gathered, output_root=outdir)
    
    # These files have already been annotated, so extract the deployment data
    # into the deployment folder
    sctt.extract_deployment_data(deployment_dir)