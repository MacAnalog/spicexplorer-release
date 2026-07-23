from abc import ABC, abstractmethod
from typing import List

import control as ctrl
import sympy as sp
import torch

from .utils import Transfer_Func_Helper


class Base_TF(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_tf(self) -> sp.Expr:
        """Returns the symbolic transfer function."""
        pass

# Custom Target TFs
class Pole_Zero_TF(Base_TF):
    def __init__(self, zeros: List[complex] = None, poles: list[complex] = None, gain: float = 1):
        """Pole/zero locations can be complex. DC gain is in dB. """
        # super.__init__()
        self._dtype  = torch.complex64
        self.zeros = zeros
        self.poles = poles
        self.gain = gain

        # Controls TF
        self.tf_controls: ctrl.TransferFunction = None
        # SymPy TF
        self.tf_sympy: sp.Expr = None

    def add_pole(self, pole: complex):
        if self.poles is not None:
            self.poles.append(pole)
        else:
            self.poles = [pole]

    def add_zero(self, zero: complex):
        if self.zeros is not None:
            self.zeros.append(zero)
        else:
            self.zeros = [zero]

    def get_tf(self) -> sp.Expr:
        self.tf_sympy = None
        # Create transfer function from zeros, poles, and gain
        tf_sys = ctrl.zpk(self.zeros, self.poles, self.gain)  # Create ZPK system

        # Convert to standard transfer function format
        self.tf_controls = ctrl.tf(tf_sys)
        self.tf_sympy    = Transfer_Func_Helper().control_tf_to_sympy(self.tf_controls)

        return self.tf_sympy

class Second_Order_LP_TF(Base_TF):
    def __init__(self, q: float, fc: float, dc_gain: float):
        # super.__init__()
        self.q = q
        self.fc = fc
        self.dc_gain = dc_gain

    def get_tf(self):
        s = sp.symbols("s")
        wc = 2 * sp.pi * self.fc
        return self.dc_gain/(s**2/wc**2 + s/(wc*self.q) + 1)

class First_Order_LP_TF(Base_TF):
    def __init__(self, fc: float, dc_gain: float):
        # super.__init__()
        self.fc = fc
        self.dc_gain = dc_gain

    def get_tf(self):
        s = sp.symbols("s")
        wc = 2 * sp.pi * self.fc
        return self.dc_gain/(s/wc + 1)

class Second_Order_BP_TF(Base_TF):
    def __init__(self, q: float, fc: float, k_bp: float):
        # super.__init__()
        self.q = q
        self.fc = fc
        self.k_bp = k_bp

    def get_tf(self):
        s = sp.symbols("s")
        wc = 2 * sp.pi * self.fc
        return self.k_bp*(wc/self.q)*s/(s**2 + (wc/self.q)*s + wc**2)


def cascade_tf(list_of_tfs: List[Base_TF], dc_gain_multiplier: float = 1.0) -> sp.Expr:
    """Can be used to cascaded first and second order filters for Chebyshev, Butterworth, etc filter types"""
    cascaded = dc_gain_multiplier
    for obj in list_of_tfs:
        cascaded *= obj.get_tf()
    return cascaded
