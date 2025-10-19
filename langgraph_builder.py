"""
LangGraph Builder - Main orchestrator for Prospect-to-Lead Workflow
Dynamically builds and executes workflow from workflow.json
"""

import json
import sys
import re
from typing import Dict, Any, TypedDict
from datetime import datetime

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from utils.logger import setup_logger, get_log_file_path
from utils.validators import validate_workflow_json
from utils.tool_loader import load_tools_config, replace_env_variables

from agents import (
    ProspectSearchAgent,
    DataEnrichmentAgent,
    ScoringAgent,
    OutreachContentAgent,
    OutreachExecutorAgent,
    ResponseTrackerAgent,
    FeedbackTrainerAgent
)

AGENT_REGISTRY = {
    'ProspectSearchAgent': ProspectSearchAgent,
    'DataEnrichmentAgent': DataEnrichmentAgent,
    'ScoringAgent': ScoringAgent,
    'OutreachContentAgent': OutreachContentAgent,
    'OutreachExecutorAgent': OutreachExecutorAgent,
    'ResponseTrackerAgent': ResponseTrackerAgent,
    'FeedbackTrainerAgent': FeedbackTrainerAgent
}

class WorkflowState(TypedDict):
    """State that flows through the workflow"""
    messages: list
    workflow_data: Dict[str, Any]
    current_step: str
    step_outputs: Dict[str, Any]

