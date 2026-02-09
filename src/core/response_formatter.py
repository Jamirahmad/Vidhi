"""
Response Formatter for Vidhi Legal Research Platform

This module formats outputs from agents and workflows into structured, readable formats.
It handles legal document formatting, citation formatting, report generation, and multilingual output.

Features:
- Legal document formatting (proper structure, numbering, sections)
- Citation formatting (AIR, SCC, SCR standards)
- Report generation (workflow reports, compliance reports, research summaries)
- Multilingual output formatting
- Multiple output formats (JSON, Markdown, HTML, Plain Text, PDF-ready)
- Court-specific formatting rules
- Structured data serialization

Author: Vidhi Development Team
License: MIT (Educational & Research Use Only)
"""

import json
import re
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OutputFormat(Enum):
    """Supported output formats"""
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    PLAIN_TEXT = "plain_text"
    LEGAL_DOCUMENT = "legal_document"
    PDF_READY = "pdf_ready"


class Language(Enum):
    """Supported languages for formatting"""
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


class DocumentSection(Enum):
    """Standard sections in legal documents"""
    TITLE = "title"
    PARTIES = "parties"
    INTRODUCTION = "introduction"
    FACTS = "facts"
    ISSUES = "issues"
    LEGAL_SUBMISSIONS = "legal_submissions"
    ARGUMENTS = "arguments"
    PRECEDENTS = "precedents"
    PRAYER = "prayer"
    VERIFICATION = "verification"
    ANNEXURES = "annexures"
    SIGNATURE = "signature"


@dataclass
class FormattingOptions:
    """Options for controlling output formatting"""
    output_format: OutputFormat = OutputFormat.PLAIN_TEXT
    language: Language = Language.ENGLISH
    include_metadata: bool = True
    include_timestamps: bool = True
    indent_level: int = 2
    line_width: int = 80
    citation_style: str = "standard"  # standard, detailed, brief
    numbering_style: str = "numeric"  # numeric, alphabetic, roman
    include_toc: bool = False
    page_numbers: bool = False
    header_footer: bool = False
    watermark: Optional[str] = None


