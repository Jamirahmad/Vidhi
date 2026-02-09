"""
Safety Guardrails for Vidhi Legal Research Platform

This module implements comprehensive safety and ethical guardrails for the Vidhi system.
It ensures the platform operates within ethical boundaries and prevents harmful outputs.

Critical Safety Measures:
- Prevention of fabricated legal information
- Citation authenticity verification
- Ethical boundary enforcement
- Content filtering and moderation
- Human verification requirements
- Bias and fairness monitoring
- Legal advice prevention
- Privacy protection
- Professional ethics compliance
- Output quality validation

Author: Vidhi Development Team
License: MIT (Educational & Research Use Only)
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Safety severity levels"""
    CRITICAL = "critical"  # Immediate block
    HIGH = "high"         # Block with warning
    MEDIUM = "medium"     # Allow with warning
    LOW = "low"          # Log only
    INFO = "info"        # Informational


class ViolationType(Enum):
    """Types of safety violations"""
    FABRICATED_CITATION = "fabricated_citation"
    LEGAL_ADVICE = "legal_advice"
    HARMFUL_CONTENT = "harmful_content"
    PRIVACY_VIOLATION = "privacy_violation"
    UNETHICAL_CONTENT = "unethical_content"
    BIAS_DETECTED = "bias_detected"
    MISSING_VERIFICATION = "missing_verification"
    INCOMPLETE_DISCLOSURE = "incomplete_disclosure"
    UNAUTHORIZED_PRACTICE = "unauthorized_practice"
    QUALITY_INSUFFICIENT = "quality_insufficient"


