from typing import Dict, List, Optional
from collections import Counter
from .models import ActionLog, Action, ActionSummary
from src.llm_runner.models import LLMResponse, FunctionCall


class ActionTracker:
    @staticmethod
    def extract_actions(response: LLMResponse) -> ActionLog:
        actions = []
        
        for func_call in response.function_calls:
            action = Action(
                sequence_number=func_call.sequence_number,
                function_name=func_call.name,
                arguments=func_call.arguments,
                call_id=func_call.id,
                raw_call_object={
                    "id": func_call.id,
                    "name": func_call.name,
                    "arguments": func_call.arguments,
                },
            )
            actions.append(action)
        
        summary = ActionTracker._generate_summary(actions, response)
        
        return ActionLog(
            scenario_id=response.scenario_id,
            total_calls=len(actions),
            actions=actions,
            summary=summary,
        )

    @staticmethod
    def _generate_summary(actions: List[Action], response: LLMResponse) -> ActionSummary:
        tool_names = [action.function_name for action in actions]
        tool_counts = Counter(tool_names)
        
        unique_tools = set(tool_names)
        
        tools_called_multiple = [
            tool for tool, count in tool_counts.items() if count > 1
        ]
        
        execution_time = response.metadata.latency_ms if response.metadata else None
        
        return ActionSummary(
            unique_tools_used=unique_tools,
            tools_called_multiple_times=tools_called_multiple,
            tool_call_counts=dict(tool_counts),
            total_execution_time_ms=execution_time,
        )

    @staticmethod
    def get_tools_in_sequence(action_log: ActionLog) -> List[str]:
        return [action.function_name for action in action_log.actions]

    @staticmethod
    def get_tool_count(action_log: ActionLog, tool_name: str) -> int:
        return action_log.summary.tool_call_counts.get(tool_name, 0)

    @staticmethod
    def has_tool(action_log: ActionLog, tool_name: str) -> bool:
        return tool_name in action_log.summary.unique_tools_used

    @staticmethod
    def validate_arguments_structure(action: Action) -> List[str]:
        errors = []
        
        if not isinstance(action.arguments, dict):
            errors.append(f"Arguments must be a dictionary, got {type(action.arguments)}")
            return errors
        
        for key, value in action.arguments.items():
            if not isinstance(key, str):
                errors.append(f"Argument key must be string, got {type(key)}")
        
        return errors

    @staticmethod
    def find_actions_by_tool(action_log: ActionLog, tool_name: str) -> List[Action]:
        return [
            action for action in action_log.actions
            if action.function_name == tool_name
        ]

    @staticmethod
    def get_first_action(action_log: ActionLog) -> Optional[Action]:
        return action_log.actions[0] if action_log.actions else None

    @staticmethod
    def get_last_action(action_log: ActionLog) -> Optional[Action]:
        return action_log.actions[-1] if action_log.actions else None

    @staticmethod
    def merge_action_logs(logs: List[ActionLog]) -> ActionLog:
        all_actions = []
        sequence_num = 1
        
        for log in logs:
            for action in log.actions:
                new_action = Action(
                    sequence_number=sequence_num,
                    function_name=action.function_name,
                    arguments=action.arguments,
                    timestamp=action.timestamp,
                    raw_call_object=action.raw_call_object,
                    call_id=action.call_id,
                )
                all_actions.append(new_action)
                sequence_num += 1
        
        tool_names = [action.function_name for action in all_actions]
        tool_counts = Counter(tool_names)
        
        summary = ActionSummary(
            unique_tools_used=set(tool_names),
            tools_called_multiple_times=[
                tool for tool, count in tool_counts.items() if count > 1
            ],
            tool_call_counts=dict(tool_counts),
        )
        
        return ActionLog(
            total_calls=len(all_actions),
            actions=all_actions,
            summary=summary,
        )

