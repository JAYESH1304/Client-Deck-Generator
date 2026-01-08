"""
Output and file management for the AI Proposal Deck Generator.
Handles session logging, change tracking, and file exports.
"""

import os
import logging
from datetime import datetime
from typing import Optional

from config import config_manager

logger = logging.getLogger(__name__)

class OutputManager:
    """Manages all file output operations and logging."""
    
    def __init__(self, client_name: str, session_id: Optional[str] = None):
        self.client_name = client_name
        self.session_id = session_id or datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Clean client name for filename
        clean_client_name = self._clean_filename(client_name)
        
        # Set up file paths
        config = config_manager.get_config()
        self.output_dir = config.output_dir
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Define file paths
        self.session_file = os.path.join(
            self.output_dir, 
            f"{clean_client_name}_session_{self.session_id}.txt"
        )
        
        self.changes_file = os.path.join(
            self.output_dir,
            f"{clean_client_name}_changes_{self.session_id}.txt"
        )
        
        # Initialize session file
        self._initialize_session_file()
    
    def _clean_filename(self, name: str) -> str:
        """Clean filename by removing invalid characters."""
        invalid_chars = '<>:"/\\|?*'
        clean_name = ''.join(c if c not in invalid_chars else '_' for c in name)
        return clean_name.strip()
    
    def _initialize_session_file(self):
        """Initialize the session file with header information."""
        header = f"""{'='*60}
AI PROPOSAL DECK GENERATOR - SESSION LOG
{'='*60}
Client: {self.client_name}
Session ID: {self.session_id}
Started: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
{'='*60}

"""
        self.write_to_session(header, append=False)
    
    def write_to_session(self, content: str, append: bool = True):
        """Write content to session log file."""
        try:
            mode = 'a' if append else 'w'
            with open(self.session_file, mode, encoding='utf-8') as f:
                f.write(content)
                if not content.endswith('\n'):
                    f.write('\n')
        except Exception as e:
            logger.error(f"Failed to write to session file: {e}")
    
    def log_user_input(self, user_input: str):
        """Log user input to session file."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        entry = f"[{timestamp}] USER: {user_input}\n"
        self.write_to_session(entry)
    
    def log_agent_response(self, response: str):
        """Log agent response to session file."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        entry = f"[{timestamp}] AGENT: {response}\n\n"
        self.write_to_session(entry)
    
    def log_system_event(self, event: str):
        """Log system events to session file."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        entry = f"[{timestamp}] SYSTEM: {event}\n"
        self.write_to_session(entry)
    
    def log_change(self, action: str, component: str = "", before: str = "", after: str = "") -> str:
        """Log content changes with before/after comparison."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        change_log = f"\n{'='*60}\n"
        change_log += f"CHANGE LOG - {timestamp}\n"
        change_log += f"Action: {action}\n"
        
        if component:
            change_log += f"Component: {component}\n"
        
        change_log += f"{'='*60}\n"
        
        if before:
            word_count_before = len(before.split())
            change_log += f"\n--- BEFORE ({word_count_before} words) ---\n"
            change_log += before + "\n"
        
        if after:
            word_count_after = len(after.split())
            change_log += f"\n--- AFTER ({word_count_after} words) ---\n"
            change_log += after + "\n"
        
        if before and after:
            word_diff = len(after.split()) - len(before.split())
            change_log += f"\n--- SUMMARY ---\n"
            change_log += f"Word count change: {word_diff:+d} words\n"
        
        change_log += f"\n{'='*60}\n"
        
        # Write to both session and changes file
        self.write_to_session(change_log)
        self.write_to_changes(change_log)
        
        return change_log
    
    def write_to_changes(self, content: str):
        """Write content to changes tracking file."""
        try:
            with open(self.changes_file, 'a', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            logger.error(f"Failed to write to changes file: {e}")
    
    def export_proposal(self, content: str, filename: Optional[str] = None) -> str:
        """Export complete proposal to file."""
        if not filename:
            clean_client = self._clean_filename(self.client_name)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            filename = f"{clean_client}_proposal_{timestamp}.txt"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log_system_event(f"Proposal exported to: {filepath}")
            return filepath
            
        except Exception as e:
            error_msg = f"Export failed: {e}"
            logger.error(error_msg)
            self.log_system_event(error_msg)
            raise
    
    def create_summary_report(self, proposal_memory) -> str:
        """Create a summary report of the session."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
SESSION SUMMARY REPORT
Generated: {timestamp}

CLIENT INFORMATION:
- Client Name: {proposal_memory.client_name}
- Company: {proposal_memory.company_name}
- Project Title: {proposal_memory.project_title}

PROPOSAL STATUS:
- Solution Finalized: {'Yes' if proposal_memory.solution_finalized else 'No'}
- Selected Components: {len(proposal_memory.selected_components)}
- Completed Slides: {sum(1 for slide in proposal_memory.slides.values() if slide.content)}
- Completion Rate: {proposal_memory.get_completion_rate():.1f}%
- Total Words: {proposal_memory.get_total_word_count()}

SOLUTION ITERATIONS: {len(proposal_memory.solution_iterations)}
"""
        
        if proposal_memory.solution_iterations:
            report += "\nSOLUTION HISTORY:\n"
            for iteration in proposal_memory.solution_iterations:
                report += f"- v{iteration.iteration}: {iteration.solution[:80]}...\n"
        
        report += f"\nCOMPONENT STATUS:\n"
        for component in proposal_memory.selected_components:
            slide = proposal_memory.slides.get(component)
            if slide:
                status = "✅ Complete" if slide.content else "⏳ Pending"
                words = slide.get_word_count()
                report += f"- {slide.title}: {status} ({words} words)\n"
        
        missing = proposal_memory.get_essential_components_missing()
        if missing:
            report += f"\nMISSING ESSENTIAL COMPONENTS:\n"
            for comp in missing:
                report += f"- {comp}\n"
        
        report += f"\nFILES GENERATED:\n"
        report += f"- Session Log: {self.session_file}\n"
        report += f"- Changes Log: {self.changes_file}\n"
        
        # Save summary report
        summary_file = os.path.join(
            self.output_dir,
            f"{self._clean_filename(self.client_name)}_summary_{self.session_id}.txt"
        )
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            report += f"- Summary Report: {summary_file}\n"
        except Exception as e:
            logger.error(f"Failed to save summary report: {e}")
        
        return report
    
    def get_session_stats(self) -> dict:
        """Get statistics about current session files."""
        stats = {
            'session_file': self.session_file,
            'changes_file': self.changes_file,
            'session_file_size': 0,
            'changes_file_size': 0,
            'session_exists': False,
            'changes_exists': False
        }
        
        try:
            if os.path.exists(self.session_file):
                stats['session_exists'] = True
                stats['session_file_size'] = os.path.getsize(self.session_file)
            
            if os.path.exists(self.changes_file):
                stats['changes_exists'] = True  
                stats['changes_file_size'] = os.path.getsize(self.changes_file)
        
        except Exception as e:
            logger.error(f"Error getting session stats: {e}")
        
        return stats
    
    def cleanup_old_files(self, days_old: int = 30):
        """Clean up old session files."""
        try:
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            
            cleaned_count = 0
            for filename in os.listdir(self.output_dir):
                filepath = os.path.join(self.output_dir, filename)
                
                if os.path.isfile(filepath) and filename.endswith('.txt'):
                    file_time = os.path.getmtime(filepath)
                    
                    if file_time < cutoff_time:
                        os.remove(filepath)
                        cleaned_count += 1
            
            self.log_system_event(f"Cleaned up {cleaned_count} old files")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 0