"""
Format Version Manager for Lyfe Supertask Knowledge Generator

This module manages different format versions and provides migration capabilities
for evolving JSON structures while maintaining backward compatibility.
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class FormatVersionManager:
    """
    Manages different format versions for evolution.
    
    Provides capabilities for:
    - Loading version-specific schemas and generators
    - Migrating content between format versions
    - Detecting format versions automatically
    - Managing deprecation and compatibility
    """
    
    SUPPORTED_VERSIONS = {
        "v1.0": {
            "schema_file": "supertask_schema_v1.0.json",
            "generator_class": "StructuralJSONGenerator",
            "deprecated": True,
            "description": "Initial structural format with guaranteed compliance",
            "introduced": "2025-07-16"
        },
        "v1.1": {
            "schema_file": "supertask_schema_v1.1.json", 
            "generator_class": "StructuralJSONGenerator",
            "deprecated": False,
            "migration_from": ["v1.0"],
            "description": "Mobile-optimized format with character limits",
            "introduced": "2025-01-14"
        }
    }
    
    DEFAULT_VERSION = "v1.1"
    SCHEMA_DIR = "src/config"
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize format version manager.
        
        Args:
            config_dir: Optional custom configuration directory.
        """
        self.config_dir = config_dir or self.SCHEMA_DIR
        self._schemas_cache = {}
        self._generators_cache = {}
        logger.info("Format version manager initialized")
    
    def get_supported_versions(self) -> List[str]:
        """Get list of supported format versions."""
        return list(self.SUPPORTED_VERSIONS.keys())
    
    def get_current_version(self) -> str:
        """Get the current default version."""
        return self.DEFAULT_VERSION
    
    def get_latest_version(self) -> str:
        """Get the latest available version."""
        versions = self.get_supported_versions()
        # Simple version sorting (assumes semantic versioning)
        return max(versions, key=lambda v: tuple(map(int, v[1:].split('.'))))
    
    def is_version_supported(self, version: str) -> bool:
        """Check if a format version is supported."""
        return version in self.SUPPORTED_VERSIONS
    
    def is_version_deprecated(self, version: str) -> bool:
        """Check if a format version is deprecated."""
        return self.SUPPORTED_VERSIONS.get(version, {}).get('deprecated', False)
    
    def get_version_info(self, version: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific version."""
        return self.SUPPORTED_VERSIONS.get(version)
    
    def load_schema(self, version: str) -> Dict[str, Any]:
        """
        Load JSON Schema for a specific version.
        
        Args:
            version: Format version (e.g., "v1.0").
            
        Returns:
            JSON Schema dictionary.
            
        Raises:
            FileNotFoundError: If schema file doesn't exist.
            ValueError: If version is not supported.
        """
        if not self.is_version_supported(version):
            raise ValueError(f"Unsupported format version: {version}")
        
        # Check cache first
        if version in self._schemas_cache:
            return self._schemas_cache[version]
        
        # Load schema from file
        version_info = self.SUPPORTED_VERSIONS[version]
        schema_file = version_info["schema_file"]
        schema_path = Path(self.config_dir) / schema_file
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        # Cache for future use
        self._schemas_cache[version] = schema
        logger.info(f"Loaded schema for version {version}")
        
        return schema
    
    def get_generator(self, version: str = None) -> Any:
        """
        Get appropriate generator for format version.
        
        Args:
            version: Format version. If None, uses default.
            
        Returns:
            Generator instance for the specified version.
            
        Raises:
            ValueError: If version is not supported.
        """
        if version is None:
            version = self.DEFAULT_VERSION
            
        if not self.is_version_supported(version):
            raise ValueError(f"Unsupported format version: {version}")
        
        # Check cache first
        if version in self._generators_cache:
            return self._generators_cache[version]
        
        # Import and create generator
        version_info = self.SUPPORTED_VERSIONS[version]
        generator_class = version_info["generator_class"]
        
        # For now, all versions use the same generator class
        # In the future, this could import different classes for different versions
        from .stage3_generation import StructuralJSONGenerator
        generator = StructuralJSONGenerator(format_version=version)
        
        # Cache for future use
        self._generators_cache[version] = generator
        logger.info(f"Created generator for version {version}")
        
        return generator
    
    def detect_format_version(self, content: Dict[str, Any]) -> Optional[str]:
        """
        Auto-detect format version from content.
        
        Args:
            content: JSON content to analyze.
            
        Returns:
            Detected version string or None if couldn't detect.
        """
        try:
            # Check metadata for version info
            metadata = content.get('metadata', {})
            if 'version' in metadata:
                # Try to map version string to format version
                version_string = metadata['version']
                if version_string.startswith('1.0'):
                    return 'v1.0'
            
            # Try validating against each schema to detect version
            for version in self.get_supported_versions():
                try:
                    schema = self.load_schema(version)
                    import jsonschema
                    jsonschema.validate(content, schema)
                    logger.info(f"Content matches format version {version}")
                    return version
                except jsonschema.ValidationError:
                    continue
                except ImportError:
                    # jsonschema not available, fall back to structure analysis
                    break
            
            # Fallback: analyze structure characteristics
            if self._has_v1_structure(content):
                return 'v1.0'
            
            logger.warning("Could not detect format version")
            return None
            
        except Exception as e:
            logger.error(f"Error detecting format version: {e}")
            return None
    
    def _has_v1_structure(self, content: Dict[str, Any]) -> bool:
        """Check if content has v1.0 structure characteristics."""
        required_v1_fields = [
            'title', 'dimension', 'archetype', 'relatedToType', 
            'relatedToId', 'estimatedDuration', 'coinsReward', 
            'flexibleItems', 'metadata'
        ]
        
        return all(field in content for field in required_v1_fields)
    
    def migrate_format(self, content: Dict[str, Any], from_version: str, to_version: str) -> Dict[str, Any]:
        """
        Migrate content between format versions.
        
        Args:
            content: Content to migrate.
            from_version: Source format version.
            to_version: Target format version.
            
        Returns:
            Migrated content.
            
        Raises:
            ValueError: If migration path is not supported.
        """
        if from_version == to_version:
            return content.copy()
        
        if not self.is_version_supported(from_version):
            raise ValueError(f"Unsupported source version: {from_version}")
        
        if not self.is_version_supported(to_version):
            raise ValueError(f"Unsupported target version: {to_version}")
        
        # For now, only support migration within v1.x versions
        if from_version == "v1.0" and to_version.startswith("v1."):
            return self._migrate_v1_0_to_v1_x(content, to_version)
        
        raise ValueError(f"Migration from {from_version} to {to_version} not implemented")
    
    def _migrate_v1_0_to_v1_x(self, content: Dict[str, Any], to_version: str) -> Dict[str, Any]:
        """
        Migrate from v1.0 to v1.x versions.
        
        Args:
            content: v1.0 content.
            to_version: Target v1.x version.
            
        Returns:
            Migrated content.
        """
        migrated = content.copy()
        
        # Update metadata
        migrated['metadata']['migrated_from'] = 'v1.0'
        migrated['metadata']['migrated_at'] = datetime.now().isoformat()
        migrated['metadata']['format_version'] = to_version
        
        # Future migrations would add version-specific transformations here
        
        logger.info(f"Migrated content from v1.0 to {to_version}")
        return migrated
    
    def validate_content(self, content: Dict[str, Any], version: str = None) -> Dict[str, Any]:
        """
        Validate content against format version.
        
        Args:
            content: Content to validate.
            version: Format version. If None, auto-detects.
            
        Returns:
            Validation result with 'valid' boolean and details.
        """
        try:
            if version is None:
                version = self.detect_format_version(content)
                if version is None:
                    return {
                        'valid': False,
                        'errors': ['Could not detect format version'],
                        'version': None
                    }
            
            schema = self.load_schema(version)
            
            try:
                import jsonschema
                jsonschema.validate(content, schema)
                return {
                    'valid': True,
                    'errors': [],
                    'version': version,
                    'schema_validated': True
                }
            except jsonschema.ValidationError as e:
                return {
                    'valid': False,
                    'errors': [e.message],
                    'version': version,
                    'schema_validated': True
                }
            except ImportError:
                # Fallback validation without jsonschema
                return {
                    'valid': self._has_v1_structure(content),
                    'errors': [] if self._has_v1_structure(content) else ['Structure validation failed'],
                    'version': version,
                    'schema_validated': False
                }
                
        except Exception as e:
            return {
                'valid': False,
                'errors': [str(e)],
                'version': version,
                'schema_validated': False
            } 