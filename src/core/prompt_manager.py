"""
Prompt Manager for Vidhi Legal Research Platform

This module manages all prompt templates used across different agents in the Vidhi system.
It provides centralized prompt management, versioning, templating, and multilingual support.

Features:
- Centralized prompt storage and retrieval
- Template variable substitution
- Multilingual prompt support (English, Hindi, Regional)
- Prompt versioning and A/B testing
- Agent-specific prompt libraries
- Dynamic prompt generation
- Prompt validation and safety checks

Author: Vidhi Development Team
License: MIT (Educational & Research Use Only)
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from datetime import datetime
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Language(Enum):
    """Supported languages for prompts"""
    ENGLISH = "english"
    HINDI = "hindi"
    TAMIL = "tamil"
    TELUGU = "telugu"
    BENGALI = "bengali"
    MARATHI = "marathi"
    GUJARATI = "gujarati"
    KANNADA = "kannada"
    MALAYALAM = "malayalam"
    PUNJABI = "punjabi"
    URDU = "urdu"


class AgentType(Enum):
    """Types of agents in the system"""
    CASE_FINDER = "case_finder"
    ISSUE_SPOTTER = "issue_spotter"
    LIMITATION_CHECKER = "limitation_checker"
    ARGUMENT_BUILDER = "argument_builder"
    DOC_COMPOSER = "doc_composer"
    COMPLIANCE_GUARD = "compliance_guard"
    AID_CONNECTOR = "aid_connector"
    ORCHESTRATOR = "orchestrator"


class PromptCategory(Enum):
    """Categories of prompts"""
    SYSTEM = "system"
    USER = "user"
    INSTRUCTION = "instruction"
    EXAMPLE = "example"
    VALIDATION = "validation"
    ERROR_HANDLING = "error_handling"


@dataclass
class PromptTemplate:
    """Template for a prompt with metadata"""
    template_id: str
    agent_type: AgentType
    category: PromptCategory
    content: str
    language: Language = Language.ENGLISH
    variables: List[str] = field(default_factory=list)
    version: str = "1.0"
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def render(self, **kwargs) -> str:
        """
        Render the template with provided variables.
        
        Args:
            **kwargs: Variable values to substitute in template
            
        Returns:
            Rendered prompt string
        """
        try:
            # Check for missing required variables
            missing_vars = set(self.variables) - set(kwargs.keys())
            if missing_vars:
                logger.warning(f"Missing variables in template {self.template_id}: {missing_vars}")
            
            # Render template
            rendered = self.content.format(**kwargs)
            return rendered
            
        except KeyError as e:
            logger.error(f"Error rendering template {self.template_id}: Missing variable {e}")
            raise
        except Exception as e:
            logger.error(f"Error rendering template {self.template_id}: {e}")
            raise


class PromptManager:
    """
    Centralized prompt management system for Vidhi.
    
    This manager:
    1. Stores and retrieves prompt templates
    2. Handles prompt versioning
    3. Supports multilingual prompts
    4. Validates prompt safety
    5. Caches frequently used prompts
    6. Provides prompt composition utilities
    """
    
    def __init__(
        self,
        prompts_directory: Optional[Path] = None,
        default_language: Language = Language.ENGLISH,
        enable_cache: bool = True
    ):
        """
        Initialize the Prompt Manager.
        
        Args:
            prompts_directory: Directory containing prompt template files
            default_language: Default language for prompts
            enable_cache: Enable prompt caching
        """
        self.prompts_directory = prompts_directory or Path("./prompts")
        self.default_language = default_language
        self.enable_cache = enable_cache
        
        # Prompt storage
        self.prompts: Dict[str, PromptTemplate] = {}
        self.prompt_cache: Dict[str, str] = {}
        
        # Load built-in prompts
        self._initialize_builtin_prompts()
        
        # Load prompts from directory if exists
        if self.prompts_directory.exists():
            self._load_prompts_from_directory()
        
        logger.info(f"PromptManager initialized with {len(self.prompts)} templates")
    
    def _initialize_builtin_prompts(self):
        """Initialize built-in prompt templates for all agents"""
        
        # ========================================
        # CASE FINDER PROMPTS
        # ========================================
        
        self.register_prompt(PromptTemplate(
            template_id="case_finder_system",
            agent_type=AgentType.CASE_FINDER,
            category=PromptCategory.SYSTEM,
            content="""You are an expert legal researcher specializing in Indian case law. 
Your role is to find relevant judicial precedents from the Supreme Court, High Courts, and tribunals.

