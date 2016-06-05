from rdkit.Chem import MolSurf

from rdkit.Chem.EState import EState_VSA as RDKit_EState_VSA

from ._base import Descriptor


__all__ = (
    'LabuteASA',
    'PEOE_VSA', 'SMR_VSA', 'SlogP_VSA',
    'EState_VSA', 'VSA_EState',
)


class LabuteASA(Descriptor):
    r"""Labute's Approximate Surface Area descriptor(rdkit wrapper)."""
    __slots__ = ()
    explicit_hydrogens = False

    @classmethod
    def preset(cls):
        yield cls()

    def __str__(self):
        return 'LabuteASA'

    def as_key(self):
        return self.__class__, ()

    def calculate(self):
        return MolSurf.LabuteASA(self.mol)

    rtype = float


class MoeTypeBase(Descriptor):
    __slots__ = ('_k',)
    explicit_hydrogens = False
    _module = MolSurf

    @classmethod
    def preset(cls):
        return map(cls, range(1, cls.k_max))

    def __str__(self):
        return self.__class__.__name__ + str(self._k)

    def as_key(self):
        return self.__class__, (self._k,)

    def __init__(self, k=1):
        assert 1 <= k <= self.k_max
        self._k = k

    def calculate(self):
        f = getattr(self._module, str(self))
        return f(self.mol)

    rtype = float


class PEOE_VSA(MoeTypeBase):
    r"""MOE type descriptors using gasteiger charge and surface area contribution(rdkit wrapper).

    :type k: int
    :param k: (:math:`1 <= k <= k_{\rm max}`)
    """
    __slots__ = ()
    k_max = 14


class SMR_VSA(MoeTypeBase):
    r"""MOE type descriptors using Wildman-Crippen MR and surface area contribution(rdkit wrapper).

    :type k: int
    :param k: (:math:`1 <= k <= k_{\rm max}`)
    """
    __slots__ = ()
    k_max = 10


class SlogP_VSA(MoeTypeBase):
    r"""MOE type descriptors using Wildman-Crippen LogP and surface area contribution(rdkit wrapper).

    :type k: int
    :param k: (:math:`1 <= k <= k_{\rm max}`)
    """
    __slots__ = ()
    k_max = 12


class EState_VSA(MoeTypeBase):
    r"""MOE type descriptors using EState indices and surface area contribution(rdkit wrapper).

    :type k: int
    :param k: (:math:`1 <= k <= k_{\rm max}`)
    """
    __slots__ = ()
    _module = RDKit_EState_VSA
    k_max = 11


class VSA_EState(MoeTypeBase):
    r"""MOE type descriptors using EState indices and surface area contribution(rdkit wrapper).

    :type k: int
    :param k: (:math:`1 <= k <= k_{\rm max}`)
    """
    __slots__ = ()
    _module = RDKit_EState_VSA
    k_max = 10
