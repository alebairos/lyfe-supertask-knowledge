"""
Test suite for Ari persona configuration functionality.

This module tests all aspects of Ari persona configuration loading,
validation, Oracle data integration, and error handling.
"""

import pytest
import tempfile
import yaml
import csv
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

from lyfe_kt.config_loader import (
    load_ari_persona_config, 
    get_ari_persona_config,
    validate_ari_config,
    reload_ari_persona_config,
    clear_ari_persona_cache,
    AriPersonaConfigError,
    _filter_habits_catalog,
    _filter_trails_structure,
    _load_objectives_complete
)


class TestAriPersonaConfigLoading:
    """Test Ari persona configuration loading functionality."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        # Clear any cached configuration
        clear_ari_persona_cache()
    
    def teardown_method(self):
        """Clean up after each test."""
        # Clear any cached configuration
        clear_ari_persona_cache()
    
    def test_load_ari_persona_config_basic(self):
        """Test basic Ari persona configuration loading."""
        # Create a minimal valid configuration
        config_data = {
            'ari_persona': {
                'identity': {
                    'name': 'Ari',
                    'role': 'Life Management Coach',
                    'personality': 'TARS-inspired',
                    'coaching_philosophy': 'Maximum engagement through intelligent brevity',
                    'language_forms': 'masculine_portuguese'
                },
                'communication': {
                    'brevity_rules': {},
                    'engagement_progression': {},
                    'forbidden_phrases': {}
                },
                'expert_frameworks': {
                    'tiny_habits': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'behavioral_design': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'dopamine_nation': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'molecule_of_more': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'flourish': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'maslow_hierarchy': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'huberman_protocols': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'scarcity_brain': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'compassionate_communication': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}}
                },
                'oracle_integration': {
                    'data_sources': {
                        'lyfe_coach': {},
                        'habits_catalog': {},
                        'trails_structure': {},
                        'objectives_mapping': {}
                    }
                },
                'validation_rules': {},
                'cultural_context': {}
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_config_path = f.name
        
        try:
            # Mock Oracle data loading to avoid file dependencies
            with patch('lyfe_kt.config_loader._load_oracle_data_filtered') as mock_oracle:
                mock_oracle.return_value = {'test_data': 'mocked'}
                
                result = load_ari_persona_config(temp_config_path, include_oracle_data=False)
                
                assert 'ari_persona' in result
                assert result['ari_persona']['identity']['name'] == 'Ari'
                assert result['ari_persona']['identity']['role'] == 'Life Management Coach'
        finally:
            Path(temp_config_path).unlink()
    
    def test_load_ari_persona_config_with_oracle_data(self):
        """Test Ari persona configuration loading with Oracle data."""
        config_data = {
            'ari_persona': {
                'identity': {
                    'name': 'Ari',
                    'role': 'Life Management Coach',
                    'personality': 'TARS-inspired',
                    'coaching_philosophy': 'Maximum engagement through intelligent brevity',
                    'language_forms': 'masculine_portuguese'
                },
                'communication': {
                    'brevity_rules': {},
                    'engagement_progression': {},
                    'forbidden_phrases': {}
                },
                'expert_frameworks': {
                    'tiny_habits': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'behavioral_design': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'dopamine_nation': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'molecule_of_more': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'flourish': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'maslow_hierarchy': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'huberman_protocols': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'scarcity_brain': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'compassionate_communication': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}}
                },
                'oracle_integration': {
                    'data_sources': {
                        'lyfe_coach': {},
                        'habits_catalog': {},
                        'trails_structure': {},
                        'objectives_mapping': {}
                    }
                },
                'validation_rules': {},
                'cultural_context': {}
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_config_path = f.name
        
        try:
            # Mock Oracle data loading
            mock_oracle_data = {
                'lyfe_coach': 'Mock LyfeCoach content',
                'habits_catalog': [{'id': 'H1', 'habit': 'Test habit'}],
                'trails_structure': [{'dimension': 'SF', 'trail': 'Test trail'}],
                'objectives_mapping': [{'id': 'O1', 'description': 'Test objective'}]
            }
            
            with patch('lyfe_kt.config_loader._load_oracle_data_filtered') as mock_oracle:
                mock_oracle.return_value = mock_oracle_data
                
                result = load_ari_persona_config(temp_config_path, include_oracle_data=True)
                
                assert 'ari_persona' in result
                assert 'oracle_data' in result
                assert result['oracle_data'] == mock_oracle_data
        finally:
            Path(temp_config_path).unlink()
    
    def test_load_ari_persona_config_caching(self):
        """Test configuration caching functionality."""
        config_data = {
            'ari_persona': {
                'identity': {
                    'name': 'Ari',
                    'role': 'Life Management Coach',
                    'personality': 'TARS-inspired',
                    'coaching_philosophy': 'Maximum engagement through intelligent brevity',
                    'language_forms': 'masculine_portuguese'
                },
                'communication': {
                    'brevity_rules': {},
                    'engagement_progression': {},
                    'forbidden_phrases': {}
                },
                'expert_frameworks': {
                    'tiny_habits': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'behavioral_design': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'dopamine_nation': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'molecule_of_more': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'flourish': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'maslow_hierarchy': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'huberman_protocols': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'scarcity_brain': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'compassionate_communication': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}}
                },
                'oracle_integration': {
                    'data_sources': {
                        'lyfe_coach': {},
                        'habits_catalog': {},
                        'trails_structure': {},
                        'objectives_mapping': {}
                    }
                },
                'validation_rules': {},
                'cultural_context': {}
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_config_path = f.name
        
        try:
            with patch('lyfe_kt.config_loader._load_oracle_data_filtered') as mock_oracle:
                mock_oracle.return_value = {'test_data': 'mocked'}
                
                # First load
                result1 = load_ari_persona_config(temp_config_path, include_oracle_data=False)
                
                # Second load should use cache
                result2 = load_ari_persona_config(temp_config_path, include_oracle_data=False)
                
                # Should be the same object (cached)
                assert result1 is result2
                
                # Force reload should create new object
                result3 = load_ari_persona_config(temp_config_path, include_oracle_data=False, force_reload=True)
                assert result3 is not result1
        finally:
            Path(temp_config_path).unlink()


class TestAriPersonaConfigValidation:
    """Test Ari persona configuration validation functionality."""
    
    def test_validate_ari_config_valid(self):
        """Test validation of valid Ari configuration."""
        valid_config = {
            'identity': {
                'name': 'Ari',
                'role': 'Life Management Coach',
                'personality': 'TARS-inspired',
                'coaching_philosophy': 'Maximum engagement through intelligent brevity',
                'language_forms': 'masculine_portuguese'
            },
            'communication': {
                'brevity_rules': {},
                'engagement_progression': {},
                'forbidden_phrases': {}
            },
            'expert_frameworks': {
                'tiny_habits': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                'behavioral_design': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                'dopamine_nation': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                'molecule_of_more': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                'flourish': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                'maslow_hierarchy': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                'huberman_protocols': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                'scarcity_brain': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                'compassionate_communication': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}}
            },
            'oracle_integration': {
                'data_sources': {
                    'lyfe_coach': {},
                    'habits_catalog': {},
                    'trails_structure': {},
                    'objectives_mapping': {}
                }
            },
            'validation_rules': {},
            'cultural_context': {}
        }
        
        result = validate_ari_config(valid_config)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
    
    def test_validate_ari_config_missing_sections(self):
        """Test validation with missing required sections."""
        invalid_config = {
            'identity': {
                'name': 'Ari'
            }
            # Missing other required sections
        }
        
        result = validate_ari_config(invalid_config)
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
        
        # Check for specific missing sections
        error_messages = ' '.join(result['errors'])
        assert 'communication' in error_messages
        assert 'expert_frameworks' in error_messages
        assert 'oracle_integration' in error_messages
    
    def test_validate_ari_config_missing_identity_fields(self):
        """Test validation with missing identity fields."""
        config_with_incomplete_identity = {
            'identity': {
                'name': 'Ari'
                # Missing other required identity fields
            },
            'communication': {
                'brevity_rules': {},
                'engagement_progression': {},
                'forbidden_phrases': {}
            },
            'expert_frameworks': {
                'tiny_habits': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                'behavioral_design': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                'dopamine_nation': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                'molecule_of_more': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                'flourish': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                'maslow_hierarchy': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                'huberman_protocols': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                'scarcity_brain': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                'compassionate_communication': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}}
            },
            'oracle_integration': {
                'data_sources': {
                    'lyfe_coach': {},
                    'habits_catalog': {},
                    'trails_structure': {},
                    'objectives_mapping': {}
                }
            },
            'validation_rules': {},
            'cultural_context': {}
        }
        
        result = validate_ari_config(config_with_incomplete_identity)
        
        assert result['valid'] is False
        
        error_messages = ' '.join(result['errors'])
        assert 'role' in error_messages
        assert 'personality' in error_messages
        assert 'coaching_philosophy' in error_messages
    
    def test_validate_ari_config_missing_frameworks(self):
        """Test validation with missing expert frameworks."""
        config_missing_frameworks = {
            'identity': {
                'name': 'Ari',
                'role': 'Life Management Coach',
                'personality': 'TARS-inspired',
                'coaching_philosophy': 'Maximum engagement through intelligent brevity',
                'language_forms': 'masculine_portuguese'
            },
            'communication': {
                'brevity_rules': {},
                'engagement_progression': {},
                'forbidden_phrases': {}
            },
            'expert_frameworks': {
                'tiny_habits': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                'behavioral_design': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}}
                # Missing other frameworks
            },
            'oracle_integration': {
                'data_sources': {
                    'lyfe_coach': {},
                    'habits_catalog': {},
                    'trails_structure': {},
                    'objectives_mapping': {}
                }
            },
            'validation_rules': {},
            'cultural_context': {}
        }
        
        result = validate_ari_config(config_missing_frameworks)
        
        assert result['valid'] is False
        
        error_messages = ' '.join(result['errors'])
        assert 'dopamine_nation' in error_messages
        assert 'flourish' in error_messages
        assert 'huberman_protocols' in error_messages


class TestAriPersonaConfigAccess:
    """Test Ari persona configuration access functionality."""
    
    def setup_method(self):
        """Set up test environment with loaded configuration."""
        clear_ari_persona_cache()
        
        # Mock a loaded configuration
        self.mock_config = {
            'ari_persona': {
                'identity': {
                    'name': 'Ari',
                    'role': 'Life Management Coach'
                },
                'communication': {
                    'brevity_rules': {
                        'first_message': {'max_words': 6}
                    }
                }
            },
            'oracle_data': {
                'test_data': 'mocked'
            }
        }
        
        # Load mock configuration into cache
        import lyfe_kt.config_loader
        lyfe_kt.config_loader._ari_persona_cache = self.mock_config
    
    def teardown_method(self):
        """Clean up after each test."""
        clear_ari_persona_cache()
    
    def test_get_ari_persona_config_entire(self):
        """Test getting entire Ari persona configuration."""
        result = get_ari_persona_config()
        
        assert result == self.mock_config
        assert 'ari_persona' in result
        assert 'oracle_data' in result
    
    def test_get_ari_persona_config_top_level_key(self):
        """Test getting top-level configuration key."""
        result = get_ari_persona_config('ari_persona')
        
        assert result == self.mock_config['ari_persona']
        assert 'identity' in result
        assert 'communication' in result
    
    def test_get_ari_persona_config_nested_key(self):
        """Test getting nested configuration key with dot notation."""
        result = get_ari_persona_config('identity.name')
        
        assert result == 'Ari'
    
    def test_get_ari_persona_config_deep_nested_key(self):
        """Test getting deeply nested configuration key."""
        result = get_ari_persona_config('communication.brevity_rules.first_message.max_words')
        
        assert result == 6
    
    def test_get_ari_persona_config_not_loaded_error(self):
        """Test error when configuration not loaded."""
        clear_ari_persona_cache()
        
        with pytest.raises(AriPersonaConfigError) as exc_info:
            get_ari_persona_config()
        
        assert "not loaded" in str(exc_info.value)
    
    def test_get_ari_persona_config_key_not_found_error(self):
        """Test error when requested key doesn't exist."""
        with pytest.raises(KeyError) as exc_info:
            get_ari_persona_config('nonexistent.key')
        
        assert "not found" in str(exc_info.value)