@dataclass
class SafetyViolation:
    """Represents a safety violation"""
    violation_type: ViolationType
    severity: SafetyLevel
    description: str
    context: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SafetyCheckResult:
    """Result of safety validation"""
    is_safe: bool
    violations: List[SafetyViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    required_actions: List[str] = field(default_factory=list)
    confidence_score: float = 1.0
    human_review_required: bool = False
    
    def has_critical_violations(self) -> bool:
        """Check if there are any critical violations"""
        return any(v.severity == SafetyLevel.CRITICAL for v in self.violations)
    
    def has_high_violations(self) -> bool:
        """Check if there are any high severity violations"""
        return any(v.severity in [SafetyLevel.CRITICAL, SafetyLevel.HIGH] for v in self.violations)


class SafetyGuardrails:
    """
    Comprehensive safety and ethics enforcement system for Vidhi.
    
    This system:
    1. Validates all outputs for safety and ethics
    2. Prevents fabricated legal information
    3. Enforces professional boundaries
    4. Protects user privacy
    5. Ensures human verification requirements
    6. Monitors for bias and fairness
    7. Validates output quality
    8. Maintains audit logs
    """
    
    def __init__(
        self,
        citation_validator=None,
        strict_mode: bool = True,
        enable_audit_log: bool = True
    ):
        """
        Initialize Safety Guardrails.
        
        Args:
            citation_validator: CitationValidator instance for citation verification
            strict_mode: Enable strict safety enforcement
            enable_audit_log: Enable safety audit logging
        """
        self.citation_validator = citation_validator
        self.strict_mode = strict_mode
        self.enable_audit_log = enable_audit_log
        
        # Audit log
        self.audit_log: List[SafetyViolation] = []
        
        # Prohibited patterns and keywords
        self.prohibited_patterns = self._initialize_prohibited_patterns()
        self.legal_advice_patterns = self._initialize_legal_advice_patterns()
        self.harmful_content_patterns = self._initialize_harmful_patterns()
        self.privacy_patterns = self._initialize_privacy_patterns()
        
        # Mandatory disclaimers
        self.required_disclaimers = self._initialize_required_disclaimers()
        
        logger.info(f"SafetyGuardrails initialized (strict_mode={strict_mode})")
    
    def _initialize_prohibited_patterns(self) -> List[Dict]:
        """Initialize patterns for prohibited content"""
        return [
            {
                'pattern': r'(?i)(fabricate|make\s+up|invent|create\s+fake)\s+(citation|case|precedent)',
                'violation_type': ViolationType.FABRICATED_CITATION,
                'severity': SafetyLevel.CRITICAL,
                'description': 'Instruction to fabricate legal information'
            },
            {
                'pattern': r'(?i)hallucinate\s+(case|citation|law|precedent)',
                'violation_type': ViolationType.FABRICATED_CITATION,
                'severity': SafetyLevel.CRITICAL,
                'description': 'Potential hallucination of legal content'
            },
            {
                'pattern': r'(?i)(fake|false|fictional)\s+(case|citation|judgment)',
                'violation_type': ViolationType.FABRICATED_CITATION,
                'severity': SafetyLevel.CRITICAL,
                'description': 'Reference to fake legal content'
            }
        ]
    
    def _initialize_legal_advice_patterns(self) -> List[Dict]:
        """Initialize patterns that indicate legal advice"""
        return [
            {
                'pattern': r'(?i)you\s+should\s+(file|sue|claim|pursue)',
                'severity': SafetyLevel.HIGH,
                'description': 'Directive legal advice detected'
            },
            {
                'pattern': r'(?i)I\s+(recommend|advise|suggest)\s+you\s+(to\s+)?(file|sue|pursue)',
                'severity': SafetyLevel.HIGH,
                'description': 'Direct legal recommendation'
            },
            {
                'pattern': r'(?i)my\s+legal\s+advice\s+is',
                'severity': SafetyLevel.CRITICAL,
                'description': 'Explicit legal advice statement'
            },
            {
                'pattern': r'(?i)you\s+will\s+(definitely|certainly)\s+(win|lose)',
                'severity': SafetyLevel.HIGH,
                'description': 'Guarantee of legal outcome'
            }
        ]
    
    def _initialize_harmful_patterns(self) -> List[Dict]:
        """Initialize patterns for harmful content"""
        return [
            {
                'pattern': r'(?i)(harm|hurt|injure|damage)\s+(opposing\s+party|witness|judge)',
                'severity': SafetyLevel.CRITICAL,
                'description': 'Content suggesting harm to legal participants'
            },
            {
                'pattern': r'(?i)(bribe|corrupt|manipulate)\s+(judge|magistrate|court)',
                'severity': SafetyLevel.CRITICAL,
                'description': 'Content suggesting judicial corruption'
            },
            {
                'pattern': r'(?i)(forge|falsify|tamper)\s+(evidence|document|record)',
                'severity': SafetyLevel.CRITICAL,
                'description': 'Content suggesting evidence tampering'
            },
            {
                'pattern': r'(?i)(threaten|intimidate|coerce)\s+(witness|complainant)',
                'severity': SafetyLevel.CRITICAL,
                'description': 'Content suggesting witness intimidation'
            }
        ]
    
    def _initialize_privacy_patterns(self) -> List[str]:
        """Initialize patterns that may indicate privacy violations"""
        return [
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Aadhaar-like number
            r'\b[A-Z]{5}\d{4}[A-Z]\b',  # PAN-like number
            r'\b\d{10}\b',  # Phone number
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email
        ]
    
    def _initialize_required_disclaimers(self) -> List[str]:
        """Initialize mandatory disclaimers"""
        return [
            "This is an AI-generated document and must be reviewed by a qualified legal professional.",
            "This does not constitute legal advice.",
            "Consult a licensed attorney before taking any legal action.",
            "Human verification is required before using this document."
        ]
    
    # ===================================================================
    # CORE SAFETY VALIDATION
    # ===================================================================
    
    def validate_output(
        self,
        content: str,
        output_type: str = "general",
        context: Optional[Dict] = None
    ) -> SafetyCheckResult:
        """
        Comprehensive safety validation of output content.
        
        Args:
            content: Content to validate
            output_type: Type of output (document, report, research, etc.)
            context: Additional context for validation
            
        Returns:
            SafetyCheckResult with validation details
        """
        context = context or {}
        violations = []
        warnings = []
        required_actions = []
        
        logger.info(f"Performing safety validation for {output_type}")
        
        # 1. Check for fabricated content
        fabrication_violations = self._check_fabricated_content(content)
        violations.extend(fabrication_violations)
        
        # 2. Check for legal advice violations
        advice_violations = self._check_legal_advice(content, output_type)
        violations.extend(advice_violations)
        
        # 3. Check for harmful content
        harmful_violations = self._check_harmful_content(content)
        violations.extend(harmful_violations)
        
        # 4. Check for privacy violations
        privacy_violations = self._check_privacy_violations(content)
        violations.extend(privacy_violations)
        
        # 5. Validate citations if present
        citation_violations = self._validate_citations_in_content(content)
        violations.extend(citation_violations)
        
        # 6. Check for required disclaimers
        disclaimer_violations = self._check_required_disclaimers(content, output_type)
        violations.extend(disclaimer_violations)
        
        # 7. Check output quality
        quality_issues = self._check_output_quality(content, output_type)
        violations.extend(quality_issues)
        
        # 8. Check for bias
        bias_warnings = self._check_bias(content)
        warnings.extend(bias_warnings)
        
        # Determine if safe
        is_safe = not any(
            v.severity in [SafetyLevel.CRITICAL, SafetyLevel.HIGH]
            for v in violations
        )
        
        # Determine if human review is required
        human_review_required = (
            len(violations) > 0 or
            output_type in ['legal_document', 'bail_application', 'writ_petition'] or
            self._contains_sensitive_content(content)
        )
        
        # Required actions
        if violations:
            required_actions.append("Address all safety violations before proceeding")
        if human_review_required:
            required_actions.append("Mandatory human review by qualified legal professional")
        
        # Calculate confidence score
        confidence = self._calculate_safety_confidence(violations, warnings)
        
        # Log violations if audit enabled
        if self.enable_audit_log:
            self.audit_log.extend(violations)
        
        result = SafetyCheckResult(
            is_safe=is_safe,
            violations=violations,
            warnings=warnings,
            required_actions=required_actions,
            confidence_score=confidence,
            human_review_required=human_review_required
        )
        
        logger.info(f"Safety validation complete: is_safe={is_safe}, violations={len(violations)}")
        return result
    
    def _check_fabricated_content(self, content: str) -> List[SafetyViolation]:
        """Check for fabricated or hallucinated content"""
        violations = []
        
        for pattern_dict in self.prohibited_patterns:
            if re.search(pattern_dict['pattern'], content):
                violation = SafetyViolation(
                    violation_type=pattern_dict['violation_type'],
                    severity=pattern_dict['severity'],
                    description=pattern_dict['description'],
                    context=self._extract_context(content, pattern_dict['pattern'])
                )
                violations.append(violation)
                logger.warning(f"Fabricated content detected: {violation.description}")
        
        return violations
    
    def _check_legal_advice(self, content: str, output_type: str) -> List[SafetyViolation]:
        """Check for unauthorized legal advice"""
        violations = []
        
        # Legal documents can contain recommendations, but must be properly qualified
        if output_type in ['legal_document', 'bail_application', 'writ_petition']:
            # More lenient for legal documents
            threshold = SafetyLevel.CRITICAL
        else:
            # Stricter for general outputs
            threshold = SafetyLevel.HIGH
        
        for pattern_dict in self.legal_advice_patterns:
            if pattern_dict['severity'].value in ['critical', 'high']:
                if re.search(pattern_dict['pattern'], content):
                    violation = SafetyViolation(
                        violation_type=ViolationType.LEGAL_ADVICE,
                        severity=pattern_dict['severity'],
                        description=pattern_dict['description'],
                        context=self._extract_context(content, pattern_dict['pattern'])
                    )
                    violations.append(violation)
                    logger.warning(f"Legal advice detected: {violation.description}")
        
        return violations
    
    def _check_harmful_content(self, content: str) -> List[SafetyViolation]:
        """Check for harmful or unethical content"""
        violations = []
        
        for pattern_dict in self.harmful_content_patterns:
            if re.search(pattern_dict['pattern'], content):
                violation = SafetyViolation(
                    violation_type=ViolationType.HARMFUL_CONTENT,
                    severity=pattern_dict['severity'],
                    description=pattern_dict['description'],
                    context=self._extract_context(content, pattern_dict['pattern'])
                )
                violations.append(violation)
                logger.error(f"HARMFUL CONTENT DETECTED: {violation.description}")
        
        return violations
    
    def _check_privacy_violations(self, content: str) -> List[SafetyViolation]:
        """Check for potential privacy violations (PII exposure)"""
        violations = []
        
        for pattern in self.privacy_patterns:
            matches = re.findall(pattern, content)
            if matches:
                violation = SafetyViolation(
                    violation_type=ViolationType.PRIVACY_VIOLATION,
                    severity=SafetyLevel.HIGH,
                    description=f"Potential PII detected: {len(matches)} instance(s)",
                    context=f"Pattern matched: {pattern}",
                    metadata={'matches_count': len(matches)}
                )
                violations.append(violation)
                logger.warning(f"Privacy concern: Potential PII detected")
        
        return violations
    
    def _validate_citations_in_content(self, content: str) -> List[SafetyViolation]:
        """Validate all citations in content for authenticity"""
        violations = []
        
        if not self.citation_validator:
            logger.warning("Citation validator not available, skipping citation validation")
            return violations
        
        # Extract citations from content
        citations = self.citation_validator.extract_citations_from_text(content)
        
        if not citations:
            return violations
        
        logger.info(f"Validating {len(citations)} citations in content")
        
        # Validate each citation
        for citation in citations:
            result = self.citation_validator.validate_citation(citation)
            
            if not result.is_valid:
                violation = SafetyViolation(
                    violation_type=ViolationType.FABRICATED_CITATION,
                    severity=SafetyLevel.HIGH,
                    description=f"Invalid citation format: {citation}",
                    context=f"Errors: {', '.join(result.errors)}",
                    metadata={'citation': citation, 'validation_result': result}
                )
                violations.append(violation)
            
            # Check citation existence in database if available
            if self.citation_validator.vectorstore:
                exists = self.citation_validator.check_against_database(citation)
                if not exists:
                    violation = SafetyViolation(
                        violation_type=ViolationType.FABRICATED_CITATION,
                        severity=SafetyLevel.CRITICAL,
                        description=f"Citation not found in verified database: {citation}",
                        context="This citation may be fabricated or hallucinated",
                        metadata={'citation': citation}
                    )
                    violations.append(violation)
                    logger.error(f"CRITICAL: Unverified citation detected: {citation}")
        
        return violations
    
    def _check_required_disclaimers(self, content: str, output_type: str) -> List[SafetyViolation]:
        """Check if required disclaimers are present"""
        violations = []
        
        # Legal documents must have disclaimers
        if output_type in ['legal_document', 'bail_application', 'writ_petition', 'legal_notice']:
            
            # Check for at least one required disclaimer
            has_disclaimer = any(
                disclaimer.lower() in content.lower()
                for disclaimer in self.required_disclaimers
            )
            
            if not has_disclaimer:
                violation = SafetyViolation(
                    violation_type=ViolationType.INCOMPLETE_DISCLOSURE,
                    severity=SafetyLevel.HIGH,
                    description="Missing required legal disclaimer",
                    context="Legal documents must include appropriate disclaimers"
                )
                violations.append(violation)
                logger.warning("Missing required disclaimer in legal document")
        
        return violations
    
    def _check_output_quality(self, content: str, output_type: str) -> List[SafetyViolation]:
        """Check output quality and completeness"""
        violations = []
        
        # Minimum length check
        if len(content.strip()) < 100:
            violation = SafetyViolation(
                violation_type=ViolationType.QUALITY_INSUFFICIENT,
                severity=SafetyLevel.MEDIUM,
                description="Output content is too short",
                context=f"Content length: {len(content)} characters"
            )
            violations.append(violation)
        
        # Check for placeholder text
        placeholders = [
            r'\[.*?\]',  # [placeholder]
            r'___+',     # ___
            r'XXX+',     # XXX
            r'TBD',      # TBD
            r'TODO'      # TODO
        ]
        
        for pattern in placeholders:
            if re.search(pattern, content):
                violation = SafetyViolation(
                    violation_type=ViolationType.QUALITY_INSUFFICIENT,
                    severity=SafetyLevel.MEDIUM,
                    description="Output contains placeholder text",
                    context=f"Pattern: {pattern}"
                )
                violations.append(violation)
                break
        
        # Check for incomplete sentences (for documents)
        if output_type in ['legal_document', 'report']:
            if content.count('.') < 3:
                violation = SafetyViolation(
                    violation_type=ViolationType.QUALITY_INSUFFICIENT,
                    severity=SafetyLevel.LOW,
                    description="Output appears incomplete (very few sentences)",
                    context=f"Sentence count: {content.count('.')}"
                )
                violations.append(violation)
        
        return violations
    
    def _check_bias(self, content: str) -> List[str]:
        """Check for potential bias in content"""
        warnings = []
        
        # Bias indicators (simplified detection)
        bias_patterns = [
            (r'(?i)(always|never|all|none)\s+(men|women|muslims|hindus|christians)', 
             "Absolute language with demographic groups"),
            (r'(?i)(obviously|clearly|undoubtedly)\s+', 
             "Overconfident language that may indicate bias"),
            (r'(?i)(should|must|need\s+to)\s+(believe|think|feel)', 
             "Prescriptive language about beliefs")
        ]
        
        for pattern, description in bias_patterns:
            if re.search(pattern, content):
                warnings.append(f"Potential bias indicator: {description}")
        
        return warnings
    
    def _contains_sensitive_content(self, content: str) -> bool:
        """Check if content contains sensitive information requiring extra review"""
        sensitive_keywords = [
            'minor', 'child', 'juvenile',
            'sexual', 'rape', 'assault',
            'murder', 'death penalty', 'capital punishment',
            'terrorism', 'national security',
            'corruption', 'bribery'
        ]
        
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in sensitive_keywords)
    
    def _extract_context(self, content: str, pattern: str, context_length: int = 100) -> str:
        """Extract context around a pattern match"""
        match = re.search(pattern, content, re.IGNORECASE)
        if not match:
            return ""
        
        start = max(0, match.start() - context_length)
        end = min(len(content), match.end() + context_length)
        
        return "..." + content[start:end] + "..."
    
    def _calculate_safety_confidence(
        self,
        violations: List[SafetyViolation],
        warnings: List[str]
    ) -> float:
        """Calculate confidence score for safety validation"""
        if not violations and not warnings:
            return 1.0
        
        confidence = 1.0
        
        # Reduce confidence for violations
        for violation in violations:
            if violation.severity == SafetyLevel.CRITICAL:
                confidence -= 0.3
            elif violation.severity == SafetyLevel.HIGH:
                confidence -= 0.2
            elif violation.severity == SafetyLevel.MEDIUM:
                confidence -= 0.1
            else:
                confidence -= 0.05
        
        # Reduce confidence for warnings
        confidence -= len(warnings) * 0.05
        
        return max(0.0, min(1.0, confidence))
    
    # ===================================================================
    # WORKFLOW VALIDATION
    # ===================================================================
    
    def validate_workflow_state(
        self,
        workflow_state: Any
    ) -> SafetyCheckResult:
        """
        Validate entire workflow state for safety compliance.
        
        Args:
            workflow_state: WorkflowState object from orchestrator
            
        Returns:
            SafetyCheckResult
        """
        violations = []
        warnings = []
        required_actions = []
        
        logger.info("Validating workflow state for safety compliance")
        
        # Check if human verification is pending
        if hasattr(workflow_state, 'current_stage'):
            stage = workflow_state.current_stage.value
            if stage != 'human_review' and stage != 'completed':
                violation = SafetyViolation(
                    violation_type=ViolationType.MISSING_VERIFICATION,
                    severity=SafetyLevel.HIGH,
                    description="Workflow has not reached human review stage",
                    context=f"Current stage: {stage}"
                )
                violations.append(violation)
                required_actions.append("Complete human review before finalization")
        
        # Validate drafted document if present
        if hasattr(workflow_state, 'drafted_document') and workflow_state.drafted_document:
            doc_result = self.validate_output(
                workflow_state.drafted_document,
                output_type='legal_document'
            )
            violations.extend(doc_result.violations)
            warnings.extend(doc_result.warnings)
        
        # Validate citations
        if hasattr(workflow_state, 'citations') and workflow_state.citations:
            citation_result = self._validate_citations_list(workflow_state.citations)
            violations.extend(citation_result.violations)
        
        # Check for workflow errors
        if hasattr(workflow_state, 'workflow_errors') and workflow_state.workflow_errors:
            if len(workflow_state.workflow_errors) > 0:
                warnings.append(f"Workflow has {len(workflow_state.workflow_errors)} error(s)")
        
        is_safe = not any(
            v.severity in [SafetyLevel.CRITICAL, SafetyLevel.HIGH]
            for v in violations
        )
        
        confidence = self._calculate_safety_confidence(violations, warnings)
        
        result = SafetyCheckResult(
            is_safe=is_safe,
            violations=violations,
            warnings=warnings,
            required_actions=required_actions,
            confidence_score=confidence,
            human_review_required=True  # Always required for workflow
        )
        
        logger.info(f"Workflow validation complete: is_safe={is_safe}")
        return result
    
    def _validate_citations_list(self, citations: List[str]) -> SafetyCheckResult:
        """Validate a list of citations"""
        violations = []
        
        if not self.citation_validator:
            return SafetyCheckResult(is_safe=True)
        
        for citation in citations:
            result = self.citation_validator.validate_citation(citation)
            
            if not result.is_valid:
                violation = SafetyViolation(
                    violation_type=ViolationType.FABRICATED_CITATION,
                    severity=SafetyLevel.HIGH,
                    description=f"Invalid citation: {citation}",
                    context=f"Errors: {', '.join(result.errors)}"
                )
                violations.append(violation)
        
        is_safe = len(violations) == 0
        
        return SafetyCheckResult(
            is_safe=is_safe,
            violations=violations
        )
    
    # ===================================================================
    # DISCLAIMER MANAGEMENT
    # ===================================================================
    
    def add_required_disclaimers(
        self,
        content: str,
        output_type: str = "general"
    ) -> str:
        """
        Add required disclaimers to content.
        
        Args:
            content: Original content
            output_type: Type of output
            
        Returns:
            Content with disclaimers added
        """
        disclaimers = []
        
        if output_type in ['legal_document', 'bail_application', 'writ_petition', 'legal_notice']:
            disclaimers.append(
                "\n\n" + "=" * 80 + "\n" +
                "IMPORTANT DISCLAIMER\n" +
                "=" * 80 + "\n" +
                "This document has been generated with AI assistance and MUST be reviewed,\n" +
                "verified, and approved by a qualified legal professional before use.\n\n" +
                "This document does NOT constitute legal advice. Consult a licensed attorney\n" +
                "before taking any legal action based on this document.\n\n" +
                "The accuracy of citations, legal provisions, and recommendations must be\n" +
                "independently verified. Human verification is MANDATORY.\n" +
                "=" * 80
            )
        else:
            disclaimers.append(
                "\n\n---\n" +
                "Disclaimer: This information is AI-generated for research purposes only.\n" +
                "It does not constitute legal advice. Consult a qualified attorney for legal guidance.\n" +
                "---"
            )
        
        return content + "".join(disclaimers)
    
    def get_disclaimer_for_output_type(self, output_type: str) -> str:
        """Get appropriate disclaimer for output type"""
        disclaimers = {
            'legal_document': (
                "MANDATORY DISCLAIMER: This is an AI-generated draft document. "
                "It MUST be reviewed, verified, and approved by a qualified legal professional "
                "before filing or use. This does not constitute legal advice."
            ),
            'research': (
                "This research is AI-generated and for informational purposes only. "
                "Verify all citations and legal principles with authoritative sources. "
                "Consult a legal professional for case-specific advice."
            ),
            'general': (
                "This content is AI-generated and does not constitute legal advice. "
                "Consult a qualified attorney for legal guidance."
            )
        }
        
        return disclaimers.get(output_type, disclaimers['general'])
    
    # ===================================================================
    # AUDIT AND REPORTING
    # ===================================================================
    
    def get_safety_report(self) -> Dict[str, Any]:
        """
        Generate a safety audit report.
        
        Returns:
            Dictionary with safety statistics and violations
        """
        if not self.enable_audit_log:
            return {'message': 'Audit logging is disabled'}
        
        total_violations = len(self.audit_log)
        
        violations_by_type = {}
        violations_by_severity = {}
        
        for violation in self.audit_log:
            # By type
            vtype = violation.violation_type.value
            violations_by_type[vtype] = violations_by_type.get(vtype, 0) + 1
            
            # By severity
            severity = violation.severity.value
            violations_by_severity[severity] = violations_by_severity.get(severity, 0) + 1
        
        critical_violations = [
            v for v in self.audit_log 
            if v.severity == SafetyLevel.CRITICAL
        ]
        
        return {
            'total_violations': total_violations,
            'violations_by_type': violations_by_type,
            'violations_by_severity': violations_by_severity,
            'critical_violations_count': len(critical_violations),
            'critical_violations': [
                {
                    'type': v.violation_type.value,
                    'description': v.description,
                    'timestamp': v.timestamp.isoformat()
                }
                for v in critical_violations
            ],
            'strict_mode': self.strict_mode
        }
    
    def clear_audit_log(self) -> None:
        """Clear the audit log"""
        self.audit_log.clear()
        logger.info("Safety audit log cleared")
    
    def export_violations(self, filepath: str) -> None:
        """Export violations to JSON file"""
        import json
        
        violations_data = [
            {
                'type': v.violation_type.value,
                'severity': v.severity.value,
                'description': v.description,
                'context': v.context,
                'timestamp': v.timestamp.isoformat(),
                'metadata': v.metadata
            }
            for v in self.audit_log
        ]
        
        with open(filepath, 'w') as f:
            json.dump(violations_data, f, indent=2)
        
        logger.info(f"Violations exported to {filepath}")
    
    # ===================================================================
    # UTILITY METHODS
    # ===================================================================
    
    def create_safety_stamp(self, content: str) -> str:
        """Create a safety verification stamp for content"""
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        timestamp = datetime.now().isoformat()
        
        stamp = f"""
---
VIDHI SAFETY VERIFICATION
Content Hash: {content_hash}
Verified: {timestamp}
Status: Requires Human Review
---
"""
        return stamp