Your responsibilities:
1. Search for cases relevant to the legal issues provided
2. Identify landmark judgments and recent precedents
3. Extract accurate citations in standard format (AIR, SCC, SCR)
4. Summarize key legal principles from each case
5. Identify supporting and contrary precedents

CRITICAL RULES:
- NEVER fabricate or hallucinate case citations
- Only cite cases you are confident exist
- Always provide accurate citation formats
- Indicate confidence level for each case
- Flag any uncertainty about case authenticity""",
            variables=[],
            version="1.0",
            description="System prompt for CaseFinder agent"
        ))
        
        self.register_prompt(PromptTemplate(
            template_id="case_finder_search",
            agent_type=AgentType.CASE_FINDER,
            category=PromptCategory.USER,
            content="""Find relevant case laws for the following legal matter:

LEGAL ISSUES:
{identified_issues}

RELEVANT STATUTES:
{relevant_statutes}

RELEVANT SECTIONS:
{relevant_sections}

JURISDICTION: {jurisdiction}
CASE TYPE: {case_type}

Please provide:
1. Top 5-10 most relevant cases with full citations
2. Brief summary of each case (2-3 sentences)
3. Key legal principles established
4. How each case applies to the current matter
5. Any contradictory precedents

Format each case as:
- Citation: [Full citation in standard format]
- Court: [Supreme Court/High Court/Tribunal]
- Year: [Year of judgment]
- Summary: [Brief summary]
- Relevance: [How it applies to current case]
- Confidence: [High/Medium/Low]""",
            variables=["identified_issues", "relevant_statutes", "relevant_sections", "jurisdiction", "case_type"],
            version="1.0",
            description="Search prompt for finding relevant case laws"
        ))
        
        # ========================================
        # ISSUE SPOTTER PROMPTS
        # ========================================
        
        self.register_prompt(PromptTemplate(
            template_id="issue_spotter_system",
            agent_type=AgentType.ISSUE_SPOTTER,
            category=PromptCategory.SYSTEM,
            content="""You are an expert legal analyst specializing in identifying legal issues in Indian law.
Your role is to analyze case facts and identify all relevant legal issues, applicable statutes, and sections.

Your responsibilities:
1. Identify all legal issues present in the case
2. Determine applicable statutes (IPC, CrPC, CPC, special acts)
3. Identify specific sections that apply
4. Categorize issues by area of law
5. Prioritize issues by importance and complexity

Focus on:
- Criminal law (IPC, CrPC, BNSS, BNS)
- Civil law (CPC, Contract Act, Property law)
- Constitutional law (Fundamental Rights, Writs)
- Special statutes (NDPS, SC/ST Act, Consumer Protection, etc.)""",
            variables=[],
            version="1.0",
            description="System prompt for IssueSpotter agent"
        ))
        
        self.register_prompt(PromptTemplate(
            template_id="issue_spotter_analyze",
            agent_type=AgentType.ISSUE_SPOTTER,
            category=PromptCategory.USER,
            content="""Analyze the following case facts and identify all legal issues:

CASE FACTS:
{case_facts}

CASE TYPE: {case_type}
JURISDICTION: {jurisdiction}

Please provide:
1. All identifiable legal issues (list each separately)
2. Applicable statutes for each issue
3. Specific sections that may apply
4. Primary vs. secondary issues
5. Any potential defenses or counter-issues

Format your response as:
LEGAL ISSUES IDENTIFIED:
1. [Issue 1]
   - Applicable Statute: [Statute name]
   - Relevant Sections: [Section numbers]
   - Issue Type: [Criminal/Civil/Constitutional/etc.]
   - Priority: [High/Medium/Low]

2. [Issue 2]
   ...

ADDITIONAL OBSERVATIONS:
[Any important legal observations or potential complications]""",
            variables=["case_facts", "case_type", "jurisdiction"],
            version="1.0",
            description="Issue analysis prompt"
        ))
        
        # ========================================
        # LIMITATION CHECKER PROMPTS
        # ========================================
        
        self.register_prompt(PromptTemplate(
            template_id="limitation_checker_system",
            agent_type=AgentType.LIMITATION_CHECKER,
            category=PromptCategory.SYSTEM,
            content="""You are an expert in the Indian Limitation Act, 1963 and limitation periods for various legal actions.
Your role is to determine whether a case is time-barred and identify applicable limitation provisions.

