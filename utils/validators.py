import json
from typing import Dict, Any, List
from pydantic import BaseModel, Field, ValidationError


class ICPConfig(BaseModel):
    """ICP (Ideal Customer Profile) configuration"""
    industry: List[str]
    location: str
    employee_count: Dict[str, int]
    revenue: Dict[str, int]


class WorkflowStep(BaseModel):
    """Workflow step configuration"""
    id: str
    agent: str
    inputs: Dict[str, Any]
    instructions: str
    tools: List[Dict[str, Any]] = []
    output_schema: Dict[str, Any]


class WorkflowConfig(BaseModel):
    """Complete workflow configuration"""
    workflow_name: str
    description: str
    config: Dict[str, Any] = {}
    steps: List[WorkflowStep]


def validate_workflow_json(workflow_path: str) -> Dict[str, Any]:
    """
    Validate workflow JSON file against schema
    
    Args:
        workflow_path: Path to workflow.json file
        
    Returns:
        Validated workflow configuration
        
    Raises:
        ValidationError: If workflow configuration is invalid
        FileNotFoundError: If workflow file doesn't exist
    """
    try:
        with open(workflow_path, 'r') as f:
            workflow_data = json.load(f)
        
        # Validate using Pydantic
        workflow = WorkflowConfig(**workflow_data)
        
        print(f"✓ Workflow '{workflow.workflow_name}' validated successfully")
        print(f"  Steps: {len(workflow.steps)}")
        
        return workflow_data
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Workflow file not found: {workflow_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in workflow file: {e}")
    except ValidationError as e:
        raise ValueError(f"Workflow validation failed: {e}")


def validate_step_output(step_id: str, output: Any, expected_schema: Dict[str, Any]) -> bool:
    """
    Validate step output against expected schema
    
    Args:
        step_id: Step identifier
        output: Output data to validate
        expected_schema: Expected output schema
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(output, dict):
        print(f"Warning: Step '{step_id}' output is not a dictionary")
        return False
    
    # Check for required top-level keys
    for key in expected_schema.keys():
        if key not in output:
            print(f"Warning: Step '{step_id}' missing required output key: {key}")
            return False
    
    return True


def extract_variable_references(value: str) -> List[str]:
    """
    Extract variable references from string like {{step.output.field}}
    
    Args:
        value: String that may contain variable references
        
    Returns:
        List of variable reference paths
    """
    import re
    pattern = r'\{\{([^}]+)\}\}'
    matches = re.findall(pattern, value)
    return matches