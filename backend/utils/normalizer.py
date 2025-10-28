"""
Data normalization utilities for car listings
Phase 7: Standardize make/model names for consistency
"""
import re
from typing import Dict, Optional


# Make name normalization mapping (aliases to canonical names)
MAKE_NORMALIZATION = {
    # Common abbreviations
    'vw': 'Volkswagen',
    'bmw': 'BMW',
    'gmc': 'GMC',
    'chevy': 'Chevrolet',
    'benz': 'Mercedes-Benz',
    'mercedes': 'Mercedes-Benz',
    'merc': 'Mercedes-Benz',
    
    # Case variations (normalize to preferred capitalization)
    'honda': 'Honda',
    'toyota': 'Toyota',
    'ford': 'Ford',
    'nissan': 'Nissan',
    'chevrolet': 'Chevrolet',
    'mazda': 'Mazda',
    'hyundai': 'Hyundai',
    'kia': 'Kia',
    'volkswagen': 'Volkswagen',
    'audi': 'Audi',
    'dodge': 'Dodge',
    'jeep': 'Jeep',
    'ram': 'Ram',
    'subaru': 'Subaru',
    'mitsubishi': 'Mitsubishi',
    'lexus': 'Lexus',
    'acura': 'Acura',
    'infiniti': 'Infiniti',
    'buick': 'Buick',
    'cadillac': 'Cadillac',
    'chrysler': 'Chrysler',
    'lincoln': 'Lincoln',
    'volvo': 'Volvo',
    'porsche': 'Porsche',
    'tesla': 'Tesla',
    'mini': 'MINI',
    'fiat': 'Fiat',
    'land rover': 'Land Rover',
    'jaguar': 'Jaguar',
    'renault': 'Renault',
    'peugeot': 'Peugeot',
    'citroën': 'Citroën',
    'citroen': 'Citroën',
    'seat': 'SEAT',
    'skoda': 'Skoda',
    'suzuki': 'Suzuki',
    'isuzu': 'Isuzu',
    'datsun': 'Datsun',
    'genesis': 'Genesis',
    'alfa romeo': 'Alfa Romeo',
    'geely': 'Geely',
    'byd': 'BYD',
    'chery': 'Chery',
    'great wall': 'Great Wall',
    'haval': 'Haval',
}

# Model name normalization patterns
MODEL_REPLACEMENTS = [
    # Remove door/passenger count indicators (can appear anywhere)
    (r'\s+\d+[pd](?=\s|$)', ''),  # "CR-V 5p Touring" -> "CR-V Touring", "Civic 4d" -> "Civic"
    
    # Standardize spacing around hyphens
    (r'\s*-\s*', '-'),  # "CR - V" -> "CR-V"
    
    # Remove trim levels in parentheses
    (r'\s*\([^)]*\)', ''),  # "Accord (EX)" -> "Accord"
    
    # Standardize Series naming
    (r'Serie\s+(\d+)', r'Series \1'),  # "Serie 3" -> "Series 3"
    (r'Series\s*-\s*(\d+)', r'Series \1'),  # "Series-3" -> "Series 3"
]


def normalize_make(make: Optional[str]) -> Optional[str]:
    """
    Normalize car make name to standard format
    
    Args:
        make: Raw make name (can be any case, abbreviation, etc.)
        
    Returns:
        Normalized make name or None if invalid
        
    Examples:
        "HONDA" -> "Honda"
        "vw" -> "Volkswagen"
        "chevy" -> "Chevrolet"
        "bmw" -> "BMW"
    """
    if not make:
        return None
    
    # Clean and lowercase for lookup
    make_clean = make.strip().lower()
    
    # Look up in normalization map
    if make_clean in MAKE_NORMALIZATION:
        return MAKE_NORMALIZATION[make_clean]
    
    # If not in map, just return title case
    return make.strip().title()