Your responsibilities:
1. Identify the applicable limitation period for each cause of action
2. Calculate whether the case is within limitation
3. Identify grounds for condonation of delay (Section 5)
4. Analyze sufficient cause and due diligence
5. Check for extension or exclusion of time provisions

Key considerations:
- Section 5: Extension of prescribed period in certain cases
- Section 14: Exclusion of time in certain cases
- Section 18: Effect of acknowledgment in writing
- Articles in the Limitation Act schedule
- Special limitation periods in specific statutes""",
            variables=[],
            version="1.0",
            description="System prompt for LimitationChecker agent"
        ))
        
        self.register_prompt(PromptTemplate(
            template_id="limitation_checker_analyze",
            agent_type=AgentType.LIMITATION_CHECKER,
            category=PromptCategory.USER,
            content="""Analyze the limitation period for the following case:

CASE FACTS:
{case_facts}

CASE TYPE: {case_type}
IDENTIFIED ISSUES: {identified_issues}
RELEVANT STATUTES: {relevant_statutes}

CAUSE OF ACTION DATE: {cause_of_action_date}
FILING DATE: {filing_date}

Please analyze:
1. Applicable limitation period(s)
2. Is the case within limitation?
3. If time-barred, by how many days?
4. Grounds for condonation of delay (if applicable)
5. Sufficient cause arguments
6. Exclusion of time provisions that may apply

Provide your analysis in this format:
LIMITATION ANALYSIS:
- Applicable Article/Provision: [Article number from Limitation Act]
- Prescribed Period: [Number of days/months/years]
- Cause of Action Date: [Date]
- Last Date for Filing: [Date]
- Actual Filing Date: [Date]
- Status: [Within Limitation / Time-barred by X days]
- Condonation Prospects: [Strong/Moderate/Weak]
- Recommended Arguments: [List key arguments]""",
            variables=["case_facts", "case_type", "identified_issues", "relevant_statutes", 
                      "cause_of_action_date", "filing_date"],
            version="1.0",
            description="Limitation analysis prompt"
        ))
        
        # ========================================
        # ARGUMENT BUILDER PROMPTS
        # ========================================
        
        self.register_prompt(PromptTemplate(
            template_id="argument_builder_system",
            agent_type=AgentType.ARGUMENT_BUILDER,
            category=PromptCategory.SYSTEM,
            content="""You are an expert legal advocate skilled in constructing persuasive legal arguments.
Your role is to build strong arguments based on facts, law, and precedents.

Your responsibilities:
1. Construct primary arguments for the case
2. Develop supporting arguments and alternative theories
3. Anticipate counter-arguments from opposing party
4. Build rebuttal arguments
5. Structure arguments logically and persuasively

Argumentation principles:
- Lead with strongest arguments
- Support with relevant case law
- Use statutory provisions effectively
- Address weaknesses proactively
- Maintain ethical boundaries
- Focus on facts and legal principles""",
            variables=[],
            version="1.0",
            description="System prompt for ArgumentBuilder agent"
        ))
        
        self.register_prompt(PromptTemplate(
            template_id="argument_builder_construct",
            agent_type=AgentType.ARGUMENT_BUILDER,
            category=PromptCategory.USER,
            content="""Construct legal arguments for the following case:

CASE FACTS:
{case_facts}

LEGAL ISSUES:
{identified_issues}

RELEVANT CASES:
{relevant_cases}

LIMITATION STATUS:
{limitation_status}

CASE TYPE: {case_type}

Please build:
1. PRIMARY ARGUMENTS (3-5 strongest arguments)
2. SUPPORTING ARGUMENTS (additional points)
3. ANTICIPATED COUNTER-ARGUMENTS (from opposing side)
4. REBUTTAL ARGUMENTS (responses to counter-arguments)
5. ALTERNATIVE THEORIES (if primary arguments fail)

Format each argument as:
ARGUMENT [Number]: [Concise title]
Legal Basis: [Statutory provision or legal principle]
Precedent Support: [Relevant case citations]
Factual Support: [Key facts from case]
Strength: [Strong/Moderate/Weak]
Explanation: [2-3 paragraph detailed explanation]""",
            variables=["case_facts", "identified_issues", "relevant_cases", "limitation_status", "case_type"],
            version="1.0",
            description="Argument construction prompt"
        ))
        
        # ========================================
        # DOC COMPOSER PROMPTS
        # ========================================
        
        self.register_prompt(PromptTemplate(
            template_id="doc_composer_system",
            agent_type=AgentType.DOC_COMPOSER,
            category=PromptCategory.SYSTEM,
            content="""You are an expert legal draftsman specializing in Indian legal documents.