class ResponseFormatter:
    """
    Comprehensive response formatter for Vidhi platform.
    
    This formatter:
    1. Formats agent outputs into structured formats
    2. Generates legal documents with proper formatting
    3. Creates reports and summaries
    4. Handles multilingual output
    5. Formats citations according to legal standards
    6. Generates various output formats (JSON, Markdown, HTML, etc.)
    """
    
    def __init__(
        self,
        default_options: Optional[FormattingOptions] = None,
        templates_directory: Optional[Path] = None
    ):
        """
        Initialize the Response Formatter.
        
        Args:
            default_options: Default formatting options
            templates_directory: Directory containing formatting templates
        """
        self.default_options = default_options or FormattingOptions()
        self.templates_directory = templates_directory or Path("./templates")
        
        # Language-specific formatting rules
        self.language_config = self._initialize_language_config()
        
        # Court-specific formatting rules
        self.court_config = self._initialize_court_config()
        
        logger.info("ResponseFormatter initialized")
    
    def _initialize_language_config(self) -> Dict[Language, Dict]:
        """Initialize language-specific formatting configuration"""
        return {
            Language.ENGLISH: {
                'date_format': '%B %d, %Y',
                'number_format': 'numeric',
                'salutation': 'Hon\'ble Court',
                'closing': 'Respectfully submitted',
                'verification_text': 'I, the undersigned, do hereby verify...'
            },
            Language.HINDI: {
                'date_format': '%d %B %Y',
                'number_format': 'devanagari',
                'salutation': 'माननीय न्यायालय',
                'closing': 'सादर प्रस्तुत',
                'verification_text': 'मैं, नीचे हस्ताक्षरकर्ता, एतद्द्वारा सत्यापित करता/करती हूं...'
            }
            # Add more languages as needed
        }
    
    def _initialize_court_config(self) -> Dict[str, Dict]:
        """Initialize court-specific formatting rules"""
        return {
            'Supreme Court': {
                'font': 'Times New Roman',
                'font_size': 12,
                'line_spacing': 1.5,
                'margin': {'top': 1, 'bottom': 1, 'left': 1.5, 'right': 1},
                'page_numbering': 'bottom_center',
                'citation_format': 'SCC'
            },
            'High Court': {
                'font': 'Times New Roman',
                'font_size': 12,
                'line_spacing': 1.5,
                'margin': {'top': 1, 'bottom': 1, 'left': 1.25, 'right': 1},
                'page_numbering': 'bottom_center',
                'citation_format': 'AIR'
            },
            'District Court': {
                'font': 'Arial',
                'font_size': 12,
                'line_spacing': 1.5,
                'margin': {'top': 1, 'bottom': 1, 'left': 1, 'right': 1},
                'page_numbering': 'bottom_right',
                'citation_format': 'local'
            }
        }
    
    # ===================================================================
    # WORKFLOW REPORT FORMATTING
    # ===================================================================
    
    def format_workflow_report(
        self,
        workflow_report: Dict,
        options: Optional[FormattingOptions] = None
    ) -> str:
        """
        Format a complete workflow report.
        
        Args:
            workflow_report: Workflow report from orchestrator
            options: Formatting options
            
        Returns:
            Formatted report string
        """
        opts = options or self.default_options
        
        if opts.output_format == OutputFormat.JSON:
            return self._format_as_json(workflow_report)
        elif opts.output_format == OutputFormat.MARKDOWN:
            return self._format_workflow_as_markdown(workflow_report)
        elif opts.output_format == OutputFormat.HTML:
            return self._format_workflow_as_html(workflow_report)
        else:
            return self._format_workflow_as_text(workflow_report)
    
    def _format_workflow_as_markdown(self, report: Dict) -> str:
        """Format workflow report as Markdown"""
        md_parts = []
        
        # Title
        md_parts.append("# Vidhi Legal Research Report\n")
        md_parts.append(f"**Generated on:** {datetime.now().strftime('%B %d, %Y at %H:%M')}\n")
        md_parts.append("---\n")
        
        # Case Information
        case_info = report.get('case_information', {})
        md_parts.append("## Case Information\n")
        md_parts.append(f"- **Case ID:** {case_info.get('case_id', 'N/A')}")
        md_parts.append(f"- **Case Type:** {case_info.get('case_type', 'N/A')}")
        md_parts.append(f"- **Jurisdiction:** {case_info.get('jurisdiction', 'N/A')}")
        md_parts.append(f"- **Court:** {case_info.get('court_name', 'N/A')}")
        md_parts.append(f"- **Document Type:** {case_info.get('document_type', 'N/A')}\n")
        
        # Workflow Summary
        workflow_summary = report.get('workflow_summary', {})
        md_parts.append("## Workflow Summary\n")
        md_parts.append(f"- **Status:** {workflow_summary.get('status', 'N/A')}")
        md_parts.append(f"- **Started:** {workflow_summary.get('started_at', 'N/A')}")
        md_parts.append(f"- **Completed:** {workflow_summary.get('completed_at', 'N/A')}")
        md_parts.append(f"- **Duration:** {workflow_summary.get('duration_seconds', 'N/A')} seconds\n")
        
        # Research Results
        research = report.get('research_results', {})
        md_parts.append("## Research Results\n")
        
        md_parts.append("### Identified Legal Issues\n")
        issues = research.get('identified_issues', [])
        if issues:
            for i, issue in enumerate(issues, 1):
                md_parts.append(f"{i}. {issue}")
        else:
            md_parts.append("*No issues identified*")
        md_parts.append("")
        
        md_parts.append("### Relevant Case Laws\n")
        md_parts.append(f"**Total Cases Found:** {research.get('relevant_cases_count', 0)}\n")
        
        md_parts.append("### Citations\n")
        citations = research.get('citations', [])
        if citations:
            for citation in citations:
                md_parts.append(f"- {citation}")
        else:
            md_parts.append("*No citations*")
        md_parts.append("")
        
        # Limitation Status
        limitation = research.get('limitation_status', {})
        if limitation:
            md_parts.append("### Limitation Analysis\n")
            md_parts.append(f"- **Status:** {limitation.get('status', 'N/A')}")
            md_parts.append(f"- **Is Time-barred:** {limitation.get('is_time_barred', 'Unknown')}\n")
        
        # Compliance Report
        compliance = report.get('compliance_report', {})
        if compliance:
            md_parts.append("## Compliance Report\n")
            md_parts.append(f"**Overall Status:** {compliance.get('overall_status', 'N/A')}\n")
            
            warnings = compliance.get('warnings', [])
            if warnings:
                md_parts.append("### Warnings\n")
                for warning in warnings:
                    md_parts.append(f"- ⚠️ {warning}")
                md_parts.append("")
        
        # Quality Indicators
        quality = report.get('quality_indicators', {})
        if quality:
            md_parts.append("## Quality Indicators\n")
            errors = quality.get('errors', [])
            warnings = quality.get('warnings', [])
            
            if errors:
                md_parts.append("### Errors\n")
                for error in errors:
                    md_parts.append(f"- ❌ {error}")
                md_parts.append("")
            
            if warnings:
                md_parts.append("### Warnings\n")
                for warning in warnings:
                    md_parts.append(f"- ⚠️ {warning}")
                md_parts.append("")
        
        # Agent Performance
        agent_perf = report.get('agent_performance', {})
        if agent_perf:
            md_parts.append("## Agent Performance\n")
            md_parts.append("| Agent | Success | Execution Time | Errors | Warnings |")
            md_parts.append("|-------|---------|----------------|--------|----------|")
            for agent_name, perf in agent_perf.items():
                success = "✅" if perf.get('success') else "❌"
                exec_time = f"{perf.get('execution_time', 0):.2f}s"
                error_count = len(perf.get('errors', []))
                warning_count = len(perf.get('warnings', []))
                md_parts.append(f"| {agent_name} | {success} | {exec_time} | {error_count} | {warning_count} |")
            md_parts.append("")
        
        # Disclaimer
        disclaimer = report.get('disclaimer', '')
        if disclaimer:
            md_parts.append("## ⚖️ Legal Disclaimer\n")
            md_parts.append(f"*{disclaimer}*\n")
        
        return "\n".join(md_parts)
    
    def _format_workflow_as_text(self, report: Dict) -> str:
        """Format workflow report as plain text"""
        lines = []
        width = 80
        
        # Header
        lines.append("=" * width)
        lines.append("VIDHI LEGAL RESEARCH REPORT".center(width))
        lines.append(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}".center(width))
        lines.append("=" * width)
        lines.append("")
        
        # Case Information
        case_info = report.get('case_information', {})
        lines.append("CASE INFORMATION")
        lines.append("-" * width)
        lines.append(f"Case ID:       {case_info.get('case_id', 'N/A')}")
        lines.append(f"Case Type:     {case_info.get('case_type', 'N/A')}")
        lines.append(f"Jurisdiction:  {case_info.get('jurisdiction', 'N/A')}")
        lines.append(f"Court:         {case_info.get('court_name', 'N/A')}")
        lines.append(f"Document Type: {case_info.get('document_type', 'N/A')}")
        lines.append("")
        
        # Workflow Summary
        workflow = report.get('workflow_summary', {})
        lines.append("WORKFLOW SUMMARY")
        lines.append("-" * width)
        lines.append(f"Status:    {workflow.get('status', 'N/A')}")
        lines.append(f"Started:   {workflow.get('started_at', 'N/A')}")
        lines.append(f"Completed: {workflow.get('completed_at', 'N/A')}")
        lines.append(f"Duration:  {workflow.get('duration_seconds', 'N/A')} seconds")
        lines.append("")
        
        # Research Results
        research = report.get('research_results', {})
        lines.append("RESEARCH RESULTS")
        lines.append("-" * width)
        
        lines.append("\nIdentified Legal Issues:")
        issues = research.get('identified_issues', [])
        if issues:
            for i, issue in enumerate(issues, 1):
                lines.append(f"  {i}. {issue}")
        else:
            lines.append("  (No issues identified)")
        
        lines.append(f"\nRelevant Cases Found: {research.get('relevant_cases_count', 0)}")
        
        lines.append("\nCitations:")
        citations = research.get('citations', [])
        if citations:
            for citation in citations:
                lines.append(f"  - {citation}")
        else:
            lines.append("  (No citations)")
        lines.append("")
        
        # Quality Indicators
        quality = report.get('quality_indicators', {})
        errors = quality.get('errors', [])
        warnings = quality.get('warnings', [])
        
        if errors or warnings:
            lines.append("QUALITY INDICATORS")
            lines.append("-" * width)
            
            if errors:
                lines.append("\nErrors:")
                for error in errors:
                    lines.append(f"  ✗ {error}")
            
            if warnings:
                lines.append("\nWarnings:")
                for warning in warnings:
                    lines.append(f"  ! {warning}")
            lines.append("")
        
        # Disclaimer
        lines.append("=" * width)
        disclaimer = report.get('disclaimer', '')
        if disclaimer:
            lines.append("LEGAL DISCLAIMER")
            lines.append("-" * width)
            lines.append(self._wrap_text(disclaimer, width))
        lines.append("=" * width)
        
        return "\n".join(lines)
    
    def _format_workflow_as_html(self, report: Dict) -> str:
        """Format workflow report as HTML"""
        html_parts = ['<!DOCTYPE html>', '<html>', '<head>']
        html_parts.append('<meta charset="UTF-8">')
        html_parts.append('<title>Vidhi Legal Research Report</title>')
        html_parts.append('<style>')
        html_parts.append(self._get_html_styles())
        html_parts.append('</style>')
        html_parts.append('</head>', '<body>')
        
        # Header
        html_parts.append('<div class="header">')
        html_parts.append('<h1>Vidhi Legal Research Report</h1>')
        html_parts.append(f'<p class="timestamp">Generated: {datetime.now().strftime("%B %d, %Y at %H:%M")}</p>')
        html_parts.append('</div>')
        
        # Case Information
        case_info = report.get('case_information', {})
        html_parts.append('<div class="section">')
        html_parts.append('<h2>Case Information</h2>')
        html_parts.append('<table class="info-table">')
        html_parts.append(f'<tr><th>Case ID</th><td>{case_info.get("case_id", "N/A")}</td></tr>')
        html_parts.append(f'<tr><th>Case Type</th><td>{case_info.get("case_type", "N/A")}</td></tr>')
        html_parts.append(f'<tr><th>Jurisdiction</th><td>{case_info.get("jurisdiction", "N/A")}</td></tr>')
        html_parts.append(f'<tr><th>Court</th><td>{case_info.get("court_name", "N/A")}</td></tr>')
        html_parts.append('</table>')
        html_parts.append('</div>')
        
        # Research Results
        research = report.get('research_results', {})
        html_parts.append('<div class="section">')
        html_parts.append('<h2>Research Results</h2>')
        
        html_parts.append('<h3>Identified Legal Issues</h3>')
        issues = research.get('identified_issues', [])
        if issues:
            html_parts.append('<ul>')
            for issue in issues:
                html_parts.append(f'<li>{issue}</li>')
            html_parts.append('</ul>')
        else:
            html_parts.append('<p class="no-data">No issues identified</p>')
        
        html_parts.append(f'<p><strong>Relevant Cases Found:</strong> {research.get("relevant_cases_count", 0)}</p>')
        
        html_parts.append('<h3>Citations</h3>')
        citations = research.get('citations', [])
        if citations:
            html_parts.append('<ul class="citations">')
            for citation in citations:
                html_parts.append(f'<li>{citation}</li>')
            html_parts.append('</ul>')
        else:
            html_parts.append('<p class="no-data">No citations</p>')
        
        html_parts.append('</div>')
        
        # Footer
        html_parts.append('<div class="footer">')
        disclaimer = report.get('disclaimer', '')
        if disclaimer:
            html_parts.append(f'<p class="disclaimer"><strong>Legal Disclaimer:</strong> {disclaimer}</p>')
        html_parts.append('</div>')
        
        html_parts.append('</body>', '</html>')
        
        return '\n'.join(html_parts)
    
    def _format_as_json(self, data: Any) -> str:
        """Format data as JSON"""
        return json.dumps(data, indent=2, default=str, ensure_ascii=False)
    
    # ===================================================================
    # LEGAL DOCUMENT FORMATTING
    # ===================================================================
    
    def format_legal_document(
        self,
        document_content: str,
        document_type: str,
        case_info: Dict,
        options: Optional[FormattingOptions] = None
    ) -> str:
        """
        Format a legal document with proper structure and formatting.
        
        Args:
            document_content: Raw document content
            document_type: Type of document (bail_application, legal_notice, etc.)
            case_info: Case information dictionary
            options: Formatting options
            
        Returns:
            Formatted legal document
        """
        opts = options or self.default_options
        
        if document_type == 'bail_application':
            return self._format_bail_application(document_content, case_info, opts)
        elif document_type == 'legal_notice':
            return self._format_legal_notice(document_content, case_info, opts)
        elif document_type == 'writ_petition':
            return self._format_writ_petition(document_content, case_info, opts)
        else:
            return self._format_generic_legal_document(document_content, case_info, opts)
    
    def _format_bail_application(
        self,
        content: str,
        case_info: Dict,
        options: FormattingOptions
    ) -> str:
        """Format a bail application with proper legal structure"""
        lines = []
        width = 80
        
        # Title and Court
        lines.append("")
        court_name = case_info.get('court_name', 'District Court')
        lines.append(court_name.upper().center(width))
        lines.append("")
        lines.append("CRIMINAL MISCELLANEOUS PETITION NO. _____ OF 2026".center(width))
        lines.append("")
        lines.append("UNDER SECTION 437/439 Cr.P.C.".center(width))
        lines.append("")
        lines.append("=" * width)
        lines.append("")
        
        # Parties
        petitioner = case_info.get('petitioner_name', '[Petitioner Name]')
        respondent = case_info.get('respondent_name', '[Respondent Name]')
        
        lines.append(f"IN THE MATTER OF:")
        lines.append("")
        lines.append(f"{petitioner}".rjust(60))
        lines.append("...Petitioner/Accused".rjust(60))
        lines.append("")
        lines.append("VERSUS".center(width))
        lines.append("")
        lines.append(f"{respondent}".rjust(60))
        lines.append("...Respondent".rjust(60))
        lines.append("")
        lines.append("=" * width)
        lines.append("")
        
        # Main Content
        lines.append("APPLICATION FOR BAIL UNDER SECTION 437/439 Cr.P.C.")
        lines.append("")
        lines.append("-" * width)
        lines.append("")
        
        # Add the actual content
        lines.append(content)
        lines.append("")
        
        # Verification
        lines.append("-" * width)
        lines.append("VERIFICATION")
        lines.append("-" * width)
        lines.append("")
        verification = """I, the undersigned, do hereby verify that the contents of the above petition are true and correct to the best of my knowledge and belief, and nothing material has been concealed therefrom."""
        lines.append(self._wrap_text(verification, width - 4, indent=4))
        lines.append("")
        lines.append("")
        lines.append("Date: _______________".ljust(40) + "Signature of Petitioner".rjust(40))
        lines.append("Place: _______________".ljust(40) + "Through Advocate".rjust(40))
        lines.append("")
        
        return "\n".join(lines)
    
    def _format_legal_notice(
        self,
        content: str,
        case_info: Dict,
        options: FormattingOptions
    ) -> str:
        """Format a legal notice"""
        lines = []
        width = 80
        
        # Header
        lines.append("")
        lines.append("LEGAL NOTICE")
        lines.append("")
        lines.append(f"Date: {datetime.now().strftime('%B %d, %Y')}")
        lines.append("")
        lines.append("-" * width)
        lines.append("")
        
        # To section
        addressee = case_info.get('respondent_name', '[Addressee Name]')
        lines.append("TO,")
        lines.append(addressee)
        lines.append("[Address]")
        lines.append("")
        
        # Subject
        lines.append(f"SUBJECT: Legal Notice under Section ___")
        lines.append("")
        lines.append("Dear Sir/Madam,")
        lines.append("")
        
        # Main content
        lines.append(content)
        lines.append("")
        
        # Closing
        lines.append("This notice is being sent to you as a final opportunity to resolve this matter amicably.")
        lines.append("")
        lines.append("If you fail to comply with the above demands within 15 days from the receipt of this notice,")
        lines.append("my client shall be constrained to initiate appropriate legal proceedings against you,")
        lines.append("which shall be at your risk as to costs and consequences.")
        lines.append("")
        lines.append("Yours faithfully,")
        lines.append("")
        lines.append("[Advocate Name]")
        lines.append("[Enrollment Number]")
        sender = case_info.get('petitioner_name', '[Client Name]')
        lines.append(f"On behalf of: {sender}")
        lines.append("")
        
        return "\n".join(lines)
    
    def _format_writ_petition(
        self,
        content: str,
        case_info: Dict,
        options: FormattingOptions
    ) -> str:
        """Format a writ petition"""
        lines = []
        width = 80
        
        # Title
        lines.append("")
        court = case_info.get('court_name', 'High Court')
        lines.append(f"IN THE {court.upper()}".center(width))
        lines.append("AT [PLACE]".center(width))
        lines.append("")
        lines.append("WRIT PETITION NO. _____ OF 2026".center(width))
        lines.append("(UNDER ARTICLE 226/227/32 OF THE CONSTITUTION OF INDIA)".center(width))
        lines.append("")
        lines.append("=" * width)
        lines.append("")
        
        # Parties
        lines.append("IN THE MATTER OF:")
        lines.append("")
        petitioner = case_info.get('petitioner_name', '[Petitioner Name]')
        lines.append(f"{petitioner}".rjust(60))
        lines.append("...Petitioner".rjust(60))
        lines.append("")
        lines.append("VERSUS".center(width))
        lines.append("")
        respondent = case_info.get('respondent_name', '[Respondent Name]')
        lines.append(f"{respondent}".rjust(60))
        lines.append("...Respondent".rjust(60))
        lines.append("")
        lines.append("=" * width)
        lines.append("")
        
        # Content
        lines.append(content)
        lines.append("")
        
        # Prayer
        lines.append("-" * width)
        lines.append("PRAYER")
        lines.append("-" * width)
        lines.append("")
        lines.append("In light of the facts stated above and the legal provisions cited,")
        lines.append("it is most respectfully prayed that this Hon'ble Court may be pleased to:")
        lines.append("")
        lines.append("a) Issue a writ of [mandamus/certiorari/prohibition/quo warranto/habeas corpus];")
        lines.append("")
        lines.append("b) Pass any other order as this Hon'ble Court may deem fit in the interest of justice.")
        lines.append("")
        
        # Verification
        lines.append("-" * width)
        lines.append("VERIFICATION")
        lines.append("-" * width)
        lines.append("")
        verification = """I, the Petitioner, do hereby verify that the contents of the above petition are true and correct to the best of my knowledge and belief based on personal knowledge and legal advice."""
        lines.append(self._wrap_text(verification, width - 4, indent=4))
        lines.append("")
        lines.append("Date: _______________".ljust(40) + "Signature of Petitioner".rjust(40))
        lines.append("")
        
        return "\n".join(lines)
    
    def _format_generic_legal_document(
        self,
        content: str,
        case_info: Dict,
        options: FormattingOptions
    ) -> str:
        """Format a generic legal document"""
        lines = []
        width = 80
        
        lines.append("")
        lines.append("=" * width)
        lines.append(f"Case ID: {case_info.get('case_id', 'N/A')}")
        lines.append(f"Document Date: {datetime.now().strftime('%B %d, %Y')}")
        lines.append("=" * width)
        lines.append("")
        lines.append(content)
        lines.append("")
        
        return "\n".join(lines)
    
    # ===================================================================
    # CITATION FORMATTING
    # ===================================================================
    
    def format_citation(
        self,
        citation: str,
        style: str = "standard"
    ) -> str:
        """
        Format a legal citation according to specified style.
        
        Args:
            citation: Citation string
            style: Citation style (standard, detailed, brief)
            
        Returns:
            Formatted citation
        """
        if style == "detailed":
            # Add more context to citation
            return f"[{citation}]"
        elif style == "brief":
            # Abbreviated format
            return citation.replace("All India Reporter", "AIR")
        else:
            # Standard format
            return citation
    
    def format_case_summary(
        self,
        case_data: Dict,
        include_full_text: bool = False
    ) -> str:
        """
        Format a case law summary.
        
        Args:
            case_data: Case information dictionary
            include_full_text: Whether to include full case text
            
        Returns:
            Formatted case summary
        """
        lines = []
        
        # Citation
        citation = case_data.get('citation', 'Citation not available')
        lines.append(f"**Citation:** {citation}")
        lines.append("")
        
        # Court and Year
        court = case_data.get('court', 'Court not specified')
        year = case_data.get('year', 'Year not specified')
        lines.append(f"**Court:** {court}")
        lines.append(f"**Year:** {year}")
        lines.append("")
        
        # Summary
        summary = case_data.get('summary', 'Summary not available')
        lines.append("**Summary:**")
        lines.append(summary)
        lines.append("")
        
        # Key principles
        principles = case_data.get('key_principles', [])
        if principles:
            lines.append("**Key Legal Principles:**")
            for i, principle in enumerate(principles, 1):
                lines.append(f"{i}. {principle}")
            lines.append("")
        
        # Relevance
        relevance = case_data.get('relevance', '')
        if relevance:
            lines.append("**Relevance to Current Case:**")
            lines.append(relevance)
            lines.append("")
        
        return "\n".join(lines)
    
    def format_citation_list(
        self,
        citations: List[str],
        grouped_by_court: bool = False
    ) -> str:
        """
        Format a list of citations.
        
        Args:
            citations: List of citation strings
            grouped_by_court: Whether to group by court type
            
        Returns:
            Formatted citation list
        """
        if not citations:
            return "No citations available"
        
        lines = []
        lines.append("CITATIONS:")
        lines.append("-" * 40)
        
        if grouped_by_court:
            # Group citations by court
            sc_citations = [c for c in citations if 'SC' in c]
            hc_citations = [c for c in citations if any(x in c for x in ['Del', 'Bom', 'Cal', 'Mad'])]
            other_citations = [c for c in citations if c not in sc_citations and c not in hc_citations]
            
            if sc_citations:
                lines.append("\nSupreme Court:")
                for citation in sc_citations:
                    lines.append(f"  • {citation}")
            
            if hc_citations:
                lines.append("\nHigh Courts:")
                for citation in hc_citations:
                    lines.append(f"  • {citation}")
            
            if other_citations:
                lines.append("\nOther Courts:")
                for citation in other_citations:
                    lines.append(f"  • {citation}")
        else:
            # Simple list
            for i, citation in enumerate(citations, 1):
                lines.append(f"{i}. {citation}")
        
        return "\n".join(lines)
    
    # ===================================================================
    # COMPLIANCE REPORT FORMATTING
    # ===================================================================
    
    def format_compliance_report(
        self,
        compliance_data: Dict,
        options: Optional[FormattingOptions] = None
    ) -> str:
        """
        Format a compliance validation report.
        
        Args:
            compliance_data: Compliance report data
            options: Formatting options
            
        Returns:
            Formatted compliance report
        """
        lines = []
        width = 80
        
        lines.append("=" * width)
        lines.append("COMPLIANCE VALIDATION REPORT".center(width))
        lines.append("=" * width)
        lines.append("")
        
        # Overall status
        overall_status = compliance_data.get('overall_status', 'Unknown')
        status_symbol = "✓" if overall_status == "PASS" else "✗"
        lines.append(f"Overall Status: {status_symbol} {overall_status}")
        lines.append("")
        
        # Checklist
        lines.append("COMPLIANCE CHECKLIST:")
        lines.append("-" * width)
        checklist = compliance_data.get('checklist', {})
        for item, status in checklist.items():
            symbol = "☑" if status == "Pass" else "☐"
            lines.append(f"{symbol} {item}: {status}")
        lines.append("")
        
        # Issues
        issues = compliance_data.get('issues', [])
        if issues:
            lines.append("ISSUES FOUND:")
            lines.append("-" * width)
            for i, issue in enumerate(issues, 1):
                lines.append(f"{i}. {issue}")
            lines.append("")
        
        # Warnings
        warnings = compliance_data.get('warnings', [])
        if warnings:
            lines.append("WARNINGS:")
            lines.append("-" * width)
            for i, warning in enumerate(warnings, 1):
                lines.append(f"{i}. ⚠ {warning}")
            lines.append("")
        
        # Recommendations
        recommendations = compliance_data.get('recommendations', [])
        if recommendations:
            lines.append("RECOMMENDATIONS:")
            lines.append("-" * width)
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
        
        lines.append("=" * width)
        
        return "\n".join(lines)
    
    # ===================================================================
    # ARGUMENT FORMATTING
    # ===================================================================
    
    def format_legal_argument(
        self,
        argument_data: Dict,
        numbering: bool = True
    ) -> str:
        """
        Format a legal argument with proper structure.
        
        Args:
            argument_data: Argument data dictionary
            numbering: Whether to include numbering
            
        Returns:
            Formatted argument
        """
        lines = []
        
        # Argument title
        title = argument_data.get('title', 'Untitled Argument')
        if numbering:
            number = argument_data.get('number', 1)
            lines.append(f"ARGUMENT {number}: {title.upper()}")
        else:
            lines.append(title.upper())
        lines.append("")
        
        # Legal basis
        legal_basis = argument_data.get('legal_basis', '')
        if legal_basis:
            lines.append(f"Legal Basis: {legal_basis}")
            lines.append("")
        
        # Precedent support
        precedents = argument_data.get('precedent_support', [])
        if precedents:
            lines.append("Precedent Support:")
            for precedent in precedents:
                lines.append(f"  • {precedent}")
            lines.append("")
        
        # Factual support
        factual = argument_data.get('factual_support', '')
        if factual:
            lines.append("Factual Support:")
            lines.append(self._wrap_text(factual, 76, indent=2))
            lines.append("")
        
        # Main explanation
        explanation = argument_data.get('explanation', '')
        if explanation:
            lines.append("Explanation:")
            lines.append(self._wrap_text(explanation, 76, indent=2))
            lines.append("")
        
        # Strength indicator
        strength = argument_data.get('strength', '')
        if strength:
            lines.append(f"Strength: {strength}")
            lines.append("")
        
        return "\n".join(lines)
    
    # ===================================================================
    # UTILITY METHODS
    # ===================================================================
    
    def _wrap_text(self, text: str, width: int = 80, indent: int = 0) -> str:
        """Wrap text to specified width with optional indentation"""
        import textwrap
        
        wrapped = textwrap.fill(
            text,
            width=width,
            initial_indent=' ' * indent,
            subsequent_indent=' ' * indent
        )
        return wrapped
    
    def _get_html_styles(self) -> str:
        """Get CSS styles for HTML formatting"""
        return """
        body {
            font-family: 'Times New Roman', serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }
        .header {
            text-align: center;
            border-bottom: 3px solid #333;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0;
            color: #1a1a1a;
        }
        .timestamp {
            color: #666;
            font-size: 14px;
        }
        .section {
            margin-bottom: 30px;
        }
        h2 {
            color: #1a1a1a;
            border-bottom: 2px solid #ddd;
            padding-bottom: 10px;
        }
        h3 {
            color: #333;
            margin-top: 20px;
        }
        .info-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .info-table th {
            background-color: #f5f5f5;
            text-align: left;
            padding: 10px;
            width: 30%;
            border: 1px solid #ddd;
        }
        .info-table td {
            padding: 10px;
            border: 1px solid #ddd;
        }
        .citations {
            background-color: #f9f9f9;
            padding: 15px;
            border-left: 4px solid #333;
        }
        .no-data {
            font-style: italic;
            color: #999;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #333;
        }
        .disclaimer {
            background-color: #fff9e6;
            border: 1px solid #e6d700;
            padding: 15px;
            border-radius: 5px;
            font-size: 14px;
        }
        """
    
    def save_to_file(
        self,
        content: str,
        filepath: Path,
        encoding: str = 'utf-8'
    ) -> None:
        """
        Save formatted content to file.
        
        Args:
            content: Content to save
            filepath: Path to save file
            encoding: File encoding
        """
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding=encoding) as f:
                f.write(content)
            logger.info(f"Content saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise


# Convenience functions

def format_quick_report(workflow_report: Dict, format_type: str = "markdown") -> str:
    """
    Quick formatting of workflow report.
    
    Args:
        workflow_report: Report from orchestrator
        format_type: Output format (json, markdown, html, text)
        
    Returns:
        Formatted report
    """
    formatter = ResponseFormatter()
    
    format_map = {
        'json': OutputFormat.JSON,
        'markdown': OutputFormat.MARKDOWN,
        'html': OutputFormat.HTML,
        'text': OutputFormat.PLAIN_TEXT
    }
    
    options = FormattingOptions(
        output_format=format_map.get(format_type, OutputFormat.PLAIN_TEXT)
    )
    
    return formatter.format_workflow_report(workflow_report, options)


# Example usage
if __name__ == "__main__":
    # Initialize formatter
    formatter = ResponseFormatter()
    
    print("=" * 80)
    print("VIDHI RESPONSE FORMATTER - DEMONSTRATION")
    print("=" * 80)
    
    # Example workflow report
    sample_report = {
        'case_information': {
            'case_id': 'BAIL_001_2026',
            'case_type': 'criminal',
            'jurisdiction': 'Delhi',
            'court_name': 'Saket District Court',
            'document_type': 'bail_application'
        },
        'workflow_summary': {
            'status': 'completed',
            'started_at': '2026-02-09T10:00:00',
            'completed_at': '2026-02-09T10:05:30',
            'duration_seconds': 330
        },
        'research_results': {
            'identified_issues': [
                'Bail under Section 437 CrPC',
                'No previous criminal record',
                'Willingness to cooperate'
            ],
            'relevant_cases_count': 5,
            'citations': [
                'AIR 1978 SC 1675',
                '2018 10 SCC 1',
                'AIR 2020 Del 456'
            ]
        },
        'quality_indicators': {
            'errors': [],
            'warnings': ['Citation AIR 2020 Del 456 not found in database']
        },
        'disclaimer': 'This document is AI-generated and must be reviewed by a qualified legal professional.'
    }
    
    # Format as Markdown
    print("\n" + "=" * 80)
    print("MARKDOWN FORMAT")
    print("=" * 80)
    markdown_output = formatter.format_workflow_report(
        sample_report,
        FormattingOptions(output_format=OutputFormat.MARKDOWN)
    )
    print(markdown_output)
    
    # Format as Plain Text
    print("\n" + "=" * 80)
    print("PLAIN TEXT FORMAT")
    print("=" * 80)
    text_output = formatter.format_workflow_report(
        sample_report,
        FormattingOptions(output_format=OutputFormat.PLAIN_TEXT)
    )
    print(text_output)
    
    # Format bail application
    print("\n" + "=" * 80)
    print("BAIL APPLICATION FORMAT")
    print("=" * 80)
    
    bail_content = """
The Petitioner most respectfully submits as follows:

1. That the Petitioner was arrested on 15th January 2026 under Section 420 IPC.

2. That the Petitioner is a first-time offender with no previous criminal record.

3. That the Petitioner is willing to cooperate fully with the investigation.

4. That the Petitioner has deep roots in the community and is not a flight risk.

5. That under the circumstances, the Petitioner deserves to be released on bail.
"""
    
    bail_doc = formatter.format_legal_document(
        bail_content,
        'bail_application',
        sample_report['case_information']
    )
    print(bail_doc[:1000] + "\n... (truncated)")
