"""
Main conversational interface for the AI Proposal Deck Generator.
Handles user interactions, solution finalization, and command processing.
"""

import logging
from typing import Optional
from datetime import datetime

from proposal_agent import ProposalAgent
from command_parser import FlexibleCommandParser
from output_manager import OutputManager
from data_models import PROPOSAL_COMPONENTS

logger = logging.getLogger(__name__)

class ConversationalAgent:
    """Enhanced conversational interface with solution finalization workflow."""
    
    def __init__(self, client_name: str, problem_statement: str, tentative_solution: str, 
                 company_name: str = "Your Company", api_key: Optional[str] = None):
        
        # Initialize core components
        self.agent = ProposalAgent(client_name, problem_statement, tentative_solution, company_name, api_key)
        self.parser = FlexibleCommandParser()
        self.output_manager = OutputManager(client_name)
        self.session_active = True
        
        # Initialize session
        self._initialize_session()
        
        # Handle solution finalization if needed
        if not self.agent.memory.solution_finalized:
            self._handle_solution_finalization()
        else:
            self._show_ready_message()
    
    def run_conversation(self):
        """Main conversation loop for interactive proposal generation."""
        if not self.session_active:
            return
            
        print("\n🎯 Starting interactive proposal generation...")
        print("Type 'help' for available commands, 'exit' to finish.\n")
        
        try:
            while self.session_active:
                try:
                    # Get user input
                    user_input = input("💬 You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle exit commands
                    if user_input.lower() in ['exit', 'quit', 'done', 'finish']:
                        print("\n✅ Session completed!")
                        break
                    
                    # Process the comment/command
                    response = self.process_comment(user_input)
                    print(f"\n🤖 AI Agent: {response}\n")
                    
                    # Check if we should auto-exit after certain commands
                    if "exported successfully" in response.lower():
                        print("💡 Proposal complete! Type 'exit' to finish or continue editing.")
                    
                except KeyboardInterrupt:
                    print("\n\n👋 Session interrupted by user.")
                    break
                    
                except EOFError:
                    print("\n\n👋 Input stream ended. Finishing session.")
                    break
                    
                except Exception as e:
                    logger.error(f"Error in conversation loop: {e}")
                    print(f"❌ Unexpected error: {e}")
                    print("💡 Try again or type 'exit' to finish.")
                    
        except Exception as e:
            logger.error(f"Fatal error in run_conversation: {e}")
            print(f"❌ Fatal error occurred: {e}")
            
        finally:
            self._finalize_session()
    
    def _finalize_session(self):
        """Clean up and finalize the session."""
        try:
            # Create final session summary
            summary = self.get_session_summary()
            self.output_manager.write_to_session(f"\n{summary}")
            self.output_manager.log_system_event("Session ended")
            
            print(f"📁 Session saved to: {self.output_manager.session_file}")
            
            # Show final stats
            stats = self.output_manager.get_session_stats()
            if stats.get('changes_exists'):
                print(f"📋 Changes logged to: {stats['changes_file']}")
                
        except Exception as e:
            logger.error(f"Error finalizing session: {e}")
    
    def get_session_summary(self) -> str:
        """Generate a session summary."""
        try:
            status = self.agent.get_proposal_status()
            
            summary = f"""
╔══════════════════════════════════════════════════════════════════╗
║                      SESSION SUMMARY                             ║
╚══════════════════════════════════════════════════════════════════╝

📋 CLIENT: {status['client_name']}
🏢 COMPANY: {self.agent.memory.company_name}
📅 SESSION: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

🎯 PROJECT STATUS:
   • Title: {status['project_title']}
   • Solution: {'✅ Finalized' if status['solution_finalized'] else '⏳ Pending'}
   • Progress: {status['completion_rate']:.1f}% complete
   • Content: {status['total_words']} words across {status['completed_slides']} slides

📊 COMPONENTS GENERATED:
"""
            
            for i, component in enumerate(self.agent.memory.selected_components, 1):
                slide = self.agent.memory.slides.get(component)
                if slide and slide.content:
                    word_count = slide.get_word_count()
                    summary += f"   {i}. ✅ {slide.title} ({word_count} words)\n"
                else:
                    summary += f"   {i}. ⏳ {PROPOSAL_COMPONENTS.get(component, {}).get('title', component)} (pending)\n"
            
            # Add available components
            available = self.agent.get_available_components()
            if available:
                summary += f"\n💡 AVAILABLE TO ADD: {len(available)} components\n"
            
            # Add solution iterations info
            if status.get('solution_iterations', 0) > 0:
                summary += f"\n🔄 SOLUTION ITERATIONS: {status['solution_iterations']}\n"
            
            summary += f"\n🕒 SESSION DURATION: Started at session initialization"
            summary += f"\n📁 OUTPUT FILES: Session log and proposal content saved"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error creating session summary: {e}")
            return f"❌ Error creating session summary: {e}"
    
    def _initialize_session(self):
        """Initialize the conversational session."""
        welcome_msg = f"""🚀 AI Proposal Agent Session Initialized
        
Client: {self.agent.memory.client_name}
Project: {self.agent.memory.project_title}
Company: {self.agent.memory.company_name}
Session: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

Current Solution: {self.agent.memory.current_solution}
Solution Status: {'✅ Finalized' if self.agent.memory.solution_finalized else '⏳ Needs Review'}
"""
        
        print(welcome_msg)
        self.output_manager.write_to_session(welcome_msg, append=False)
        self.output_manager.log_system_event("Session initialized")
        
        print(f"💾 Session output: {self.output_manager.session_file}")
    
    def _handle_solution_finalization(self):
        """Handle the solution finalization workflow."""
        print("\n" + "="*70)
        print("🎯 SOLUTION FINALIZATION REQUIRED")
        print("="*70)
        print("\nBefore generating your proposal deck, let's finalize your solution approach.")
        print(f"\nCurrent solution: {self.agent.memory.current_solution}")
        
        # Get AI suggestions for improvements
        print("\n🤖 Analyzing your solution and generating improvement suggestions...")
        self.output_manager.log_system_event("Starting solution analysis")
        
        try:
            suggestions = self.agent.suggest_solution_improvements()
            
            solution_analysis = f"""
SOLUTION ANALYSIS & IMPROVEMENT SUGGESTIONS:
{suggestions}
"""
            print(solution_analysis)
            self.output_manager.write_to_session(solution_analysis)
            
        except Exception as e:
            logger.error(f"Failed to generate solution suggestions: {e}")
            print("⚠️  Could not generate AI suggestions. Proceeding with current solution.")
        
        print("\n" + "-"*70)
        print("Please review your solution. You can:")
        print("• Type 'yes', 'approved', or 'looks good' to finalize current solution")
        print("• Type 'new solution: [your improved solution]' to update")
        print("• Simply describe your improved solution")
        print("• Type 'help' for more guidance")
        print("-"*70)
        
        # Solution finalization loop
        while not self.agent.memory.solution_finalized:
            try:
                user_input = input("\n💭 Your decision: ").strip()
                self.output_manager.log_user_input(user_input)
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit']:
                    self.session_active = False
                    break
                
                response = self._process_solution_input(user_input)
                print(f"\n{response}")
                self.output_manager.log_agent_response(response)
                
                if self.agent.memory.solution_finalized:
                    break
                    
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted.")
                self.session_active = False
                break
    
    def _process_solution_input(self, user_input: str) -> str:
        """Process user input during solution finalization."""
        
        # Check for approval
        if self.parser.is_approval_comment(user_input):
            self.agent.finalize_solution()
            self.output_manager.log_system_event("Solution finalized by user approval")
            return "✅ Solution finalized! Ready to generate proposal deck."
        
        # Check for new solution
        new_solution = self.parser.extract_solution_from_comment(user_input)
        if new_solution:
            old_solution = self.agent.iterate_solution(new_solution, f"User input: {user_input}")
            self.agent.finalize_solution()
            
            # Log the change
            self.output_manager.log_change(
                "Solution Updated and Finalized",
                "Previous Solution",
                old_solution,
                new_solution
            )
            
            return f"✅ Solution updated and finalized!\n\nNew solution: {new_solution}"
        
        # Help request
        if 'help' in user_input.lower():
            return self._get_solution_help()
        
        # Unclear input
        return (
            "Please provide a clear decision:\n"
            "• 'yes' or 'approved' to finalize current solution\n"
            "• 'new solution: [your solution]' to update\n"
            "• Or simply describe your improved solution"
        )
    
    def _get_solution_help(self) -> str:
        """Get help for solution finalization."""
        return f"""
🆘 **Solution Finalization Help**

**To approve current solution:**
• "Yes" / "Approved" / "Looks good" / "OK"

**To update solution:**
• "New solution: AI-powered analytics with real-time dashboards"
• "Solution: Cloud-based automation platform with ML capabilities"  
• Or just describe your solution: "Comprehensive digital transformation using microservices architecture"

**Tips for a strong solution:**
• Be specific about technologies and approaches
• Include measurable outcomes or benefits
• Consider implementation methodology
• Address the client's core problem directly

**Current solution:** {self.agent.memory.current_solution}
"""
    
    def _show_ready_message(self):
        """Show ready message after solution finalization."""
        print("\n" + "="*70)
        print("🎉 READY TO GENERATE PROPOSAL DECK!")
        print("="*70)
        
        status = self.agent.get_proposal_status()
        
        print(f"✅ Solution: {self.agent.memory.current_solution}")
        print(f"📊 Selected components: {status['selected_components']}")
        print(f"📝 Completion: {status['completion_rate']:.1f}% ({status['completed_slides']} slides)")
        
        print("\n💬 Tell me what you'd like to do:")
        print("• 'Generate full deck' - Create complete proposal")
        print("• 'Generate executive summary' - Create specific section")  
        print("• 'Edit pricing to include monthly payments' - Modify section")
        print("• 'Add risk management section' - Add new component")
        print("• 'Show status' - View current progress")
        print("• 'Export proposal' - Save final document")
        print("-"*70)
    
    def process_comment(self, comment: str) -> str:
        """Process user comment and execute appropriate action."""
        if not comment.strip():
            return "Please provide a comment or instruction."
        
        # Log user input
        self.output_manager.log_user_input(comment)
        
        # Handle solution finalization if not done
        if not self.agent.memory.solution_finalized:
            return "Please finalize your solution first before generating slides."
        
        # Parse command
        command = self.parser.parse_command(comment)
        
        try:
            # Route to appropriate handler
            if command["action"] == "generate_full":
                response = self._generate_full_deck()
            
            elif command["action"] == "generate_slide":
                if command["component"]:
                    response = self._generate_slide(command["component"], command["feedback"])
                else:
                    response = "Please specify which component/section to generate."
            
            elif command["action"] == "edit_slide":
                if command["component"]:
                    response = self._edit_slide(command["component"], command["feedback"])
                else:
                    response = self._suggest_component_from_comment(comment)
            
            elif command["action"] == "add_component":
                response = self._add_component(command, comment)
            
            elif command["action"] == "show_info":
                response = self._show_status()
            
            elif command["action"] == "export":
                response = self._export_proposal()
            
            elif command["action"] == "help":
                response = self.parser.get_command_help()
            
            else:
                response = self._handle_flexible_command(comment, command)
            
            # Log response
            self.output_manager.log_agent_response(response)
            return response
                
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            error_msg = f"❌ Sorry, I encountered an error: {str(e)}"
            self.output_manager.log_agent_response(error_msg)
            return error_msg
    
    def _generate_full_deck(self) -> str:
        """Generate complete proposal deck."""
        try:
            self.output_manager.log_system_event("Starting full deck generation")
            slides = self.agent.generate_proposal_deck()
            
            result = [f"🎯 Complete proposal deck generated with {len(slides)} sections!\n"]
            
            for i, slide in enumerate(slides, 1):
                word_count = slide.get_word_count()
                result.append(f"✅ {i}. {slide.title} ({word_count} words)")
            
            # Save deck content to file
            deck_content = self.agent.export_deck_content()
            export_file = self.output_manager.export_proposal(deck_content)
            
            result.append(f"\n📄 Full deck saved to: {export_file}")
            
            # Log completion
            self.output_manager.log_system_event(f"Full deck generated: {len(slides)} slides")
            
            return "\n".join(result)
            
        except ValueError as e:
            return str(e)
        except Exception as e:
            return f"❌ Error generating deck: {str(e)}"
    
    def _generate_slide(self, component: str, feedback: str = "") -> str:
        """Generate specific slide component."""
        try:
            slide, previous_content = self.agent.generate_slide(component, feedback)
            
            # Log the change
            self.output_manager.log_change(
                f"Generated {slide.title}",
                component,
                previous_content or "[No previous content]",
                slide.content
            )
            
            word_count = slide.get_word_count()
            response = f"✅ Generated: {slide.title} ({word_count} words)\n\n{slide.content}"
            
            return response
            
        except ValueError as e:
            available = ', '.join(PROPOSAL_COMPONENTS.keys())
            return f"❌ Invalid component: {component}.\nAvailable: {available}"
        except Exception as e:
            return f"❌ Error generating slide: {str(e)}"
    
    def _edit_slide(self, component: str, feedback: str) -> str:
        """Edit specific slide with feedback and show before/after."""
        try:
            # Get previous content
            if component in self.agent.memory.slides:
                previous_content = self.agent.memory.slides[component].content
            else:
                previous_content = "[No previous content]"
            
            slide, _ = self.agent.generate_slide(component, feedback)
            
            # Log the change with before/after
            self.output_manager.log_change(
                f"Edited {slide.title}",
                component,
                previous_content,
                slide.content
            )
            
            word_count = slide.get_word_count()
            response = f"✅ Updated: {slide.title} ({word_count} words)\n\n"
            
            if previous_content and previous_content != "[No previous content]":
                prev_words = len(previous_content.split())
                word_diff = word_count - prev_words
                response += f"📈 Changes: {word_diff:+d} words from previous version\n\n"
            
            response += f"--- UPDATED CONTENT ---\n{slide.content}"
            
            return response
            
        except ValueError as e:
            return f"❌ Invalid component: {component}"
        except Exception as e:
            return f"❌ Error editing slide: {str(e)}"
    
    def _suggest_component_from_comment(self, comment: str) -> str:
        """Suggest component when user wants to edit but didn't specify which."""
        comment_lower = comment.lower()
        
        # Try to match based on content keywords
        suggestions = []
        for component, info in PROPOSAL_COMPONENTS.items():
            title_words = info["title"].lower().split()
            desc_words = info["description"].lower().split()
            
            if any(word in comment_lower for word in title_words + desc_words):
                suggestions.append((component, info["title"]))
        
        if suggestions:
            if len(suggestions) == 1:
                component, title = suggestions[0]
                return self._edit_slide(component, comment)
            else:
                response = f"🤔 I found multiple possible sections to edit:\n"
                for comp, title in suggestions:
                    response += f"• {title} - say 'edit {comp}'\n"
                return response
        
        # Show all available components
        response = "I'm not sure which section to edit. Current sections:\n"
        for component in self.agent.memory.selected_components:
            slide = self.agent.memory.slides[component]
            status = "✅" if slide.content else "⏳"
            word_count = slide.get_word_count()
            response += f"{status} {slide.title} ({word_count} words) - say 'edit {component}'\n"
        
        return response
    
    def _add_component(self, command: dict, comment: str) -> str:
        """Add new component to proposal."""
        # Try to extract component from comment
        for component, info in PROPOSAL_COMPONENTS.items():
            if any(word in comment.lower() for word in info["title"].lower().split()):
                if self.agent.add_component(component):
                    return f"✅ Added: {info['title']}\nSay 'generate {component}' to create content."
                else:
                    return f"❌ Could not add component: {component}"
        
        # Show available components
        available = self.agent.get_available_components()
        if available:
            response = "Available components to add:\n"
            for comp, info in available.items():
                response += f"• {info['title']} - say 'add {comp}'\n"
            return response
        else:
            return "All components are already included in your proposal."
    
    def _show_status(self) -> str:
        """Show current proposal status."""
        status = self.agent.get_proposal_status()
        
        response = [f"📊 PROPOSAL STATUS FOR {status['client_name']}"]
        response.append("="*50)
        response.append(f"Project: {status['project_title']}")
        response.append(f"Solution: {'✅ Finalized' if status['solution_finalized'] else '⏳ Pending'}")
        response.append(f"Progress: {status['completion_rate']:.1f}% complete")
        response.append(f"Content: {status['total_words']} words across {status['completed_slides']} slides")
        response.append("")
        
        # Show component status
        response.append("COMPONENT STATUS:")
        for i, component in enumerate(self.agent.memory.selected_components, 1):
            slide = self.agent.memory.slides.get(component)
            if slide:
                status_icon = "✅" if slide.content else "⏳"
                word_count = slide.get_word_count()
                response.append(f"{i}. {status_icon} {slide.title} ({word_count} words)")
        
        # Show available to add
        available = self.agent.get_available_components()
        if available:
            response.append("\nAVAILABLE TO ADD:")
            for comp, info in available.items():
                importance = info.get("importance", "")
                indicator = "⭐" if importance == "essential" else "💡" if importance == "important" else "🔍"
                response.append(f"{indicator} {info['title']} - say 'add {comp}'")
        
        # Show recent activity
        if status['solution_iterations'] > 0:
            response.append(f"\n🔄 Solution iterations: {status['solution_iterations']}")
        
        status_content = "\n".join(response)
        return status_content
    
    def _export_proposal(self) -> str:
        """Export complete proposal to file."""
        try:
            content = self.agent.export_deck_content()
            export_file = self.output_manager.export_proposal(content)
            
            # Create summary report
            summary = self.output_manager.create_summary_report(self.agent.memory)
            
            self.output_manager.log_system_event(f"Proposal exported to {export_file}")
            
            return f"✅ Proposal exported successfully!\n\nFiles created:\n• Proposal: {export_file}\n• Session summary available\n\n{summary}"
            
        except Exception as e:
            return f"❌ Export failed: {str(e)}"
    
    def _handle_flexible_command(self, comment: str, command: dict) -> str:
        """Handle commands with enhanced flexibility."""
        
        # If we have suggestions from the parser, show them
        if command.get("suggestions"):
            response = f"🤔 I understand you want to work with: '{comment}'\n\n"
            response += "Here are some suggestions:\n"
            for suggestion in command["suggestions"]:
                response += f"• {suggestion}\n"
            return response
        
        # General help response
        return f"""🤔 I understand you want to work with: '{comment}'

Here are some things you can try:
• 'Generate full deck' - Create complete proposal
• 'Generate pricing section' - Create specific component
• 'Edit executive summary to focus on ROI' - Modify content
• 'Add risk management' - Include new section
• 'Show status' - View current progress
• 'Export proposal' - Save final document

Or just tell me naturally what you'd like to do!"""