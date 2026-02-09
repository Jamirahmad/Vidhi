"""
Task Router for Vidhi Legal Research Platform

This module routes user requests to appropriate agents and workflows based on intent classification.
It acts as the intelligent entry point that determines how to handle each user query.

Features:
- Intent classification (research, drafting, compliance, etc.)
- Automatic workflow selection
- Agent routing decisions
- Multi-agent coordination
- Task complexity assessment
- Context-aware routing
- Fallback handling
- Safety pre-filtering
- Session integration
- Priority management

Author: Vidhi Development Team
License: MIT (Educational & Research Use Only)
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of tasks the system can handle"""
    # Research tasks
    CASE_RESEARCH = "case_research"
    STATUTE_LOOKUP = "statute_lookup"
    PRECEDENT_SEARCH = "precedent_search"
    LEGAL_ISSUE_ANALYSIS = "legal_issue_analysis"
    
    # Drafting tasks
    DOCUMENT_DRAFTING = "document_drafting"
    BAIL_APPLICATION = "bail_application"
    LEGAL_NOTICE = "legal_notice"
    WRIT_PETITION = "writ_petition"
    CIVIL_SUIT = "civil_suit"
    AFFIDAVIT = "affidavit"
    REPLY = "reply"
    
    # Analysis tasks
    LIMITATION_CHECK = "limitation_check"
    COMPLIANCE_CHECK = "compliance_check"
    ARGUMENT_BUILDING = "argument_building"
    
    # Utility tasks
    CITATION_VALIDATION = "citation_validation"
    DOCUMENT_REVIEW = "document_review"
    LEGAL_AID_SEARCH = "legal_aid_search"
    
    # General tasks
    GENERAL_QUERY = "general_query"
    CLARIFICATION = "clarification"
    UNKNOWN = "unknown"


class TaskComplexity(Enum):
    """Complexity levels for tasks"""
    SIMPLE = "simple"      # Single agent, quick response
    MODERATE = "moderate"  # Few agents, moderate time
    COMPLEX = "complex"    # Full workflow, multiple agents
    VERY_COMPLEX = "very_complex"  # Extended workflow, human review


class WorkflowType(Enum):
    """Types of workflows to execute"""
    FULL_WORKFLOW = "full_workflow"           # Complete research + drafting
    RESEARCH_ONLY = "research_only"           # Just research, no drafting
    DRAFTING_ONLY = "drafting_only"           # Just drafting, assume research done
    VALIDATION_ONLY = "validation_only"       # Just validation/compliance
    QUICK_QUERY = "quick_query"               # Simple Q&A, no workflow
    MULTI_STEP = "multi_step"                 # Custom multi-step process


class Priority(Enum):
    """Task priority levels"""
    CRITICAL = "critical"  # Urgent legal matters
    HIGH = "high"          # Important tasks
    NORMAL = "normal"      # Regular tasks
    LOW = "low"           # Background tasks


@dataclass
class RoutingDecision:
    """Result of routing analysis"""
    task_type: TaskType
    complexity: TaskComplexity
    workflow_type: WorkflowType
    priority: Priority
    target_agents: List[str] = field(default_factory=list)
    estimated_time_minutes: Optional[int] = None
    requires_human_input: bool = False
    confidence_score: float = 1.0
    routing_metadata: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


@dataclass
class TaskContext:
    """Context extracted from user request"""
    raw_query: str
    case_type: Optional[str] = None
    jurisdiction: Optional[str] = None
    document_type: Optional[str] = None
    urgency_indicators: List[str] = field(default_factory=list)
    entity_mentions: Dict[str, List[str]] = field(default_factory=dict)
    extracted_sections: List[str] = field(default_factory=list)
    extracted_acts: List[str] = field(default_factory=list)
    has_file_attachment: bool = False
    session_context: Optional[Dict] = None


