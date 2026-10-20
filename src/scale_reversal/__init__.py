"""Computations of the accompanying manuscript on scale reversal.

Every computation calls :mod:`qrq` (pinned to version 0.2.0). This package
adds only what is specific to the study: the registered window grid and price
grid, readers for the sealed evidence archive, the reproduction and
reporting of the published cohort, price sweep and amplitude-amplification
counts, and the reconstruction-task comparison with its date-block bootstrap.

Modules:

``evidence``       locations of the sealed evidence (``SR_*`` variables)
``grid``           the registered study window grid
``archive``        readers for the sealed archive layout
``cohort``         reproduction of the published cohort counts
``price_sweep``    the study price grid and its published tables
``amplified``      the amplitude-amplification sensitivity
``tasks``          crossing versus noncrossing reconstruction-task comparison
``task_inputs``    normalisation of the sealed task inputs
``cli``            ``python -m scale_reversal`` / ``scale-reversal``
"""
__version__ = "1.0.0"
