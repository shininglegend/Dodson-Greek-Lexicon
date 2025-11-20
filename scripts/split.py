#!/usr/bin/env python3
"""
Split dodson.xml into separate JSON files organized by the first Greek letter.
Each file contains all entries starting with that letter.
"""

import xml.etree.ElementTree as ET
import json
from pathlib import Path
from collections import defaultdict


def normalize_greek_letter(letter):
    """
    Normalize Greek letters by removing diacritical marks and converting to lowercase.
    Returns the base letter for grouping purposes.
    """
    # Greek letter normalization mapping (uppercase/lowercase with diacritics to base lowercase)
    normalization_map = {
        # Alpha variants
        'ἀ': 'α', 'ἁ': 'α', 'ά': 'α', 'ὰ': 'α', 'ᾶ': 'α', 'ἄ': 'α', 'ἂ': 'α', 'ἆ': 'α',
        'ἅ': 'α', 'ἃ': 'α', 'ἇ': 'α', 'ᾳ': 'α', 'ᾴ': 'α', 'ᾲ': 'α', 'ᾷ': 'α',
        'ᾀ': 'α', 'ᾁ': 'α', 'ᾄ': 'α', 'ᾂ': 'α', 'ᾅ': 'α', 'ᾃ': 'α', 'ᾆ': 'α', 'ᾇ': 'α',
        'Ἀ': 'α', 'Ἁ': 'α', 'Ά': 'α', 'Ὰ': 'α', 'Ἄ': 'α', 'Ἂ': 'α', 'Ἆ': 'α',
        'Ἅ': 'α', 'Ἃ': 'α', 'Ἇ': 'α', 'ᾼ': 'α', 'ᾈ': 'α', 'ᾉ': 'α', 'ᾌ': 'α', 'ᾊ': 'α',
        'ᾍ': 'α', 'ᾋ': 'α', 'ᾎ': 'α', 'ᾏ': 'α',
        # Epsilon variants
        'ἐ': 'ε', 'ἑ': 'ε', 'έ': 'ε', 'ὲ': 'ε', 'ἔ': 'ε', 'ἒ': 'ε', 'ἕ': 'ε', 'ἓ': 'ε',
        'Ἐ': 'ε', 'Ἑ': 'ε', 'Έ': 'ε', 'Ὲ': 'ε', 'Ἔ': 'ε', 'Ἒ': 'ε', 'Ἕ': 'ε', 'Ἓ': 'ε',
        # Eta variants
        'ἠ': 'η', 'ἡ': 'η', 'ή': 'η', 'ὴ': 'η', 'ῆ': 'η', 'ἤ': 'η', 'ἢ': 'η', 'ἦ': 'η',
        'ἥ': 'η', 'ἣ': 'η', 'ἧ': 'η', 'ῃ': 'η', 'ῄ': 'η', 'ῂ': 'η', 'ῇ': 'η',
        'ᾐ': 'η', 'ᾑ': 'η', 'ᾔ': 'η', 'ᾒ': 'η', 'ᾕ': 'η', 'ᾓ': 'η', 'ᾖ': 'η', 'ᾗ': 'η',
        'Ἠ': 'η', 'Ἡ': 'η', 'Ή': 'η', 'Ὴ': 'η', 'Ἤ': 'η', 'Ἢ': 'η', 'Ἦ': 'η',
        'Ἥ': 'η', 'Ἣ': 'η', 'Ἧ': 'η', 'ῌ': 'η', 'ᾘ': 'η', 'ᾙ': 'η', 'ᾜ': 'η', 'ᾚ': 'η',
        'ᾝ': 'η', 'ᾛ': 'η', 'ᾞ': 'η', 'ᾟ': 'η',
        # Iota variants
        'ἰ': 'ι', 'ἱ': 'ι', 'ί': 'ι', 'ὶ': 'ι', 'ῖ': 'ι', 'ἴ': 'ι', 'ἲ': 'ι', 'ἶ': 'ι',
        'ἵ': 'ι', 'ἳ': 'ι', 'ἷ': 'ι', 'ϊ': 'ι', 'ΐ': 'ι', 'ῒ': 'ι', 'ῗ': 'ι',
        'Ἰ': 'ι', 'Ἱ': 'ι', 'Ί': 'ι', 'Ὶ': 'ι', 'Ἴ': 'ι', 'Ἲ': 'ι', 'Ἶ': 'ι',
        'Ἵ': 'ι', 'Ἳ': 'ι', 'Ἷ': 'ι', 'Ϊ': 'ι',
        # Omicron variants
        'ὀ': 'ο', 'ὁ': 'ο', 'ό': 'ο', 'ὸ': 'ο', 'ὄ': 'ο', 'ὂ': 'ο', 'ὅ': 'ο', 'ὃ': 'ο',
        'Ὀ': 'ο', 'Ὁ': 'ο', 'Ό': 'ο', 'Ὸ': 'ο', 'Ὄ': 'ο', 'Ὂ': 'ο', 'Ὅ': 'ο', 'Ὃ': 'ο',
        # Upsilon variants
        'ὐ': 'υ', 'ὑ': 'υ', 'ύ': 'υ', 'ὺ': 'υ', 'ῦ': 'υ', 'ὔ': 'υ', 'ὒ': 'υ', 'ὖ': 'υ',
        'ὕ': 'υ', 'ὓ': 'υ', 'ὗ': 'υ', 'ϋ': 'υ', 'ΰ': 'υ', 'ῢ': 'υ', 'ῧ': 'υ',
        'Ὑ': 'υ', 'Ύ': 'υ', 'Ὺ': 'υ', 'Ὕ': 'υ', 'Ὓ': 'υ', 'Ὗ': 'υ', 'Ϋ': 'υ',
        # Omega variants
        'ὠ': 'ω', 'ὡ': 'ω', 'ώ': 'ω', 'ὼ': 'ω', 'ῶ': 'ω', 'ὤ': 'ω', 'ὢ': 'ω', 'ὦ': 'ω',
        'ὥ': 'ω', 'ὣ': 'ω', 'ὧ': 'ω', 'ῳ': 'ω', 'ῴ': 'ω', 'ῲ': 'ω', 'ῷ': 'ω',
        'ᾠ': 'ω', 'ᾡ': 'ω', 'ᾤ': 'ω', 'ᾢ': 'ω', 'ᾥ': 'ω', 'ᾣ': 'ω', 'ᾦ': 'ω', 'ᾧ': 'ω',
        'Ὠ': 'ω', 'Ὡ': 'ω', 'Ώ': 'ω', 'Ὼ': 'ω', 'Ὤ': 'ω', 'Ὢ': 'ω', 'Ὦ': 'ω',
        'Ὥ': 'ω', 'Ὣ': 'ω', 'Ὧ': 'ω', 'ῼ': 'ω', 'ᾨ': 'ω', 'ᾩ': 'ω', 'ᾬ': 'ω', 'ᾪ': 'ω',
        'ᾭ': 'ω', 'ᾫ': 'ω', 'ᾮ': 'ω', 'ᾯ': 'ω',
        # Rho variants
        'ῥ': 'ρ', 'ῤ': 'ρ', 'Ῥ': 'ρ',
        # Simple uppercase to lowercase
        'Α': 'α', 'Β': 'β', 'Γ': 'γ', 'Δ': 'δ', 'Ε': 'ε', 'Ζ': 'ζ', 'Η': 'η', 'Θ': 'θ',
        'Ι': 'ι', 'Κ': 'κ', 'Λ': 'λ', 'Μ': 'μ', 'Ν': 'ν', 'Ξ': 'ξ', 'Ο': 'ο', 'Π': 'π',
        'Ρ': 'ρ', 'Σ': 'σ', 'Τ': 'τ', 'Υ': 'υ', 'Φ': 'φ', 'Χ': 'χ', 'Ψ': 'ψ', 'Ω': 'ω',
        # Final sigma
        'ς': 'σ',
    }
    
    return normalization_map.get(letter, letter.lower())


