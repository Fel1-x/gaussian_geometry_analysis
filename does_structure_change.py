import os
import re
import sys
import math

def parse_input_orientation_table(lines, start_idx):
    """
    Parse an 'Input orientation:' table starting at lines[start_idx].
    Returns a list of tuples (center, atomic_number, x, y, z).
    """
    coords = []
    n = len(lines)
    dashed = re.compile(r'^\s*-{6,}\s*$')

    i = start_idx + 1
    while i < n and not dashed.match(lines[i]):  # find first dashed line
        i += 1
    if i >= n:
        return []
    i += 1
    while i < n and not dashed.match(lines[i]):  # skip header block
        i += 1
    if i >= n:
        return []
    i += 1  # first data line

    while i < n:
        line = lines[i].strip()
        if not line or dashed.match(line):
            break
        parts = line.split()
        if len(parts) >= 6:
            try:
                center = int(parts[0])
                atomic_number = int(parts[1])
                x, y, z = map(float, parts[-3:])
                coords.append((center, atomic_number, x, y, z))
            except Exception:
                break
        else:
            break
        i += 1
    return coords

def closest_atom_to_atom(coords, target_atomic_number, reference_atomic_number):
    """
    Return the center number of the reference atom closest to the first target atom.
    Returns None if either atom type is absent.
    """
    targets = [(c, x, y, z) for c, an, x, y, z in coords if an == target_atomic_number]
    refs = [(c, x, y, z) for c, an, x, y, z in coords if an == reference_atomic_number]

    if not targets or not refs:
        return None

    t_center, tx, ty, tz = targets[0]
    best_center = None
    best_d2 = float('inf')

    for r_center, rx, ry, rz in refs:
        dx, dy, dz = tx - rx, ty - ry, tz - rz
        d2 = dx*dx + dy*dy + dz*dz
        if d2 < best_d2:
            best_d2 = d2
            best_center = r_center

    return best_center

def analyze_log_file(path, target_an, ref_an):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    input_re = re.compile(r'^\s*Input orientation:\s*$')
    opt_re = re.compile(r'^\s*Optimization completed\.\s*$')
    stationary_re = re.compile(r'^\s*--\s*Stationary point found\.\s*$')

    first_center = None
    for i, line in enumerate(lines):
        if input_re.match(line):
            coords = parse_input_orientation_table(lines, i)
            first_center = closest_atom_to_atom(coords, target_an, ref_an)
            break

    post_center = None
    for i, line in enumerate(lines):
        if opt_re.match(line):
            j = i + 1
            found_stationary = False
            while j < min(len(lines), i + 50):
                if stationary_re.match(lines[j]):
                    found_stationary = True
                    break
                j += 1
            if not found_stationary:
                continue

            k = j + 1
            while k < len(lines):
                if input_re.match(lines[k]):
                    coords = parse_input_orientation_table(lines, k)
                    post_center = closest_atom_to_atom(coords, target_an, ref_an)
                    break
                k += 1
            break

    return first_center, post_center

def analyze_directory_logs(directory, target_an, ref_an, show_only_no=False):
    """
    Print whether Br’s closest carbon is the same before vs after optimisation.
    If show_only_no=True, only print cases where it changes (NO).
    """
    tot = 0
    tot_no = 0
    if not os.path.isdir(directory):
        raise ValueError(f"Not a directory: {directory}")

    for fname in sorted(os.listdir(directory)):
        if not fname.lower().endswith('.log'):
            continue
        path = os.path.join(directory, fname)
        if not os.path.isfile(path):
            continue

        tot += 1

        try:
            first_center, post_center = analyze_log_file(path, target_an, ref_an)
        except Exception as e:
            print(f"{fname}: ERROR reading file: {e}")
            continue

        # If Br (or C) absent in both contexts, print nothing.
        if first_center is None and post_center is None:
            continue

        same = (first_center is not None and
                post_center is not None and
                first_center == post_center)

        if same:
            verdict = 'YES'
        elif first_center is not None and post_center is not None:
            verdict = 'NO'
            tot_no += 1
        else:
            verdict = 'N/A'


        if show_only_no and verdict != 'NO':
            continue

        def fmt_center(c):
            return f"C#{c}" if c is not None else "N/A"

        print(f"{fname}: first closest = {fmt_center(first_center)}; after optimisation = {fmt_center(post_center)}; same atom? {verdict}")
    print(f"Total files: {tot}, total NOs: {tot_no}")

if __name__ == "__main__":
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print("Usage: python does_structure_change.py <log_directory> <target_atomic_number> <reference_atomic_number> [--only-no]")
        sys.exit(2)

    logdir = sys.argv[1]
    target_an = int(sys.argv[2])
    ref_an = int(sys.argv[3])
    only_no = (len(sys.argv) == 5 and sys.argv[4] == "--only-no")

    analyze_directory_logs(logdir, target_an, ref_an, show_only_no=only_no)