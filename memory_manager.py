"""
Memory management for the AI Proposal Deck Generator.
Handles saving/loading proposal data and conversation history.
"""

import json
import os
import logging
from typing import Optional
from datetime import datetime

from data_models import ProposalMemory, Slide, SlideVersion, SolutionIteration
from config import config_manager

logger = logging.getLogger(__name__)

class MemoryManager:
    """Handles all memory operations for proposal data."""
    
    def __init__(self, memory_file: Optional[str] = None):
        self.memory_file = memory_file or config_manager.get_config().memory_file
    
    def load_memory(self) -> Optional[ProposalMemory]:
        """Load memory from JSON file."""
        try:
            if not os.path.exists(self.memory_file):
                logger.info("No existing memory file found")
                return None
            
            with open(self.memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Reconstruct slides with versions
            slides = {}
            for k, v in data.get("slides", {}).items():
                slide = Slide(component_key=k, title=v["title"], content=v["content"])
                
                # Reconstruct versions
                for version_data in v.get("versions", []):
                    slide.versions.append(SlideVersion(**version_data))
                
                slides[k] = slide
            
            # Reconstruct solution iterations
            solution_iterations = []
            for iter_data in data.get("solution_iterations", []):
                solution_iterations.append(SolutionIteration(**iter_data))
            
            memory = ProposalMemory(
                client_name=data["client_name"],
                problem_statement=data["problem_statement"],
                current_solution=data["current_solution"],
                solution_finalized=data.get("solution_finalized", False),
                project_title=data.get("project_title", ""),
                company_name=data.get("company_name", "Your Company"),
                selected_components=data.get("selected_components", []),
                slides=slides,
                solution_iterations=solution_iterations,
                conversation_history=data.get("conversation_history", []),
                created_at=data.get("created_at", datetime.now().isoformat()),
                last_updated=data.get("last_updated", datetime.now().isoformat())
            )
            
            logger.info(f"Memory loaded successfully from {self.memory_file}")
            return memory
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in memory file: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading memory: {e}")
            return None

    def save_memory(self, memory: ProposalMemory) -> bool:
        """Save memory to JSON file."""
        try:
            # Convert slides to serializable format
            slides = {}
            for k, v in memory.slides.items():
                slides[k] = {
                    "title": v.title,
                    "content": v.content,
                    "versions": [
                        {
                            "version": ver.version,
                            "content": ver.content,
                            "timestamp": ver.timestamp,
                            "user_feedback": ver.user_feedback
                        }
                        for ver in v.versions
                    ]
                }
            
            # Convert solution iterations
            solution_iterations = [
                {
                    "iteration": si.iteration,
                    "solution": si.solution,
                    "rationale": si.rationale,
                    "timestamp": si.timestamp
                }
                for si in memory.solution_iterations
            ]
            
            # Update timestamp
            memory.last_updated = datetime.now().isoformat()
            
            # Prepare data for JSON serialization
            data = {
                "client_name": memory.client_name,
                "problem_statement": memory.problem_statement,
                "current_solution": memory.current_solution,
                "solution_finalized": memory.solution_finalized,
                "project_title": memory.project_title,
                "company_name": memory.company_name,
                "selected_components": memory.selected_components,
                "slides": slides,
                "solution_iterations": solution_iterations,
                "conversation_history": memory.conversation_history,
                "created_at": memory.created_at,
                "last_updated": memory.last_updated
            }
            
            # Create backup of existing file if it exists
            if os.path.exists(self.memory_file):
                backup_file = f"{self.memory_file}.backup"
                try:
                    os.rename(self.memory_file, backup_file)
                except OSError:
                    pass  # Backup failed, continue with save
            
            # Save to file
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info("Memory saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
            return False
    
    def backup_memory(self, backup_suffix: Optional[str] = None) -> str:
        """Create a backup of current memory file."""
        if not os.path.exists(self.memory_file):
            raise FileNotFoundError("No memory file to backup")
        
        if not backup_suffix:
            backup_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        backup_file = f"{self.memory_file}.backup_{backup_suffix}"
        
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as src:
                with open(backup_file, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            logger.info(f"Memory backed up to {backup_file}")
            return backup_file
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise
    
    def restore_memory(self, backup_file: str) -> bool:
        """Restore memory from backup file."""
        try:
            if not os.path.exists(backup_file):
                raise FileNotFoundError(f"Backup file not found: {backup_file}")
            
            with open(backup_file, 'r', encoding='utf-8') as src:
                with open(self.memory_file, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            logger.info(f"Memory restored from {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    def clear_memory(self) -> bool:
        """Clear current memory file."""
        try:
            if os.path.exists(self.memory_file):
                os.remove(self.memory_file)
                logger.info("Memory cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
            return False
    
    def get_memory_stats(self) -> dict:
        """Get statistics about current memory file."""
        stats = {
            "file_exists": False,
            "file_size": 0,
            "last_modified": None,
            "is_valid_json": False
        }
        
        try:
            if os.path.exists(self.memory_file):
                stats["file_exists"] = True
                stats["file_size"] = os.path.getsize(self.memory_file)
                stats["last_modified"] = datetime.fromtimestamp(
                    os.path.getmtime(self.memory_file)
                ).isoformat()
                
                # Check if valid JSON
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                    stats["is_valid_json"] = True
        
        except json.JSONDecodeError:
            stats["is_valid_json"] = False
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
        
        return stats