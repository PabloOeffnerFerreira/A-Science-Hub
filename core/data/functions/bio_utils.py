
from __future__ import annotations

# Standard RNA codon table (U-based)
CODON_TABLE = {
    'UUU': 'Phe', 'UUC': 'Phe', 'UUA': 'Leu', 'UUG': 'Leu',
    'CUU': 'Leu', 'CUC': 'Leu', 'CUA': 'Leu', 'CUG': 'Leu',
    'AUU': 'Ile', 'AUC': 'Ile', 'AUA': 'Ile', 'AUG': 'Met',
    'GUU': 'Val', 'GUC': 'Val', 'GUA': 'Val', 'GUG': 'Val',
    'UCU': 'Ser', 'UCC': 'Ser', 'UCA': 'Ser', 'UCG': 'Ser',
    'CCU': 'Pro', 'CCC': 'Pro', 'CCA': 'Pro', 'CCG': 'Pro',
    'ACU': 'Thr', 'ACC': 'Thr', 'ACA': 'Thr', 'ACG': 'Thr',
    'GCU': 'Ala', 'GCC': 'Ala', 'GCA': 'Ala', 'GCG': 'Ala',
    'UAU': 'Tyr', 'UAC': 'Tyr', 'UAA': 'STOP', 'UAG': 'STOP',
    'CAU': 'His', 'CAC': 'His', 'CAA': 'Gln', 'CAG': 'Gln',
    'AAU': 'Asn', 'AAC': 'Asn', 'AAA': 'Lys', 'AAG': 'Lys',
    'GAU': 'Asp', 'GAC': 'Asp', 'GAA': 'Glu', 'GAG': 'Glu',
    'UGU': 'Cys', 'UGC': 'Cys', 'UGA': 'STOP', 'UGG': 'Trp',
    'CGU': 'Arg', 'CGC': 'Arg', 'CGA': 'Arg', 'CGG': 'Arg',
    'AGU': 'Ser', 'AGC': 'Ser', 'AGA': 'Arg', 'AGG': 'Arg',
    'GGU': 'Gly', 'GGC': 'Gly', 'GGA': 'Gly', 'GGG': 'Gly'
}

# Very lightweight grouping for a simple chart
AMINO_ACID_GROUPS = {
    'Phe': 'Hydrophobic', 'Leu': 'Hydrophobic', 'Ile': 'Hydrophobic', 'Met': 'Hydrophobic',
    'Val': 'Hydrophobic', 'Ser': 'Polar', 'Pro': 'Hydrophobic', 'Thr': 'Polar',
    'Ala': 'Hydrophobic', 'Tyr': 'Polar', 'STOP': 'Stop Codon', 'His': 'Charged',
    'Gln': 'Polar', 'Asn': 'Polar', 'Lys': 'Charged', 'Asp': 'Charged',
    'Glu': 'Charged', 'Cys': 'Polar', 'Trp': 'Hydrophobic', 'Arg': 'Charged',
    'Gly': 'Hydrophobic'
}

SITES = {
    "EcoRI (GAATTC)": "GAATTC",
    "BamHI (GGATCC)": "GGATCC",
    "HindIII (AAGCTT)": "AAGCTT",
    "NotI (GCGGCCGC)": "GCGGCCGC",
    "Custom": ""
}

AA_MASS = {
    # average residue masses (approx, without water)
    "A": 89.09, "R": 174.20, "N": 132.12, "D": 133.10, "C": 121.15,
    "E": 147.13, "Q": 146.15, "G": 75.07, "H": 155.16, "I": 131.17,
    "L": 131.17, "K": 146.19, "M": 149.21, "F": 165.19, "P": 115.13,
    "S": 105.09, "T": 119.12, "W": 204.23, "Y": 181.19, "V": 117.15
}