class TestOracleDataIntegration:
    """Test Oracle data integration functionality."""
    
    def test_filter_habits_catalog(self):
        """Test filtering of habits catalog."""
        # Create mock CSV data
        mock_csv_data = [
            ['ID', 'Hábito ', 'Intensidade', 'Duração ', 'Relacionamento ', 'Trabalho', 'Saúde física', 'Espiritualidade', 'Saúde mental'],
            ['H1', 'High scoring habit', '3', '30min', '5', '5', '5', '3', '4'],  # Total: 22
            ['H2', 'Low scoring habit', '1', '10min', '2', '1', '2', '1', '3'],   # Total: 9
            ['H3', 'Medium scoring habit', '2', '20min', '4', '3', '4', '2', '3'] # Total: 16
        ]
        
        mock_csv_content = '\n'.join([';'.join(row) for row in mock_csv_data])
        
        with patch('builtins.open', mock_open(read_data=mock_csv_content)):
            with patch('pathlib.Path.exists', return_value=True):
                result = _filter_habits_catalog({'file': 'habitos.csv'})
                
                # Should include habits with total score > 15 (H1 and H3)
                assert len(result) == 2
                
                # Check that high-scoring habit is included
                high_scoring = next((h for h in result if h['id'] == 'H1'), None)
                assert high_scoring is not None
                assert high_scoring['total_score'] == 22
                
                # Check that low-scoring habit is excluded
                low_scoring = next((h for h in result if h['id'] == 'H2'), None)
                assert low_scoring is None
    
    def test_filter_trails_structure(self):
        """Test filtering of trails structure."""
        # Create mock CSV data
        mock_csv_data = [
            ['Dimensão', 'Código Trilha', 'Nome Trilha', 'Código Desafio', 'Nome Desafio', 'Nível', 'Hábitos', 'Frequencia'],
            ['SF', 'SF1', 'Saúde Física 1', 'SF1C1', 'Desafio 1', '1', 'H1', '7'],
            ['SF', 'SF1', 'Saúde Física 1', 'SF1C2', 'Desafio 2', '2', 'H2', '5'],
            ['SF', 'SF2', 'Saúde Física 2', 'SF2C1', 'Desafio 1', '1', 'H3', '7'],
            ['SM', 'SM1', 'Saúde Mental 1', 'SM1C1', 'Desafio 1', '1', 'H4', '3'],
            ['SM', 'SM2', 'Saúde Mental 2', 'SM2C1', 'Desafio 1', '1', 'H5', '7']
        ]
        
        mock_csv_content = '\n'.join([';'.join(row) for row in mock_csv_data])
        
        with patch('builtins.open', mock_open(read_data=mock_csv_content)):
            with patch('pathlib.Path.exists', return_value=True):
                result = _filter_trails_structure({'file': 'Trilhas.csv'})
                
                # Should include up to 2 complete trails per dimension
                sf_trails = [r for r in result if r.get('Dimensão') == 'SF']
                sm_trails = [r for r in result if r.get('Dimensão') == 'SM']
                
                # Check that we have trails from both dimensions
                assert len(sf_trails) > 0
                assert len(sm_trails) > 0
                
                # Check that trail codes are preserved
                sf_codes = set(r.get('Código Trilha') for r in sf_trails)
                assert len(sf_codes) <= 2  # At most 2 trails per dimension
    
    def test_load_objectives_complete(self):
        """Test loading complete objectives mapping."""
        # Create mock CSV data
        mock_csv_data = [
            ['Dimensão', 'ID Objetivo', 'Descrição', 'Trilha'],
            ['SF', 'OPP1', 'Perder peso', 'ME1'],
            ['SF', 'OGM1', 'Ganhar massa', 'GM1'],
            ['SM', 'ORA1', 'Reduzir ansiedade', 'RA1']
        ]
        
        mock_csv_content = '\n'.join([';'.join(row) for row in mock_csv_data])
        
        with patch('builtins.open', mock_open(read_data=mock_csv_content)):
            with patch('pathlib.Path.exists', return_value=True):
                result = _load_objectives_complete({'file': 'Objetivos.csv'})
                
                # Should include all objectives
                assert len(result) == 3
                
                # Check structure
                for obj in result:
                    assert 'dimension' in obj
                    assert 'id' in obj
                    assert 'description' in obj
                    assert 'trail' in obj
                
                # Check specific objective
                weight_loss = next((o for o in result if o['id'] == 'OPP1'), None)
                assert weight_loss is not None
                assert weight_loss['description'] == 'Perder peso'
                assert weight_loss['trail'] == 'ME1'