class TaskRouter:
    """
    Intelligent task router for Vidhi platform.
    
    This router:
    1. Classifies user intent from natural language queries
    2. Determines appropriate workflow and agents
    3. Assesses task complexity and priority
    4. Extracts relevant context from queries
    5. Routes to orchestrator or individual agents
    6. Handles multi-turn conversations
    7. Applies safety pre-filtering
    8. Manages fallback strategies
    """
    
    def __init__(
        self,
        session_memory=None,
        safety_guardrails=None,
        strict_routing: bool = False
    ):
        """
        Initialize Task Router.
        
        Args:
            session_memory: SessionMemory instance for context
            safety_guardrails: SafetyGuardrails for pre-filtering
            strict_routing: Require high confidence for routing
        """
        self.session_memory = session_memory
        self.safety_guardrails = safety_guardrails
        self.strict_routing = strict_routing
        
        # Intent patterns
        self.intent_patterns = self._initialize_intent_patterns()
        
        # Entity patterns
        self.entity_patterns = self._initialize_entity_patterns()
        
        # Complexity indicators
        self.complexity_indicators = self._initialize_complexity_indicators()
        
        # Workflow mappings
        self.task_to_workflow = self._initialize_workflow_mappings()
        
        logger.info("TaskRouter initialized")
    
    def _initialize_intent_patterns(self) -> Dict[TaskType, List[Dict]]:
        """Initialize patterns for intent classification"""
        return {
            # Research intents
            TaskType.CASE_RESEARCH: [
                {
                    'pattern': r'(?i)(find|search|look\s+for|need)\s+(case|judgment|precedent|ruling)',
                    'weight': 0.9
                },
                {
                    'pattern': r'(?i)(relevant|similar|related)\s+(case|precedent)',
                    'weight': 0.9
                },
                {
                    'pattern': r'(?i)(case\s+law|judicial\s+precedent)',
                    'weight': 0.85
                }
            ],
            
            TaskType.STATUTE_LOOKUP: [
                {
                    'pattern': r'(?i)(section|article|provision)\s+\d+',
                    'weight': 0.9
                },
                {
                    'pattern': r'(?i)(IPC|CrPC|CPC|Constitution)',
                    'weight': 0.85
                },
                {
                    'pattern': r'(?i)what\s+(is|does)\s+(section|article)',
                    'weight': 0.8
                }
            ],
            
            TaskType.LEGAL_ISSUE_ANALYSIS: [
                {
                    'pattern': r'(?i)(analyze|identify|spot)\s+(issue|problem|question)',
                    'weight': 0.9
                },
                {
                    'pattern': r'(?i)what\s+(are\s+the\s+)?legal\s+issue',
                    'weight': 0.85
                },
                {
                    'pattern': r'(?i)(applicable|relevant)\s+(law|provision|section)',
                    'weight': 0.8
                }
            ],
            
            # Drafting intents
            TaskType.BAIL_APPLICATION: [
                {
                    'pattern': r'(?i)(draft|prepare|write|create)\s+(a\s+)?bail\s+application',
                    'weight': 1.0
                },
                {
                    'pattern': r'(?i)bail\s+(under\s+)?(section\s+)?(437|439)',
                    'weight': 0.95
                },
                {
                    'pattern': r'(?i)need\s+bail',
                    'weight': 0.85
                }
            ],
            
            TaskType.LEGAL_NOTICE: [
                {
                    'pattern': r'(?i)(draft|send|prepare|write)\s+(a\s+)?legal\s+notice',
                    'weight': 1.0
                },
                {
                    'pattern': r'(?i)notice\s+(under|to)',
                    'weight': 0.85
                },
                {
                    'pattern': r'(?i)demand\s+notice',
                    'weight': 0.8
                }
            ],
            
            TaskType.WRIT_PETITION: [
                {
                    'pattern': r'(?i)(draft|file|prepare)\s+(a\s+)?writ\s+petition',
                    'weight': 1.0
                },
                {
                    'pattern': r'(?i)(article\s+)?(226|227|32)',
                    'weight': 0.9
                },
                {
                    'pattern': r'(?i)(mandamus|certiorari|prohibition|quo\s+warranto|habeas\s+corpus)',
                    'weight': 0.95
                }
            ],
            
            TaskType.DOCUMENT_DRAFTING: [
                {
                    'pattern': r'(?i)(draft|prepare|write|create)\s+(a\s+)?(document|petition|application)',
                    'weight': 0.85
                },
                {
                    'pattern': r'(?i)help\s+(me\s+)?draft',
                    'weight': 0.8
                }
            ],
            
            # Analysis intents
            TaskType.LIMITATION_CHECK: [
                {
                    'pattern': r'(?i)(limitation|time[\s-]bar|barred\s+by\s+time)',
                    'weight': 0.95
                },
                {
                    'pattern': r'(?i)(is\s+it|am\s+I)\s+(too\s+)?late\s+to\s+file',
                    'weight': 0.9
                },
                {
                    'pattern': r'(?i)limitation\s+act',
                    'weight': 0.85
                }
            ],
            
            TaskType.COMPLIANCE_CHECK: [
                {
                    'pattern': r'(?i)(check|verify|validate)\s+(compliance|format|requirement)',
                    'weight': 0.9
                },
                {
                    'pattern': r'(?i)(is\s+this|does\s+this)\s+(compliant|correct|proper)',
                    'weight': 0.85
                },
                {
                    'pattern': r'(?i)court\s+(requirement|rule|format)',
                    'weight': 0.8
                }
            ],
            
            TaskType.ARGUMENT_BUILDING: [
                {
                    'pattern': r'(?i)(build|construct|make|prepare)\s+(argument|submission)',
                    'weight': 0.9
                },
                {
                    'pattern': r'(?i)how\s+(can|should)\s+I\s+argue',
                    'weight': 0.85
                },
                {
                    'pattern': r'(?i)(legal\s+)?argument\s+(for|against)',
                    'weight': 0.85
                }
            ],
            
            # Utility intents
            TaskType.CITATION_VALIDATION: [
                {
                    'pattern': r'(?i)(validate|verify|check)\s+(citation|case\s+reference)',
                    'weight': 0.95
                },
                {
                    'pattern': r'(?i)(is\s+this|correct)\s+citation',
                    'weight': 0.9
                }
            ],
            
            TaskType.DOCUMENT_REVIEW: [
                {
                    'pattern': r'(?i)(review|check|examine|look\s+at)\s+(my\s+)?(document|draft)',
                    'weight': 0.9
                },
                {
                    'pattern': r'(?i)(fix|correct|improve)\s+(my\s+)?document',
                    'weight': 0.85
                }
            ],
            
            TaskType.LEGAL_AID_SEARCH: [
                {
                    'pattern': r'(?i)(legal\s+aid|free\s+legal|pro\s+bono)',
                    'weight': 0.95
                },
                {
                    'pattern': r'(?i)(can\'t\s+afford|cannot\s+afford)\s+(a\s+)?lawyer',
                    'weight': 0.9
                },
                {
                    'pattern': r'(?i)(NALSA|SLSA|DLSA)',
                    'weight': 0.9
                }
            ],
            
            # General
            TaskType.GENERAL_QUERY: [
                {
                    'pattern': r'(?i)^(what|how|why|when|where|who)',
                    'weight': 0.7
                },
                {
                    'pattern': r'(?i)(explain|tell\s+me\s+about|information\s+on)',
                    'weight': 0.75
                }
            ]
        }
    
    def _initialize_entity_patterns(self) -> Dict[str, str]:
        """Initialize patterns for entity extraction"""
        return {
            'ipc_section': r'(?i)section\s+(\d+[A-Z]?)\s+IPC',
            'crpc_section': r'(?i)section\s+(\d+[A-Z]?)\s+Cr\.?P\.?C',
            'cpc_section': r'(?i)section\s+(\d+[A-Z]?)\s+C\.?P\.?C',
            'article': r'(?i)article\s+(\d+[A-Z]?)',
            'jurisdiction': r'(?i)(Delhi|Mumbai|Kolkata|Chennai|Bangalore|Hyderabad|Pune|Ahmedabad|Supreme\s+Court|High\s+Court)',
            'court_name': r'(?i)(Supreme\s+Court|High\s+Court|District\s+Court|Sessions\s+Court|Magistrate)',
            'case_type': r'(?i)(criminal|civil|writ|constitutional|bail|divorce|property|contract)',
            'urgency': r'(?i)(urgent|emergency|immediate|asap|today|tomorrow)'
        }
    
    def _initialize_complexity_indicators(self) -> Dict[TaskComplexity, Dict]:
        """Initialize complexity assessment criteria"""
        return {
            TaskComplexity.SIMPLE: {
                'max_agents': 1,
                'keywords': ['explain', 'what is', 'define', 'quick question'],
                'estimated_time': 2
            },
            TaskComplexity.MODERATE: {
                'max_agents': 3,
                'keywords': ['find cases', 'check limitation', 'validate'],
                'estimated_time': 10
            },
            TaskComplexity.COMPLEX: {
                'max_agents': 5,
                'keywords': ['draft', 'prepare', 'full research', 'comprehensive'],
                'estimated_time': 30
            },
            TaskComplexity.VERY_COMPLEX: {
                'max_agents': 7,
                'keywords': ['complete workflow', 'everything', 'start to finish'],
                'estimated_time': 60
            }
        }
    
    def _initialize_workflow_mappings(self) -> Dict[TaskType, WorkflowType]:
        """Map task types to workflow types"""
        return {
            # Research tasks -> Research workflow
            TaskType.CASE_RESEARCH: WorkflowType.RESEARCH_ONLY,
            TaskType.STATUTE_LOOKUP: WorkflowType.QUICK_QUERY,
            TaskType.PRECEDENT_SEARCH: WorkflowType.RESEARCH_ONLY,
            TaskType.LEGAL_ISSUE_ANALYSIS: WorkflowType.RESEARCH_ONLY,
            
            # Drafting tasks -> Full workflow (research + drafting)
            TaskType.BAIL_APPLICATION: WorkflowType.FULL_WORKFLOW,
            TaskType.LEGAL_NOTICE: WorkflowType.FULL_WORKFLOW,
            TaskType.WRIT_PETITION: WorkflowType.FULL_WORKFLOW,
            TaskType.CIVIL_SUIT: WorkflowType.FULL_WORKFLOW,
            TaskType.AFFIDAVIT: WorkflowType.DRAFTING_ONLY,
            TaskType.DOCUMENT_DRAFTING: WorkflowType.FULL_WORKFLOW,
            
            # Analysis tasks -> Targeted workflow
            TaskType.LIMITATION_CHECK: WorkflowType.VALIDATION_ONLY,
            TaskType.COMPLIANCE_CHECK: WorkflowType.VALIDATION_ONLY,
            TaskType.ARGUMENT_BUILDING: WorkflowType.MULTI_STEP,
            
            # Utility tasks -> Quick processing
            TaskType.CITATION_VALIDATION: WorkflowType.QUICK_QUERY,
            TaskType.DOCUMENT_REVIEW: WorkflowType.VALIDATION_ONLY,
            TaskType.LEGAL_AID_SEARCH: WorkflowType.QUICK_QUERY,
            
            # General
            TaskType.GENERAL_QUERY: WorkflowType.QUICK_QUERY,
            TaskType.CLARIFICATION: WorkflowType.QUICK_QUERY
        }
    
    # ===================================================================
    # CORE ROUTING METHODS
    # ===================================================================
    
    def route_request(
        self,
        user_query: str,
        session_context: Optional[Dict] = None,
        has_attachment: bool = False
    ) -> RoutingDecision:
        """
        Route a user request to appropriate workflow/agents.
        
        Args:
            user_query: User's natural language query
            session_context: Optional session context
            has_attachment: Whether request has file attachment
            
        Returns:
            RoutingDecision with routing information
        """
        logger.info(f"Routing request: {user_query[:100]}...")
        
        # Safety pre-filtering
        if self.safety_guardrails:
            safety_result = self.safety_guardrails.validate_output(
                user_query,
                output_type="user_query"
            )
            
            if not safety_result.is_safe:
                logger.warning("Request blocked by safety filter")
                return self._create_blocked_decision(safety_result)
        
        # Extract context from query
        task_context = self._extract_task_context(
            user_query,
            session_context,
            has_attachment
        )
        
        # Classify intent
        task_type, confidence = self._classify_intent(task_context)
        
        # Determine workflow type
        workflow_type = self._determine_workflow(task_type, task_context)
        
        # Assess complexity
        complexity = self._assess_complexity(task_type, task_context)
        
        # Determine priority
        priority = self._determine_priority(task_context)
        
        # Select target agents
        target_agents = self._select_agents(task_type, workflow_type, complexity)
        
        # Estimate time
        estimated_time = self._estimate_time(complexity, workflow_type)
        
        # Check if human input needed
        requires_human = self._requires_human_input(task_type, complexity)
        
        # Generate warnings
        warnings = self._generate_warnings(task_context, confidence)
        
        decision = RoutingDecision(
            task_type=task_type,
            complexity=complexity,
            workflow_type=workflow_type,
            priority=priority,
            target_agents=target_agents,
            estimated_time_minutes=estimated_time,
            requires_human_input=requires_human,
            confidence_score=confidence,
            routing_metadata={
                'extracted_entities': task_context.entity_mentions,
                'urgency_indicators': task_context.urgency_indicators,
                'has_attachment': has_attachment
            },
            warnings=warnings
        )
        
        logger.info(
            f"Routing decision: {task_type.value} -> {workflow_type.value} "
            f"(confidence: {confidence:.2f})"
        )
        
        return decision
    
    def _extract_task_context(
        self,
        query: str,
        session_context: Optional[Dict],
        has_attachment: bool
    ) -> TaskContext:
        """Extract context information from query"""
        context = TaskContext(
            raw_query=query,
            has_file_attachment=has_attachment,
            session_context=session_context
        )
        
        # Extract entities
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, query)
            if matches:
                if entity_type not in context.entity_mentions:
                    context.entity_mentions[entity_type] = []
                context.entity_mentions[entity_type].extend(matches)
        
        # Extract case type
        if 'case_type' in context.entity_mentions:
            context.case_type = context.entity_mentions['case_type'][0]
        
        # Extract jurisdiction
        if 'jurisdiction' in context.entity_mentions:
            context.jurisdiction = context.entity_mentions['jurisdiction'][0]
        
        # Extract urgency indicators
        if 'urgency' in context.entity_mentions:
            context.urgency_indicators = context.entity_mentions['urgency']
        
        # Extract sections
        for key in ['ipc_section', 'crpc_section', 'cpc_section']:
            if key in context.entity_mentions:
                context.extracted_sections.extend(context.entity_mentions[key])
        
        # Get session context if available
        if self.session_memory and not session_context:
            case_memory = self.session_memory.get_case_memory()
            if case_memory:
                context.session_context = {
                    'case_id': case_memory.case_id,
                    'case_type': case_memory.case_type,
                    'jurisdiction': case_memory.jurisdiction
                }
        
        return context
    
    def _classify_intent(self, task_context: TaskContext) -> Tuple[TaskType, float]:
        """
        Classify user intent from task context.
        
        Returns:
            Tuple of (TaskType, confidence_score)
        """
        query = task_context.raw_query.lower()
        
        # Score each task type
        scores: Dict[TaskType, float] = {}
        
        for task_type, patterns in self.intent_patterns.items():
            score = 0.0
            
            for pattern_dict in patterns:
                if re.search(pattern_dict['pattern'], query):
                    score = max(score, pattern_dict['weight'])
            
            if score > 0:
                scores[task_type] = score
        
        # Add contextual boosting
        scores = self._apply_contextual_boosting(scores, task_context)
        
        # Select best match
        if scores:
            best_task = max(scores.items(), key=lambda x: x[1])
            return best_task[0], best_task[1]
        else:
            # Default to general query
            return TaskType.GENERAL_QUERY, 0.5
    
    def _apply_contextual_boosting(
        self,
        scores: Dict[TaskType, float],
        task_context: TaskContext
    ) -> Dict[TaskType, float]:
        """Apply contextual boosting to intent scores"""
        
        # Boost drafting tasks if attachment present
        if task_context.has_file_attachment:
            for task_type in scores:
                if 'draft' in task_type.value or 'review' in task_type.value:
                    scores[task_type] *= 1.2
        
        # Boost based on session context
        if task_context.session_context:
            session_case_type = task_context.session_context.get('case_type', '')
            
            # If session is criminal, boost criminal-related tasks
            if 'criminal' in session_case_type.lower():
                if TaskType.BAIL_APPLICATION in scores:
                    scores[TaskType.BAIL_APPLICATION] *= 1.15
        
        # Boost based on extracted sections
        if task_context.extracted_sections:
            if TaskType.STATUTE_LOOKUP in scores:
                scores[TaskType.STATUTE_LOOKUP] *= 1.1
        
        return scores
    
    def _determine_workflow(
        self,
        task_type: TaskType,
        task_context: TaskContext
    ) -> WorkflowType:
        """Determine appropriate workflow type"""
        
        # Get default workflow for task type
        workflow = self.task_to_workflow.get(task_type, WorkflowType.QUICK_QUERY)
        
        # Override based on context
        query_lower = task_context.raw_query.lower()
        
        # User explicitly requests full workflow
        if any(kw in query_lower for kw in ['complete', 'full', 'comprehensive', 'entire']):
            if workflow != WorkflowType.QUICK_QUERY:
                workflow = WorkflowType.FULL_WORKFLOW
        
        # User requests only research
        if any(kw in query_lower for kw in ['just research', 'only find', 'research only']):
            workflow = WorkflowType.RESEARCH_ONLY
        
        # User has session with existing research
        if task_context.session_context and self.session_memory:
            case_memory = self.session_memory.get_case_memory()
            if case_memory and len(case_memory.relevant_cases) > 0:
                # Research already done, can do drafting only
                if task_type in [TaskType.BAIL_APPLICATION, TaskType.LEGAL_NOTICE]:
                    workflow = WorkflowType.DRAFTING_ONLY
        
        return workflow
    
    def _assess_complexity(
        self,
        task_type: TaskType,
        task_context: TaskContext
    ) -> TaskComplexity:
        """Assess task complexity"""
        
        # Base complexity by task type
        complexity_map = {
            TaskType.STATUTE_LOOKUP: TaskComplexity.SIMPLE,
            TaskType.CITATION_VALIDATION: TaskComplexity.SIMPLE,
            TaskType.GENERAL_QUERY: TaskComplexity.SIMPLE,
            
            TaskType.CASE_RESEARCH: TaskComplexity.MODERATE,
            TaskType.LIMITATION_CHECK: TaskComplexity.MODERATE,
            TaskType.LEGAL_AID_SEARCH: TaskComplexity.MODERATE,
            
            TaskType.DOCUMENT_DRAFTING: TaskComplexity.COMPLEX,
            TaskType.BAIL_APPLICATION: TaskComplexity.COMPLEX,
            TaskType.LEGAL_NOTICE: TaskComplexity.COMPLEX,
            
            TaskType.WRIT_PETITION: TaskComplexity.VERY_COMPLEX,
            TaskType.CIVIL_SUIT: TaskComplexity.VERY_COMPLEX,
        }
        
        base_complexity = complexity_map.get(task_type, TaskComplexity.MODERATE)
        
        # Adjust based on context
        query_lower = task_context.raw_query.lower()
        
        # Complexity boosters
        if any(kw in query_lower for kw in ['comprehensive', 'detailed', 'thorough', 'complete']):
            if base_complexity == TaskComplexity.SIMPLE:
                base_complexity = TaskComplexity.MODERATE
            elif base_complexity == TaskComplexity.MODERATE:
                base_complexity = TaskComplexity.COMPLEX
        
        # Complexity reducers
        if any(kw in query_lower for kw in ['quick', 'simple', 'brief', 'just']):
            if base_complexity == TaskComplexity.COMPLEX:
                base_complexity = TaskComplexity.MODERATE
            elif base_complexity == TaskComplexity.VERY_COMPLEX:
                base_complexity = TaskComplexity.COMPLEX
        
        return base_complexity
    
    def _determine_priority(self, task_context: TaskContext) -> Priority:
        """Determine task priority"""
        
        # Check urgency indicators
        if task_context.urgency_indicators:
            urgency_terms = [u.lower() for u in task_context.urgency_indicators]
            
            if any(t in urgency_terms for t in ['emergency', 'urgent', 'immediate']):
                return Priority.CRITICAL
            elif any(t in urgency_terms for t in ['asap', 'soon', 'today']):
                return Priority.HIGH
        
        # Check case type
        if task_context.case_type:
            case_type_lower = task_context.case_type.lower()
            
            # Criminal cases often more urgent
            if 'criminal' in case_type_lower or 'bail' in case_type_lower:
                return Priority.HIGH
        
        # Default priority
        return Priority.NORMAL
    
    def _select_agents(
        self,
        task_type: TaskType,
        workflow_type: WorkflowType,
        complexity: TaskComplexity
    ) -> List[str]:
        """Select appropriate agents for the task"""
        agents = []
        
        # Map task types to agents
        if task_type in [TaskType.CASE_RESEARCH, TaskType.PRECEDENT_SEARCH]:
            agents.append("CaseFinder")
        
        if task_type == TaskType.LEGAL_ISSUE_ANALYSIS:
            agents.append("IssueSpotter")
        
        if task_type == TaskType.LIMITATION_CHECK:
            agents.append("LimitationChecker")
        
        if task_type in [TaskType.ARGUMENT_BUILDING]:
            agents.append("ArgumentBuilder")
        
        if task_type in [TaskType.BAIL_APPLICATION, TaskType.LEGAL_NOTICE, 
                         TaskType.WRIT_PETITION, TaskType.DOCUMENT_DRAFTING]:
            agents.extend(["IssueSpotter", "CaseFinder", "ArgumentBuilder", "DocComposer"])
        
        if task_type in [TaskType.COMPLIANCE_CHECK, TaskType.DOCUMENT_REVIEW]:
            agents.append("ComplianceGuard")
        
        if task_type == TaskType.LEGAL_AID_SEARCH:
            agents.append("AidConnector")
        
        # For full workflows, use orchestrator (which manages all agents)
        if workflow_type == WorkflowType.FULL_WORKFLOW:
            agents = ["Orchestrator"]  # Orchestrator coordinates all agents
        
        return agents
    
    def _estimate_time(
        self,
        complexity: TaskComplexity,
        workflow_type: WorkflowType
    ) -> int:
        """Estimate execution time in minutes"""
        
        base_times = {
            TaskComplexity.SIMPLE: 2,
            TaskComplexity.MODERATE: 10,
            TaskComplexity.COMPLEX: 30,
            TaskComplexity.VERY_COMPLEX: 60
        }
        
        base_time = base_times.get(complexity, 10)
        
        # Adjust for workflow type
        workflow_multipliers = {
            WorkflowType.QUICK_QUERY: 0.5,
            WorkflowType.RESEARCH_ONLY: 0.7,
            WorkflowType.DRAFTING_ONLY: 0.8,
            WorkflowType.VALIDATION_ONLY: 0.6,
            WorkflowType.FULL_WORKFLOW: 1.0,
            WorkflowType.MULTI_STEP: 1.2
        }
        
        multiplier = workflow_multipliers.get(workflow_type, 1.0)
        
        return int(base_time * multiplier)
    
    def _requires_human_input(
        self,
        task_type: TaskType,
        complexity: TaskComplexity
    ) -> bool:
        """Determine if human input is required during execution"""
        
        # Complex tasks always require human review
        if complexity in [TaskComplexity.COMPLEX, TaskComplexity.VERY_COMPLEX]:
            return True
        
        # Drafting tasks require human review
        if 'draft' in task_type.value or 'application' in task_type.value:
            return True
        
        return False
    
    def _generate_warnings(
        self,
        task_context: TaskContext,
        confidence: float
    ) -> List[str]:
        """Generate warnings for the routing decision"""
        warnings = []
        
        # Low confidence warning
        if confidence < 0.7:
            warnings.append(
                f"Low intent classification confidence ({confidence:.2f}). "
                "May need clarification from user."
            )
        
        # Missing important context
        if not task_context.case_type and not task_context.jurisdiction:
            if any(kw in task_context.raw_query.lower() 
                   for kw in ['draft', 'prepare', 'file']):
                warnings.append(
                    "Missing case type or jurisdiction. May need to ask user for details."
                )
        
        # Urgency without clear task
        if task_context.urgency_indicators and confidence < 0.8:
            warnings.append(
                "Urgent request detected but intent unclear. "
                "Recommend seeking immediate clarification."
            )
        
        return warnings
    
    def _create_blocked_decision(self, safety_result) -> RoutingDecision:
        """Create a routing decision for blocked requests"""
        return RoutingDecision(
            task_type=TaskType.UNKNOWN,
            complexity=TaskComplexity.SIMPLE,
            workflow_type=WorkflowType.QUICK_QUERY,
            priority=Priority.LOW,
            target_agents=[],
            confidence_score=0.0,
            warnings=[
                "Request blocked by safety filter",
                *[v.description for v in safety_result.violations]
            ]
        )
    
    # ===================================================================
    # MULTI-TURN CONVERSATION SUPPORT
    # ===================================================================
    
    def route_with_session(
        self,
        user_query: str,
        session_id: str,
        has_attachment: bool = False
    ) -> RoutingDecision:
        """
        Route with session context awareness.
        
        Args:
            user_query: User query
            session_id: Session identifier
            has_attachment: File attachment present
            
        Returns:
            RoutingDecision
        """
        # Get session context
        session_context = None
        if self.session_memory:
            case_memory = self.session_memory.get_case_memory()
            if case_memory:
                session_context = {
                    'case_id': case_memory.case_id,
                    'case_type': case_memory.case_type,
                    'jurisdiction': case_memory.jurisdiction,
                    'has_research': len(case_memory.relevant_cases) > 0
                }
        
        return self.route_request(user_query, session_context, has_attachment)
    
    def handle_clarification_needed(
        self,
        original_query: str,
        routing_decision: RoutingDecision
    ) -> List[str]:
        """
        Generate clarification questions when routing is uncertain.
        
        Args:
            original_query: Original user query
            routing_decision: Initial routing decision
            
        Returns:
            List of clarification questions
        """
        questions = []
        
        # Low confidence - need general clarification
        if routing_decision.confidence_score < 0.7:
            questions.append(
                "I want to make sure I understand correctly. "
                "Could you clarify what you need help with?"
            )
        
        # Missing case type
        if routing_decision.task_type in [TaskType.DOCUMENT_DRAFTING, 
                                           TaskType.BAIL_APPLICATION]:
            task_context = self._extract_task_context(original_query, None, False)
            if not task_context.case_type:
                questions.append(
                    "What type of case is this? (e.g., criminal, civil, writ)"
                )
        
        # Missing jurisdiction
        if not any('jurisdiction' in w.lower() 
                  for w in routing_decision.routing_metadata.get('extracted_entities', {})):
            if routing_decision.complexity != TaskComplexity.SIMPLE:
                questions.append(
                    "Which court or jurisdiction is this for? "
                    "(e.g., Delhi High Court, Mumbai District Court)"
                )
        
        return questions
    
    # ===================================================================
    # UTILITY METHODS
    # ===================================================================
    
    def get_routing_summary(self, decision: RoutingDecision) -> str:
        """Get human-readable routing summary"""
        lines = []
        lines.append(f"Task Type: {decision.task_type.value}")
        lines.append(f"Complexity: {decision.complexity.value}")
        lines.append(f"Workflow: {decision.workflow_type.value}")
        lines.append(f"Priority: {decision.priority.value}")
        lines.append(f"Agents: {', '.join(decision.target_agents)}")
        lines.append(f"Estimated Time: {decision.estimated_time_minutes} minutes")
        lines.append(f"Confidence: {decision.confidence_score:.2%}")
        
        if decision.warnings:
            lines.append("\nWarnings:")
            for warning in decision.warnings:
                lines.append(f"  - {warning}")
        
        return "\n".join(lines)