Your role is to draft professional, compliant, and well-structured legal documents.

Your responsibilities:
1. Draft legally sound documents with proper formatting
2. Use appropriate legal terminology and language
3. Include all necessary clauses and sections
4. Ensure court-specific formatting requirements
5. Cite cases and statutes accurately
6. Maintain formal legal style

Drafting principles:
- Use clear, precise language
- Follow standard document structure
- Include all mandatory sections
- Proper numbering and paragraphing
- Accurate citations in standard format
- Professional tone throughout
- Comply with court rules and procedures

CRITICAL: Never fabricate case citations or legal provisions. Only include verified information.""",
            variables=[],
            version="1.0",
            description="System prompt for DocComposer agent"
        ))
        
        self.register_prompt(PromptTemplate(
            template_id="doc_composer_bail_application",
            agent_type=AgentType.DOC_COMPOSER,
            category=PromptCategory.USER,
            content="""Draft a bail application with the following information:

COURT: {court_name}
CASE TYPE: {case_type}
PETITIONER (ACCUSED): {petitioner_name}
RESPONDENT: {respondent_name}

CASE FACTS:
{case_facts}

LEGAL ISSUES:
{identified_issues}

RELEVANT CASES:
{relevant_cases}

ARGUMENTS:
{arguments}

LANGUAGE: {language_preference}

Please draft a complete bail application including:

1. TITLE/HEADING
   - Court name
   - Case number/type
   - Parties' names

2. INTRODUCTION
   - Brief introduction of parties
   - Current custody status

3. FACTS OF THE CASE
   - Chronological narration of facts
   - Date of arrest and allegations
   - Current status

4. LEGAL SUBMISSIONS
   - Grounds for bail under Section 437/439 CrPC
   - Applicable case law with citations
   - Legal arguments

5. PRAYER
   - Relief sought
   - Alternative prayers if applicable

6. VERIFICATION
   - Standard verification clause

7. ANNEXURES LIST
   - List of documents to be annexed

Format the document professionally with proper legal drafting conventions.
Use formal legal language and maintain court-appropriate tone.""",
            variables=["court_name", "case_type", "petitioner_name", "respondent_name", 
                      "case_facts", "identified_issues", "relevant_cases", "arguments", "language_preference"],
            version="1.0",
            description="Bail application drafting prompt"
        ))
        
        self.register_prompt(PromptTemplate(
            template_id="doc_composer_legal_notice",
            agent_type=AgentType.DOC_COMPOSER,
            category=PromptCategory.USER,
            content="""Draft a legal notice with the following information:

CLIENT (SENDER): {petitioner_name}
ADDRESSEE (RECIPIENT): {respondent_name}

CASE FACTS:
{case_facts}

LEGAL ISSUES:
{identified_issues}

RELEVANT LAWS:
{relevant_statutes}

DEMAND/RELIEF SOUGHT:
{relief_sought}

LANGUAGE: {language_preference}

Please draft a complete legal notice including:

1. DATE AND PLACE

2. TO (Addressee details)

3. SUBJECT LINE

4. DEAR SIR/MADAM

5. FACTS
   - Clear chronological narration
   - All relevant details

6. LEGAL POSITION
   - Applicable laws and provisions
   - Rights of the sender
   - Liabilities of the recipient

7. NOTICE AND DEMAND
   - Clear statement of demands
   - Reasonable timeline for compliance (typically 15-30 days)
   - Consequences of non-compliance

8. CLOSING
   - Professional closing

9. SIGNATURE BLOCK
   - Advocate details
   - On behalf of client

Use formal legal language and maintain a firm but professional tone.""",
            variables=["petitioner_name", "respondent_name", "case_facts", "identified_issues", 
                      "relevant_statutes", "relief_sought", "language_preference"],
            version="1.0",
            description="Legal notice drafting prompt"
        ))
        
        # ========================================
        # COMPLIANCE GUARD PROMPTS
        # ========================================
        
        self.register_prompt(PromptTemplate(
            template_id="compliance_guard_system",
            agent_type=AgentType.COMPLIANCE_GUARD,
            category=PromptCategory.SYSTEM,
            content="""You are a legal compliance expert specializing in court rules and filing requirements.
Your role is to validate legal documents for compliance with court rules and procedures.

Your responsibilities:
1. Check document formatting and structure
2. Verify all required sections are present
3. Validate citation formats
4. Check annexure requirements
5. Verify affidavit and verification clauses
6. Ensure court fee compliance
7. Check vakalatnama requirements
8. Validate procedural compliance