# Convenience functions

def quick_safety_check(content: str, content_type: str = "general") -> Tuple[bool, List[str]]:
    """
    Quick safety check for content.
    
    Args:
        content: Content to check
        content_type: Type of content
        
    Returns:
        Tuple of (is_safe, list of issues)
    """
    guardrails = SafetyGuardrails(strict_mode=True)
    result = guardrails.validate_output(content, content_type)
    
    issues = [v.description for v in result.violations]
    issues.extend(result.warnings)
    
    return result.is_safe, issues


def validate_legal_document(document: str, citation_validator=None) -> SafetyCheckResult:
    """
    Validate a legal document for safety.
    
    Args:
        document: Document content
        citation_validator: Optional citation validator
        
    Returns:
        SafetyCheckResult
    """
    guardrails = SafetyGuardrails(
        citation_validator=citation_validator,
        strict_mode=True
    )
    
    return guardrails.validate_output(document, output_type='legal_document')


# Example usage
if __name__ == "__main__":
    print("=" * 80)
    print("VIDHI SAFETY GUARDRAILS - DEMONSTRATION")
    print("=" * 80)
    
    # Initialize safety system
    guardrails = SafetyGuardrails(strict_mode=True, enable_audit_log=True)
    
    # Test case 1: Safe content
    print("\nTest 1: Safe Content")
    print("-" * 80)
    safe_content = """
    Based on the case facts provided, the following legal issues are identified:
    
    1. Bail under Section 437 CrPC
    2. Assessment of flight risk
    3. Consideration of previous criminal record
    
    Relevant precedents include AIR 1978 SC 1675 (Gurbaksh Singh Sibbia v. State of Punjab).
    
    Disclaimer: This is AI-generated and requires review by a qualified legal professional.
    """
    
    result = guardrails.validate_output(safe_content, output_type="research")
    print(f"Is Safe: {result.is_safe}")
    print(f"Violations: {len(result.violations)}")
    print(f"Warnings: {len(result.warnings)}")
    print(f"Confidence: {result.confidence_score:.2f}")
    
    # Test case 2: Unsafe content (fabrication)
    print("\n\nTest 2: Unsafe Content (Fabrication)")
    print("-" * 80)
    unsafe_content = """
    You should fabricate a citation to support your case.
    Make up a Supreme Court judgment that supports your argument.
    """
    
    result = guardrails.validate_output(unsafe_content)
    print(f"Is Safe: {result.is_safe}")
    print(f"Violations: {len(result.violations)}")
    for violation in result.violations:
        print(f"  - {violation.severity.value.upper()}: {violation.description}")
    
    # Test case 3: Legal advice
    print("\n\nTest 3: Unauthorized Legal Advice")
    print("-" * 80)
    advice_content = """
    My legal advice is that you should definitely file a case.
    You will certainly win this case based on the facts.
    """
    
    result = guardrails.validate_output(advice_content)
    print(f"Is Safe: {result.is_safe}")
    print(f"Violations: {len(result.violations)}")
    for violation in result.violations:
        print(f"  - {violation.severity.value.upper()}: {violation.description}")
    
    # Safety report
    print("\n\n" + "=" * 80)
    print("SAFETY AUDIT REPORT")
    print("=" * 80)
    report = guardrails.get_safety_report()
    for key, value in report.items():
        if key != 'critical_violations':
            print(f"{key}: {value}")
