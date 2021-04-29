# LICENSED INTERNAL CODE. PROPERTY OF IBM.
# IBM Research Zurich Licensed Internal Code
# (C) Copyright IBM Corp. 2021
# ALL RIGHTS RESERVED

from typing import List, Iterator, Optional, Generator, TypeVar, Type

import attr
from rxn_utilities.container_utilities import remove_duplicates

from .conversion import canonicalize_smiles, cleanup_smiles
from .molecule_list import molecule_list_from_string, molecule_list_to_string

T = TypeVar('T', bound='ReactionEquation')


@attr.s(auto_attribs=True)
class ReactionEquation:
    """
    Defines a reaction equation, as given by the molecules involved in a reaction.

    Attributes:
        reactants: SMILES strings for compounds on the left of the reaction arrow.
        agents: SMILES strings for compounds above the reaction arrow. Are
            sometimes merged with the reactants.
        products: SMILES strings for compounds on the right of the reaction arrow.
    """
    reactants: List[str]
    agents: List[str]
    products: List[str]

    def __iter__(self) -> Iterator[List[str]]:
        """Helper function to simplify functionality acting on all three
        compound groups"""
        return (i for i in (self.reactants, self.agents, self.products))

    def iter_all_smiles(self) -> Generator[str, None, None]:
        """Helper function to iterate over all the SMILES in the reaction equation"""
        return (molecule for group in self for molecule in group)

    def to_string(self, fragment_bond: Optional[str] = None) -> str:
        """
        Convert a ReactionEquation to an "rxn" reaction SMILES.
        """

        smiles_groups = (molecule_list_to_string(group, fragment_bond) for group in self)
        return '>'.join(smiles_groups)

    @classmethod
    def from_string(cls: Type[T], reaction_string: str, fragment_bond: Optional[str] = None) -> T:
        """
        Convert a ReactionEquation from an "rxn" reaction SMILES.
        """

        groups = [
            molecule_list_from_string(smiles_group, fragment_bond=fragment_bond)
            for smiles_group in reaction_string.split('>')
        ]

        return cls(*groups)


def merge_reactants_and_agents(reaction: ReactionEquation) -> ReactionEquation:
    return ReactionEquation(
        reactants=reaction.reactants + reaction.agents, agents=[], products=reaction.products
    )


def sort_compounds(reaction: ReactionEquation) -> ReactionEquation:
    """
    Reorder the compounds of each group in alphabetic order.
    """
    sorted_compound_groups = (sorted(group) for group in reaction)
    return ReactionEquation(*sorted_compound_groups)


def canonicalize_compounds(
    reaction: ReactionEquation, check_valence: bool = True
) -> ReactionEquation:
    """
    Canonicalize the molecules of a ReactionEquation.
    """
    canonicalized_compound_groups = (
        [canonicalize_smiles(s, check_valence=check_valence) for s in compound_group]
        for compound_group in reaction
    )
    return ReactionEquation(*canonicalized_compound_groups)


def remove_duplicate_compounds(reaction: ReactionEquation) -> ReactionEquation:
    """
    Remove compounds that are duplicated in the same category
    """
    groups_without_duplicates = (remove_duplicates(group) for group in reaction)
    return ReactionEquation(*groups_without_duplicates)


def cleanup_compounds(reaction: ReactionEquation) -> ReactionEquation:
    """
    Basic cleanup of the compounds.
    """
    clean_compound_groups = (
        [cleanup_smiles(s) for s in compound_group] for compound_group in reaction
    )
    return ReactionEquation(*clean_compound_groups)


def rxn_standardization(reaction: ReactionEquation) -> ReactionEquation:
    """
    Apply the standard rxn postprocessing of reaction equations.

    Consists in the following
    1. merge reactants and agents
    2. canonicalize all the SMILES
    3. sort the compounds in each group
    4. remove the duplicates
    """
    return remove_duplicate_compounds(
        sort_compounds(canonicalize_compounds(merge_reactants_and_agents(reaction)))
    )


def has_repeated_molecules(reaction_equation: ReactionEquation) -> bool:
    all_molecules = list(reaction_equation.iter_all_smiles())
    return len(set(all_molecules)) < len(all_molecules)
