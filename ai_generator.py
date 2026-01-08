"""
AI content generation for the Proposal Deck Generator.
Handles interaction with Gemini API and content generation with retry logic.
"""

import time
import logging
from typing import Optional

from config import config_manager, GEMINI_AVAILABLE

logger = logging.getLogger(__name__)

if GEMINI_AVAILABLE:
    import google.generativeai as genai

class AIGenerator:
    """Enhanced AI content generator with retry logic and quality checks."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        config = config_manager.get_config()
        
        self.api_key = api_key or config.api_key
        self.model_name = model or config.model
        self.max_retries = config.max_retries
        self.retry_delay = config.retry_delay
        self.ready = False
        
        self._initialize_ai()
    
    def _initialize_ai(self):
        """Initialize AI model connection."""
        if not GEMINI_AVAILABLE:
            logger.warning("Gemini SDK not available - running in fallback mode")
            return
        
        if not self.api_key:
            logger.warning("No API key provided - running in fallback mode")
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.ready = True
            logger.info(f"AI Generator initialized successfully with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.ready = False
    
    def generate_content(self, prompt: str) -> str:
        """Generate content with retry logic and quality checks."""
        if not self.ready:
            return self._create_fallback_content(prompt)
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Generation attempt {attempt + 1} for prompt: {prompt[:100]}...")
                
                response = self.model.generate_content(prompt)
                content = getattr(response, "text", str(response)).strip()
                
                # Quality check
                if self._is_quality_content(content):
                    logger.debug(f"Content generated successfully ({len(content)} characters)")
                    return content
                else:
                    logger.warning(f"Generated content failed quality check (attempt {attempt + 1})")
                    
            except Exception as e:
                logger.warning(f"Generation attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    sleep_time = self.retry_delay * (attempt + 1)
                    logger.debug(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
        
        logger.error("All generation attempts failed, using fallback")
        return self._create_fallback_content(prompt)
    
    def _is_quality_content(self, content: str) -> bool:
        """Check if generated content meets quality standards."""
        if not content:
            return False
        
        # Basic quality checks
        min_length = 50
        if len(content) < min_length:
            return False
        
        # Check for common error patterns
        error_patterns = [
            "I cannot",
            "I'm unable to",
            "I don't have access",
            "I can't provide",
            "I'm sorry, but"
        ]
        
        content_lower = content.lower()
        for pattern in error_patterns:
            if pattern.lower() in content_lower:
                return False
        
        # Check for reasonable word count
        word_count = len(content.split())
        if word_count < 10:
            return False
        
        return True
    
    def _create_fallback_content(self, prompt: str) -> str:
        """Create fallback content when AI is unavailable."""
        logger.info("Using fallback content generation")
        
        # Try to extract context from prompt for better fallback
        fallback_content = "⚠️ AI-Generated Content Unavailable\n\n"
        
        if "executive summary" in prompt.lower():
            fallback_content += self._fallback_executive_summary()
        elif "pricing" in prompt.lower() or "commercial" in prompt.lower():
            fallback_content += self._fallback_pricing()
        elif "solution" in prompt.lower():
            fallback_content += self._fallback_solution()
        elif "cover" in prompt.lower():
            fallback_content += self._fallback_cover()
        else:
            fallback_content += self._fallback_generic()
        
        return fallback_content
    
    def _fallback_executive_summary(self) -> str:
        """Fallback content for executive summary."""
        return """# Executive Summary

**Problem Statement**
- [Describe the client's main challenge]
- [Quantify the business impact]

**Our Solution**
- [Brief overview of proposed approach]
- [Key differentiators]

**Expected Outcomes**
- [Measurable benefits]
- [Timeline for delivery]

**Investment Required**
- [High-level cost estimate]

*Note: Please configure GEMINI_API_KEY for AI-generated content.*"""
    
    def _fallback_pricing(self) -> str:
        """Fallback content for pricing section."""
        return """# Pricing & Investment

**Pricing Model**
- [Fixed price / Time & materials / Milestone-based]

**Investment Breakdown**
- Phase 1: [Description] - $[Amount]
- Phase 2: [Description] - $[Amount]
- Phase 3: [Description] - $[Amount]

**Payment Terms**
- [Payment schedule]
- [Terms and conditions]

**Value Justification**
- [ROI calculation]
- [Cost savings explanation]

*Note: Please configure GEMINI_API_KEY for AI-generated content.*"""
    
    def _fallback_solution(self) -> str:
        """Fallback content for solution section."""
        return """# Solution Approach

**Methodology**
- [Step 1: Discovery and Analysis]
- [Step 2: Design and Planning]
- [Step 3: Implementation]
- [Step 4: Testing and Deployment]

**Technology Stack**
- [Core technologies]
- [Integration points]

**Delivery Approach**
- [Project phases]
- [Key milestones]

**Quality Assurance**
- [Testing approach]
- [Success criteria]

*Note: Please configure GEMINI_API_KEY for AI-generated content.*"""
    
    def _fallback_cover(self) -> str:
        """Fallback content for cover slide."""
        return """# [Project Title]

**Prepared for:** [Client Name]
**Prepared by:** [Your Company]
**Date:** [Current Date]
**Version:** 1.0

---

**Proposal Overview**
Comprehensive solution proposal for [client's business challenge]

*Note: Please configure GEMINI_API_KEY for AI-generated content.*"""
    
    def _fallback_generic(self) -> str:
        """Generic fallback content."""
        return """**Professional Content Required**

This section requires:
• Detailed analysis tailored to your client
• Industry-specific insights and recommendations  
• Quantified benefits and business impact
• Professional language and structure

**To enable AI content generation:**
1. Set GEMINI_API_KEY environment variable
2. Install: pip install google-generativeai
3. Regenerate this section

**Manual Content Recommendation:**
Please develop this section with specific details relevant to your client's situation, industry requirements, and business objectives.

*Note: Please configure GEMINI_API_KEY for AI-generated content.*"""
    
    def test_connection(self) -> bool:
        """Test AI connection and functionality."""
        if not self.ready:
            return False
        
        try:
            test_prompt = "Generate a brief professional greeting."
            response = self.generate_content(test_prompt)
            return len(response) > 10 and "unavailable" not in response.lower()
        
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_status(self) -> dict:
        """Get current status of AI generator."""
        return {
            "ready": self.ready,
            "model": self.model_name,
            "api_key_configured": bool(self.api_key),
            "gemini_available": GEMINI_AVAILABLE,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay
        }