def get_first_letter_key(orth_text):
    """
    Extract and normalize the first Greek letter from the orth text.
    Returns the normalized base letter for grouping.
    """
    if not orth_text:
        return 'other'
    
    first_char = orth_text[0]
    normalized = normalize_greek_letter(first_char)
    
    # Map to Greek alphabet
    greek_alphabet = 'αβγδεζηθικλμνξοπρστυφχψω'
    if normalized and normalized in greek_alphabet:
        return normalized
    else:
        return 'other'


def parse_xml_to_json(xml_file):
    """
    Parse the dodson.xml file and organize entries by first letter.
    Returns a dictionary with letters as keys and lists of entries as values.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Organize entries by first letter
    entries_by_letter = defaultdict(list)
    
    # Find all entry elements
    for entry in root.findall('.//{http://www.crosswire.org/2008/TEIOSIS/namespace}entry'):
        entry_data = {}
        
        # Get the 'n' attribute (entry number and word)
        entry_data['n'] = entry.get('n', '')
        
        # Get orth (orthography - the Greek word)
        orth_elem = entry.find('.//{http://www.crosswire.org/2008/TEIOSIS/namespace}orth')
        if orth_elem is not None:
            entry_data['orth'] = orth_elem.text or ''
        else:
            entry_data['orth'] = ''
        
        # Get all definitions
        defs = entry.findall('.//{http://www.crosswire.org/2008/TEIOSIS/namespace}def')
        entry_data['definitions'] = []
        for def_elem in defs:
            def_data = {
                'role': def_elem.get('role', ''),
                'text': def_elem.text or ''
            }
            entry_data['definitions'].append(def_data)
        
        # Determine which letter this entry belongs to
        first_letter = get_first_letter_key(entry_data['orth'])
        entries_by_letter[first_letter].append(entry_data)
    
    return entries_by_letter


def write_json_files(entries_by_letter, output_dir):
    """
    Write entries to separate JSON files, one per letter.
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    files_created = []
    
    # Write a file for each letter that has entries
    for letter in sorted(entries_by_letter.keys()):
        entries = entries_by_letter[letter]
        
        # Create filename
        if letter == 'other':
            filename = 'other.json'
        else:
            filename = f'{letter}.json'
        
        filepath = output_path / filename
        
        # Write JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'letter': letter,
                'count': len(entries),
                'entries': entries
            }, f, ensure_ascii=False, indent=2)
        
        files_created.append(filename)
        print(f'Created {filename} with {len(entries)} entries')
    
    return files_created


def main():
    """Main function to orchestrate the splitting process."""
    # File paths
    xml_file = Path(__file__).parent.parent / 'dodson.xml'
    output_dir = Path(__file__).parent.parent / 'split-json'
    
    print(f'Reading XML file: {xml_file}')
    
    # Parse XML and organize by letter
    entries_by_letter = parse_xml_to_json(xml_file)
    
    print(f'\nFound entries for {len(entries_by_letter)} different letters/groups')
    
    # Write JSON files
    print(f'\nWriting JSON files to: {output_dir}')
    files_created = write_json_files(entries_by_letter, output_dir)
    
    print(f'\n✓ Successfully created {len(files_created)} JSON files')


if __name__ == '__main__':
    main()
