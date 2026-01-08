"""
Natural language command parsing for the AI Proposal Deck Generator.
Processes user comments and determines intended actions with confidence scoring.
"""

import re
import logging
from typing import Dict, Any, Optional, List

from data_models import PROPOSAL_COMPONENTS

logger = logging.getLogger(__name__)

class FlexibleCommandParser:
    """Enhanced command parser that understands natural language with high flexibility."""
    
    def __init__(self):
        self.command_patterns = self._build_command_patterns()
        self.component_keywords = self._build_component_keywords()
    
    def _build_command_patterns(self) -> Dict[str, List[str]]:
        """Build regex patterns for different command types."""
        return {
            "generate_full": [
                r"generate.*(?:full|complete|entire|all).*(?:deck|slides|proposal)",
                r"create.*(?:full|complete|entire|all).*(?:deck|slides|proposal)",
                r"build.*(?:full|complete|entire|all).*(?:deck|slides|proposal)",
                r"make.*(?:full|complete|entire|all).*(?:deck|slides|proposal)",
                r"(?:full|complete|entire|all).*(?:deck|slides|proposal)",
                r"generate.*(?:everything|all)",
                r"create.*(?:everything|all)",
                r"start.*generation",
                r"build.*proposal"
            ],
            
            "generate_slide": [
                r"generate.*(?:slide|section|component)",
                r"create.*(?:slide|section|component)",
                r"build.*(?:slide|section|component)",
                r"make.*(?:slide|section|component)",
                r"add.*(?:slide|section|component)",
                r"write.*(?:slide|section|component)",
                r"develop.*(?:slide|section|component)"
            ],
            
            "edit_slide": [
                r"edit.*(?:slide|section|component)",
                r"modify.*(?:slide|section|component)",
                r"change.*(?:slide|section|component)",
                r"update.*(?:slide|section|component)",
                r"revise.*(?:slide|section|component)",
                r"improve.*(?:slide|section|component)",
                r"fix.*(?:slide|section|component)",
                r"enhance.*(?:slide|section|component)",
                r"refine.*(?:slide|section|component)",
                r"adjust.*(?:slide|section|component)"
            ],
            
            "solution": [
                r"(?:iterate|improve|refine|change|update).*solution",
                r"solution.*(?:iterate|improve|refine|change|update)",
                r"new.*solution",
                r"different.*solution",
                r"better.*solution",
                r"modify.*solution",
                r"enhance.*solution",
                r"revise.*solution"
            ],
            
            "finalize_solution": [
                r"finalize.*solution",
                r"(?:solution.*(?:fine|good|ok|ready|approved))",
                r"(?:accept|approve).*solution",
                r"solution.*(?:finalized|approved|accepted)",
                r"(?:yes|ok|good|ready).*solution",
                r"solution.*(?:looks|seems).*(?:good|fine|ok)"
            ],
            
            "show_info": [
                r"(?:show|display|list|view).*(?:summary|status|slides|components|progress)",
                r"what.*(?:slides|components|do.*have)",
                r"(?:summary|status|progress)",
                r"where.*(?:are|is).*we",
                r"current.*(?:state|status)",
                r"what.*(?:completed|done|finished)"
            ],
            
            "add_component": [
                r"add.*(?:slide|section|component)",
                r"include.*(?:slide|section|component)",  
                r"need.*(?:slide|section|component)",
                r"want.*(?:slide|section|component)",
                r"insert.*(?:slide|section|component)"
            ],
            
            "export": [
                r"(?:export|save|download).*(?:deck|file|proposal)",
                r"save.*(?:to.*file|deck|proposal)",
                r"create.*file",
                r"generate.*file",
                r"output.*file"
            ],
            
            "help": [
                r"help",
                r"what.*(?:can|should).*(?:i|do)",
                r"how.*(?:do|to)",
                r"instructions",
                r"guide",
                r"commands",
                r"\?"
            ]
        }
    
    def _build_component_keywords(self) -> Dict[str, List[str]]:
        """Build keyword mappings for component identification."""
        return {
            "cover": ["cover", "title", "front", "first", "opening"],
            "executive_summary": ["executive", "summary", "overview", "abstract", "brief"],
            "client_context": ["client", "context", "needs", "background", "situation"],
            "objectives": ["objectives", "understanding", "goals", "aims", "targets"],
            "solution_approach": ["solution", "approach", "methodology", "technical", "method", "strategy"],
            "value_proposition": ["value", "proposition", "benefits", "impact", "roi", "return"],
            "engagement_model": ["engagement", "model", "delivery", "team", "structure"],
            "timeline": ["timeline", "plan", "schedule", "milestones", "phases", "roadmap"],
            "pricing": ["pricing", "cost", "commercials", "payment", "budget", "investment", "price"],
            "risk_management": ["risk", "mitigation", "challenges", "issues", "problems"],
            "support": ["support", "next steps", "maintenance", "ongoing", "follow-up"],
            "about_company": ["about", "company", "us", "team", "experience", "credentials"],
            "closing": ["closing", "conclusion", "thank", "contact", "end", "final"]
        }
    
    def parse_command(self, comment: str) -> Dict[str, Any]:
        """Parse user comment with enhanced flexibility and confidence scoring."""
        original_comment = comment
        comment_lower = comment.lower().strip()
        
        command = {
            "action": "unknown",
            "component": None,
            "feedback": original_comment,
            "confidence": 0.0,
            "suggestions": []
        }
        
        # Check for explicit component mentions first
        detected_components = self._detect_components(comment_lower)
        if detected_components:
            command["component"] = detected_components[0]  # Use first match
            command["confidence"] += 0.3
        
        # Pattern matching with confidence scoring
        best_action = None
        best_confidence = 0.0
        
        for action, patterns in self.command_patterns.items():
            action_confidence = self._calculate_pattern_confidence(comment_lower, patterns)
            
            if action_confidence > best_confidence:
                best_confidence = action_confidence
                best_action = action
        
        if best_action and best_confidence > 0.5:
            command["action"] = best_action
            command["confidence"] = best_confidence
        
        # Special handling for ambiguous cases
        command = self._handle_special_cases(comment_lower, command)
        
        # Generate suggestions for low confidence commands
        if command["confidence"] < 0.6:
            command["suggestions"] = self._generate_suggestions(comment_lower, detected_components)
        
        logger.debug(f"Parsed command: {command['action']} (confidence: {command['confidence']:.2f})")
        
        return command
    
    def _calculate_pattern_confidence(self, comment: str, patterns: List[str]) -> float:
        """Calculate confidence score for pattern matching."""
        max_confidence = 0.0
        
        for pattern in patterns:
            if re.search(pattern, comment):
                # Base confidence for pattern match
                confidence = 0.7
                
                # Boost confidence for exact word matches
                pattern_words = re.findall(r'\w+', pattern.lower())
                comment_words = comment.split()
                
                exact_matches = sum(1 for word in pattern_words if word in comment_words)
                if exact_matches > 0:
                    confidence += 0.1 * exact_matches
                
                max_confidence = max(max_confidence, min(confidence, 1.0))
        
        return max_confidence
    
    def _detect_components(self, comment: str) -> List[str]:
        """Detect component references in comment."""
        detected = []
        
        for component, keywords in self.component_keywords.items():
            for keyword in keywords:
                if keyword in comment:
                    detected.append(component)
                    break
        
        return detected
    
    def _handle_special_cases(self, comment: str, command: Dict[str, Any]) -> Dict[str, Any]:
        """Handle special cases and edge conditions."""
        
        # If action is unknown but component is detected, assume edit/generate
        if command["action"] == "unknown" and command["component"]:
            if any(word in comment for word in ["edit", "modify", "change", "update", "improve"]):
                command["action"] = "edit_slide"
                command["confidence"] = 0.7
            else:
                command["action"] = "generate_slide"
                command["confidence"] = 0.6
        
        # Handle approval/confirmation words for solution
        approval_words = ["yes", "ok", "good", "fine", "approved", "correct", "right"]
        if any(word in comment for word in approval_words):
            if "solution" in comment:
                command["action"] = "finalize_solution"
                command["confidence"] = 0.8
        
        # Handle negations
        negation_words = ["no", "not", "don't", "can't", "won't", "never"]
        if any(word in comment for word in negation_words):
            command["confidence"] *= 0.7  # Reduce confidence for negations
        
        return command
    
    def _generate_suggestions(self, comment: str, components: List[str]) -> List[str]:
        """Generate helpful suggestions for unclear commands."""
        suggestions = []
        
        # If components detected but action unclear
        if components:
            comp_info = PROPOSAL_COMPONENTS.get(components[0], {})
            comp_title = comp_info.get("title", components[0])
            
            suggestions.extend([
                f"Generate {comp_title}",
                f"Edit {comp_title} with your requirements",
                f"Show {comp_title} status"
            ])
        
        # Generic suggestions
        if not suggestions:
            suggestions = [
                "Generate full deck",
                "Show current status", 
                "Edit a specific section",
                "Export proposal to file"
            ]
        
        return suggestions
    
    def extract_solution_from_comment(self, comment: str) -> Optional[str]:
        """Extract new solution text from user comment."""
        # Look for explicit solution markers
        solution_markers = ["solution:", "new solution:", "solution is:", "approach:"]
        
        for marker in solution_markers:
            if marker in comment.lower():
                parts = comment.lower().split(marker, 1)
                if len(parts) > 1:
                    return parts[1].strip()
        
        # If comment is long enough, treat whole comment as solution
        if len(comment) > 50 and not any(word in comment.lower() 
                                        for word in ["edit", "modify", "change", "show", "generate"]):
            return comment.strip()
        
        return None
    
    def is_approval_comment(self, comment: str) -> bool:
        """Check if comment indicates approval/confirmation."""
        approval_patterns = [
            r"^(?:yes|ok|good|fine|approved|correct|right)$",
            r"looks?\s+(?:good|fine|ok)",
            r"(?:that|this|it).*(?:good|fine|ok|right)",
            r"approve.*(?:solution|this|it)",
            r"finalize.*(?:solution|this|it)"
        ]
        
        comment_lower = comment.lower().strip()
        
        return any(re.search(pattern, comment_lower) for pattern in approval_patterns)
    
    def get_command_help(self) -> str:
        """Get help text explaining available commands."""
        return """
🆘 **Natural Language Commands**

**Generation:**
• "Generate the full deck"
• "Create executive summary"
• "Build pricing section"
• "Make cover slide"

**Editing:**
• "Edit pricing to include monthly payments"
• "Modify executive summary with more ROI details"
• "Update solution approach with cloud architecture"
• "Improve value proposition section"

**Solution Management:**
• "New solution: AI-powered analytics platform"
• "Iterate on solution with machine learning"
• "Yes, finalize this solution"

**Information:**
• "Show current status"
• "What do we have so far?"
• "Display progress summary"

**Components:**
• "Add risk management section"
• "Include about company slide"
• "Need timeline component"

**Export:**
• "Export the proposal"
• "Save to file"
• "Create final document"

Just speak naturally - I understand flexible phrasing!
"""