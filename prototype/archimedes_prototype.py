#!/usr/bin/env python3
"""
PROJECT ARCHIMEDES - Prototype: Multi-Agent Scientific Reasoning Engine
Bio Pilot: Microbial Growth Curve Analysis & Hypothesis Testing

Simulates a multi-agent system for low-risk bio data analysis.
Uses synthetic logistic growth data mimicking public E. coli datasets.
Agents: Orchestrator, HypothesisGenerator, Analyst, Critic, KnowledgeAgent
"""

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy import stats
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib

def logistic_growth(t, K, r, t0, A0=0.01):
    return K / (1 + (K / A0 - 1) * np.exp(-r * (t - t0)))

def generate_synthetic_growth_data(n_conditions=5, n_reps=4, n_timepoints=48, seed=42):
    np.random.seed(seed)
    conditions = ['M9_glucose', 'M9_glycerol', 'LB', 'M9_glucose_lowN', 'M9_acetate']
    base_params = {
        'M9_glucose': {'K': 1.2, 'r': 0.45, 't0': 2.0},
        'M9_glycerol': {'K': 0.9, 'r': 0.32, 't0': 3.5},
        'LB': {'K': 1.8, 'r': 0.65, 't0': 1.5},
        'M9_glucose_lowN': {'K': 0.7, 'r': 0.28, 't0': 4.0},
        'M9_acetate': {'K': 0.6, 'r': 0.22, 't0': 5.0},
    }
    records = []
    for cond in conditions[:n_conditions]:
        p = base_params[cond]
        for rep in range(n_reps):
            t = np.linspace(0, 24, n_timepoints)
            noise = np.random.normal(0, 0.03, n_timepoints)
            od = logistic_growth(t, p['K'] * (1 + np.random.normal(0, 0.05)), p['r'] * (1 + np.random.normal(0, 0.08)), p['t0'] + np.random.normal(0, 0.3)) + noise
            od = np.clip(od, 0.001, None)
            for ti, odi in zip(t, od):
                records.append({'condition': cond, 'replicate': rep, 'time_h': round(ti, 2), 'od600': round(odi, 4), 'strain': 'Ecoli_BW25113'})
    return pd.DataFrame(records)

# ... (full agent classes and Orchestrator as previously defined; see full version in local artifacts)
print('Prototype ready. Run the full script for complete agents.')
