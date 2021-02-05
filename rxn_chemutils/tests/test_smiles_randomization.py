# LICENSED INTERNAL CODE. PROPERTY OF IBM.
# IBM Research Zurich Licensed Internal Code
# (C) Copyright IBM Corp. 2021
# ALL RIGHTS RESERVED

from typing import Callable, List

from rxn_chemutils.smiles_randomization import (
    randomize_smiles_restricted, randomize_smiles_unrestricted, randomize_smiles_rotated
)

randomization_functions: List[Callable[[str], str]] = [
    randomize_smiles_unrestricted,
    randomize_smiles_restricted,
    randomize_smiles_rotated,
]


def test_generates_all_randomizations_for_simple_example():
    # Check that everything is recovered in a simple example with all methods
    smiles = 'C1ON1'

    # 6 possible SMILES: 3 different starting atoms x 2 directions
    expected = {'C1ON1', 'C1NO1', 'O1NC1', 'O1CN1', 'N1CO1', 'N1OC1'}
    for fn in randomization_functions:
        samples = {fn(smiles) for _ in range(100)}
        assert samples == expected

    # randomizing with rotation and no order reversal: only 3 possibilities
    assert len(
        {randomize_smiles_rotated(smiles, with_order_reversal=False)
         for _ in range(100)}
    ) == 3


def test_does_not_sanitize_molecules():
    # Check that no aromatization or cleanup is done
    smiles = 'C1=CC=CC=C1N(=O)=O'

    for fn in randomization_functions:
        samples = {fn(smiles) for _ in range(10)}
        assert not any('c' in sample for sample in samples)
        assert not any('[N+]' in sample for sample in samples)


def test_keeps_stereochemistry():
    # Simple molecule with a stereocenter
    smiles = 'COC[C@](CNC)(Cl)Br'

    for fn in randomization_functions:
        samples = {fn(smiles) for _ in range(10)}
        # All the samples must have kept at least one '@'
        assert all('@' in sample for sample in samples)


def test_number_generated_molecules():
    # For a test molecule, verify that the unrestricted randomization generates
    # most molecules, followed by the restricted one, followed by the rotated one.
    # NB: the exact values below depend on the number of samples.

    adenine = 'Nc1ncnc2[nH]cnc12'
    n_samples = 300

    rotated = {randomize_smiles_rotated(adenine) for _ in range(n_samples)}
    restricted = {randomize_smiles_restricted(adenine) for _ in range(n_samples)}
    unrestricted = {randomize_smiles_unrestricted(adenine) for _ in range(n_samples)}

    assert 18 < len(rotated) < 22
    assert 45 < len(restricted) < 60
    assert 90 < len(unrestricted)