def normalize_model(model: Optional[str]) -> Optional[str]:
    """
    Normalize car model name to standard format
    
    Args:
        model: Raw model name
        
    Returns:
        Normalized model name or None if invalid
        
    Examples:
        "CR-V 5p" -> "CR-V"
        "Serie 3" -> "Series 3"
        "F-250 SUPER DUTY" -> "F-250 Super Duty"
    """
    if not model:
        return None
    
    # Start with the original model
    normalized = model.strip()
    
    # Apply replacement patterns
    for pattern, replacement in MODEL_REPLACEMENTS:
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    # Title case, but preserve uppercase acronyms
    # Split by spaces and hyphens, title case each part
    parts = re.split(r'([-\s])', normalized)
    result_parts = []
    for part in parts:
        if part in ['-', ' ']:
            result_parts.append(part)
        elif len(part) <= 1:
            # Single characters
            result_parts.append(part.upper())
        elif part.isupper() and len(part) == 2:
            # Two-letter acronyms like "XL", "EX", "SE"
            result_parts.append(part)
        elif re.match(r'^[A-Z]-?\d+', part, re.IGNORECASE):
            # Patterns like "F-250", "E-450", "F250"
            result_parts.append(part.upper())
        else:
            # Regular words - title case
            result_parts.append(part.title())
    
    normalized = ''.join(result_parts)
    
    return normalized if normalized else None


def normalize_car_data(title: str = None, make: str = None, model: str = None, 
                       year: int = None, mileage: int = None) -> Dict:
    """
    Normalize all car data fields for consistency
    
    Args:
        title: Listing title (used as fallback)
        make: Car make/brand
        model: Car model
        year: Car year
        mileage: Odometer reading
        
    Returns:
        Dict with normalized fields: {'make': str, 'model': str, 'year': int, 'mileage': int}
        
    Examples:
        normalize_car_data(make="vw", model="Golf 5p") 
        -> {'make': 'Volkswagen', 'model': 'Golf', 'year': None, 'mileage': None}
        
        normalize_car_data(make="HONDA", model="CR-V 5p", year=2020) 
        -> {'make': 'Honda', 'model': 'CR-V', 'year': 2020, 'mileage': None}
    """
    normalized = {
        'make': normalize_make(make),
        'model': normalize_model(model),
        'year': year,
        'mileage': mileage
    }
    
    return normalized


def is_normalized(make: str = None, model: str = None) -> bool:
    """
    Check if make/model are already normalized
    
    Args:
        make: Car make to check
        model: Car model to check
        
    Returns:
        True if already normalized, False otherwise
    """
    if make:
        normalized_make = normalize_make(make)
        if normalized_make != make:
            return False
    
    if model:
        normalized_model = normalize_model(model)
        if normalized_model != model:
            return False
    
    return True


if __name__ == "__main__":
    # Test the normalizer
    test_cases = [
        ("vw", "Golf 5p", "Volkswagen", "Golf"),
        ("HONDA", "CR-V 5p Touring", "Honda", "CR-V Touring"),
        ("bmw", "Serie 3 4p", "BMW", "Series 3"),
        ("chevy", "Silverado 1500", "Chevrolet", "Silverado 1500"),
        ("Mercedes", "E-class", "Mercedes-Benz", "E-Class"),
        ("RENAULT", "KOLEOS PRIVILEGE", "Renault", "Koleos Privilege"),
    ]
    
    print("Testing normalizer...")
    for make_in, model_in, make_expected, model_expected in test_cases:
        result = normalize_car_data(make=make_in, model=model_in)
        make_match = result['make'] == make_expected
        model_match = result['model'] == model_expected
        status = "✓" if (make_match and model_match) else "✗"
        print(f"{status} {make_in:15} {model_in:25} -> {result['make']:15} {result['model']}")
        if not make_match:
            print(f"   Expected make: {make_expected}, got: {result['make']}")
        if not model_match:
            print(f"   Expected model: {model_expected}, got: {result['model']}")