Validation areas:
- Document structure and formatting
- Mandatory sections and clauses
- Citation accuracy and format
- Court-specific rules compliance
- Procedural requirements
- Filing checklist items""",
            variables=[],
            version="1.0",
            description="System prompt for ComplianceGuard agent"
        ))
        
        self.register_prompt(PromptTemplate(
            template_id="compliance_guard_validate",
            agent_type=AgentType.COMPLIANCE_GUARD,
            category=PromptCategory.USER,
            content="""Validate the following legal document for compliance:

DOCUMENT:
{drafted_document}

DOCUMENT TYPE: {document_type}
COURT: {court_name}
JURISDICTION: {jurisdiction}

CITATIONS USED:
{citations}

Please check:
1. FORMATTING COMPLIANCE
   - Proper headings and structure
   - Correct numbering and paragraphing
   - Appropriate font and spacing

2. MANDATORY SECTIONS
   - All required sections present
   - Proper order and organization
   - Complete information in each section

3. CITATION VALIDATION
   - Citation format correctness
   - Citation completeness
   - Potential citation errors

4. PROCEDURAL REQUIREMENTS
   - Verification clause present
   - Prayer/relief clearly stated
   - Proper party descriptions

5. COURT-SPECIFIC REQUIREMENTS
   - Court fee calculations
   - Required annexures listed
   - Vakalatnama requirements
   - Any special court rules

Provide your compliance report as:
COMPLIANCE STATUS: [PASS / FAIL / NEEDS REVIEW]

ISSUES FOUND:
[List all compliance issues]

WARNINGS:
[List potential issues or improvements]

CHECKLIST:
☐ Formatting: [Pass/Fail]
☐ Mandatory Sections: [Pass/Fail]
☐ Citations: [Pass/Fail]
☐ Verification: [Pass/Fail]
☐ Prayer: [Pass/Fail]

RECOMMENDATIONS:
[List specific actions to achieve compliance]""",
            variables=["drafted_document", "document_type", "court_name", "jurisdiction", "citations"],
            version="1.0",
            description="Document compliance validation prompt"
        ))
        
        # ========================================
        # AID CONNECTOR PROMPTS
        # ========================================
        
        self.register_prompt(PromptTemplate(
            template_id="aid_connector_system",
            agent_type=AgentType.AID_CONNECTOR,
            category=PromptCategory.SYSTEM,
            content="""You are a legal aid and pro-bono services specialist.
Your role is to identify and recommend legal aid options for eligible individuals.

Your responsibilities:
1. Assess eligibility for legal aid
2. Identify relevant legal aid schemes
3. Recommend pro-bono legal services
4. Provide information on government schemes
5. Suggest NGO and charitable legal services

Legal aid categories:
- State Legal Services Authority (SLSA)
- District Legal Services Authority (DLSA)
- National Legal Services Authority (NALSA)
- Supreme Court Legal Services Committee
- High Court Legal Services Committee
- NGO legal aid programs
- Pro-bono lawyer networks""",
            variables=[],
            version="1.0",
            description="System prompt for AidConnector agent"
        ))
        
        self.register_prompt(PromptTemplate(
            template_id="aid_connector_assess",
            agent_type=AgentType.AID_CONNECTOR,
            category=PromptCategory.USER,
            content="""Assess legal aid eligibility and recommend options:

CASE TYPE: {case_type}
JURISDICTION: {jurisdiction}
URGENCY: {urgency_level}

CASE ISSUES:
{identified_issues}

Please provide:
1. ELIGIBILITY ASSESSMENT
   - Likely eligible based on case type
   - Criteria to verify

2. LEGAL AID SCHEMES
   - State Legal Services Authority
   - District Legal Services Authority
   - Specific schemes for case type

3. PRO-BONO OPTIONS
   - Bar association pro-bono panels
   - NGO legal services
   - Law school legal clinics

4. APPLICATION PROCESS
   - Required documents
   - Where to apply
   - Timeline expectations

5. CONTACT INFORMATION
   - Relevant authority details
   - Application helplines

