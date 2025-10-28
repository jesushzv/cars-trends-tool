"""
Parser utilities for extracting car information from listing titles
Phase 4: Extract make, model, year, mileage
"""
import re
from typing import Dict, Optional, Tuple


# Common car makes (expanded for international coverage, especially Mexico)
COMMON_MAKES = {
    # American brands
    'honda', 'toyota', 'ford', 'chevrolet', 'chevy', 'nissan', 'mazda',
    'dodge', 'jeep', 'ram', 'gmc', 'buick', 'cadillac', 'chrysler', 'lincoln',
    'tesla', 'pontiac', 'oldsmobile', 'mercury', 'saturn', 'hummer',
    # Japanese brands
    'subaru', 'mitsubishi', 'lexus', 'acura', 'infiniti', 'suzuki', 'isuzu', 'datsun',
    # Korean brands
    'hyundai', 'kia', 'genesis', 'daewoo',
    # European brands
    'volkswagen', 'vw', 'bmw', 'mercedes', 'audi', 'volvo', 'porsche', 'mini',
    'fiat', 'land rover', 'jaguar', 'renault', 'peugeot', 'citroën', 'citroen',
    'seat', 'skoda', 'opel', 'vauxhall', 'alfa romeo', 'lancia', 'maserati',
    'ferrari', 'lamborghini', 'bentley', 'rolls royce', 'aston martin', 'lotus',
    'smart', 'saab', 'mg', 'rover', 'alpine',
    # Chinese brands
    'geely', 'byd', 'chery', 'great wall', 'haval', 'mg',
    # Indian brands
    'tata', 'mahindra',
    # Other
    'lada', 'yugo', 'proton'
}

# Make aliases (for normalization)
MAKE_ALIASES = {
    'chevy': 'chevrolet',
    'vw': 'volkswagen',
    'benz': 'mercedes',
    'citroen': 'citroën'
}


def extract_year(text: str) -> Optional[int]:
    """
    Extract year from text (typically 1990-2025)
    
    Args:
        text: Text to search for year
        
    Returns:
        Year as integer or None
        
    Examples:
        "2020 Honda Accord" -> 2020
        "Honda Civic 2015" -> 2015
        "No year here" -> None
    """
    if not text:
        return None
    
    # Look for 4-digit year between 1990 and 2025
    pattern = r'\b(19[9]\d|20[0-2]\d)\b'
    matches = re.findall(pattern, text)
    
    if matches:
        # Return the first valid year found
        year = int(matches[0])
        if 1990 <= year <= 2025:
            return year
    
    return None


def extract_make_model(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract car make and model from text
    
    Args:
        text: Text to parse (typically a title)
        
    Returns:
        Tuple of (make, model) or (None, None)
        
    Examples:
        "2020 Honda Accord" -> ("Honda", "Accord")
        "Toyota Camry LE" -> ("Toyota", "Camry")
        "Just a car" -> (None, None)
    """
    if not text:
        return None, None
    
    text_lower = text.lower()
    
    # Try to find a known make
    make_found = None
    make_position = -1
    
    for make in COMMON_MAKES:
        # Look for whole word match
        pattern = r'\b' + re.escape(make) + r'\b'
        match = re.search(pattern, text_lower)
        if match:
            make_found = make
            make_position = match.start()
            break
    
    if not make_found:
        return None, None
    
    # Normalize make
    make_normalized = MAKE_ALIASES.get(make_found, make_found).title()
    
    # Try to extract model (next word(s) after make)
    # Split text into words, find make, take next 1-2 words as model
    words = text.split()
    model_words = []
    
    for i, word in enumerate(words):
        if word.lower() in [make_found, make_found.replace(' ', '')]:
            # Found the make, next words are likely the model
            # Take next 1-2 words, excluding years and common terms
            for j in range(i + 1, min(i + 3, len(words))):
                next_word = words[j]
                # Skip if it's a year, price, or common descriptor
                if re.match(r'^\d{4}$', next_word):  # Year
                    continue
                if re.match(r'^\$', next_word):  # Price
                    break
                if next_word.lower() in ['with', 'in', 'for', 'at', '-', '|']:
                    break
                model_words.append(next_word)
            break
    
    model = ' '.join(model_words) if model_words else None
    
    # Clean up model (remove special chars)
    if model:
        model = re.sub(r'[^\w\s-]', '', model).strip()
    
    return make_normalized, model if model else None


def extract_mileage(text: str) -> Optional[int]:
    """
    Extract mileage from text
    
    Args:
        text: Text to search for mileage
        
    Returns:
        Mileage as integer or None
        
    Examples:
        "50k miles" -> 50000
        "120,000 miles" -> 120000
        "No mileage" -> None
    """
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Pattern for numbers followed by 'k', 'km', 'miles', 'mi', etc.
    # Matches: "50k", "50K", "50,000", "50000 miles", "50k miles"
    patterns = [
        r'(\d{1,3}(?:,\d{3})*)\s*(?:miles|mi|km|kms)',  # "120,000 miles"
        r'(\d+)k\b',  # "50k"
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            value = matches[0].replace(',', '')
            miles = int(value)
            
            # If value is in 'k' format (50k = 50,000)
            if 'k' in text_lower:
                miles = miles * 1000
            
            # Sanity check (0 to 500,000 miles)
            if 0 < miles <= 500000:
                return miles
    
    return None


def parse_listing_title(title: str) -> Dict[str, Optional[any]]:
    """
    Parse a listing title to extract all car information
    
    Args:
        title: Listing title
        
    Returns:
        Dict with keys: year, make, model, mileage
        
    Example:
        "2020 Honda Accord - 50k miles" -> {
            'year': 2020,
            'make': 'Honda', 
            'model': 'Accord',
            'mileage': 50000
        }
    """
    year = extract_year(title)
    make, model = extract_make_model(title)
    mileage = extract_mileage(title)
    
    return {
        'year': year,
        'make': make,
        'model': model,
        'mileage': mileage
    }


if __name__ == "__main__":
    # Test the parser
    test_titles = [
        "2020 Honda Accord - 50k miles",
        "Toyota Camry 2018",
        "2015 Ford F-150 XLT",
        "Nissan Altima 2019 - 30,000 miles",
        "Chevy Silverado 1500",
        "BMW 3 Series 2016",
    ]
    
    print("Testing parser...")
    for title in test_titles:
        result = parse_listing_title(title)
        print(f"\n'{title}'")
        print(f"  -> Year: {result['year']}, Make: {result['make']}, Model: {result['model']}, Mileage: {result['mileage']}")