class LangGraphWorkflowBuilder:
    """Builds and executes LangGraph workflow from JSON configuration"""
    
    def __init__(self, workflow_path: str = 'workflow.json'):
        self.logger = setup_logger('LangGraphBuilder', get_log_file_path())
        self.workflow_path = workflow_path
        self.workflow_config = None
        self.graph = None
        
        self.logger.info("="*60)
        self.logger.info("LangGraph Workflow Builder Initialized")
        self.logger.info("="*60)
    
    def load_workflow(self) -> Dict[str, Any]:
        """Load and validate workflow configuration"""
        self.logger.info(f"Loading workflow from: {self.workflow_path}")
        
        try:
            self.workflow_config = validate_workflow_json(self.workflow_path)
            self.logger.info(f"✓ Workflow '{self.workflow_config['workflow_name']}' loaded")
            self.logger.info(f"  Description: {self.workflow_config['description']}")
            self.logger.info(f"  Steps: {len(self.workflow_config['steps'])}")
            return self.workflow_config
        except Exception as e:
            self.logger.error(f"✗ Failed to load workflow: {e}")
            raise
    
    def build_graph(self) -> StateGraph:
        """Build LangGraph from workflow configuration"""
        self.logger.info("\n📊 Building LangGraph...")
        workflow = StateGraph(WorkflowState)
        
        for step in self.workflow_config['steps']:
            step_id = step['id']
            agent_name = step['agent']
            node_func = self._create_node_function(step)
            workflow.add_node(step_id, node_func)
            self.logger.info(f"  ✓ Added node: {step_id} ({agent_name})")
        
        steps = self.workflow_config['steps']
        workflow.set_entry_point(steps[0]['id'])
        
        for i in range(len(steps) - 1):
            current_step = steps[i]['id']
            next_step = steps[i + 1]['id']
            workflow.add_edge(current_step, next_step)
            self.logger.info(f"  ✓ Added edge: {current_step} → {next_step}")
        
        workflow.add_edge(steps[-1]['id'], END)
        self.logger.info(f"  ✓ Added edge: {steps[-1]['id']} → END")
        
        self.graph = workflow.compile()
        self.logger.info("\n✓ LangGraph compiled successfully")
        return self.graph
    
    def _create_node_function(self, step: Dict[str, Any]):
        def node_function(state: WorkflowState) -> WorkflowState:
            step_id = step['id']
            agent_class_name = step['agent']
            
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"🤖 Executing: {agent_class_name} (Step: {step_id})")
            self.logger.info(f"{'='*60}")
            
            tools_config = load_tools_config(step)
            agent_class = AGENT_REGISTRY.get(agent_class_name)
            if not agent_class:
                raise ValueError(f"Unknown agent: {agent_class_name}")
            
            agent = agent_class(step, tools_config)
            inputs = self._resolve_inputs(step['inputs'], state['step_outputs'], 
                                         self.workflow_config.get('config', {}))
            
            self.logger.info(f"📥 Inputs: {list(inputs.keys())}")
            
            try:
                output = agent.execute(inputs)
                state['step_outputs'][step_id] = output
                state['current_step'] = step_id
                
                self.logger.info(f"📤 Output keys: {list(output.keys())}")
                reasoning = agent.get_reasoning_log()
                self.logger.info(f"💭 Thoughts: {len(reasoning['thoughts'])}")
                self.logger.info(f"🎬 Actions: {len(reasoning['actions'])}")
                
                return state
            except Exception as e:
                self.logger.error(f"✗ Agent execution failed: {e}")
                raise
        
        return node_function
    
    def _resolve_inputs(self, input_config: Dict, step_outputs: Dict, 
                       workflow_config: Dict) -> Dict[str, Any]:
        def resolve_value(value):
            if isinstance(value, str):
                pattern = r'\{\{([^}]+)\}\}'
                match = re.search(pattern, value)
                
                if match:
                    ref_path = match.group(1)
                    parts = ref_path.split('.')
                    
                    if parts[0] == 'config':
                        result = workflow_config
                        for part in parts[1:]:
                            result = result.get(part, {})
                        return result
                    elif len(parts) >= 3:
                        step_id = parts[0]
                        if step_id in step_outputs:
                            result = step_outputs[step_id]
                            for part in parts[2:]:
                                if isinstance(result, dict):
                                    result = result.get(part, {})
                            return result
                return value
            elif isinstance(value, dict):
                return {k: resolve_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [resolve_value(item) for item in value]
            else:
                return value
        
        return resolve_value(input_config)
    
    def execute(self) -> Dict[str, Any]:
        self.logger.info("\n" + "="*60)
        self.logger.info("▶️  Starting Workflow Execution")
        self.logger.info("="*60)
        
        start_time = datetime.now()
        
        initial_state = {
            'messages': [HumanMessage(content="Start prospect-to-lead workflow")],
            'workflow_data': self.workflow_config,
            'current_step': '',
            'step_outputs': {}
        }
        
        try:
            final_state = self.graph.invoke(initial_state)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.info("\n" + "="*60)
            self.logger.info("✅ Workflow Completed Successfully")
            self.logger.info(f"⏱️  Duration: {duration:.2f} seconds")
            self.logger.info("="*60)
            
            self._print_summary(final_state['step_outputs'])
            return final_state['step_outputs']
        except Exception as e:
            self.logger.error(f"\n❌ Workflow execution failed: {e}")
            raise
    
    def _print_summary(self, step_outputs: Dict[str, Any]):
        print("\n" + "="*60)
        print("📊 WORKFLOW EXECUTION SUMMARY")
        print("="*60)
        
        if 'prospect_search' in step_outputs:
            leads = step_outputs['prospect_search'].get('leads', [])
            print(f"\n🔍 Prospect Search: {len(leads)} leads found")
        
        if 'enrichment' in step_outputs:
            enriched = step_outputs['enrichment'].get('enriched_leads', [])
            print(f"📊 Data Enrichment: {len(enriched)} leads enriched")
        
        if 'scoring' in step_outputs:
            ranked = step_outputs['scoring'].get('ranked_leads', [])
            if ranked:
                avg_score = sum(l['score'] for l in ranked) / len(ranked)
                print(f"⭐ Lead Scoring: {len(ranked)} qualified leads")
                print(f"   Average score: {avg_score:.1f}/100")
                print(f"   Top lead: {ranked[0]['company']} ({ranked[0]['score']:.1f})")
        
        if 'outreach_content' in step_outputs:
            messages = step_outputs['outreach_content'].get('messages', [])
            print(f"✉️  Outreach Content: {len(messages)} emails generated")
        
        if 'send' in step_outputs:
            sent_status = step_outputs['send'].get('sent_status', [])
            successful = sum(1 for s in sent_status if s['status'] in ['sent', 'simulated'])
            print(f"📤 Email Sending: {successful}/{len(sent_status)} successful")
        
        if 'response_tracking' in step_outputs:
            responses = step_outputs['response_tracking'].get('responses', [])
            opened = sum(1 for r in responses if r.get('opened'))
            replied = sum(1 for r in responses if r.get('replied'))
            meetings = sum(1 for r in responses if r.get('meeting_booked'))
            print(f"📈 Response Tracking:")
            print(f"   Opens: {opened}/{len(responses)}")
            print(f"   Replies: {replied}/{len(responses)}")
            print(f"   Meetings: {meetings}/{len(responses)}")
        
        if 'feedback_trainer' in step_outputs:
            metrics = step_outputs['feedback_trainer'].get('metrics', {})
            recommendations = step_outputs['feedback_trainer'].get('recommendations', [])
            print(f"🎓 Feedback Analysis:")
            print(f"   Open Rate: {metrics.get('open_rate', 0):.1f}%")
            print(f"   Reply Rate: {metrics.get('reply_rate', 0):.1f}%")
            print(f"   Recommendations: {len(recommendations)}")
        
        print("="*60)

def main():
    """Main entry point"""
    print("\n" + "🤖 "*20)
    print("   LANGGRAPH PROSPECT-TO-LEAD WORKFLOW")
    print("   Autonomous AI Agent System")
    print("🤖 "*20 + "\n")
    
    try:
        builder = LangGraphWorkflowBuilder()
        builder.load_workflow()
        builder.build_graph()
        results = builder.execute()
        
        print("\n✅ All tasks completed successfully!")
        print("📁 Check the 'logs/' folder for detailed execution logs")
        print("📁 Check the 'data/' folder for feedback recommendations")
        
        return 0
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())