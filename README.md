# Gaussian 17 Geometry Analysis

A Python tool for checking how **Gaussian 17 geometry optimisations** may affect molecular structures. It extracts coordinates from tables within .log files and compares which **reference atom** is closest to a chosen **target atom** before and after optimisation.

---

## Usage

```bash
python does_structure_change.py <log_directory> <target_atomic_number> <reference_atomic_number>
```

Example (Br = 35, C = 6):

```bash
python does_structure_change.py ./logs 35 6
```

Show only cases where the closest atom changes:

```bash
python does_structure_change.py ./logs 35 6 --only-no
```

---

## Output

```
file1.log: first closest = A#12; after optimisation = A#14; same atom? NO
file2.log: first closest = A#8; after optimisation = A#8; same atom? YES
Total files: 20, total NOs: 7
```

---

## Requirements

- Python 3.7+
- No external libraries

---
