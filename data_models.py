"""
Data models and structures for the AI Proposal Deck Generator.
Defines core data classes and proposal components.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

# Proposal components configuration
PROPOSAL_COMPONENTS = {
    "cover": {
        "title": "Cover Slide",
        "description": "Client name, project title, company branding, proposal date",
        "importance": "essential"
    },
    "executive_summary": {
        "title": "Executive Summary", 
        "description": "Problem statement, opportunity, unique position, proposed outcomes",
        "importance": "essential"
    },
    "client_context": {
        "title": "Client Context & Needs",
        "description": "Client industry background, current challenges, business impact",
        "importance": "important"
    },
    "objectives": {
        "title": "Our Understanding of the Objectives",
        "description": "Restatement of client objectives, success metrics, requirements",
        "importance": "important"
    },
    "solution_approach": {
        "title": "Solution Approach",
        "description": "Detailed solution methodology, technology stack, implementation phases",
        "importance": "essential"
    },
    "value_proposition": {
        "title": "Value Proposition & Business Impact",
        "description": "Quantified benefits, cost savings, ROI, efficiency improvements",
        "importance": "essential"
    },
    "engagement_model": {
        "title": "Engagement Model",
        "description": "Service delivery model, team structure, communication protocols",
        "importance": "important"
    },
    "timeline": {
        "title": "Project Plan & Timeline",
        "description": "Project phases, milestones, timeline, resource allocation",
        "importance": "important"
    },
    "pricing": {
        "title": "Commercials / Pricing",
        "description": "Pricing model, cost breakdown, payment terms, ROI justification",
        "importance": "essential"
    },
    "risk_management": {
        "title": "Risk Management & Mitigation", 
        "description": "Risk identification, mitigation strategies, contingency plans",
        "importance": "optional"
    },
    "support": {
        "title": "Support & Next Steps",
        "description": "Post-implementation support, maintenance, next steps",
        "importance": "important"
    },
    "about_company": {
        "title": "About Company",
        "description": "Company overview, core competencies, relevant experience",
        "importance": "important"
    },
    "closing": {
        "title": "Closing Slide",
        "description": "Thank you, contact information, call to action",
        "importance": "essential"
    }
}

@dataclass
class SlideVersion:
    """Track slide versions for iteration history."""
    version: int
    content: str
    timestamp: str
    user_feedback: str = ""

@dataclass
class Slide:
    """Slide structure with versioning support."""
    component_key: str
    title: str
    content: str = ""
    versions: List[SlideVersion] = field(default_factory=list)
    
    def add_version(self, content: str, feedback: str = ""):
        """Add new version with timestamp."""
        version_num = len(self.versions) + 1
        timestamp = datetime.now().isoformat()
        self.versions.append(SlideVersion(version_num, content, timestamp, feedback))
        self.content = content
    
    def get_word_count(self) -> int:
        """Get word count of current content."""
        return len(self.content.split()) if self.content else 0
    
    def get_latest_version(self) -> Optional[SlideVersion]:
        """Get the latest version."""
        return self.versions[-1] if self.versions else None

@dataclass 
class SolutionIteration:
    """Track solution iterations with rationale."""
    iteration: int
    solution: str
    rationale: str
    timestamp: str

@dataclass
class ProposalMemory:
    """Main memory structure for proposal data."""
    client_name: str
    problem_statement: str
    current_solution: str
    solution_finalized: bool = False
    project_title: str = ""
    company_name: str = "Your Company"
    selected_components: List[str] = field(default_factory=list)
    slides: Dict[str, Slide] = field(default_factory=dict)
    solution_iterations: List[SolutionIteration] = field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def get_completion_rate(self) -> float:
        """Get proposal completion rate."""
        if not self.selected_components:
            return 0.0
        
        completed = sum(1 for comp in self.selected_components 
                       if comp in self.slides and self.slides[comp].content)
        return (completed / len(self.selected_components)) * 100
    
    def get_total_word_count(self) -> int:
        """Get total word count across all slides."""
        return sum(slide.get_word_count() for slide in self.slides.values())
    
    def get_essential_components_missing(self) -> List[str]:
        """Get list of missing essential components."""
        essential = [k for k, v in PROPOSAL_COMPONENTS.items() 
                    if v["importance"] == "essential"]
        
        return [comp for comp in essential 
                if comp not in self.slides or not self.slides[comp].content]

def get_default_essential_components() -> List[str]:
    """Get list of default essential components."""
    return [k for k, v in PROPOSAL_COMPONENTS.items() 
            if v["importance"] == "essential"]

def get_component_info(component_key: str) -> Optional[Dict[str, str]]:
    """Get component information by key."""
    return PROPOSAL_COMPONENTS.get(component_key)

def is_valid_component(component_key: str) -> bool:
    """Check if component key is valid."""
    return component_key in PROPOSAL_COMPONENTS