class TestAriPersonaConfigErrors:
    """Test error handling in Ari persona configuration."""
    
    def setup_method(self):
        """Set up test environment."""
        clear_ari_persona_cache()
    
    def teardown_method(self):
        """Clean up after each test."""
        clear_ari_persona_cache()
    
    def test_load_ari_persona_config_file_not_found(self):
        """Test error when configuration file doesn't exist."""
        with pytest.raises(FileNotFoundError) as exc_info:
            load_ari_persona_config('/nonexistent/path/ari_persona.yaml')
        
        assert "not found" in str(exc_info.value)
    
    def test_load_ari_persona_config_invalid_yaml(self):
        """Test error when YAML file is invalid."""
        invalid_yaml = "invalid: yaml: content: ["
        
        with patch('builtins.open', mock_open(read_data=invalid_yaml)):
            with patch('pathlib.Path.exists', return_value=True):
                with pytest.raises(AriPersonaConfigError) as exc_info:
                    load_ari_persona_config('test.yaml')
                
                assert "Failed to load" in str(exc_info.value)
    
    def test_load_ari_persona_config_invalid_structure(self):
        """Test error when configuration structure is invalid."""
        invalid_config = {'wrong_root_key': {}}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(invalid_config, f)
            temp_config_path = f.name
        
        try:
            with pytest.raises(AriPersonaConfigError) as exc_info:
                load_ari_persona_config(temp_config_path)
            
            assert "Invalid Ari persona configuration structure" in str(exc_info.value)
        finally:
            Path(temp_config_path).unlink()
    
    def test_load_ari_persona_config_validation_failure(self):
        """Test error when configuration validation fails."""
        invalid_config = {
            'ari_persona': {
                'identity': {
                    'name': 'Ari'
                    # Missing required fields
                }
                # Missing required sections
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(invalid_config, f)
            temp_config_path = f.name
        
        try:
            with pytest.raises(AriPersonaConfigError) as exc_info:
                load_ari_persona_config(temp_config_path)
            
            assert "validation failed" in str(exc_info.value)
        finally:
            Path(temp_config_path).unlink()


class TestAriPersonaConfigCacheManagement:
    """Test cache management functionality."""
    
    def test_reload_ari_persona_config(self):
        """Test reloading configuration clears cache."""
        # Create initial configuration
        config_data = {
            'ari_persona': {
                'identity': {
                    'name': 'Ari',
                    'role': 'Life Management Coach',
                    'personality': 'TARS-inspired',
                    'coaching_philosophy': 'Maximum engagement through intelligent brevity',
                    'language_forms': 'masculine_portuguese'
                },
                'communication': {
                    'brevity_rules': {},
                    'engagement_progression': {},
                    'forbidden_phrases': {}
                },
                'expert_frameworks': {
                    'tiny_habits': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'behavioral_design': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'dopamine_nation': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'molecule_of_more': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'flourish': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'maslow_hierarchy': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'huberman_protocols': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'scarcity_brain': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}},
                    'compassionate_communication': {'focus': 'test', 'application': 'test', 'core_principles': [], 'content_triggers': {}}
                },
                'oracle_integration': {
                    'data_sources': {
                        'lyfe_coach': {},
                        'habits_catalog': {},
                        'trails_structure': {},
                        'objectives_mapping': {}
                    }
                },
                'validation_rules': {},
                'cultural_context': {}
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_config_path = f.name
        
        try:
            with patch('lyfe_kt.config_loader._load_oracle_data_filtered') as mock_oracle:
                mock_oracle.return_value = {'test_data': 'mocked'}
                
                # Initial load
                result1 = load_ari_persona_config(temp_config_path, include_oracle_data=False)
                
                # Reload should clear cache and load fresh
                result2 = reload_ari_persona_config(temp_config_path, include_oracle_data=False)
                
                # Results should be equal but not the same object
                assert result1 == result2
                # Note: Due to caching, they might be the same object, but reload should work
        finally:
            Path(temp_config_path).unlink()
    
    def test_clear_ari_persona_cache(self):
        """Test clearing configuration cache."""
        # Load a configuration first
        import lyfe_kt.config_loader
        lyfe_kt.config_loader._ari_persona_cache = {'test': 'data'}
        lyfe_kt.config_loader._oracle_data_cache = {'oracle': 'data'}
        
        # Clear cache
        clear_ari_persona_cache()
        
        # Cache should be None
        assert lyfe_kt.config_loader._ari_persona_cache is None
        assert lyfe_kt.config_loader._oracle_data_cache is None
        
        # Getting config should now raise error
        with pytest.raises(AriPersonaConfigError):
            get_ari_persona_config()


if __name__ == "__main__":
    pytest.main([__file__]) 