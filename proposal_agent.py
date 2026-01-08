"""
Core proposal agent that handles solution finalization and slide generation.
Main business logic for the AI Proposal Deck Generator.
"""

import logging
from typing import List, Tuple, Optional, Dict
from datetime import datetime

from data_models import (
    ProposalMemory, Slide, SolutionIteration, PROPOSAL_COMPONENTS, 
    get_default_essential_components, is_valid_component
)
from memory_manager import MemoryManager
from ai_generator import AIGenerator
from config import config_manager

logger = logging.getLogger(__name__)

class ProposalAgent:
    """Core AI Proposal Agent with solution finalization and slide generation."""
    
    def __init__(self, client_name: str, problem_statement: str, tentative_solution: str, 
                 company_name: str = "Your Company", api_key: Optional[str] = None):
        
        self.memory_manager = MemoryManager()
        self.ai_generator = AIGenerator(api_key=api_key)
        
        # Load or create memory
        self.memory = self._initialize_memory(
            client_name, problem_statement, tentative_solution, company_name
        )
        
        logger.info(f"Proposal agent initialized for {client_name}")
    
    def _initialize_memory(self, client_name: str, problem_statement: str, 
                          tentative_solution: str, company_name: str) -> ProposalMemory:
        """Initialize or load existing memory."""
        
        # Try to load existing memory
        existing_memory = self.memory_manager.load_memory()
        
        if (existing_memory and 
            existing_memory.client_name == client_name and 
            existing_memory.problem_statement == problem_statement):
            
            # Update existing memory with new solution
            existing_memory.current_solution = tentative_solution
            existing_memory.company_name = company_name
            logger.info("Loaded and updated existing proposal memory")
            return existing_memory
        else:
            # Create new memory with essential components
            essential_components = get_default_essential_components()
            
            memory = ProposalMemory(
                client_name=client_name,
                problem_statement=problem_statement,
                current_solution=tentative_solution,
                company_name=company_name,
                selected_components=essential_components
            )
            
            # Initialize slides for essential components
            for component in essential_components:
                memory.slides[component] = Slide(
                    component_key=component,
                    title=PROPOSAL_COMPONENTS[component]["title"]
                )
            
            # Generate project title
            memory.project_title = self._generate_project_title(client_name, tentative_solution)
            
            logger.info("Created new proposal memory")
            return memory
    
    def _generate_project_title(self, client_name: str, solution: str) -> str:
        """Generate project title based on client and solution."""
        solution_words = solution.split()[:4]
        title = f"{client_name} - {' '.join(solution_words)} Initiative"
        return title.replace('  ', ' ')
    
    def save_memory(self) -> bool:
        """Save current memory state."""
        return self.memory_manager.save_memory(self.memory)
    
    def suggest_solution_improvements(self) -> str:
        """AI suggests improvements to current solution."""
        prompt = f"""
        You are a business consultant analyzing a proposed solution. 
        
        CLIENT: {self.memory.client_name}
        PROBLEM: {self.memory.problem_statement}
        CURRENT SOLUTION: {self.memory.current_solution}
        
        Analyze this solution and provide 3-5 specific, actionable improvement suggestions that would:
        1. Address potential gaps or weaknesses
        2. Add significant business value
        3. Make the solution more comprehensive or effective
        4. Consider implementation challenges
        5. Enhance competitive advantage
        
        Format your response as a numbered list with brief explanations for each suggestion.
        Focus on practical enhancements that a business consultant would recommend.
        """
        
        return self.ai_generator.generate_content(prompt)
    
    def iterate_solution(self, new_solution: str, rationale: str = "") -> str:
        """Update solution with new iteration and rationale."""
        iteration_num = len(self.memory.solution_iterations) + 1
        
        # Add iteration to history
        self.memory.solution_iterations.append(SolutionIteration(
            iteration=iteration_num,
            solution=new_solution,
            rationale=rationale or f"User iteration #{iteration_num}",
            timestamp=datetime.now().isoformat()
        ))
        
        # Update current solution
        old_solution = self.memory.current_solution
        self.memory.current_solution = new_solution
        
        # Update project title
        self.memory.project_title = self._generate_project_title(
            self.memory.client_name, new_solution
        )
        
        # Save changes
        self.save_memory()
        
        logger.info(f"Solution iteration #{iteration_num}: {new_solution[:100]}...")
        return old_solution
    
    def finalize_solution(self, final_solution: Optional[str] = None) -> bool:
        """Finalize the solution after user approval."""
        
        if final_solution and final_solution != self.memory.current_solution:
            # Update solution if provided
            self.iterate_solution(final_solution, "Final solution approved by user")
        
        self.memory.solution_finalized = True
        self.save_memory()
        
        logger.info("Solution finalized successfully")
        return True
    
    def build_slide_prompt(self, component: str, user_feedback: str = "") -> str:
        """Build comprehensive prompt for slide generation."""
        
        if not is_valid_component(component):
            raise ValueError(f"Invalid component: {component}")
        
        component_info = PROPOSAL_COMPONENTS[component]
        
        base_context = f"""
        You are creating professional slide content for a business proposal presentation.
        
        CLIENT INFORMATION:
        - Client Name: {self.memory.client_name}
        - Problem Statement: {self.memory.problem_statement}
        - Approved Solution: {self.memory.current_solution}
        - Project Title: {self.memory.project_title}
        - Your Company: {self.memory.company_name}
        
        SLIDE DETAILS:
        - Slide Title: {component_info['title']}
        - Purpose: {component_info['description']}
        - Importance Level: {component_info['importance']}
        """
        
        if user_feedback:
            base_context += f"\n\nSPECIFIC USER REQUIREMENTS:\n{user_feedback}"
        
        # Add component-specific instructions
        specific_instructions = self._get_component_specific_instructions(component)
        
        prompt = f"""
        {base_context}
        
        {specific_instructions}
        
        FORMATTING REQUIREMENTS:
        - Use professional, client-ready language appropriate for executive presentation
        - Structure with clear headings and bullet points for readability
        - Keep content concise but comprehensive (aim for 150-300 words)
        - Include specific, quantifiable details relevant to the client's situation
        - Make it persuasive and action-oriented
        - Use active voice and strong value propositions
        
        Generate ONLY the slide content ready for presentation. 
        Do not include meta-commentary, explanations, or placeholders.
        """
        
        return prompt
    
    def _get_component_specific_instructions(self, component: str) -> str:
        """Get component-specific generation instructions."""
        
        instructions = {
            "cover": f"""
            Create a professional cover slide with these elements:
            - Client name prominently displayed: {self.memory.client_name}
            - Project title: {self.memory.project_title}
            - Your company name: {self.memory.company_name}
            - Current date: {datetime.now().strftime('%B %d, %Y')}
            - Version: 1.0
            - Brief tagline about the proposal's value
            """,
            
            "executive_summary": """
            Create a compelling executive summary that includes:
            - Clear problem statement with business impact
            - Your unique positioning and approach
            - High-level solution overview with key benefits
            - Expected outcomes with quantified results
            - Investment overview and ROI justification
            - Call to action for next steps
            """,
            
            "value_proposition": """
            Focus on quantified business value:
            - Specific cost savings with dollar amounts or percentages
            - Efficiency improvements with measurable metrics
            - Revenue impact and growth opportunities
            - Competitive advantages gained
            - ROI calculations with timeframes
            - Risk reduction benefits
            """,
            
            "pricing": """
            Structure pricing professionally:
            - Clear pricing model explanation (fixed, T&M, milestone-based)
            - Detailed cost breakdown by phase or component
            - Payment terms and schedule
            - Assumptions and what's included/excluded
            - Value justification linking cost to benefits
            - Optional add-ons or variations
            """,
            
            "timeline": """
            Provide a realistic project timeline:
            - Project phases with clear objectives
            - Key milestones and deliverables
            - Duration estimates for each phase
            - Resource allocation and dependencies
            - Critical path identification
            - Go-live date and post-implementation activities
            """,
            
            "risk_management": """
            Address potential risks proactively:
            - Technical and implementation risks
            - Business and operational risks
            - Timeline and resource risks
            - Mitigation strategies for each risk
            - Contingency plans and alternatives
            - Risk monitoring and escalation process
            """
        }
        
        return instructions.get(component, 
            "Create comprehensive, professional content addressing all requirements for this section.")
    
    def generate_slide(self, component: str, user_feedback: str = "") -> Tuple[Slide, str]:
        """Generate content for a specific slide component."""
        
        if not is_valid_component(component):
            raise ValueError(f"Invalid component: {component}")
        
        if not self.memory.solution_finalized:
            raise ValueError("Solution must be finalized before generating slides")
        
        # Ensure component is in selected components
        if component not in self.memory.selected_components:
            self.add_component(component)
        
        # Get existing slide or create new one
        slide = self.memory.slides.get(component)
        if not slide:
            slide = Slide(
                component_key=component,
                title=PROPOSAL_COMPONENTS[component]["title"]
            )
            self.memory.slides[component] = slide
        
        # Store previous content for change tracking
        previous_content = slide.content
        
        # Build prompt and generate content
        prompt = self.build_slide_prompt(component, user_feedback)
        logger.debug(f"Generating slide: {slide.title}")
        
        new_content = self.ai_generator.generate_content(prompt)
        
        # Add version and update slide
        slide.add_version(new_content, user_feedback)
        self.memory.slides[component] = slide
        
        # Save changes
        self.save_memory()
        
        logger.info(f"Generated slide '{slide.title}' ({len(new_content)} characters)")
        return slide, previous_content
    
    def generate_proposal_deck(self) -> List[Slide]:
        """Generate complete proposal deck with all selected components."""
        
        if not self.memory.solution_finalized:
            raise ValueError("Solution must be finalized before generating deck")
        
        logger.info("Starting full deck generation")
        slides = []
        
        # Generate slides in logical order
        component_order = [
            "cover", "executive_summary", "client_context", "objectives",
            "solution_approach", "value_proposition", "engagement_model", 
            "timeline", "pricing", "risk_management", "support", 
            "about_company", "closing"
        ]
        
        # Filter to only selected components in proper order
        ordered_components = [comp for comp in component_order 
                            if comp in self.memory.selected_components]
        
        for component in ordered_components:
            try:
                slide, _ = self.generate_slide(component)
                slides.append(slide)
                
                # Brief pause to avoid rate limiting
                import time
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Failed to generate slide {component}: {e}")
                # Add placeholder slide
                slide = self.memory.slides.get(component)
                if slide:
                    slides.append(slide)
        
        logger.info(f"Full deck generation completed: {len(slides)} slides")
        return slides
    
    def add_component(self, component: str) -> bool:
        """Add a new component to the proposal."""
        
        if not is_valid_component(component):
            logger.warning(f"Invalid component: {component}")
            return False
        
        if component in self.memory.selected_components:
            logger.info(f"Component {component} already selected")
            return True
        
        # Add to selected components
        self.memory.selected_components.append(component)
        
        # Create slide if not exists
        if component not in self.memory.slides:
            self.memory.slides[component] = Slide(
                component_key=component,
                title=PROPOSAL_COMPONENTS[component]["title"]
            )
        
        self.save_memory()
        logger.info(f"Added component: {PROPOSAL_COMPONENTS[component]['title']}")
        return True
    
    def remove_component(self, component: str) -> bool:
        """Remove a component from the proposal."""
        
        if component not in self.memory.selected_components:
            return False
        
        # Check if it's essential
        if PROPOSAL_COMPONENTS.get(component, {}).get("importance") == "essential":
            logger.warning(f"Cannot remove essential component: {component}")
            return False
        
        self.memory.selected_components.remove(component)
        self.save_memory()
        logger.info(f"Removed component: {component}")
        return True
    
    def get_available_components(self) -> Dict[str, Dict]:
        """Get components that can be added to the proposal."""
        return {k: v for k, v in PROPOSAL_COMPONENTS.items() 
                if k not in self.memory.selected_components}
    
    def get_proposal_status(self) -> Dict:
        """Get comprehensive status of the proposal."""
        completed_slides = sum(1 for slide in self.memory.slides.values() if slide.content)
        
        return {
            "client_name": self.memory.client_name,
            "project_title": self.memory.project_title,
            "solution_finalized": self.memory.solution_finalized,
            "current_solution": self.memory.current_solution,
            "selected_components": len(self.memory.selected_components),
            "completed_slides": completed_slides,
            "completion_rate": self.memory.get_completion_rate(),
            "total_words": self.memory.get_total_word_count(),
            "solution_iterations": len(self.memory.solution_iterations),
            "missing_essential": self.memory.get_essential_components_missing(),
            "last_updated": self.memory.last_updated
        }
    
    def export_deck_content(self) -> str:
        """Export complete deck as formatted text."""
        
        output = []
        output.append(f"PROPOSAL DECK FOR {self.memory.client_name.upper()}")
        output.append(f"Project: {self.memory.project_title}")
        output.append(f"Prepared by: {self.memory.company_name}")
        output.append(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        output.append("=" * 70)
        output.append("")
        
        # Add solution summary
        output.append("SOLUTION SUMMARY")
        output.append("-" * 20)
        output.append(f"Problem: {self.memory.problem_statement}")
        output.append(f"Solution: {self.memory.current_solution}")
        output.append("")
        
        # Add slides content
        component_order = [
            "cover", "executive_summary", "client_context", "objectives",
            "solution_approach", "value_proposition", "engagement_model", 
            "timeline", "pricing", "risk_management", "support", 
            "about_company", "closing"
        ]
        
        # Filter to selected components in order
        ordered_components = [comp for comp in component_order 
                            if comp in self.memory.selected_components]
        
        for i, component in enumerate(ordered_components, 1):
            slide = self.memory.slides.get(component)
            if slide:
                output.append(f"{i}. {slide.title}")
                output.append("-" * 50)
                
                if slide.content:
                    output.append(slide.content)
                else:
                    output.append("[Content not yet generated]")
                
                output.append("")
                output.append("")
        
        # Add generation statistics
        output.append("GENERATION STATISTICS")
        output.append("-" * 25)
        output.append(f"Total Components: {len(self.memory.selected_components)}")
        output.append(f"Generated Slides: {sum(1 for s in self.memory.slides.values() if s.content)}")
        output.append(f"Total Words: {self.memory.get_total_word_count()}")
        output.append(f"Solution Iterations: {len(self.memory.solution_iterations)}")
        output.append(f"Completion Rate: {self.memory.get_completion_rate():.1f}%")
        
        return "\n".join(output)
    
    def validate_proposal(self) -> Dict[str, any]:
        """Validate proposal completeness and quality."""
        
        validation = {
            "is_complete": True,
            "issues": [],
            "warnings": [],
            "recommendations": [],
            "quality_score": 0.0
        }
        
        # Check essential components
        missing_essential = self.memory.get_essential_components_missing()
        if missing_essential:
            validation["is_complete"] = False
            validation["issues"].append(f"Missing essential components: {', '.join(missing_essential)}")
        
        # Check slide content quality
        empty_slides = []
        short_slides = []
        
        for component, slide in self.memory.slides.items():
            if not slide.content:
                empty_slides.append(component)
            elif len(slide.content.split()) < 50:
                short_slides.append(component)
        
        if empty_slides:
            validation["issues"].append(f"Empty slides: {', '.join(empty_slides)}")
        
        if short_slides:
            validation["warnings"].append(f"Short slides (< 50 words): {', '.join(short_slides)}")
        
        # Calculate quality score
        total_components = len(self.memory.selected_components)
        completed_components = sum(1 for slide in self.memory.slides.values() if slide.content)
        
        if total_components > 0:
            completion_score = completed_components / total_components
            
            # Word count score
            avg_words = self.memory.get_total_word_count() / max(completed_components, 1)
            word_score = min(avg_words / 150, 1.0)  # Ideal ~150 words per slide
            
            validation["quality_score"] = (completion_score * 0.7 + word_score * 0.3) * 100
        
        # Generate recommendations
        if validation["quality_score"] < 70:
            validation["recommendations"].append("Complete missing sections to improve quality score")
        
        if short_slides:
            validation["recommendations"].append("Expand content for short slides with more details")
        
        return validation