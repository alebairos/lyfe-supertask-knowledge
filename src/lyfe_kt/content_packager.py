"""
Content Packaging Module for Lyfe Supertask Knowledge Generator

This module provides functionality to package pipeline content into organized
folders and clean up the work directory for the next project.

Simple implementation focused on core functionality:
- Auto-detect titles from supertask files
- Create timestamped package folders
- Move content safely (no deletion)
- Clean work directory while preserving structure
"""

import os
import shutil
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from .session_logger import SessionLogger, get_session
import glob

logger = logging.getLogger(__name__)


class ContentPackagingError(Exception):
    """Custom exception for content packaging errors."""
    pass


class ContentPackager:
    """
    Simple content packager that organizes pipeline output into timestamped folders.
    
    The simplest thing that could possibly work:
    1. Auto-detect title from generated supertasks
    2. Create packages/title-date-time/ folder
    3. Move work content to package
    4. Clean work directory but keep structure
    """
    
    def __init__(self, work_dir: str = "work", packages_dir: str = "packages"):
        """
        Initialize content packager.
        
        Args:
            work_dir: Work directory containing pipeline output
            packages_dir: Target directory for packaged content
        """
        self.work_dir = Path(work_dir)
        self.packages_dir = Path(packages_dir)
        self.work_subdirs = ["01_raw", "02_preprocessed", "03_output", "reports"]
        
        logger.info(f"ContentPackager initialized: {self.work_dir} → {self.packages_dir}")
    
    def detect_title(self) -> str:
        """
        Auto-detect package title from supertask files.
        
        Logic:
        1. Look for JSON files in work/03_output/
        2. Extract common prefix from filenames
        3. Fallback to timestamp if no clear pattern
        
        Returns:
            Detected title string
        """
        try:
            output_dir = self.work_dir / "03_output"
            
            if not output_dir.exists():
                logger.warning(f"Output directory not found: {output_dir}")
                return self._get_timestamp_title()
            
            # Find all JSON files
            json_files = list(output_dir.glob("*.json"))
            
            if not json_files:
                logger.warning("No JSON files found in output directory")
                return self._get_timestamp_title()
            
            # Extract common prefix from filenames
            filenames = [f.stem for f in json_files]  # Remove .json extension
            logger.info(f"Found {len(filenames)} files: {filenames[:3]}...")
            
            # Find common prefix
            if len(filenames) == 1:
                # Single file - use its name (remove numbers/suffixes)
                title = self._clean_filename(filenames[0])
            else:
                # Multiple files - find common prefix
                title = self._find_common_prefix(filenames)
            
            if not title or len(title) < 3:
                logger.warning(f"No clear title pattern found, using timestamp")
                return self._get_timestamp_title()
            
            logger.info(f"Auto-detected title: '{title}'")
            return title
            
        except Exception as e:
            logger.error(f"Error detecting title: {e}")
            return self._get_timestamp_title()
    
    def _clean_filename(self, filename: str) -> str:
        """Clean filename to extract meaningful title."""
        # Remove common suffixes and numbers
        cleaned = filename
        
        # Remove numbered suffixes like "_01", "_02"
        import re
        cleaned = re.sub(r'_\d+$', '', cleaned)
        
        # Remove difficulty suffixes
        cleaned = re.sub(r'_(beginner|advanced)$', '', cleaned)
        
        # Remove timestamp patterns
        cleaned = re.sub(r'_\d{4}-\d{2}-\d{2}.*$', '', cleaned)
        
        return cleaned
    
    def _find_common_prefix(self, filenames: List[str]) -> str:
        """Find common prefix from multiple filenames."""
        if not filenames:
            return ""
        
        # Clean all filenames first
        cleaned_names = [self._clean_filename(name) for name in filenames]
        
        # Find common prefix
        prefix = cleaned_names[0]
        for name in cleaned_names[1:]:
            while prefix and not name.startswith(prefix):
                prefix = prefix[:-1]
        
        # Remove trailing underscores or hyphens
        prefix = prefix.rstrip('_-')
        
        return prefix
    
    def _get_timestamp_title(self) -> str:
        """Generate timestamp-based title as fallback."""
        return f"content-{datetime.now().strftime('%Y-%m-%d')}"
    
    def create_package(self, title: Optional[str] = None) -> str:
        """
        Create timestamped package folder.
        
        Args:
            title: Optional custom title. If None, auto-detects.
            
        Returns:
            Path to created package folder
        """
        try:
            if title is None:
                title = self.detect_title()
            
            # Create timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
            package_name = f"{title}-{timestamp}"
            
            # Create package directory
            package_path = self.packages_dir / package_name
            package_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Created package directory: {package_path}")
            return str(package_path)
            
        except Exception as e:
            raise ContentPackagingError(f"Failed to create package: {e}")
    
    def move_content(self, package_path: str):
        """
        Move all work content to package folder.
        
        Args:
            package_path: Target package directory
        """
        try:
            package_dir = Path(package_path)
            files_moved = 0
            
            # Move each work subdirectory
            for subdir_name in self.work_subdirs:
                source_dir = self.work_dir / subdir_name
                target_dir = package_dir / subdir_name
                
                if source_dir.exists() and any(source_dir.iterdir()):
                    # Directory has content, move it
                    shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
                    
                    # Count files moved
                    if target_dir.exists():
                        moved_files = len(list(target_dir.rglob("*")))
                        files_moved += moved_files
                        logger.info(f"Moved {moved_files} items from {subdir_name}/")
                else:
                    # Create empty directory in package
                    target_dir.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created empty directory: {subdir_name}/")
            
            # Move any other files in work root (exclude workspace files)
            exclude_files = {".gitignore", "README.md"}
            for item in self.work_dir.iterdir():
                if item.is_file() and item.name not in exclude_files:
                    target_file = package_dir / item.name
                    shutil.copy2(item, target_file)
                    files_moved += 1
                    logger.info(f"Moved file: {item.name}")
                else:
                    logger.info(f"Skipped workspace file: {item.name}")
            
            logger.info(f"Total files moved: {files_moved}")
            
        except Exception as e:
            raise ContentPackagingError(f"Failed to move content: {e}")
    
    def clean_work_directory(self):
        """
        Clean work directory but preserve structural folders.
        
        Removes all files and content but keeps the folder structure:
        - work/01_raw/ (empty)
        - work/02_preprocessed/ (empty)  
        - work/03_output/ (empty)
        - work/reports/ (empty)
        """
        try:
            files_removed = 0
            
            # Clean each subdirectory
            for subdir_name in self.work_subdirs:
                subdir_path = self.work_dir / subdir_name
                
                if subdir_path.exists():
                    # Remove all contents but keep the directory
                    for item in subdir_path.iterdir():
                        if item.is_dir():
                            shutil.rmtree(item)
                        else:
                            item.unlink()
                        files_removed += 1
                    logger.info(f"Cleaned {subdir_name}/ (kept folder structure)")
                else:
                    # Create the directory if it doesn't exist
                    subdir_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created structural directory: {subdir_name}/")
            
            # Remove files in work root (but keep .gitignore, README.md)
            keep_files = {".gitignore", "README.md"}
            for item in self.work_dir.iterdir():
                if item.is_file() and item.name not in keep_files:
                    item.unlink()
                    files_removed += 1
                    logger.info(f"Removed file: {item.name}")
            
            logger.info(f"Work directory cleaned: {files_removed} items removed, structure preserved")
            
        except Exception as e:
            raise ContentPackagingError(f"Failed to clean work directory: {e}")
    
    def package_content(self, title: Optional[str] = None, keep_work: bool = False, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete packaging workflow with execution logs - the main method.
        
        Args:
            title: Optional custom title
            keep_work: If True, don't clean work directory
            session_id: Optional session ID for log correlation
            
        Returns:
            Dictionary with packaging results
        """
        try:
            logger.info("Starting content packaging workflow")
            
            # Check if there's content to package
            if not self._has_content_to_package():
                logger.warning("No content found to package")
                return {
                    "success": False,
                    "message": "No content found in work directory",
                    "package_path": None
                }
            
            # Create package
            package_path = self.create_package(title)
            
            # Move content
            self.move_content(package_path)
            
            # 🆕 NEW: Copy execution logs and create documentation
            logs_captured = self._copy_execution_logs(package_path, session_id)
            
            # Clean work directory (unless keep_work is True)
            if not keep_work:
                self.clean_work_directory()
            
            result = {
                "success": True,
                "message": f"Content packaged successfully with {logs_captured} log files",
                "package_path": package_path,
                "title": title or self.detect_title(),
                "logs_captured": logs_captured
            }
            
            logger.info(f"Packaging completed successfully: {package_path}")
            return result
            
        except Exception as e:
            logger.error(f"Packaging failed: {e}")
            return {
                "success": False,
                "message": f"Packaging failed: {str(e)}",
                "package_path": None
            }
    
    def _has_content_to_package(self) -> bool:
        """Check if work directory has any content to package."""
        try:
            for subdir_name in self.work_subdirs:
                subdir_path = self.work_dir / subdir_name
                if subdir_path.exists() and any(subdir_path.iterdir()):
                    return True
            
            # Check for files in work root
            for item in self.work_dir.iterdir():
                if item.is_file() and item.name not in {".gitignore", "README.md"}:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _copy_execution_logs(self, package_path: Path, session_id: Optional[str] = None) -> int:
        """
        Copy execution logs and create documentation for the package.
        
        Args:
            package_path: Path to the package directory
            session_id: Optional session ID for log correlation
            
        Returns:
            Number of log files captured
        """
        try:
            logs_captured = 0
            logs_dir = package_path / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            # Copy prompt audit logs
            prompt_audit_file = Path("logs") / "prompts" / "prompts_audit.log"
            if prompt_audit_file.exists():
                if session_id:
                    # Filter logs by session ID
                    self._copy_session_specific_logs(prompt_audit_file, logs_dir / "prompts_audit.log", session_id)
                else:
                    # Copy all prompt logs
                    shutil.copy2(prompt_audit_file, logs_dir / "prompts_audit.log")
                logs_captured += 1
            
            # Copy processing logs
            processing_log_file = Path("logs") / "lyfe-kt.log"
            if processing_log_file.exists():
                if session_id:
                    # Filter processing logs by session ID
                    self._copy_session_specific_logs(processing_log_file, logs_dir / "processing.log", session_id)
                else:
                    # Copy recent processing logs (last 1000 lines)
                    self._copy_recent_logs(processing_log_file, logs_dir / "processing.log")
                logs_captured += 1
            
            # Generate execution summary and metadata
            if session_id:
                session_logger = get_session(session_id)
                if session_logger:
                    # Generate execution summary
                    summary_content = session_logger.generate_execution_summary()
                    with open(logs_dir / "execution_summary.md", 'w', encoding='utf-8') as f:
                        f.write(summary_content)
                    logs_captured += 1
                    
                    # Generate execution metadata
                    metadata = session_logger.get_session_metadata()
                    with open(logs_dir / "metadata.json", 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)
                    logs_captured += 1
            
            logger.info(f"Captured {logs_captured} log files in package")
            return logs_captured
            
        except Exception as e:
            logger.error(f"Failed to copy execution logs: {e}")
            return 0
    
    def _copy_session_specific_logs(self, source_file: Path, target_file: Path, session_id: str):
        """Copy only logs related to specific session."""
        try:
            with open(source_file, 'r', encoding='utf-8') as source:
                with open(target_file, 'w', encoding='utf-8') as target:
                    current_entry = []
                    in_session_entry = False
                    
                    for line in source:
                        if line.startswith("=== PROMPT REQUEST ===") or line.startswith("=== RESPONSE ==="):
                            # Save previous entry if it was for our session
                            if in_session_entry and current_entry:
                                target.writelines(current_entry)
                            
                            # Start new entry
                            current_entry = [line]
                            in_session_entry = False
                        elif line.startswith("Session ID:"):
                            current_entry.append(line)
                            # Check if this entry is for our session
                            if session_id in line:
                                in_session_entry = True
                        else:
                            current_entry.append(line)
                    
                    # Don't forget the last entry
                    if in_session_entry and current_entry:
                        target.writelines(current_entry)
                        
        except Exception as e:
            logger.error(f"Failed to filter session logs: {e}")
            # Fallback: copy entire file
            shutil.copy2(source_file, target_file)
    
    def _copy_recent_logs(self, source_file: Path, target_file: Path, max_lines: int = 1000):
        """Copy recent logs from source to target."""
        try:
            with open(source_file, 'r', encoding='utf-8') as source:
                lines = source.readlines()
                recent_lines = lines[-max_lines:] if len(lines) > max_lines else lines
                
            with open(target_file, 'w', encoding='utf-8') as target:
                target.writelines(recent_lines)
                
        except Exception as e:
            logger.error(f"Failed to copy recent logs: {e}")
            # Fallback: copy entire file
            shutil.copy2(source_file, target_file) 