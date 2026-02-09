"""
Citation Validator for Indian Legal System

This module validates legal citations from Indian courts including:
- Supreme Court of India
- High Courts
- Tribunals
- Other judicial bodies

It checks citation formats, verifies authenticity, and prevents hallucinated case laws.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CourtType(Enum):
    """Enumeration of Indian court types"""
    SUPREME_COURT = "Supreme Court"
    HIGH_COURT = "High Court"
    DISTRICT_COURT = "District Court"
    TRIBUNAL = "Tribunal"
    CONSUMER_COURT = "Consumer Court"
    UNKNOWN = "Unknown"


class CitationFormat(Enum):
    """Common Indian legal citation formats"""
    AIR = "AIR"  # All India Reporter
    SCC = "SCC"  # Supreme Court Cases
    SCR = "SCR"  # Supreme Court Reports
    SCALE = "SCALE"  # Supreme Court Almanac
    HIGH_COURT = "HC"  # High Court
    TRIBUNAL = "TRIB"  # Tribunal
    UNKNOWN = "UNKNOWN"


@dataclass
class ValidationResult:
    """Result of citation validation"""
    is_valid: bool
    citation: str
    format_type: CitationFormat
    court_type: CourtType
    year: Optional[int] = None
    volume: Optional[str] = None
    page: Optional[str] = None
    errors: List[str] = None
    warnings: List[str] = None
    confidence_score: float = 0.0
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class CitationValidator:
    """
    Validates Indian legal citations for format, authenticity, and completeness.
    
    This validator:
    1. Checks citation format compliance
    2. Validates year, volume, and page numbers
    3. Identifies court type and reporter series
    4. Provides confidence scores
    5. Prevents fake/hallucinated citations (when integrated with vectorstore)
    """
    
    # Citation patterns for different formats
    CITATION_PATTERNS = {
        CitationFormat.AIR: r'AIR\s+(\d{4})\s+(SC|[A-Z]{2,})\s+(\d+)',
        CitationFormat.SCC: r'(\d{4})\s+(\d+)\s+SCC\s+(\d+)',
        CitationFormat.SCR: r'(\d{4})\s+(\d+)\s+SCR\s+(\d+)',
        CitationFormat.SCALE: r'(\d{4})\s+(\d+)\s+SCALE\s+(\d+)',
        CitationFormat.HIGH_COURT: r'(\d{4})\s+(\d+)\s+([A-Z]{2,})\s+(\d+)',
    }
    
    # Court abbreviations
    COURT_ABBREVIATIONS = {
        'SC': CourtType.SUPREME_COURT,
        'Del': CourtType.HIGH_COURT,
        'Bom': CourtType.HIGH_COURT,
        'Cal': CourtType.HIGH_COURT,
        'Mad': CourtType.HIGH_COURT,
        'Ker': CourtType.HIGH_COURT,
        'AP': CourtType.HIGH_COURT,
        'Guj': CourtType.HIGH_COURT,
        'P&H': CourtType.HIGH_COURT,
        'MP': CourtType.HIGH_COURT,
        'Raj': CourtType.HIGH_COURT,
        'Ori': CourtType.HIGH_COURT,
        'Pat': CourtType.HIGH_COURT,
        'All': CourtType.HIGH_COURT,
        'Kant': CourtType.HIGH_COURT,
        'J&K': CourtType.HIGH_COURT,
        'Uttk': CourtType.HIGH_COURT,
        'HP': CourtType.HIGH_COURT,
        'Gauh': CourtType.HIGH_COURT,
        'Sikk': CourtType.HIGH_COURT,
        'Megh': CourtType.HIGH_COURT,
        'Tri': CourtType.HIGH_COURT,
        'Chh': CourtType.HIGH_COURT,
        'Jhar': CourtType.HIGH_COURT,
        'Tel': CourtType.HIGH_COURT,
    }
    
    def __init__(self, vectorstore=None):
        """
        Initialize the citation validator.
        
        Args:
            vectorstore: Optional vectorstore for checking citation existence
        """
        self.vectorstore = vectorstore
        logger.info("CitationValidator initialized")
    
    def validate_citation(self, citation: str) -> ValidationResult:
        """
        Validate a legal citation.
        
        Args:
            citation: Citation string to validate
            
        Returns:
            ValidationResult object with validation details
        """
        citation = citation.strip()
        
        # Try to match against known patterns
        format_type, match_result = self._identify_format(citation)
        
        if format_type == CitationFormat.UNKNOWN:
            return ValidationResult(
                is_valid=False,
                citation=citation,
                format_type=CitationFormat.UNKNOWN,
                court_type=CourtType.UNKNOWN,
                errors=["Citation format not recognized"],
                confidence_score=0.0
            )
        
        # Extract components based on format
        year, volume, page, court_abbr = self._extract_components(match_result, format_type)
        
        # Identify court type
        court_type = self._identify_court(court_abbr, format_type)
        
        # Validate components
        errors, warnings = self._validate_components(year, volume, page)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(errors, warnings, format_type)
        
        is_valid = len(errors) == 0
        
        result = ValidationResult(
            is_valid=is_valid,
            citation=citation,
            format_type=format_type,
            court_type=court_type,
            year=year,
            volume=volume,
            page=page,
            errors=errors,
            warnings=warnings,
            confidence_score=confidence
        )
        
        logger.info(f"Validated citation: {citation} - Valid: {is_valid}")
        return result
    
    def validate_multiple(self, citations: List[str]) -> List[ValidationResult]:
        """
        Validate multiple citations.
        
        Args:
            citations: List of citation strings
            
        Returns:
            List of ValidationResult objects
        """
        results = []
        for citation in citations:
            result = self.validate_citation(citation)
            results.append(result)
        return results
    
    def check_against_database(self, citation: str) -> bool:
        """
        Check if citation exists in the vectorstore/database.
        This prevents hallucinated citations.
        
        Args:
            citation: Citation to check
            
        Returns:
            True if citation exists, False otherwise
        """
        if self.vectorstore is None:
            logger.warning("Vectorstore not configured, cannot verify citation existence")
            return False
        
        try:
            # Query vectorstore for similar citations
            results = self.vectorstore.similarity_search(citation, k=5)
            
            # Check if any result is an exact or close match
            for result in results:
                if self._is_matching_citation(citation, result.page_content):
                    logger.info(f"Citation found in database: {citation}")
                    return True
            
            logger.warning(f"Citation NOT found in database: {citation}")
            return False
            
        except Exception as e:
            logger.error(f"Error checking citation in database: {str(e)}")
            return False
    
    def extract_citations_from_text(self, text: str) -> List[str]:
        """
        Extract all citations from a text document.
        
        Args:
            text: Text containing citations
            
        Returns:
            List of extracted citations
        """
        citations = []
        
        # Try all patterns
        for format_type, pattern in self.CITATION_PATTERNS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                citations.append(match.group(0))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_citations = []
        for citation in citations:
            normalized = citation.strip()
            if normalized not in seen:
                seen.add(normalized)
                unique_citations.append(normalized)
        
        logger.info(f"Extracted {len(unique_citations)} citations from text")
        return unique_citations
    
    def _identify_format(self, citation: str) -> Tuple[CitationFormat, Optional[re.Match]]:
        """Identify citation format by matching patterns"""
        for format_type, pattern in self.CITATION_PATTERNS.items():
            match = re.search(pattern, citation, re.IGNORECASE)
            if match:
                return format_type, match
        return CitationFormat.UNKNOWN, None
    
    def _extract_components(self, match: re.Match, format_type: CitationFormat) -> Tuple:
        """Extract year, volume, page, and court from regex match"""
        if not match:
            return None, None, None, None
        
        groups = match.groups()
        
        if format_type == CitationFormat.AIR:
            year = int(groups[0])
            court_abbr = groups[1]
            page = groups[2]
            volume = None
        elif format_type in [CitationFormat.SCC, CitationFormat.SCR, CitationFormat.SCALE]:
            year = int(groups[0])
            volume = groups[1]
            page = groups[2]
            court_abbr = 'SC'
        elif format_type == CitationFormat.HIGH_COURT:
            year = int(groups[0])
            volume = groups[1]
            court_abbr = groups[2]
            page = groups[3]
        else:
            year, volume, page, court_abbr = None, None, None, None
        
        return year, volume, page, court_abbr
    
    def _identify_court(self, court_abbr: Optional[str], format_type: CitationFormat) -> CourtType:
        """Identify court type from abbreviation"""
        if not court_abbr:
            return CourtType.UNKNOWN
        
        return self.COURT_ABBREVIATIONS.get(court_abbr, CourtType.UNKNOWN)
    
    def _validate_components(self, year: Optional[int], volume: Optional[str], 
                            page: Optional[str]) -> Tuple[List[str], List[str]]:
        """Validate citation components"""
        errors = []
        warnings = []
        
        # Validate year
        if year:
            current_year = 2026  # Update as needed
            if year < 1950:
                warnings.append(f"Year {year} is before 1950 (Indian Constitution)")
            elif year > current_year:
                errors.append(f"Year {year} is in the future")
        else:
            errors.append("Year not found in citation")
        
        # Validate page number
        if page:
            try:
                page_num = int(page)
                if page_num <= 0:
                    errors.append("Page number must be positive")
                elif page_num > 10000:
                    warnings.append(f"Unusually high page number: {page_num}")
            except ValueError:
                errors.append(f"Invalid page number: {page}")
        
        # Validate volume (if present)
        if volume:
            try:
                vol_num = int(volume)
                if vol_num <= 0:
                    errors.append("Volume number must be positive")
                elif vol_num > 500:
                    warnings.append(f"Unusually high volume number: {vol_num}")
            except ValueError:
                # Volume might be alphanumeric, which is okay
                pass
        
        return errors, warnings
    
    def _calculate_confidence(self, errors: List[str], warnings: List[str], 
                             format_type: CitationFormat) -> float:
        """Calculate confidence score for citation validity"""
        if errors:
            return 0.0
        
        confidence = 1.0
        
        # Reduce confidence for warnings
        confidence -= len(warnings) * 0.1
        
        # Known formats have higher confidence
        if format_type in [CitationFormat.AIR, CitationFormat.SCC, CitationFormat.SCR]:
            confidence = min(1.0, confidence + 0.1)
        
        return max(0.0, min(1.0, confidence))
    
    def _is_matching_citation(self, citation1: str, citation2: str) -> bool:
        """Check if two citations refer to the same case"""
        # Normalize both citations
        norm1 = re.sub(r'\s+', ' ', citation1.strip().upper())
        norm2 = re.sub(r'\s+', ' ', citation2.strip().upper())
        
        # Exact match
        if norm1 == norm2:
            return True
        
        # Extract key components and compare
        # This is a simplified check; you might want more sophisticated matching
        pattern = r'(\d{4}).*?(\d+)'
        match1 = re.search(pattern, norm1)
        match2 = re.search(pattern, norm2)
        
        if match1 and match2:
            # Compare year and page number
            return match1.groups() == match2.groups()
        
        return False
    
    def format_citation(self, validation_result: ValidationResult) -> str:
        """
        Format a citation in standard format.
        
        Args:
            validation_result: ValidationResult object
            
        Returns:
            Formatted citation string
        """
        if not validation_result.is_valid:
            return validation_result.citation
        
        year = validation_result.year
        volume = validation_result.volume
        page = validation_result.page
        format_type = validation_result.format_type
        
        if format_type == CitationFormat.AIR:
            court = "SC" if validation_result.court_type == CourtType.SUPREME_COURT else ""
            return f"AIR {year} {court} {page}".strip()
        elif format_type == CitationFormat.SCC:
            return f"{year} {volume} SCC {page}"
        elif format_type == CitationFormat.SCR:
            return f"{year} {volume} SCR {page}"
        else:
            return validation_result.citation
    
    def get_validation_report(self, results: List[ValidationResult]) -> Dict:
        """
        Generate a validation report for multiple citations.
        
        Args:
            results: List of ValidationResult objects
            
        Returns:
            Dictionary with validation statistics
        """
        total = len(results)
        valid = sum(1 for r in results if r.is_valid)
        invalid = total - valid
        
        avg_confidence = sum(r.confidence_score for r in results) / total if total > 0 else 0
        
        format_distribution = {}
        for result in results:
            format_name = result.format_type.value
            format_distribution[format_name] = format_distribution.get(format_name, 0) + 1
        
        court_distribution = {}
        for result in results:
            court_name = result.court_type.value
            court_distribution[court_name] = court_distribution.get(court_name, 0) + 1
        
        all_errors = []
        all_warnings = []
        for result in results:
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
        
        return {
            'total_citations': total,
            'valid_citations': valid,
            'invalid_citations': invalid,
            'validity_rate': f"{(valid/total*100):.2f}%" if total > 0 else "0%",
            'average_confidence': f"{avg_confidence:.2f}",
            'format_distribution': format_distribution,
            'court_distribution': court_distribution,
            'total_errors': len(all_errors),
            'total_warnings': len(all_warnings),
            'unique_errors': list(set(all_errors)),
            'unique_warnings': list(set(all_warnings))
        }


# Utility functions
def validate_citation_batch(citations: List[str], vectorstore=None) -> Tuple[List[ValidationResult], Dict]:
    """
    Validate a batch of citations and return results with report.
    
    Args:
        citations: List of citations to validate
        vectorstore: Optional vectorstore for existence checking
        
    Returns:
        Tuple of (validation_results, report)
    """
    validator = CitationValidator(vectorstore=vectorstore)
    results = validator.validate_multiple(citations)
    report = validator.get_validation_report(results)
    return results, report


def is_valid_citation(citation: str) -> bool:
    """
    Quick check if a citation is valid.
    
    Args:
        citation: Citation string
        
    Returns:
        True if valid, False otherwise
    """
    validator = CitationValidator()
    result = validator.validate_citation(citation)
    return result.is_valid


# Example usage
if __name__ == "__main__":
    # Example citations
    test_citations = [
        "AIR 1973 SC 1461",  # Kesavananda Bharati case
        "2018 10 SCC 1",
        "(2013) 5 SCC 1",
        "AIR 2020 Del 456",
        "2015 3 SCR 789",
        "Invalid Citation Format",
        "AIR 2030 SC 123",  # Future date - should be invalid
    ]
    
    validator = CitationValidator()
    
    print("=" * 80)
    print("CITATION VALIDATION RESULTS")
    print("=" * 80)
    
    results = validator.validate_multiple(test_citations)
    
    for result in results:
        print(f"\nCitation: {result.citation}")
        print(f"Valid: {result.is_valid}")
        print(f"Format: {result.format_type.value}")
        print(f"Court: {result.court_type.value}")
        if result.year:
            print(f"Year: {result.year}")
        if result.volume:
            print(f"Volume: {result.volume}")
        if result.page:
            print(f"Page: {result.page}")
        print(f"Confidence: {result.confidence_score:.2f}")
        
        if result.errors:
            print(f"Errors: {', '.join(result.errors)}")
        if result.warnings:
            print(f"Warnings: {', '.join(result.warnings)}")
    
    print("\n" + "=" * 80)
    print("VALIDATION REPORT")
    print("=" * 80)
    
    report = validator.get_validation_report(results)
    for key, value in report.items():
        print(f"{key}: {value}")
