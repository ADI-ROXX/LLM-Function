import pytest
from src.action_tracker import ActionTracker, ActionLog, Action, ActionSummary
from src.llm_runner.models import (
    LLMResponse,
    FunctionCall,
    ResponseMetadata,
    LLMProvider,
)


def test_extract_actions_empty():
    response = LLMResponse(
        provider=LLMProvider.DEEPSEEK,
        model="deepseek-chat",
        response_text="Hello",
        function_calls=[],
        metadata=ResponseMetadata(latency_ms=100, model="deepseek-chat"),
    )
    
    action_log = ActionTracker.extract_actions(response)
    
    assert action_log.total_calls == 0
    assert len(action_log.actions) == 0


def test_extract_actions_single_call():
    response = LLMResponse(
        provider=LLMProvider.DEEPSEEK,
        model="deepseek-chat",
        response_text="Reading file",
        function_calls=[
            FunctionCall(
                id="call_1",
                name="read_file",
                arguments={"file_path": "test.txt"},
                sequence_number=1,
            )
        ],
        metadata=ResponseMetadata(latency_ms=150, model="deepseek-chat"),
    )
    
    action_log = ActionTracker.extract_actions(response)
    
    assert action_log.total_calls == 1
    assert len(action_log.actions) == 1
    assert action_log.actions[0].function_name == "read_file"
    assert action_log.actions[0].arguments == {"file_path": "test.txt"}


def test_extract_actions_multiple_calls():
    response = LLMResponse(
        provider=LLMProvider.DEEPSEEK,
        model="deepseek-chat",
        function_calls=[
            FunctionCall(
                id="call_1",
                name="read_file",
                arguments={"file_path": "test.txt"},
                sequence_number=1,
            ),
            FunctionCall(
                id="call_2",
                name="edit_file",
                arguments={"file_path": "test.txt", "old_text": "a", "new_text": "b"},
                sequence_number=2,
            ),
        ],
        metadata=ResponseMetadata(latency_ms=200, model="deepseek-chat"),
    )
    
    action_log = ActionTracker.extract_actions(response)
    
    assert action_log.total_calls == 2
    assert len(action_log.actions) == 2


def test_summary_generation():
    response = LLMResponse(
        provider=LLMProvider.DEEPSEEK,
        model="deepseek-chat",
        function_calls=[
            FunctionCall(
                id="call_1",
                name="read_file",
                arguments={"file_path": "test1.txt"},
                sequence_number=1,
            ),
            FunctionCall(
                id="call_2",
                name="read_file",
                arguments={"file_path": "test2.txt"},
                sequence_number=2,
            ),
            FunctionCall(
                id="call_3",
                name="edit_file",
                arguments={"file_path": "test.txt", "old_text": "a", "new_text": "b"},
                sequence_number=3,
            ),
        ],
        metadata=ResponseMetadata(latency_ms=300, model="deepseek-chat"),
    )
    
    action_log = ActionTracker.extract_actions(response)
    
    assert len(action_log.summary.unique_tools_used) == 2
    assert "read_file" in action_log.summary.unique_tools_used
    assert "edit_file" in action_log.summary.unique_tools_used
    
    assert "read_file" in action_log.summary.tools_called_multiple_times
    assert "edit_file" not in action_log.summary.tools_called_multiple_times
    
    assert action_log.summary.tool_call_counts["read_file"] == 2
    assert action_log.summary.tool_call_counts["edit_file"] == 1


def test_get_tools_in_sequence():
    action_log = ActionLog(
        total_calls=3,
        actions=[
            Action(sequence_number=1, function_name="read_file", arguments={}),
            Action(sequence_number=2, function_name="search_code", arguments={}),
            Action(sequence_number=3, function_name="edit_file", arguments={}),
        ],
    )
    
    sequence = ActionTracker.get_tools_in_sequence(action_log)
    
    assert sequence == ["read_file", "search_code", "edit_file"]


def test_get_tool_count():
    action_log = ActionLog(
        total_calls=2,
        actions=[
            Action(sequence_number=1, function_name="read_file", arguments={}),
            Action(sequence_number=2, function_name="read_file", arguments={}),
        ],
        summary=ActionSummary(tool_call_counts={"read_file": 2}),
    )
    
    count = ActionTracker.get_tool_count(action_log, "read_file")
    assert count == 2
    
    count = ActionTracker.get_tool_count(action_log, "edit_file")
    assert count == 0


def test_has_tool():
    action_log = ActionLog(
        total_calls=1,
        actions=[
            Action(sequence_number=1, function_name="read_file", arguments={}),
        ],
        summary=ActionSummary(unique_tools_used={"read_file"}),
    )
    
    assert ActionTracker.has_tool(action_log, "read_file")
    assert not ActionTracker.has_tool(action_log, "edit_file")


def test_validate_arguments_structure():
    valid_action = Action(
        sequence_number=1,
        function_name="read_file",
        arguments={"file_path": "test.txt"},
    )
    
    errors = ActionTracker.validate_arguments_structure(valid_action)
    assert len(errors) == 0


def test_find_actions_by_tool():
    action_log = ActionLog(
        total_calls=3,
        actions=[
            Action(sequence_number=1, function_name="read_file", arguments={"file": "a"}),
            Action(sequence_number=2, function_name="edit_file", arguments={}),
            Action(sequence_number=3, function_name="read_file", arguments={"file": "b"}),
        ],
    )
    
    read_actions = ActionTracker.find_actions_by_tool(action_log, "read_file")
    
    assert len(read_actions) == 2
    assert read_actions[0].sequence_number == 1
    assert read_actions[1].sequence_number == 3


def test_get_first_and_last_action():
    action_log = ActionLog(
        total_calls=3,
        actions=[
            Action(sequence_number=1, function_name="read_file", arguments={}),
            Action(sequence_number=2, function_name="search_code", arguments={}),
            Action(sequence_number=3, function_name="edit_file", arguments={}),
        ],
    )
    
    first = ActionTracker.get_first_action(action_log)
    assert first.function_name == "read_file"
    
    last = ActionTracker.get_last_action(action_log)
    assert last.function_name == "edit_file"


def test_merge_action_logs():
    log1 = ActionLog(
        total_calls=2,
        actions=[
            Action(sequence_number=1, function_name="read_file", arguments={}),
            Action(sequence_number=2, function_name="edit_file", arguments={}),
        ],
    )
    
    log2 = ActionLog(
        total_calls=1,
        actions=[
            Action(sequence_number=1, function_name="search_code", arguments={}),
        ],
    )
    
    merged = ActionTracker.merge_action_logs([log1, log2])
    
    assert merged.total_calls == 3
    assert len(merged.actions) == 3
    assert merged.actions[0].sequence_number == 1
    assert merged.actions[1].sequence_number == 2
    assert merged.actions[2].sequence_number == 3