# Convenience functions

def quick_route(user_query: str) -> RoutingDecision:
    """Quick routing without session context"""
    router = TaskRouter()
    return router.route_request(user_query)


def route_with_safety(
    user_query: str,
    safety_guardrails
) -> RoutingDecision:
    """Route with safety pre-filtering"""
    router = TaskRouter(safety_guardrails=safety_guardrails)
    return router.route_request(user_query)


# Example usage
if __name__ == "__main__":
    print("=" * 80)
    print("VIDHI TASK ROUTER - DEMONSTRATION")
    print("=" * 80)
    
    router = TaskRouter()
    
    # Test queries
    test_queries = [
        "I need help drafting a bail application for my client",
        "Find me relevant case laws on Section 420 IPC",
        "Is my case time-barred under limitation act?",
        "Draft a legal notice for property dispute",
        "What is Section 437 CrPC?",
        "I need urgent legal aid, cannot afford a lawyer",
        "Check if this document is compliant with court rules",
        "Explain the concept of habeas corpus"
    ]
    
    for query in test_queries:
        print("\n" + "=" * 80)
        print(f"Query: {query}")
        print("-" * 80)
        
        decision = router.route_request(query)
        print(router.get_routing_summary(decision))
    
    print("\n" + "=" * 80)
    print("Task routing demonstration complete!")
