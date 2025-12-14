"""
AI Provider integrations for OpenAI GPT and Anthropic Sonnet
"""
from typing import List, Dict, Optional
from enum import Enum
import openai
from anthropic import Anthropic
from app.core.config import settings

class AIModel(str, Enum):
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4O = "gpt-4o"  # Latest GPT-4 model
    GPT_4O_MINI = "gpt-4o-mini"  # Cheaper GPT-4 variant
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"

class AIProvider:
    """Base class for AI providers"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AI client connections"""
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def review_code(
        self,
        code: str,
        language: str,
        model: AIModel,
        custom_prompt: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict:
        """
        Review code using specified AI model
        
        Args:
            code: Source code to review
            language: Programming language
            model: AI model to use
            custom_prompt: Optional custom prompt
            context: Optional context (file path, git diff, etc.)
        
        Returns:
            Review results with issues, suggestions, and explanations
        """
        if model.value.startswith("gpt"):
            return await self._review_with_openai(code, language, model, custom_prompt, context)
        elif model.value.startswith("claude"):
            return await self._review_with_anthropic(code, language, model, custom_prompt, context)
        else:
            raise ValueError(f"Unsupported model: {model}")
    
    async def _review_with_openai(
        self,
        code: str,
        language: str,
        model: AIModel,
        custom_prompt: Optional[str],
        context: Optional[str]
    ) -> Dict:
        """Review code using OpenAI"""
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")
        
        prompt = self._build_prompt(code, language, custom_prompt, context)
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model.value,
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer. Analyze code for bugs, security issues, style problems, and documentation gaps. Provide structured, actionable feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            result = response.choices[0].message.content
            return self._parse_review_result(result, model)
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def _review_with_anthropic(
        self,
        code: str,
        language: str,
        model: AIModel,
        custom_prompt: Optional[str],
        context: Optional[str]
    ) -> Dict:
        """Review code using Anthropic"""
        if not self.anthropic_client:
            raise ValueError("Anthropic API key not configured")
        
        prompt = self._build_prompt(code, language, custom_prompt, context)
        
        try:
            message = self.anthropic_client.messages.create(
                model=model.value,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = message.content[0].text
            return self._parse_review_result(result, model)
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    def _build_prompt(
        self,
        code: str,
        language: str,
        custom_prompt: Optional[str],
        context: Optional[str]
    ) -> str:
        """Build the review prompt"""
        if custom_prompt:
            base_prompt = custom_prompt
        else:
            base_prompt = """Review the following code and identify:
1. Bugs and Logic Errors: Identify potential bugs, logic errors, edge cases, and runtime issues
2. Security Vulnerabilities: Find security issues like SQL injection, XSS, authentication flaws, insecure dependencies
3. Code Style Issues: Check for style violations, naming conventions, formatting issues
4. Documentation/Comments: Assess code documentation, missing comments, unclear explanations

For each issue found, provide:
- Type (bug/security/style/documentation)
- Severity (critical/high/medium/low)
- Location (line numbers)
- Description
- Suggested fix (if applicable)
- Learning explanation (why this is an issue)

Format your response as JSON with the following structure:
{
  "issues": [
    {
      "type": "bug|security|style|documentation",
      "severity": "critical|high|medium|low",
      "line": <line_number>,
      "column": <column_number>,
      "description": "<issue description>",
      "suggestion": "<suggested fix>",
      "explanation": "<learning explanation>"
    }
  ],
  "summary": {
    "total_issues": <count>,
    "by_type": {"bug": <count>, "security": <count>, "style": <count>, "documentation": <count>},
    "by_severity": {"critical": <count>, "high": <count>, "medium": <count>, "low": <count>}
  },
  "overall_score": <0-100>,
  "recommendations": ["<general recommendations>"]
}"""
        
        prompt = f"{base_prompt}\n\nLanguage: {language}\n"
        
        if context:
            prompt += f"\nContext:\n{context}\n"
        
        prompt += f"\nCode to review:\n```{language}\n{code}\n```"
        
        return prompt
    
    def _parse_review_result(self, result: str, model: AIModel) -> Dict:
        """Parse AI response into structured format"""
        import json
        import re
        
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                parsed["raw_response"] = result
                parsed["model_used"] = model.value
                return parsed
            except json.JSONDecodeError:
                pass
        
        # Fallback: return structured response
        return {
            "issues": [],
            "summary": {
                "total_issues": 0,
                "by_type": {},
                "by_severity": {}
            },
            "overall_score": 100,
            "recommendations": [],
            "raw_response": result,
            "model_used": model.value,
            "parse_error": "Could not parse JSON from response"
        }

# Global provider instance
ai_provider = AIProvider()