Format as:
RECOMMENDED OPTIONS:
1. [Option name]
   Type: [Government/NGO/Pro-bono]
   Eligibility: [Criteria]
   How to Apply: [Process]
   Contact: [Details]
   Expected Timeline: [Duration]""",
            variables=["case_type", "jurisdiction", "urgency_level", "identified_issues"],
            version="1.0",
            description="Legal aid assessment prompt"
        ))
        
        # ========================================
        # MULTILINGUAL PROMPTS (HINDI EXAMPLES)
        # ========================================
        
        self.register_prompt(PromptTemplate(
            template_id="issue_spotter_analyze_hindi",
            agent_type=AgentType.ISSUE_SPOTTER,
            category=PromptCategory.USER,
            content="""निम्नलिखित मामले के तथ्यों का विश्लेषण करें और सभी कानूनी मुद्दों की पहचान करें:

मामले के तथ्य:
{case_facts}

मामले का प्रकार: {case_type}
क्षेत्राधिकार: {jurisdiction}

कृपया प्रदान करें:
1. सभी पहचाने गए कानूनी मुद्दे
2. प्रत्येक मुद्दे के लिए लागू क़ानून
3. विशिष्ट धाराएँ जो लागू हो सकती हैं
4. प्राथमिक बनाम द्वितीयक मुद्दे

