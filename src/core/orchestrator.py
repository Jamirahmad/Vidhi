"""
Legal Orchestrator - Central Workflow Manager for Vidhi

This is the core orchestration engine that coordinates all agents in the Vidhi platform.
It manages workflows for legal research, document drafting, and compliance validation.

Agents Managed:
- CaseFinder: Searches relevant case laws and judicial precedents
- IssueSpotter: Identifies legal issues, IPC/CrPC/CPC sections
- LimitationChecker: Checks limitation periods and time-bar applicability
- ArgumentBuilder: Builds supporting and counter-arguments
- DocComposer: Drafts legal documents
- ComplianceGuard: Validates filings, annexures, formatting
- AidConnector: Suggests legal aid/pro-bono options

Author: Vidhi Development Team
License: MIT (Educational & Research Use Only)
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import asyncio
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CaseType(Enum):
    """Types of legal cases supported"""
    CIVIL = "civil"
    CRIMINAL = "criminal"
    TRIBUNAL = "tribunal"
    CONSUMER = "consumer"
    FAMILY = "family"
    CONSTITUTIONAL = "constitutional"
    WRIT = "writ"
    UNKNOWN = "unknown"


class WorkflowStage(Enum):
    """Stages in the legal research and drafting workflow"""
    INITIALIZATION = "initialization"
    ISSUE_IDENTIFICATION = "issue_identification"
    CASE_RESEARCH = "case_research"
    LIMITATION_CHECK = "limitation_check"
    ARGUMENT_BUILDING = "argument_building"
    DOCUMENT_DRAFTING = "document_drafting"
    COMPLIANCE_VALIDATION = "compliance_validation"
    AID_ASSESSMENT = "aid_assessment"
    HUMAN_REVIEW = "human_review"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentType(Enum):
    """Types of legal documents that can be drafted"""
    BAIL_APPLICATION = "bail_application"
    CIVIL_SUIT = "civil_suit"
    WRIT_PETITION = "writ_petition"
    LEGAL_NOTICE = "legal_notice"
    AFFIDAVIT = "affidavit"
    REPLY = "reply"
    VAKALATNAMA = "vakalatnama"
    APPEAL = "appeal"
    REVISION_PETITION = "revision_petition"
    COMPLAINT = "complaint"
    OTHER = "other"


@dataclass
class CaseContext:
    """Container for case-related information and context"""
    case_id: str
    case_type: CaseType
    case_facts: str
    jurisdiction: str  # State/Court
    court_name: Optional[str] = None
    petitioner_name: Optional[str] = None
    respondent_name: Optional[str] = None
    relevant_statutes: List[str] = field(default_factory=list)
    relevant_sections: List[str] = field(default_factory=list)
    document_type: Optional[DocumentType] = None
    urgency_level: str = "normal"  # normal, urgent, extremely_urgent
    language_preference: str = "english"  # english, hindi, regional
    additional_context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AgentResult:
    """Result from an individual agent's execution"""
    agent_name: str
    success: bool
    data: Dict[str, Any]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowState:
    """State management for the entire workflow"""
    case_context: CaseContext
    current_stage: WorkflowStage
    agent_results: Dict[str, AgentResult] = field(default_factory=dict)
    identified_issues: List[str] = field(default_factory=list)
    relevant_cases: List[Dict] = field(default_factory=list)
    limitation_status: Optional[Dict] = None
    arguments: Optional[Dict] = None
    drafted_document: Optional[str] = None
    compliance_report: Optional[Dict] = None
    aid_recommendations: List[Dict] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)
    workflow_errors: List[str] = field(default_factory=list)
    workflow_warnings: List[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class LegalOrchestrator:
    """
    Central orchestrator for managing legal research and document automation workflows.
    
    This orchestrator:
    1. Manages multi-agent coordination
    2. Maintains workflow state
    3. Handles error recovery
    4. Ensures human verification checkpoints
    5. Validates all outputs
    6. Provides comprehensive logging
    """
    
    def __init__(
        self,
        vectorstore=None,
        config: Optional[Dict] = None,
        enable_cache: bool = True
    ):
        """
        Initialize the Legal Orchestrator.
        
        Args:
            vectorstore: ChromaDB/FAISS vectorstore for case law retrieval
            config: Configuration dictionary for agents and settings
            enable_cache: Enable caching of agent results
        """
        self.vectorstore = vectorstore
        self.config = config or self._get_default_config()
        self.enable_cache = enable_cache
        
        # Initialize agents (lazy loading)
        self.agents = {}
        self._agent_initialized = {}
        
        # Workflow state cache
        self.active_workflows: Dict[str, WorkflowState] = {}
        
        # Performance tracking
        self.metrics = {
            'total_workflows': 0,
            'successful_workflows': 0,
            'failed_workflows': 0,
            'average_execution_time': 0.0
        }
        
        logger.info("LegalOrchestrator initialized successfully")
    
    def _get_default_config(self) -> Dict:
        """Get default configuration for the orchestrator"""
        return {
            'max_retries': 3,
            'timeout_seconds': 300,
            'require_human_verification': True,
            'enable_citation_validation': True,
            'enable_compliance_check': True,
            'enable_aid_suggestions': True,
            'parallel_execution': False,
            'save_intermediate_results': True,
            'output_directory': './outputs'
        }
    
    def _initialize_agent(self, agent_name: str) -> Any:
        """
        Lazy initialization of agents to save resources.
        
        Args:
            agent_name: Name of the agent to initialize
            
        Returns:
            Initialized agent instance
        """
        if agent_name in self._agent_initialized and self._agent_initialized[agent_name]:
            return self.agents[agent_name]
        
        logger.info(f"Initializing agent: {agent_name}")
        
        try:
            # Import and initialize agent based on name
            # This is a placeholder - actual implementation will import real agent classes
            if agent_name == "CaseFinder":
                from src.agents.case_finder import CaseFinder
                agent = CaseFinder(vectorstore=self.vectorstore)
            elif agent_name == "IssueSpotter":
                from src.agents.issue_spotter import IssueSpotter
                agent = IssueSpotter()
            elif agent_name == "LimitationChecker":
                from src.agents.limitation_checker import LimitationChecker
                agent = LimitationChecker()
            elif agent_name == "ArgumentBuilder":
                from src.agents.argument_builder import ArgumentBuilder
                agent = ArgumentBuilder()
            elif agent_name == "DocComposer":
                from src.agents.doc_composer import DocComposer
                agent = DocComposer()
            elif agent_name == "ComplianceGuard":
                from src.agents.compliance_guard import ComplianceGuard
                agent = ComplianceGuard()
            elif agent_name == "AidConnector":
                from src.agents.aid_connector import AidConnector
                agent = AidConnector()
            else:
                raise ValueError(f"Unknown agent: {agent_name}")
            
            self.agents[agent_name] = agent
            self._agent_initialized[agent_name] = True
            logger.info(f"Agent {agent_name} initialized successfully")
            return agent
            
        except ImportError as e:
            logger.warning(f"Agent {agent_name} not yet implemented: {e}")
            # Return mock agent for development
            return self._create_mock_agent(agent_name)
        except Exception as e:
            logger.error(f"Error initializing agent {agent_name}: {e}")
            raise
    
    def _create_mock_agent(self, agent_name: str) -> Any:
        """Create a mock agent for development/testing"""
        class MockAgent:
            def __init__(self, name):
                self.name = name
            
            def execute(self, *args, **kwargs):
                logger.warning(f"Mock execution for {self.name}")
                return {
                    'success': True,
                    'data': {'message': f'Mock result from {self.name}'},
                    'mock': True
                }
        
        return MockAgent(agent_name)
    
    async def start_workflow(
        self,
        case_context: CaseContext,
        workflow_type: str = "full"
    ) -> WorkflowState:
        """
        Start a complete legal research and drafting workflow.
        
        Args:
            case_context: Case information and context
            workflow_type: Type of workflow (full, research_only, drafting_only)
            
        Returns:
            WorkflowState with complete results
        """
        logger.info(f"Starting workflow for case {case_context.case_id}")
        start_time = datetime.now()
        
        # Initialize workflow state
        state = WorkflowState(
            case_context=case_context,
            current_stage=WorkflowStage.INITIALIZATION
        )
        
        # Store in active workflows
        self.active_workflows[case_context.case_id] = state
        self.metrics['total_workflows'] += 1
        
        try:
            # Execute workflow stages sequentially
            if workflow_type in ["full", "research_only"]:
                # Stage 1: Issue Identification
                state = await self._execute_issue_identification(state)
                
                # Stage 2: Case Research
                state = await self._execute_case_research(state)
                
                # Stage 3: Limitation Check
                state = await self._execute_limitation_check(state)
                
                # Stage 4: Argument Building
                state = await self._execute_argument_building(state)
            
            if workflow_type in ["full", "drafting_only"]:
                # Stage 5: Document Drafting
                state = await self._execute_document_drafting(state)
                
                # Stage 6: Compliance Validation
                state = await self._execute_compliance_validation(state)
            
            # Stage 7: Aid Assessment (optional)
            if self.config.get('enable_aid_suggestions', True):
                state = await self._execute_aid_assessment(state)
            
            # Stage 8: Human Review Checkpoint
            state.current_stage = WorkflowStage.HUMAN_REVIEW
            logger.info("Workflow ready for human review")
            
            # Mark workflow as completed
            state.current_stage = WorkflowStage.COMPLETED
            state.completed_at = datetime.now()
            
            # Update metrics
            self.metrics['successful_workflows'] += 1
            execution_time = (state.completed_at - start_time).total_seconds()
            self._update_average_execution_time(execution_time)
            
            logger.info(f"Workflow completed successfully in {execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Workflow failed: {str(e)}")
            state.current_stage = WorkflowStage.FAILED
            state.workflow_errors.append(str(e))
            state.completed_at = datetime.now()
            self.metrics['failed_workflows'] += 1
            
        return state
    
    async def _execute_issue_identification(self, state: WorkflowState) -> WorkflowState:
        """Execute Issue Identification stage"""
        logger.info("Stage 1: Issue Identification")
        state.current_stage = WorkflowStage.ISSUE_IDENTIFICATION
        
        try:
            agent = self._initialize_agent("IssueSpotter")
            
            # Prepare input for IssueSpotter
            input_data = {
                'case_facts': state.case_context.case_facts,
                'case_type': state.case_context.case_type.value,
                'jurisdiction': state.case_context.jurisdiction
            }
            
            # Execute agent
            start_time = datetime.now()
            result = await self._execute_agent_with_retry(agent, input_data)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Store result
            agent_result = AgentResult(
                agent_name="IssueSpotter",
                success=result.get('success', False),
                data=result.get('data', {}),
                errors=result.get('errors', []),
                warnings=result.get('warnings', []),
                execution_time=execution_time
            )
            state.agent_results['IssueSpotter'] = agent_result
            
            # Update state with identified issues
            if agent_result.success:
                state.identified_issues = result['data'].get('identified_issues', [])
                state.case_context.relevant_sections = result['data'].get('relevant_sections', [])
                state.case_context.relevant_statutes = result['data'].get('relevant_statutes', [])
                logger.info(f"Identified {len(state.identified_issues)} legal issues")
            else:
                state.workflow_errors.extend(agent_result.errors)
                raise Exception("Issue identification failed")
                
        except Exception as e:
            logger.error(f"Error in issue identification: {e}")
            state.workflow_errors.append(f"Issue identification error: {str(e)}")
            raise
        
        return state
    
    async def _execute_case_research(self, state: WorkflowState) -> WorkflowState:
        """Execute Case Research stage"""
        logger.info("Stage 2: Case Research")
        state.current_stage = WorkflowStage.CASE_RESEARCH
        
        try:
            agent = self._initialize_agent("CaseFinder")
            
            # Prepare input for CaseFinder
            input_data = {
                'identified_issues': state.identified_issues,
                'relevant_sections': state.case_context.relevant_sections,
                'relevant_statutes': state.case_context.relevant_statutes,
                'jurisdiction': state.case_context.jurisdiction,
                'case_type': state.case_context.case_type.value
            }
            
            # Execute agent
            start_time = datetime.now()
            result = await self._execute_agent_with_retry(agent, input_data)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Store result
            agent_result = AgentResult(
                agent_name="CaseFinder",
                success=result.get('success', False),
                data=result.get('data', {}),
                errors=result.get('errors', []),
                warnings=result.get('warnings', []),
                execution_time=execution_time
            )
            state.agent_results['CaseFinder'] = agent_result
            
            # Update state with relevant cases
            if agent_result.success:
                state.relevant_cases = result['data'].get('relevant_cases', [])
                state.citations = result['data'].get('citations', [])
                
                # Validate citations if enabled
                if self.config.get('enable_citation_validation', True):
                    state = await self._validate_citations(state)
                
                logger.info(f"Found {len(state.relevant_cases)} relevant cases")
            else:
                state.workflow_errors.extend(agent_result.errors)
                raise Exception("Case research failed")
                
        except Exception as e:
            logger.error(f"Error in case research: {e}")
            state.workflow_errors.append(f"Case research error: {str(e)}")
            raise
        
        return state
    
    async def _execute_limitation_check(self, state: WorkflowState) -> WorkflowState:
        """Execute Limitation Check stage"""
        logger.info("Stage 3: Limitation Check")
        state.current_stage = WorkflowStage.LIMITATION_CHECK
        
        try:
            agent = self._initialize_agent("LimitationChecker")
            
            # Prepare input
            input_data = {
                'case_facts': state.case_context.case_facts,
                'case_type': state.case_context.case_type.value,
                'identified_issues': state.identified_issues,
                'relevant_statutes': state.case_context.relevant_statutes
            }
            
            # Execute agent
            start_time = datetime.now()
            result = await self._execute_agent_with_retry(agent, input_data)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Store result
            agent_result = AgentResult(
                agent_name="LimitationChecker",
                success=result.get('success', False),
                data=result.get('data', {}),
                errors=result.get('errors', []),
                warnings=result.get('warnings', []),
                execution_time=execution_time
            )
            state.agent_results['LimitationChecker'] = agent_result
            
            # Update state
            if agent_result.success:
                state.limitation_status = result['data'].get('limitation_status', {})
                
                # Add warnings if time-barred
                if state.limitation_status.get('is_time_barred', False):
                    state.workflow_warnings.append(
                        "WARNING: Case may be time-barred. Review limitation period carefully."
                    )
                
                logger.info(f"Limitation status: {state.limitation_status.get('status', 'unknown')}")
            else:
                # Limitation check failure is not fatal
                state.workflow_warnings.append("Limitation check could not be completed")
                
        except Exception as e:
            logger.warning(f"Error in limitation check: {e}")
            state.workflow_warnings.append(f"Limitation check error: {str(e)}")
        
        return state
    
    async def _execute_argument_building(self, state: WorkflowState) -> WorkflowState:
        """Execute Argument Building stage"""
        logger.info("Stage 4: Argument Building")
        state.current_stage = WorkflowStage.ARGUMENT_BUILDING
        
        try:
            agent = self._initialize_agent("ArgumentBuilder")
            
            # Prepare input
            input_data = {
                'case_facts': state.case_context.case_facts,
                'identified_issues': state.identified_issues,
                'relevant_cases': state.relevant_cases,
                'limitation_status': state.limitation_status,
                'case_type': state.case_context.case_type.value
            }
            
            # Execute agent
            start_time = datetime.now()
            result = await self._execute_agent_with_retry(agent, input_data)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Store result
            agent_result = AgentResult(
                agent_name="ArgumentBuilder",
                success=result.get('success', False),
                data=result.get('data', {}),
                errors=result.get('errors', []),
                warnings=result.get('warnings', []),
                execution_time=execution_time
            )
            state.agent_results['ArgumentBuilder'] = agent_result
            
            # Update state
            if agent_result.success:
                state.arguments = result['data'].get('arguments', {})
                logger.info("Arguments built successfully")
            else:
                state.workflow_errors.extend(agent_result.errors)
                raise Exception("Argument building failed")
                
        except Exception as e:
            logger.error(f"Error in argument building: {e}")
            state.workflow_errors.append(f"Argument building error: {str(e)}")
            raise
        
        return state
    
    async def _execute_document_drafting(self, state: WorkflowState) -> WorkflowState:
        """Execute Document Drafting stage"""
        logger.info("Stage 5: Document Drafting")
        state.current_stage = WorkflowStage.DOCUMENT_DRAFTING
        
        try:
            agent = self._initialize_agent("DocComposer")
            
            # Prepare comprehensive input
            input_data = {
                'case_context': {
                    'case_facts': state.case_context.case_facts,
                    'case_type': state.case_context.case_type.value,
                    'document_type': state.case_context.document_type.value if state.case_context.document_type else None,
                    'jurisdiction': state.case_context.jurisdiction,
                    'court_name': state.case_context.court_name,
                    'petitioner_name': state.case_context.petitioner_name,
                    'respondent_name': state.case_context.respondent_name,
                    'language_preference': state.case_context.language_preference
                },
                'identified_issues': state.identified_issues,
                'relevant_cases': state.relevant_cases,
                'arguments': state.arguments,
                'limitation_status': state.limitation_status,
                'citations': state.citations
            }
            
            # Execute agent
            start_time = datetime.now()
            result = await self._execute_agent_with_retry(agent, input_data)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Store result
            agent_result = AgentResult(
                agent_name="DocComposer",
                success=result.get('success', False),
                data=result.get('data', {}),
                errors=result.get('errors', []),
                warnings=result.get('warnings', []),
                execution_time=execution_time
            )
            state.agent_results['DocComposer'] = agent_result
            
            # Update state
            if agent_result.success:
                state.drafted_document = result['data'].get('drafted_document', '')
                
                # Save document if configured
                if self.config.get('save_intermediate_results', True):
                    self._save_document(state)
                
                logger.info("Document drafted successfully")
            else:
                state.workflow_errors.extend(agent_result.errors)
                raise Exception("Document drafting failed")
                
        except Exception as e:
            logger.error(f"Error in document drafting: {e}")
            state.workflow_errors.append(f"Document drafting error: {str(e)}")
            raise
        
        return state
    
    async def _execute_compliance_validation(self, state: WorkflowState) -> WorkflowState:
        """Execute Compliance Validation stage"""
        logger.info("Stage 6: Compliance Validation")
        state.current_stage = WorkflowStage.COMPLIANCE_VALIDATION
        
        try:
            agent = self._initialize_agent("ComplianceGuard")
            
            # Prepare input
            input_data = {
                'drafted_document': state.drafted_document,
                'case_context': {
                    'case_type': state.case_context.case_type.value,
                    'document_type': state.case_context.document_type.value if state.case_context.document_type else None,
                    'jurisdiction': state.case_context.jurisdiction,
                    'court_name': state.case_context.court_name
                },
                'citations': state.citations
            }
            
            # Execute agent
            start_time = datetime.now()
            result = await self._execute_agent_with_retry(agent, input_data)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Store result
            agent_result = AgentResult(
                agent_name="ComplianceGuard",
                success=result.get('success', False),
                data=result.get('data', {}),
                errors=result.get('errors', []),
                warnings=result.get('warnings', []),
                execution_time=execution_time
            )
            state.agent_results['ComplianceGuard'] = agent_result
            
            # Update state
            if agent_result.success:
                state.compliance_report = result['data'].get('compliance_report', {})
                
                # Add compliance warnings
                compliance_warnings = state.compliance_report.get('warnings', [])
                state.workflow_warnings.extend(compliance_warnings)
                
                logger.info("Compliance validation completed")
            else:
                # Compliance check failure is not fatal, but should be noted
                state.workflow_warnings.append("Compliance validation could not be completed")
                
        except Exception as e:
            logger.warning(f"Error in compliance validation: {e}")
            state.workflow_warnings.append(f"Compliance validation error: {str(e)}")
        
        return state
    
    async def _execute_aid_assessment(self, state: WorkflowState) -> WorkflowState:
        """Execute Aid Assessment stage"""
        logger.info("Stage 7: Aid Assessment")
        state.current_stage = WorkflowStage.AID_ASSESSMENT
        
        try:
            agent = self._initialize_agent("AidConnector")
            
            # Prepare input
            input_data = {
                'case_context': {
                    'case_type': state.case_context.case_type.value,
                    'jurisdiction': state.case_context.jurisdiction,
                    'urgency_level': state.case_context.urgency_level
                },
                'identified_issues': state.identified_issues
            }
            
            # Execute agent
            start_time = datetime.now()
            result = await self._execute_agent_with_retry(agent, input_data)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Store result
            agent_result = AgentResult(
                agent_name="AidConnector",
                success=result.get('success', False),
                data=result.get('data', {}),
                errors=result.get('errors', []),
                warnings=result.get('warnings', []),
                execution_time=execution_time
            )
            state.agent_results['AidConnector'] = agent_result
            
            # Update state
            if agent_result.success:
                state.aid_recommendations = result['data'].get('aid_recommendations', [])
                logger.info(f"Found {len(state.aid_recommendations)} aid options")
                
        except Exception as e:
            logger.warning(f"Error in aid assessment: {e}")
            # Aid assessment failure is not critical
        
        return state
    
    async def _execute_agent_with_retry(
        self,
        agent: Any,
        input_data: Dict,
        max_retries: Optional[int] = None
    ) -> Dict:
        """
        Execute an agent with retry logic.
        
        Args:
            agent: Agent instance to execute
            input_data: Input data for the agent
            max_retries: Maximum number of retries (defaults to config)
            
        Returns:
            Agent execution result
        """
        if max_retries is None:
            max_retries = self.config.get('max_retries', 3)
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Executing {agent.name if hasattr(agent, 'name') else 'agent'} (attempt {attempt + 1}/{max_retries})")
                
                # Execute agent (handle both sync and async)
                if asyncio.iscoroutinefunction(agent.execute):
                    result = await agent.execute(**input_data)
                else:
                    result = agent.execute(**input_data)
                
                return result
                
            except Exception as e:
                last_error = e
                logger.warning(f"Agent execution failed (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    # Wait before retry with exponential backoff
                    await asyncio.sleep(2 ** attempt)
        
        # All retries failed
        logger.error(f"Agent execution failed after {max_retries} attempts")
        return {
            'success': False,
            'data': {},
            'errors': [f"Agent execution failed: {str(last_error)}"]
        }
    
    async def _validate_citations(self, state: WorkflowState) -> WorkflowState:
        """Validate all citations using CitationValidator"""
        logger.info("Validating citations")
        
        try:
            from src.core.citation_validator import CitationValidator
            
            validator = CitationValidator(vectorstore=self.vectorstore)
            
            # Validate all citations
            validated_results = validator.validate_multiple(state.citations)
            
            # Check for invalid citations
            invalid_citations = [
                r.citation for r in validated_results if not r.is_valid
            ]
            
            if invalid_citations:
                warning_msg = f"Invalid citations detected: {', '.join(invalid_citations)}"
                state.workflow_warnings.append(warning_msg)
                logger.warning(warning_msg)
            
            # Check against database if enabled
            if self.vectorstore:
                unverified_citations = []
                for citation in state.citations:
                    if not validator.check_against_database(citation):
                        unverified_citations.append(citation)
                
                if unverified_citations:
                    warning_msg = f"Citations not found in database: {', '.join(unverified_citations)}"
                    state.workflow_warnings.append(warning_msg)
                    logger.warning(warning_msg)
            
            logger.info(f"Citation validation completed. Valid: {len(state.citations) - len(invalid_citations)}/{len(state.citations)}")
            
        except Exception as e:
            logger.error(f"Error validating citations: {e}")
            state.workflow_warnings.append(f"Citation validation error: {str(e)}")
        
        return state
    
    def _save_document(self, state: WorkflowState):
        """Save drafted document to file"""
        try:
            output_dir = Path(self.config.get('output_directory', './outputs'))
            output_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{state.case_context.case_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(state.drafted_document)
            
            logger.info(f"Document saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving document: {e}")
    
    def _update_average_execution_time(self, execution_time: float):
        """Update average execution time metric"""
        total = self.metrics['total_workflows']
        current_avg = self.metrics['average_execution_time']
        
        new_avg = ((current_avg * (total - 1)) + execution_time) / total
        self.metrics['average_execution_time'] = new_avg
    
    def get_workflow_status(self, case_id: str) -> Optional[Dict]:
        """
        Get current status of a workflow.
        
        Args:
            case_id: Case ID to check
            
        Returns:
            Workflow status dictionary or None if not found
        """
        if case_id not in self.active_workflows:
            return None
        
        state = self.active_workflows[case_id]
        
        return {
            'case_id': case_id,
            'current_stage': state.current_stage.value,
            'progress_percentage': self._calculate_progress(state),
            'identified_issues_count': len(state.identified_issues),
            'relevant_cases_count': len(state.relevant_cases),
            'has_drafted_document': state.drafted_document is not None,
            'errors_count': len(state.workflow_errors),
            'warnings_count': len(state.workflow_warnings),
            'started_at': state.started_at.isoformat(),
            'completed_at': state.completed_at.isoformat() if state.completed_at else None
        }
    
    def _calculate_progress(self, state: WorkflowState) -> float:
        """Calculate workflow progress percentage"""
        stage_weights = {
            WorkflowStage.INITIALIZATION: 0.0,
            WorkflowStage.ISSUE_IDENTIFICATION: 0.15,
            WorkflowStage.CASE_RESEARCH: 0.30,
            WorkflowStage.LIMITATION_CHECK: 0.45,
            WorkflowStage.ARGUMENT_BUILDING: 0.60,
            WorkflowStage.DOCUMENT_DRAFTING: 0.75,
            WorkflowStage.COMPLIANCE_VALIDATION: 0.85,
            WorkflowStage.AID_ASSESSMENT: 0.95,
            WorkflowStage.HUMAN_REVIEW: 0.98,
            WorkflowStage.COMPLETED: 1.0,
            WorkflowStage.FAILED: 0.0
        }
        
        return stage_weights.get(state.current_stage, 0.0)
    
    def get_metrics(self) -> Dict:
        """Get orchestrator performance metrics"""
        return {
            **self.metrics,
            'success_rate': (
                f"{(self.metrics['successful_workflows'] / self.metrics['total_workflows'] * 100):.2f}%"
                if self.metrics['total_workflows'] > 0 else "0%"
            ),
            'active_workflows': len(self.active_workflows)
        }
    
    def generate_final_report(self, case_id: str) -> Optional[Dict]:
        """
        Generate comprehensive final report for a completed workflow.
        
        Args:
            case_id: Case ID
            
        Returns:
            Complete workflow report
        """
        if case_id not in self.active_workflows:
            return None
        
        state = self.active_workflows[case_id]
        
        report = {
            'case_information': {
                'case_id': state.case_context.case_id,
                'case_type': state.case_context.case_type.value,
                'jurisdiction': state.case_context.jurisdiction,
                'court_name': state.case_context.court_name,
                'document_type': state.case_context.document_type.value if state.case_context.document_type else None
            },
            'workflow_summary': {
                'status': state.current_stage.value,
                'started_at': state.started_at.isoformat(),
                'completed_at': state.completed_at.isoformat() if state.completed_at else None,
                'duration_seconds': (
                    (state.completed_at - state.started_at).total_seconds()
                    if state.completed_at else None
                )
            },
            'research_results': {
                'identified_issues': state.identified_issues,
                'relevant_cases_count': len(state.relevant_cases),
                'citations': state.citations,
                'limitation_status': state.limitation_status
            },
            'drafted_document': state.drafted_document,
            'compliance_report': state.compliance_report,
            'aid_recommendations': state.aid_recommendations,
            'quality_indicators': {
                'errors': state.workflow_errors,
                'warnings': state.workflow_warnings,
                'citation_validation_passed': len(state.workflow_warnings) == 0
            },
            'agent_performance': {
                agent_name: {
                    'success': result.success,
                    'execution_time': result.execution_time,
                    'errors': result.errors,
                    'warnings': result.warnings
                }
                for agent_name, result in state.agent_results.items()
            },
            'human_review_required': self.config.get('require_human_verification', True),
            'disclaimer': (
                "This document is generated by an AI assistant and must be reviewed "
                "by a qualified legal professional before use. It does not constitute "
                "legal advice."
            )
        }
        
        return report


# Convenience functions for common workflows

async def create_bail_application(
    case_facts: str,
    jurisdiction: str,
    accused_name: str,
    vectorstore=None
) -> Dict:
    """
    Quick helper to create a bail application.
    
    Args:
        case_facts: Facts of the case
        jurisdiction: Jurisdiction (state/court)
        accused_name: Name of the accused
        vectorstore: Optional vectorstore
        
    Returns:
        Final report with drafted bail application
    """
    orchestrator = LegalOrchestrator(vectorstore=vectorstore)
    
    case_context = CaseContext(
        case_id=f"bail_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        case_type=CaseType.CRIMINAL,
        case_facts=case_facts,
        jurisdiction=jurisdiction,
        petitioner_name=accused_name,
        document_type=DocumentType.BAIL_APPLICATION,
        urgency_level="urgent"
    )
    
    state = await orchestrator.start_workflow(case_context)
    return orchestrator.generate_final_report(case_context.case_id)


async def research_case_law(
    legal_issue: str,
    jurisdiction: str,
    vectorstore=None
) -> Dict:
    """
    Quick helper for legal research only.
    
    Args:
        legal_issue: Legal issue to research
        jurisdiction: Jurisdiction
        vectorstore: Optional vectorstore
        
    Returns:
        Research results
    """
    orchestrator = LegalOrchestrator(vectorstore=vectorstore)
    
    case_context = CaseContext(
        case_id=f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        case_type=CaseType.UNKNOWN,
        case_facts=legal_issue,
        jurisdiction=jurisdiction
    )
    
    state = await orchestrator.start_workflow(case_context, workflow_type="research_only")
    return orchestrator.generate_final_report(case_context.case_id)


# Main execution example
if __name__ == "__main__":
    import asyncio
    
    async def main():
        """Example usage of the orchestrator"""
        
        # Example: Create a bail application
        print("=" * 80)
        print("VIDHI LEGAL ORCHESTRATOR - EXAMPLE WORKFLOW")
        print("=" * 80)
        
        case_facts = """
        The accused was arrested on 15th January 2026 under Section 420 IPC for 
        alleged cheating. The accused is a first-time offender with no prior 
        criminal record. The accused is willing to cooperate with the investigation 
        and has strong roots in the community.
        """
        
        orchestrator = LegalOrchestrator()
        
        case_context = CaseContext(
            case_id="BAIL_001_2026",
            case_type=CaseType.CRIMINAL,
            case_facts=case_facts,
            jurisdiction="Delhi",
            court_name="Saket District Court",
            petitioner_name="John Doe",
            respondent_name="State of Delhi",
            document_type=DocumentType.BAIL_APPLICATION,
            urgency_level="urgent"
        )
        
        print("\nStarting workflow...")
        state = await orchestrator.start_workflow(case_context)
        
        print(f"\nWorkflow Status: {state.current_stage.value}")
        print(f"Errors: {len(state.workflow_errors)}")
        print(f"Warnings: {len(state.workflow_warnings)}")
        
        # Generate final report
        report = orchestrator.generate_final_report(case_context.case_id)
        
        print("\n" + "=" * 80)
        print("FINAL REPORT")
        print("=" * 80)
        print(json.dumps(report, indent=2, default=str))
        
        # Display metrics
        print("\n" + "=" * 80)
        print("ORCHESTRATOR METRICS")
        print("=" * 80)
        metrics = orchestrator.get_metrics()
        for key, value in metrics.items():
            print(f"{key}: {value}")
    
    # Run the example
    asyncio.run(main())
