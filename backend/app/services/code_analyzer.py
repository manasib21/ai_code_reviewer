"""
Code analyzer for preprocessing and language detection
"""
from typing import Dict, Optional
import re

class CodeAnalyzer:
    """Analyzes code structure and detects language"""
    
    LANGUAGE_PATTERNS = {
        "python": [r"\.py$", r"^import\s+\w+", r"^from\s+\w+\s+import"],
        "javascript": [r"\.js$", r"^import\s+.*from", r"^const\s+\w+\s*=", r"^function\s+\w+"],
        "typescript": [r"\.ts$", r"^import\s+.*from", r":\s*\w+\s*=", r"interface\s+\w+"],
        "java": [r"\.java$", r"^package\s+\w+", r"^public\s+class\s+\w+"],
        "go": [r"\.go$", r"^package\s+\w+", r"^func\s+\w+\("],
        "rust": [r"\.rs$", r"^use\s+\w+", r"^fn\s+\w+\("],
        "cpp": [r"\.(cpp|cc|cxx|c\+\+)$", r"^#include\s*<", r"^using\s+namespace", r"^#include\s*<.*\.hpp"],
        "c": [r"\.c$", r"^#include\s*<", r"^#include\s*\"", r"^int\s+main\s*\(", r"^void\s+\w+\s*\("],
    }
    
    def detect_language(self, code: str, file_path: Optional[str] = None) -> str:
        """Detect programming language from code or file path"""
        if file_path:
            for lang, patterns in self.LANGUAGE_PATTERNS.items():
                if any(re.search(pattern, file_path, re.IGNORECASE) for pattern in patterns):
                    return lang
        
        # Try to detect from code content
        code_lower = code.lower()
        for lang, patterns in self.LANGUAGE_PATTERNS.items():
            if any(re.search(pattern, code, re.IGNORECASE) for pattern in patterns[1:]):
                return lang
        
        return "unknown"
    
    def extract_context(self, code: str, file_path: Optional[str] = None) -> str:
        """Extract context information from code"""
        context_parts = []
        
        if file_path:
            context_parts.append(f"File: {file_path}")
        
        # Extract imports
        imports = re.findall(r"^(?:import|from|require|#include|use|package)\s+.*$", code, re.MULTILINE)
        if imports:
            context_parts.append(f"Imports: {len(imports)} found")
        
        # Extract function/class definitions
        functions = re.findall(r"^(?:def|function|fn|pub\s+fn|public\s+\w+\s+)\s*(\w+)\s*\(", code, re.MULTILINE)
        classes = re.findall(r"^class\s+(\w+)", code, re.MULTILINE)
        
        if functions:
            context_parts.append(f"Functions: {', '.join(functions[:5])}")
        if classes:
            context_parts.append(f"Classes: {', '.join(classes[:5])}")
        
        return "\n".join(context_parts)