अपनी प्रतिक्रिया इस प्रकार प्रारूपित करें:
पहचाने गए कानूनी मुद्दे:
1. [मुद्दा 1]
   - लागू क़ानून: [क़ानून का नाम]
   - संबंधित धाराएँ: [धारा संख्या]
   - मुद्दे का प्रकार: [आपराधिक/नागरिक/संवैधानिक/आदि]
   - प्राथमिकता: [उच्च/मध्यम/निम्न]""",
            variables=["case_facts", "case_type", "jurisdiction"],
            version="1.0",
            description="Hindi version of issue analysis prompt",
            language=Language.HINDI
        ))
        
        logger.info("Built-in prompts initialized")
    
    def register_prompt(self, prompt: PromptTemplate) -> None:
        """
        Register a new prompt template.
        
        Args:
            prompt: PromptTemplate to register
        """
        self.prompts[prompt.template_id] = prompt
        logger.debug(f"Registered prompt: {prompt.template_id}")
    
    def get_prompt(
        self,
        template_id: str,
        language: Optional[Language] = None,
        **variables
    ) -> str:
        """
        Get and render a prompt template.
        
        Args:
            template_id: ID of the template to retrieve
            language: Optional language override
            **variables: Variables to substitute in template
            
        Returns:
            Rendered prompt string
        """
        # Check cache first
        cache_key = f"{template_id}_{language or self.default_language.value}_{hash(frozenset(variables.items()))}"
        if self.enable_cache and cache_key in self.prompt_cache:
            logger.debug(f"Cache hit for prompt: {template_id}")
            return self.prompt_cache[cache_key]
        
        # Handle language variants
        if language and language != Language.ENGLISH:
            language_template_id = f"{template_id}_{language.value}"
            if language_template_id in self.prompts:
                template_id = language_template_id
            else:
                logger.warning(f"No {language.value} version of {template_id}, using default")
        
        # Get template
        if template_id not in self.prompts:
            raise ValueError(f"Prompt template not found: {template_id}")
        
        template = self.prompts[template_id]
        
        # Render template
        rendered = template.render(**variables)
        
        # Cache if enabled
        if self.enable_cache:
            self.prompt_cache[cache_key] = rendered
        
        return rendered
    
    def get_agent_prompts(
        self,
        agent_type: AgentType,
        language: Optional[Language] = None
    ) -> Dict[str, PromptTemplate]:
        """
        Get all prompts for a specific agent.
        
        Args:
            agent_type: Type of agent
            language: Optional language filter
            
        Returns:
            Dictionary of prompts for the agent
        """
        agent_prompts = {}
        for template_id, template in self.prompts.items():
            if template.agent_type == agent_type:
                if language is None or template.language == language:
                    agent_prompts[template_id] = template
        
        return agent_prompts
    
    def compose_prompts(
        self,
        template_ids: List[str],
        separator: str = "\n\n",
        **variables
    ) -> str:
        """
        Compose multiple prompts together.
        
        Args:
            template_ids: List of template IDs to compose
            separator: Separator between prompts
            **variables: Variables for all templates
            
        Returns:
            Composed prompt string
        """
        prompts = []
        for template_id in template_ids:
            rendered = self.get_prompt(template_id, **variables)
            prompts.append(rendered)
        
        return separator.join(prompts)
    
    def validate_prompt(self, prompt_text: str) -> Tuple[bool, List[str]]:
        """
        Validate a prompt for safety and compliance.
        
        Args:
            prompt_text: Prompt text to validate
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        # Check for potential safety issues
        forbidden_patterns = [
            r"fabricate",
            r"make up",
            r"hallucinate",
            r"create fake",
            r"invent citation"
        ]
        
        for pattern in forbidden_patterns:
            if re.search(pattern, prompt_text, re.IGNORECASE):
                issues.append(f"Potentially unsafe instruction detected: {pattern}")
        
        # Check length
        if len(prompt_text) < 10:
            issues.append("Prompt is too short")
        
        if len(prompt_text) > 50000:
            issues.append("Prompt exceeds maximum length")
        
        # Check for proper structure
        if not any(char.isalpha() for char in prompt_text):
            issues.append("Prompt contains no alphabetic characters")
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    def save_prompts_to_file(self, filepath: Path) -> None:
        """
        Save all prompts to a YAML file.
        
        Args:
            filepath: Path to save prompts
        """
        prompts_data = []
        for template_id, template in self.prompts.items():
            prompts_data.append({
                'template_id': template.template_id,
                'agent_type': template.agent_type.value,
                'category': template.category.value,
                'content': template.content,
                'language': template.language.value,
                'variables': template.variables,
                'version': template.version,
                'description': template.description,
                'metadata': template.metadata
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(prompts_data, f, allow_unicode=True, default_flow_style=False)
        
        logger.info(f"Saved {len(prompts_data)} prompts to {filepath}")
    
    def _load_prompts_from_directory(self) -> None:
        """Load prompts from YAML files in the prompts directory"""
        yaml_files = list(self.prompts_directory.glob("*.yaml")) + \
                     list(self.prompts_directory.glob("*.yml"))
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    prompts_data = yaml.safe_load(f)
                
                if isinstance(prompts_data, list):
                    for prompt_dict in prompts_data:
                        template = PromptTemplate(
                            template_id=prompt_dict['template_id'],
                            agent_type=AgentType(prompt_dict['agent_type']),
                            category=PromptCategory(prompt_dict['category']),
                            content=prompt_dict['content'],
                            language=Language(prompt_dict.get('language', 'english')),
                            variables=prompt_dict.get('variables', []),
                            version=prompt_dict.get('version', '1.0'),
                            description=prompt_dict.get('description', ''),
                            metadata=prompt_dict.get('metadata', {})
                        )
                        self.register_prompt(template)
                
                logger.info(f"Loaded prompts from {yaml_file}")
                
            except Exception as e:
                logger.error(f"Error loading prompts from {yaml_file}: {e}")
    
    def list_prompts(
        self,
        agent_type: Optional[AgentType] = None,
        language: Optional[Language] = None,
        category: Optional[PromptCategory] = None
    ) -> List[str]:
        """
        List available prompt template IDs with optional filters.
        
        Args:
            agent_type: Filter by agent type
            language: Filter by language
            category: Filter by category
            
        Returns:
            List of template IDs matching filters
        """
        results = []
        for template_id, template in self.prompts.items():
            if agent_type and template.agent_type != agent_type:
                continue
            if language and template.language != language:
                continue
            if category and template.category != category:
                continue
            results.append(template_id)
        
        return sorted(results)
    
    def get_prompt_info(self, template_id: str) -> Optional[Dict]:
        """
        Get information about a prompt template.
        
        Args:
            template_id: Template ID
            
        Returns:
            Dictionary with template information
        """
        if template_id not in self.prompts:
            return None
        
        template = self.prompts[template_id]
        return {
            'template_id': template.template_id,
            'agent_type': template.agent_type.value,
            'category': template.category.value,
            'language': template.language.value,
            'version': template.version,
            'description': template.description,
            'variables': template.variables,
            'content_length': len(template.content),
            'created_at': template.created_at.isoformat()
        }
    
    def create_agent_prompt_set(
        self,
        agent_type: AgentType,
        task_context: Dict[str, Any],
        language: Optional[Language] = None
    ) -> Dict[str, str]:
        """
        Create a complete prompt set for an agent's task.
        
        Args:
            agent_type: Type of agent
            task_context: Context variables for the task
            language: Optional language preference
            
        Returns:
            Dictionary with system and user prompts
        """
        lang = language or self.default_language
        
        # Get system prompt
        system_template_id = f"{agent_type.value}_system"
        system_prompt = self.get_prompt(system_template_id, language=lang)
        
        # Get appropriate user prompt based on agent type and context
        user_template_id = self._select_user_prompt_template(agent_type, task_context)
        user_prompt = self.get_prompt(user_template_id, language=lang, **task_context)
        
        return {
            'system': system_prompt,
            'user': user_prompt
        }
    
    def _select_user_prompt_template(
        self,
        agent_type: AgentType,
        task_context: Dict[str, Any]
    ) -> str:
        """Select appropriate user prompt based on agent and context"""
        
        # Default templates
        default_templates = {
            AgentType.CASE_FINDER: "case_finder_search",
            AgentType.ISSUE_SPOTTER: "issue_spotter_analyze",
            AgentType.LIMITATION_CHECKER: "limitation_checker_analyze",
            AgentType.ARGUMENT_BUILDER: "argument_builder_construct",
            AgentType.COMPLIANCE_GUARD: "compliance_guard_validate",
            AgentType.AID_CONNECTOR: "aid_connector_assess"
        }
        
        # Special handling for DocComposer based on document type
        if agent_type == AgentType.DOC_COMPOSER:
            doc_type = task_context.get('document_type', 'other')
            if doc_type == 'bail_application':
                return "doc_composer_bail_application"
            elif doc_type == 'legal_notice':
                return "doc_composer_legal_notice"
            else:
                return "doc_composer_system"  # Fallback
        
        return default_templates.get(agent_type, f"{agent_type.value}_system")
    
    def clear_cache(self) -> None:
        """Clear the prompt cache"""
        self.prompt_cache.clear()
        logger.info("Prompt cache cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded prompts"""
        stats = {
            'total_prompts': len(self.prompts),
            'cache_size': len(self.prompt_cache) if self.enable_cache else 0,
            'by_agent': {},
            'by_language': {},
            'by_category': {}
        }
        
        for template in self.prompts.values():
            # Count by agent
            agent = template.agent_type.value
            stats['by_agent'][agent] = stats['by_agent'].get(agent, 0) + 1
            
            # Count by language
            lang = template.language.value
            stats['by_language'][lang] = stats['by_language'].get(lang, 0) + 1
            
            # Count by category
            cat = template.category.value
            stats['by_category'][cat] = stats['by_category'].get(cat, 0) + 1
        
        return stats


# Utility functions

def create_default_prompt_manager(prompts_dir: Optional[Path] = None) -> PromptManager:
    """
    Create a PromptManager with default configuration.
    
    Args:
        prompts_dir: Optional custom prompts directory
        
    Returns:
        Configured PromptManager instance
    """
    return PromptManager(
        prompts_directory=prompts_dir,
        default_language=Language.ENGLISH,
        enable_cache=True
    )


# Example usage
if __name__ == "__main__":
    # Create prompt manager
    pm = create_default_prompt_manager()
    
    print("=" * 80)
    print("VIDHI PROMPT MANAGER - DEMONSTRATION")
    print("=" * 80)
    
    # Show statistics
    print("\nPROMPT STATISTICS:")
    stats = pm.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # List prompts by agent
    print("\n" + "=" * 80)
    print("CASE FINDER PROMPTS:")
    case_finder_prompts = pm.list_prompts(agent_type=AgentType.CASE_FINDER)
    for prompt_id in case_finder_prompts:
        info = pm.get_prompt_info(prompt_id)
        print(f"  - {prompt_id}: {info['description']}")
    
    # Example: Get and render a prompt
    print("\n" + "=" * 80)
    print("EXAMPLE: RENDERED ISSUE SPOTTER PROMPT")
    print("=" * 80)
    
    rendered = pm.get_prompt(
        "issue_spotter_analyze",
        case_facts="The accused was arrested for theft of mobile phone worth Rs. 25,000.",
        case_type="criminal",
        jurisdiction="Delhi"
    )
    print(rendered)
    
    # Example: Create complete prompt set for an agent
    print("\n" + "=" * 80)
    print("EXAMPLE: COMPLETE PROMPT SET FOR CASE FINDER")
    print("=" * 80)
    
    prompt_set = pm.create_agent_prompt_set(
        agent_type=AgentType.CASE_FINDER,
        task_context={
            'identified_issues': "Theft of mobile phone, cheating",
            'relevant_statutes': "IPC",
            'relevant_sections': "Section 379, 420",
            'jurisdiction': "Delhi",
            'case_type': "criminal"
        }
    )
    
    print("SYSTEM PROMPT:")
    print(prompt_set['system'][:500] + "...")
    print("\nUSER PROMPT:")
    print(prompt_set['user'][:500] + "...")
    
    # Save prompts to file
    print("\n" + "=" * 80)
    output_file = Path("./vidhi_prompts.yaml")
    pm.save_prompts_to_file(output_file)
    print(f"Prompts saved to: {output_file}")
