import numpy as np

from ._atomic_property import AtomicProperty, get_properties
from ._base import Descriptor


__all__ = ('BCUT',)


class BCUTBase(Descriptor):
    __slots__ = ()
    explicit_hydrogens = False
    require_connected = True


class Burden(BCUTBase):
    __slots__ = ()

    def as_key(self):
        return self.__class__, ()

    def calculate(self):
        N = self.mol.GetNumAtoms()

        mat = 0.001 * np.ones((N, N))

        for bond in self.mol.GetBonds():
            a = bond.GetBeginAtom()
            b = bond.GetEndAtom()
            i = a.GetIdx()
            j = b.GetIdx()

            try:
                w = bond.GetBondTypeAsDouble() / 10.0
            except RuntimeError:
                self.fail(ValueError('unknown bond type'))

            if a.GetDegree() == 1 or b.GetDegree() == 1:
                w += 0.01

            mat[i, j] = w
            mat[j, i] = w

        return mat


class BurdenEigenValues(BCUTBase):
    __slots__ = ('_prop',)

    def as_key(self):
        return self.__class__, (self._prop,)

    def __init__(self, prop):
        self._prop = prop

    def dependencies(self):
        return {
            'ps': self._prop,
            'burden': Burden(),
        }

    def calculate(self, burden, ps):
        bmat = burden.copy()

        np.fill_diagonal(bmat, ps)
        ev = np.linalg.eig(bmat)[0]

        if np.iscomplexobj(ev):
            ev = ev.real

        return np.sort(ev)[-1::-1]


class BCUT(BCUTBase):
    r"""BCUT descriptor.

    :type prop: :py:class:`str` or :py:class:`function`
    :param prop: :ref:`atomic_properties`

    :type nth: int
    :param nth: n-th eigen value. 0 is highest, -1 is lowest.

    :returns: NaN when

        * any atomic properties are NaN
        * :math:`\left| nth \right| > A`
    """
    __slots__ = ('_prop', '_nth',)

    @classmethod
    def preset(cls):
        return (
            cls(a, n)
            for a in get_properties(istate=True, charge=True)
            for n in [0, -1]
        )

    def __str__(self):
        if self._nth < 0:
            return 'BCUT{}-{}l'.format(self._prop, np.abs(self._nth))
        else:
            return 'BCUT{}-{}h'.format(self._prop, self._nth + 1)

    def as_key(self):
        return self.__class__, (self._prop, self._nth)

    def __init__(self, prop='m', nth=0):
        self._prop = AtomicProperty(self.explicit_hydrogens, prop)
        self._nth = nth

    def dependencies(self):
        return {'bev': BurdenEigenValues(self._prop)}

    def calculate(self, bev):
        try:
            return bev[self._nth]
        except IndexError:
            self.fail(ValueError('nth greater then atom count'))

    rtype = float
