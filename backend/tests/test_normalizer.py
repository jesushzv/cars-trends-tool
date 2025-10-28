"""
Tests for data normalization utilities
Phase 7: Test make/model normalization
"""
import pytest
from utils.normalizer import normalize_make, normalize_model, normalize_car_data, is_normalized


class TestMakeNormalization:
    """Test make name normalization"""
    
    def test_normalize_make_lowercase(self):
        assert normalize_make("honda") == "Honda"
        assert normalize_make("toyota") == "Toyota"
    
    def test_normalize_make_uppercase(self):
        assert normalize_make("HONDA") == "Honda"
        assert normalize_make("FORD") == "Ford"
    
    def test_normalize_make_abbreviations(self):
        assert normalize_make("vw") == "Volkswagen"
        assert normalize_make("VW") == "Volkswagen"
        assert normalize_make("chevy") == "Chevrolet"
        assert normalize_make("bmw") == "BMW"
        assert normalize_make("gmc") == "GMC"
    
    def test_normalize_make_mercedes_variations(self):
        assert normalize_make("mercedes") == "Mercedes-Benz"
        assert normalize_make("Mercedes") == "Mercedes-Benz"
        assert normalize_make("benz") == "Mercedes-Benz"
    
    def test_normalize_make_none(self):
        assert normalize_make(None) is None
        assert normalize_make("") is None
    
    def test_normalize_make_unknown(self):
        # Unknown makes should be title-cased
        assert normalize_make("unknown") == "Unknown"
        assert normalize_make("NEWBRAND") == "Newbrand"


class TestModelNormalization:
    """Test model name normalization"""
    
    def test_normalize_model_remove_passenger_count(self):
        assert normalize_model("CR-V 5p") == "CR-V"
        assert normalize_model("Civic 4d") == "Civic"
        assert normalize_model("Golf 5p Touring") == "Golf Touring"
    
    def test_normalize_model_series_naming(self):
        assert normalize_model("Serie 3") == "Series 3"
        assert normalize_model("Serie 5 4p") == "Series 5"
        assert normalize_model("Series-3") == "Series 3"
    
    def test_normalize_model_hyphen_spacing(self):
        assert normalize_model("CR - V") == "CR-V"
        assert normalize_model("F - 150") == "F-150"
    
    def test_normalize_model_title_case(self):
        assert normalize_model("ACCORD") == "Accord"
        assert normalize_model("camry") == "Camry"
        assert normalize_model("KOLEOS PRIVILEGE") == "Koleos Privilege"
    
    def test_normalize_model_truck_models(self):
        assert normalize_model("F-250 SUPER DUTY") == "F-250 Super Duty"
        assert normalize_model("f150") == "F150"
        assert normalize_model("Silverado 1500") == "Silverado 1500"
    
    def test_normalize_model_none(self):
        assert normalize_model(None) is None
        assert normalize_model("") is None
    
    def test_normalize_model_preserve_acronyms(self):
        assert normalize_model("CR-V EX") == "CR-V EX"
        assert normalize_model("Accord LX") == "Accord LX"


class TestCarDataNormalization:
    """Test complete car data normalization"""
    
    def test_normalize_car_data_complete(self):
        result = normalize_car_data(
            make="vw",
            model="Golf 5p",
            year=2020,
            mileage=50000
        )
        assert result['make'] == "Volkswagen"
        assert result['model'] == "Golf"
        assert result['year'] == 2020
        assert result['mileage'] == 50000
    
    def test_normalize_car_data_partial(self):
        result = normalize_car_data(make="HONDA", model="CR-V 5p Touring")
        assert result['make'] == "Honda"
        assert result['model'] == "CR-V Touring"
        assert result['year'] is None
        assert result['mileage'] is None
    
    def test_normalize_car_data_none_values(self):
        result = normalize_car_data()
        assert result['make'] is None
        assert result['model'] is None
        assert result['year'] is None
        assert result['mileage'] is None
    
    def test_normalize_car_data_mixed_case(self):
        result = normalize_car_data(
            make="chevy",
            model="SILVERADO 1500"
        )
        assert result['make'] == "Chevrolet"
        assert result['model'] == "Silverado 1500"
    
    def test_normalize_car_data_renault(self):
        result = normalize_car_data(
            make="RENAULT",
            model="KOLEOS PRIVILEGE"
        )
        assert result['make'] == "Renault"
        assert result['model'] == "Koleos Privilege"
    
    def test_normalize_car_data_bmw_series(self):
        result = normalize_car_data(
            make="bmw",
            model="Serie 3 4p"
        )
        assert result['make'] == "BMW"
        assert result['model'] == "Series 3"


class TestIsNormalized:
    """Test normalization checking"""
    
    def test_is_normalized_true(self):
        assert is_normalized(make="Honda", model="Accord") is True
        assert is_normalized(make="BMW", model="Series 3") is True
    
    def test_is_normalized_false_make(self):
        assert is_normalized(make="honda", model="Accord") is False
        assert is_normalized(make="vw", model="Golf") is False
    
    def test_is_normalized_false_model(self):
        assert is_normalized(make="Honda", model="CR-V 5p") is False
        assert is_normalized(make="BMW", model="Serie 3") is False
    
    def test_is_normalized_none(self):
        assert is_normalized() is True
        assert is_normalized(make=None, model=None) is True


class TestRealWorldCases:
    """Test with real-world examples from scrapers"""
    
    def test_mercado_libre_examples(self):
        # Honda CR-V from Mercado Libre
        result = normalize_car_data(make="Honda", model="Cr-v 5p Touring Hev L4/2.0/t Aut")
        assert result['make'] == "Honda"
        assert result['model'] == "Cr-V Touring Hev L4/2.0/T Aut"
        
        # BMW Serie 2 from Mercado Libre
        result = normalize_car_data(make="Bmw", model="Serie 2 2.0 220i Coupe")
        assert result['make'] == "BMW"
        assert result['model'] == "Series 2 2.0 220I Coupe"
    
    def test_craigslist_examples(self):
        # Renault Koleos from Craigslist
        result = normalize_car_data(make="Renault", model="Koleos")
        assert result['make'] == "Renault"
        assert result['model'] == "Koleos"
        
        # Ford F-250 from Craigslist
        result = normalize_car_data(make="Ford", model="F-250")
        assert result['make'] == "Ford"
        assert result['model'] == "F-250"
    
    def test_edge_cases(self):
        # Empty model
        result = normalize_car_data(make="Honda", model="")
        assert result['make'] == "Honda"
        assert result['model'] is None
        
        # Whitespace
        result = normalize_car_data(make="  Honda  ", model="  Accord  ")
        assert result['make'] == "Honda"
        assert result['model'] == "Accord"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

