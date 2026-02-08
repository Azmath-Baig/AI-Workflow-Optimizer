import pytest
import json
from app import extract_json, engineering_score

class TestJSONExtraction:
    """Test JSON extraction from text with and without noise"""
    
    def test_extract_valid_json(self):
        """Test extraction of valid JSON"""
        result = extract_json('{"test": "value"}')
        assert result == {"test": "value"}
    
    def test_extract_json_with_surrounding_text(self):
        """Test extraction of JSON surrounded by text"""
        result = extract_json('Some explanation {"test": "value"} more text')
        assert result == {"test": "value"}
    
    def test_extract_json_with_newlines(self):
        """Test extraction of JSON with newlines"""
        json_str = '''{
            "key": "value",
            "number": 42
        }'''
        result = extract_json(json_str)
        assert result == {"key": "value", "number": 42}
    
    def test_extract_invalid_json(self):
        """Test that invalid JSON returns None"""
        result = extract_json('no json here at all')
        assert result is None
    
    def test_extract_malformed_json(self):
        """Test that malformed JSON returns None gracefully"""
        result = extract_json('{"incomplete": "json"')
        assert result is None
    
    def test_extract_nested_json(self):
        """Test extraction of nested JSON structures"""
        nested = '{"outer": {"inner": "value"}}'
        result = extract_json(nested)
        assert result == {"outer": {"inner": "value"}}
    
    def test_extract_json_with_array(self):
        """Test extraction of JSON with arrays"""
        with_array = '{"items": [1, 2, 3]}'
        result = extract_json(with_array)
        assert result == {"items": [1, 2, 3]}


class TestSchemaValidation:
    """Test that schema validation works correctly"""
    
    def test_valid_output_structure(self):
        """Test that a valid output passes schema validation"""
        from jsonschema import validate
        from app import SCHEMA
        
        valid_output = {
            "project_specification": {},
            "folder_structure": {},
            "environment_variables": [],
            "security_architecture": {},
            "optimized_prompt": {},
            "ai_prompt_strategy": {
                "generation_sequence": [],
                "validation_loop": "",
                "self_critique_strategy": "",
                "hallucination_prevention_rules": []
            },
            "interaction_plan": [],
            "risks": [],
            "ai_failure_cases": [],
            "testing_checklist": [],
            "refactor_advice": [],
            "secret_hacks": []
        }
        
        # Should not raise exception
        validate(instance=valid_output, schema=SCHEMA)
    
    def test_missing_required_field(self):
        """Test that missing required field raises ValidationError"""
        from jsonschema import validate, ValidationError
        from app import SCHEMA
        
        invalid_output = {
            "project_specification": {},
            # Missing all other required fields
        }
        
        with pytest.raises(ValidationError):
            validate(instance=invalid_output, schema=SCHEMA)
    
    def test_wrong_type_environment_variables(self):
        """Test that wrong type for environment_variables raises error"""
        from jsonschema import validate, ValidationError
        from app import SCHEMA
        
        invalid_output = {
            "project_specification": {},
            "folder_structure": {},
            "environment_variables": "should be array, not string",
            "security_architecture": {},
            "optimized_prompt": {},
            "ai_prompt_strategy": {
                "generation_sequence": [],
                "validation_loop": "",
                "self_critique_strategy": "",
                "hallucination_prevention_rules": []
            },
            "interaction_plan": [],
            "risks": [],
            "ai_failure_cases": [],
            "testing_checklist": [],
            "refactor_advice": [],
            "secret_hacks": []
        }
        
        with pytest.raises(ValidationError):
            validate(instance=invalid_output, schema=SCHEMA)


class TestMultiPassValidation:
    """Test the multi-pass validation logic"""
    
    def test_extraction_then_validation_flow(self):
        """Test that extraction followed by schema validation works"""
        raw_response = '''
        The system generates this plan:
        {
            "project_specification": {},
            "folder_structure": {},
            "environment_variables": [],
            "security_architecture": {},
            "optimized_prompt": {},
            "ai_prompt_strategy": {
                "generation_sequence": [],
                "validation_loop": "test",
                "self_critique_strategy": "test",
                "hallucination_prevention_rules": []
            },
            "interaction_plan": [],
            "risks": [],
            "ai_failure_cases": [],
            "testing_checklist": [],
            "refactor_advice": [],
            "secret_hacks": []
        }
        '''
        
        from jsonschema import validate
        from app import SCHEMA
        
        extracted = extract_json(raw_response)
        assert extracted is not None
        
        # Should validate without raising
        validate(instance=extracted, schema=SCHEMA)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
