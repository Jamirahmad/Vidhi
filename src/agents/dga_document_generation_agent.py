"""
DGA – Document Generation Agent

Responsibilities:
- Generate draft legal documents using approved templates
- Populate drafts using verified inputs only
- NEVER invent facts, citations, or legal opinions
- ALWAYS require human (lawyer) review before use
"""

from typing import Dict, Any, List
from pathlib import Path

from src.agents.base_agent import BaseAgent, AgentResultStatus


TEMPLATE_DIR = Path("src/prompts/templates")


class DocumentGenerationAgent(BaseAgent):
    """
    DGA – Document Generation Agent (DocComposer)
    """

    def __init__(self):
        super().__init__(
            name="DGA_DocumentGenerationAgent",
            requires_human_review=True  # Drafts are never final
        )

    # ------------------------------------------------------------------
    # Input Validation
    # ------------------------------------------------------------------

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        required_fields = [
            "document_type",
            "case_facts",
            "issues",
            "arguments",
            "jurisdiction",
            "court"
        ]

        missing = [f for f in required_fields if f not in input_data]
        if missing:
            raise ValueError(f"Missing required input fields: {missing}")

        if not isinstance(input_data["case_facts"], str):
            raise TypeError("case_facts must be a string")

        if not isinstance(input_data["issues"], list):
            raise TypeError("issues must be a list")

        if not isinstance(input_data["arguments"], list):
            raise TypeError("arguments must be a list")

    # ------------------------------------------------------------------
    # Template Loader
    # ------------------------------------------------------------------

    def _load_template(self, document_type: str) -> str:
        template_map = {
            "bail_application": "bail_application_template.md",
            "legal_notice": "legal_notice_template.md",
            "civil_suit": "civil_suit_template.md",
            "writ_petition": "writ_petition_template.md",
            "affidavit": "affidavit_template.md"
        }

        template_name = template_map.get(document_type.lower())
        if not template_name:
            raise ValueError(f"Unsupported document_type: {document_type}")

        template_path = TEMPLATE_DIR / template_name

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        return template_path.read_text(encoding="utf-8")

    # ------------------------------------------------------------------
    # Core Logic
    # ------------------------------------------------------------------

    def run(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        document_type = input_data["document_type"]
        case_facts = input_data["case_facts"]
        issues = input_data["issues"]
        arguments = input_data["arguments"]
        jurisdiction = input_data["jurisdiction"]
        court = input_data["court"]

        template = self._load_template(document_type)

        # --- Controlled population (NO free-form generation) ---
        populated_document = template

        populated_document = populated_document.replace(
            "{{CASE_FACTS}}",
            case_facts.strip()
        )

        populated_document = populated_document.replace(
            "{{LEGAL_ISSUES}}",
            "\n".join(f"- {issue}" for issue in issues)
        )

        populated_document = populated_document.replace(
            "{{ARGUMENTS}}",
            "\n".join(f"- {arg}" for arg in arguments)
        )

        populated_document = populated_document.replace(
            "{{JURISDICTION}}",
            jurisdiction
        )

        populated_document = populated_document.replace(
            "{{COURT}}",
            court
        )

        # --- Safety Check ---
        if "{{" in populated_document or "}}" in populated_document:
            return {
                "status": AgentResultStatus.UNCERTAIN,
                "draft_document": populated_document,
                "reason": "Unresolved placeholders found in template"
            }

        return {
            "status": AgentResultStatus.SUCCESS,
            "document_type": document_type,
            "draft_document": populated_document,
            "note": "This is a draft document and must be reviewed by a qualified lawyer before use."
        }

    # ------------------------------------------------------------------
    # Output Validation
    # ------------------------------------------------------------------

    def validate_output(self, output_data: Dict[str, Any]) -> None:
        required_fields = [
            "status",
            "draft_document"
        ]

        missing = [f for f in required_fields if f not in output_data]
        if missing:
            raise ValueError(f"Missing required output fields: {missing}")

        if not isinstance(output_data["draft_document"], str):
            raise TypeError("draft_document must be a string")
