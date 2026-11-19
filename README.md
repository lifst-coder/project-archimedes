# PROJECT ARCHIMEDES
Autonomous Scientific Discovery Engine

See ARCHIMEDES_Report.md for the full technical report (in Korean).

## Prototype
- `prototype/archimedes_prototype.py`: Multi-agent system for hypothesis generation, analysis, and critique on synthetic microbial growth data.
- `prototype/test_prototype.py`: Unit tests.
- `prototype/run_result.json`: Example run output.

Run the prototype:
```bash
pip install numpy pandas scipy
python prototype/archimedes_prototype.py
python prototype/test_prototype.py
```

Data is generated on the fly by the script (synthetic E. coli growth curves).
