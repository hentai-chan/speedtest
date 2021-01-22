#!/usr/bin/env python3

import math

def square_function(xmin, xmax) -> map:
    """
    Return the range of f:[xmin,xmax] ⟶ ℝ, x ↦ x²
    """
    return map(lambda x: int(math.pow(2, x)), range(xmin, xmax+1))
