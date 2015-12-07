#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A polynomial vectorizer for use in The Cannon.
"""

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

__all__ = ["PolynomialVectorizer"]

import numpy as np
from collections import (Counter, OrderedDict)
from six import string_types


from .base import BaseVectorizer


class PolynomialVectorizer(BaseVectorizer):
    """
    A vectorizer class that models spectral fluxes as a linear combination of
    label terms in a polynomial fashion.

    :param label:
        The label terms to use.

    :param fiducials:
        The fiducial offsets for the labels.

    :param scales:
        The scaling values for the labels.

    :param terms:
        The terms that constitute the label vector.
    """

    def __init__(self, *args, **kwargs):
        super(PolynomialVectorizer, self).__init__(*args, **kwargs)

        # Check that the terms are OK, and parse them into a useful format.
        self._parsed_terms = parse_label_vector_description(
            self.terms, columns=self.labels)      
        return None


    def get_label_vector(self, labels):
        """
        Return the values of the label vector, given the labels.

        :param labels:
            The labels to calculate the label vector for. This can be a 
            one-dimensional vector of `K` labels (using the same order and
            length provided by self.labels), or a two-dimensional array of
            `N` by `K` values. The returning array will be of shape `(N, 1+D)`,
            where `D` is the number of terms in the label vector description.
        """

        labels = np.array(labels)

        # How many dimensions?
        if labels.ndim == 1:
            labels = labels.reshape((1, labels.size))
        elif labels.ndim > 2:
            raise ValueError("labels must be a 1-d or 2-d array")
        N = labels.shape[0]

        # Offset and scale the labels before building the vector.
        scaled_labels = (labels - self.fiducials)/self.scales

        columns = [np.ones(N, dtype=float)]
        for term in self._parsed_terms:
            column = 1.
            for index, order in term:
                column *= scaled_labels[index]**order
                # TODO: check that if we are giving many label rows that we
                # calculate this properly.
                raise a
            columns.append(column)

        return np.vstack(columns)


    def get_label_vector_derivative(self, labels, d_label):
        raise NotImplementedError("soon..")



def _is_structured_label_vector(label_vector):
    """
    Return whether the provided label vector is structured as a polynomial
    vector description appropriately or not.

    :param label_vector:
        A structured or unstructured description of a polynomial label vector.
    """

    if not isinstance(label_vector, (list, tuple)):
        return False

    for descriptor in label_vector:
        if not isinstance(descriptor, (list, tuple)):
            return False

        for term in descriptor:
            if not isinstance(term, (list, tuple)) \
            or len(term) != 2 \
            or not isinstance(term[-1], (int, float)):
                return False

    if len(label_vector) == 0 or sum(map(len, label_vector)) == 0:
        return False

    return True


def parse_label_vector_description(description, columns=None, **kwargs):
    """
    Return a structured form of a label vector from unstructured,
    human-readable input.

    :param description:
        A human-readable or structured form of a label vector.

    :type description:
        str or list

    :param columns: [optional]
        If `columns` are provided, instead of text columns being provided as the
        output parameter, the corresponding index location in `column` will be
        given.

    :returns:
        A structured form of the label vector as a multi-level list.


    :Example:

    >>> parse_label_vector("Teff^4 + logg*Teff^3 + feh + feh^0*Teff")
    [
        [
            ("Teff", 4),
        ],
        [
            ("logg", 1),
            ("Teff", 3)
        ],
        [
            ("feh", 1),
        ],
        [
            ("feh", 0),
            ("Teff", 1)
        ]
    ]
    """

    if _is_structured_label_vector(description):
        return description

    # Allow for custom characters, but don't advertise it.
    # (Astronomers have bad enough habits already.)
    kwds = dict(zip(("sep", "mul", "pow"), "+*^"))
    kwds.update(kwargs)
    sep, mul, pow = (kwds[k] for k in ("sep", "mul", "pow"))

    if isinstance(description, string_types):
        description = description.split(sep)
    description = [_.strip() for _ in description]

    # Functions to parse the parameter (or index) and order for each term.
    get_power = lambda t: float(t.split(pow)[1].strip()) if pow in t else 1
    if columns is None:
        get_label = lambda d: d.split(pow)[0].strip()
    else:
        get_label = lambda d: list(columns).index(d.split(pow)[0].strip())

    label_vector = []
    for descriptor in (item.split(mul) for item in description):

        labels = map(get_label, descriptor)
        orders = map(get_power, descriptor)

        term = OrderedDict()
        for label, order in zip(labels, orders):
            term[label] = term.get(label, 0) + order # Sum repeat term powers.

        # Prevent uses of x^0 etc clogging up the label vector.
        valid_terms = [(l, o) for l, o in term.items() if o != 0]
        if not np.all(np.isfinite([o for l, o in valid_terms])):
            raise ValueError("non-finite power provided")

        if len(valid_terms) > 0:
            label_vector.append(valid_terms)
    
    if sum(map(len, label_vector)) == 0:
        raise ValueError("no valid terms provided")

    return label_vector


def build_label_vector(labels, order, cross_term_order=-1, **kwargs):
    """
    Build a label vector description.

    :param labels:
        The labels to use in describing the label vector.

    :param order:
        The maximum order of the terms (e.g., order 3 implies A^3 is a term).

    :param cross_term_order: [optional]
        The maximum order of the cross-terms (e.g., cross_term_order 2 implies
        A^2*B is a term). If the provided `cross_term_order` value is negative, 
        then `cross_term_order = order - 1` will be assumed.

    :param mul: [optional]
        The operator to use to represent multiplication in the description of 
        the label vector.

    :param pow: [optional]
        The operator to use to represent exponents in the description of the
        label vector.

    :returns:
        A human-readable form of the label vector.
    """

    sep = kwargs.pop("sep", "+")
    mul = kwargs.pop("mul", "*")
    pow = kwargs.pop("pow", "^")

    #I make no apologies: it's fun to code like this for short complex functions
    items = []
    if 0 > cross_term_order:
        cross_term_order = order - 1

    for o in range(1, 1 + max(order, 1 + cross_term_order)):
        for t in map(Counter, combinations_with_replacement(labels, o)):
            # Python 2 and 3 behave differently here, so generate an ordered
            # dictionary based on sorting the keys.
            t = OrderedDict([(k, t[k]) for k in sorted(t.keys())])
            if len(t) == 1 and order >= max(t.values()) \
            or len(t) > 1 and cross_term_order >= max(t.values()):
                c = [pow.join([[l], [l, str(p)]][p > 1]) for l, p in t.items()]
                if c: items.append(mul.join(map(str, c)))
    return " {} ".format(sep).join(items)