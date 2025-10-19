from typing import Dict, Any, List
from abc import ABC, abstractmethod
import json
from datetime import datetime


class BaseAgent(ABC):
    """Base class for all workflow agents"""
    
    def __init__(self, step_config: Dict[str, Any], tools_config: Dict[str, Any]):
        """
        Initialize agent
        
        Args:
            step_config: Step configuration from workflow.json
            tools_config: Configured tools with API keys loaded
        """
        self.step_id = step_config['id']
        self.agent_name = step_config['agent']
        self.instructions = step_config['instructions']
        self.tools_config = tools_config
        self.inputs = step_config.get('inputs', {})
        self.output_schema = step_config.get('output_schema', {})
        
        # ReAct prompting components
        self.thoughts: List[str] = []
        self.actions: List[Dict[str, Any]] = []
        self.observations: List[str] = []
    
    def think(self, thought: str):
        """Record a reasoning thought (ReAct pattern)"""
        self.thoughts.append(thought)
        print(f"💭 Thought: {thought}")
    
    def act(self, action: str, details: Dict[str, Any] = None):
        """Record an action taken (ReAct pattern)"""
        action_record = {
            'action': action,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        self.actions.append(action_record)
        print(f"🎬 Action: {action}")
    
    def observe(self, observation: str):
        """Record an observation from action results (ReAct pattern)"""
        self.observations.append(observation)
        print(f"👁️  Observation: {observation}")
    
    @abstractmethod
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's task
        
        Args:
            inputs: Input data from previous steps
            
        Returns:
            Output data matching the output_schema
        """
        pass
    
    def get_reasoning_log(self) -> Dict[str, Any]:
        """Get complete reasoning log (thoughts, actions, observations)"""
        return {
            'thoughts': self.thoughts,
            'actions': self.actions,
            'observations': self.observations
        }
    
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """
        Validate output against schema
        
        Args:
            output: Output to validate
            
        Returns:
            True if valid
        """
        for key in self.output_schema.keys():
            if key not in output:
                print(f"⚠️  Warning: Missing expected output key: {key}")
                return False
        return True
    
    def log_execution(self, success: bool, output: Any = None, error: str = None):
        """Log execution results"""
        log_entry = {
            'agent': self.agent_name,
            'step_id': self.step_id,
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'reasoning': self.get_reasoning_log()
        }
        
        if success:
            log_entry['output'] = output
        else:
            log_entry['error'] = error
        
        return log_entry


# Import all agents for easy access
from .prospect_search import ProspectSearchAgent
from .enrichment import DataEnrichmentAgent
from .scoring import ScoringAgent
from .outreach_content import OutreachContentAgent
from .outreach_executor import OutreachExecutorAgent
from .response_tracker import ResponseTrackerAgent
from .feedback_trainer import FeedbackTrainerAgent

__all__ = [
    'BaseAgent',
    'ProspectSearchAgent',
    'DataEnrichmentAgent',
    'ScoringAgent',
    'OutreachContentAgent',
    'OutreachExecutorAgent',
    'ResponseTrackerAgent',
    'FeedbackTrainerAgent'
]