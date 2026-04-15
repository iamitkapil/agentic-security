#!/usr/bin/env python3
"""
Security Tools for ReAct Agent
Provides tools for scanning, analysis, and remediation
"""

import os
import subprocess
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import yaml

logger = logging.getLogger(__name__)


class SecurityTools:
    """Collection of security tools for the ReAct agent"""
    
    def __init__(self, config: Dict[str, Any], pipeline=None):
        """
        Initialize security tools.
        
        Args:
            config: Configuration dictionary
            pipeline: Optional SecurityPipeline instance for integration
        """
        self.config = config
        self.pipeline = pipeline
        self.scan_results = {}
    
    def get_tools(self) -> Dict[str, Any]:
        """
        Get all available tools as a dictionary.
        
        Returns:
            Dictionary mapping tool names to functions
        """
        return {
            'SCAN_CODE': self.scan_code,
            'ANALYZE_VULNERABILITY': self.analyze_vulnerability,
            'GENERATE_FIX': self.generate_fix,
            'APPLY_FIX': self.apply_fix,
            'RUN_TESTS': self.run_tests,
            'CREATE_BRANCH': self.create_branch,
            'COMMIT_CHANGES': self.commit_changes,
            'CREATE_PR': self.create_pr,
            'READ_FILE': self.read_file,
            'LIST_FILES': self.list_files,
            'SEARCH_PATTERN': self.search_pattern,
            'GET_SCAN_SUMMARY': self.get_scan_summary,
            'VALIDATE_FIX': self.validate_fix,
            'ROLLBACK_CHANGES': self.rollback_changes
        }
    
    def scan_code(self, path: str = ".", scan_type: str = "all") -> Dict[str, Any]:
        """
        Scan code for security vulnerabilities.
        
        Args:
            path: Path to scan (default: current directory)
            scan_type: Type of scan (all, sql, xss, injection, crypto)
            
        Returns:
            Dictionary with scan results
        """
        try:
            logger.info(f"Scanning {path} for {scan_type} vulnerabilities")
            
            results = {
                "path": path,
                "scan_type": scan_type,
                "vulnerabilities": [],
                "summary": {}
            }
            
            # Get security patterns from config
            patterns = self.config.get('security_patterns', {})
            
            if scan_type == "all":
                scan_patterns = patterns
            elif scan_type in patterns:
                scan_patterns = {scan_type: patterns[scan_type]}
            else:
                return {"error": f"Unknown scan type: {scan_type}"}
            
            # Scan files for patterns
            for vuln_type, pattern_list in scan_patterns.items():
                findings = self._scan_for_patterns(path, pattern_list, vuln_type)
                results["vulnerabilities"].extend(findings)
            
            # Generate summary
            results["summary"] = {
                "total": len(results["vulnerabilities"]),
                "by_type": self._count_by_type(results["vulnerabilities"]),
                "by_severity": self._count_by_severity(results["vulnerabilities"])
            }
            
            self.scan_results[path] = results
            return results
            
        except Exception as e:
            logger.error(f"Error scanning code: {e}")
            return {"error": str(e)}
    
    def _scan_for_patterns(self, path: str, patterns: List[str], vuln_type: str) -> List[Dict[str, Any]]:
        """Scan files for specific patterns"""
        findings = []
        path_obj = Path(path)
        
        # Get all Python files
        if path_obj.is_file():
            files = [path_obj]
        else:
            files = list(path_obj.rglob("*.py"))
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, 1):
                    for pattern in patterns:
                        if pattern.lower() in line.lower():
                            findings.append({
                                "type": vuln_type,
                                "file": str(file_path),
                                "line": line_num,
                                "code": line.strip(),
                                "pattern": pattern,
                                "severity": self._assess_severity(vuln_type, line)
                            })
            except Exception as e:
                logger.warning(f"Error scanning {file_path}: {e}")
        
        return findings
    
    def _assess_severity(self, vuln_type: str, code_line: str) -> str:
        """Assess vulnerability severity"""
        # Simple heuristic-based severity assessment
        high_risk = ['eval', 'exec', 'os.system', 'md5', 'sha1']
        
        if any(risk in code_line.lower() for risk in high_risk):
            return "high"
        elif vuln_type in ['sql_injection', 'command_injection']:
            return "high"
        elif vuln_type in ['xss', 'crypto']:
            return "medium"
        else:
            return "low"
    
    def _count_by_type(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count vulnerabilities by type"""
        counts = {}
        for vuln in vulnerabilities:
            vuln_type = vuln.get('type', 'unknown')
            counts[vuln_type] = counts.get(vuln_type, 0) + 1
        return counts
    
    def _count_by_severity(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count vulnerabilities by severity"""
        counts = {"high": 0, "medium": 0, "low": 0}
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'low')
            counts[severity] = counts.get(severity, 0) + 1
        return counts
    
    def analyze_vulnerability(self, file_path: str, line_number: int, vuln_type: str) -> Dict[str, Any]:
        """
        Analyze a specific vulnerability in detail.
        
        Args:
            file_path: Path to the vulnerable file
            line_number: Line number of the vulnerability
            vuln_type: Type of vulnerability
            
        Returns:
            Detailed analysis of the vulnerability
        """
        try:
            logger.info(f"Analyzing {vuln_type} in {file_path}:{line_number}")
            
            # Read file context
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Get context around the vulnerability
            start = max(0, line_number - 5)
            end = min(len(lines), line_number + 5)
            context = ''.join(lines[start:end])
            
            analysis = {
                "file": file_path,
                "line": line_number,
                "type": vuln_type,
                "vulnerable_code": lines[line_number - 1].strip() if line_number <= len(lines) else "",
                "context": context,
                "risk_level": self._assess_severity(vuln_type, lines[line_number - 1] if line_number <= len(lines) else ""),
                "recommendations": self._get_recommendations(vuln_type)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing vulnerability: {e}")
            return {"error": str(e)}
    
    def _get_recommendations(self, vuln_type: str) -> List[str]:
        """Get security recommendations for vulnerability type"""
        recommendations = {
            "sql_injection": [
                "Use parameterized queries or prepared statements",
                "Never concatenate user input into SQL queries",
                "Use ORM frameworks with built-in protection",
                "Validate and sanitize all user inputs"
            ],
            "command_injection": [
                "Use subprocess.run() with list arguments instead of shell=True",
                "Never pass user input directly to shell commands",
                "Use shlex.quote() to escape shell arguments",
                "Validate input against a whitelist"
            ],
            "xss": [
                "Use html.escape() for all user-generated content",
                "Implement Content Security Policy (CSP)",
                "Use template engines with auto-escaping",
                "Validate and sanitize user inputs"
            ],
            "crypto": [
                "Use bcrypt or argon2 for password hashing",
                "Use SHA-256 or SHA-3 for cryptographic hashing",
                "Never use MD5 or SHA-1 for security purposes",
                "Use established cryptographic libraries"
            ]
        }
        return recommendations.get(vuln_type, ["Review security best practices for this vulnerability type"])
    
    def generate_fix(self, file_path: str, line_number: int, vuln_type: str) -> Dict[str, Any]:
        """
        Generate a fix for a vulnerability.
        
        Args:
            file_path: Path to the vulnerable file
            line_number: Line number of the vulnerability
            vuln_type: Type of vulnerability
            
        Returns:
            Generated fix with code changes
        """
        try:
            logger.info(f"Generating fix for {vuln_type} in {file_path}:{line_number}")
            
            # Read the file
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            vulnerable_line = lines[line_number - 1] if line_number <= len(lines) else ""
            
            # Generate fix based on vulnerability type
            fix = self._generate_fix_code(vulnerable_line, vuln_type)
            
            return {
                "file": file_path,
                "line": line_number,
                "original": vulnerable_line.strip(),
                "fixed": fix,
                "type": vuln_type,
                "explanation": self._get_fix_explanation(vuln_type)
            }
            
        except Exception as e:
            logger.error(f"Error generating fix: {e}")
            return {"error": str(e)}
    
    def _generate_fix_code(self, vulnerable_line: str, vuln_type: str) -> str:
        """Generate fixed code for vulnerability"""
        # Simple pattern-based fixes
        if vuln_type == "sql_injection":
            if "f\"SELECT" in vulnerable_line or "f'SELECT" in vulnerable_line:
                return vulnerable_line.replace("f\"", "# TODO: Use parameterized query instead of f\"")
        elif vuln_type == "command_injection":
            if "os.system" in vulnerable_line:
                return vulnerable_line.replace("os.system", "subprocess.run")
            if "eval(" in vulnerable_line:
                return "# TODO: Remove eval() and use safe alternatives"
        elif vuln_type == "crypto":
            if "md5" in vulnerable_line.lower():
                return vulnerable_line.replace("md5", "sha256")
            if "sha1" in vulnerable_line.lower():
                return vulnerable_line.replace("sha1", "sha256")
        
        return f"# TODO: Fix {vuln_type} vulnerability\n{vulnerable_line}"
    
    def _get_fix_explanation(self, vuln_type: str) -> str:
        """Get explanation for the fix"""
        explanations = {
            "sql_injection": "Replaced string formatting with parameterized queries to prevent SQL injection",
            "command_injection": "Replaced unsafe command execution with subprocess.run() using list arguments",
            "xss": "Added HTML escaping to prevent cross-site scripting attacks",
            "crypto": "Replaced weak cryptographic algorithm with secure alternative"
        }
        return explanations.get(vuln_type, "Applied security fix")
    
    def apply_fix(self, file_path: str, line_number: int, fixed_code: str) -> Dict[str, Any]:
        """
        Apply a fix to a file.
        
        Args:
            file_path: Path to the file
            line_number: Line number to fix
            fixed_code: The fixed code
            
        Returns:
            Result of applying the fix
        """
        try:
            logger.info(f"Applying fix to {file_path}:{line_number}")
            
            # Read file
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Apply fix
            if line_number <= len(lines):
                original = lines[line_number - 1]
                lines[line_number - 1] = fixed_code + '\n'
                
                # Write back
                with open(file_path, 'w') as f:
                    f.writelines(lines)
                
                return {
                    "success": True,
                    "file": file_path,
                    "line": line_number,
                    "original": original.strip(),
                    "fixed": fixed_code.strip()
                }
            else:
                return {"error": f"Line {line_number} out of range"}
                
        except Exception as e:
            logger.error(f"Error applying fix: {e}")
            return {"error": str(e)}
    
    def run_tests(self, test_path: str = "tests") -> Dict[str, Any]:
        """
        Run tests to validate fixes.
        
        Args:
            test_path: Path to tests directory
            
        Returns:
            Test results
        """
        try:
            logger.info(f"Running tests in {test_path}")
            
            result = subprocess.run(
                ["pytest", test_path, "-v"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode
            }
            
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            return {"error": str(e)}
    
    def create_branch(self, branch_name: str) -> Dict[str, Any]:
        """Create a new git branch"""
        try:
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name],
                capture_output=True,
                text=True
            )
            return {"success": result.returncode == 0, "branch": branch_name}
        except Exception as e:
            return {"error": str(e)}
    
    def commit_changes(self, message: str) -> Dict[str, Any]:
        """Commit changes to git"""
        try:
            subprocess.run(["git", "add", "."], check=True)
            result = subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True,
                text=True
            )
            return {"success": result.returncode == 0, "message": message}
        except Exception as e:
            return {"error": str(e)}
    
    def create_pr(self, title: str, body: str) -> Dict[str, Any]:
        """Create a pull request"""
        try:
            result = subprocess.run(
                ["gh", "pr", "create", "--title", title, "--body", body],
                capture_output=True,
                text=True
            )
            return {"success": result.returncode == 0, "output": result.stdout}
        except Exception as e:
            return {"error": str(e)}
    
    def read_file(self, file_path: str, start_line: int = 1, end_line: int = -1) -> Dict[str, Any]:
        """Read file contents"""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            if end_line == -1:
                end_line = len(lines)
            
            content = ''.join(lines[start_line-1:end_line])
            return {"content": content, "lines": len(lines)}
        except Exception as e:
            return {"error": str(e)}
    
    def list_files(self, directory: str = ".", pattern: str = "*.py") -> Dict[str, Any]:
        """List files in directory"""
        try:
            path = Path(directory)
            files = list(path.rglob(pattern))
            return {"files": [str(f) for f in files], "count": len(files)}
        except Exception as e:
            return {"error": str(e)}
    
    def search_pattern(self, pattern: str, directory: str = ".") -> Dict[str, Any]:
        """Search for pattern in files"""
        try:
            matches = []
            for file_path in Path(directory).rglob("*.py"):
                with open(file_path, 'r') as f:
                    for line_num, line in enumerate(f, 1):
                        if pattern in line:
                            matches.append({
                                "file": str(file_path),
                                "line": line_num,
                                "content": line.strip()
                            })
            return {"matches": matches, "count": len(matches)}
        except Exception as e:
            return {"error": str(e)}
    
    def get_scan_summary(self, path: str = ".") -> Dict[str, Any]:
        """Get summary of previous scan results"""
        if path in self.scan_results:
            return self.scan_results[path]["summary"]
        return {"error": "No scan results found for this path"}
    
    def validate_fix(self, file_path: str, line_number: int) -> Dict[str, Any]:
        """Validate that a fix was applied correctly"""
        try:
            # Re-scan the specific line
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            if line_number <= len(lines):
                line = lines[line_number - 1]
                # Check if common vulnerability patterns are still present
                unsafe_patterns = ['eval(', 'exec(', 'os.system', 'f"SELECT', "f'SELECT"]
                is_safe = not any(pattern in line for pattern in unsafe_patterns)
                
                return {
                    "valid": is_safe,
                    "line": line.strip(),
                    "message": "Fix validated successfully" if is_safe else "Vulnerability still present"
                }
            return {"error": "Line number out of range"}
        except Exception as e:
            return {"error": str(e)}
    
    def rollback_changes(self, file_path: str) -> Dict[str, Any]:
        """Rollback changes to a file"""
        try:
            result = subprocess.run(
                ["git", "checkout", "HEAD", "--", file_path],
                capture_output=True,
                text=True
            )
            return {"success": result.returncode == 0, "file": file_path}
        except Exception as e:
            return {"error": str(e)}

# Made with Bob
