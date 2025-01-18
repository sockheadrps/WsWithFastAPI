import functools
import json
from typing import Any
from enum import Enum
import asyncio

from rich import print  # Import Rich's print function
from rich.syntax import Syntax
from rich.panel import Panel
from pydantic import BaseModel
from starlette.websockets import WebSocket





def json_printer(func):
    """
    Decorator to log function calls and return values with Rich formatting.
    Excludes WebSocket objects from logging.
    Handles both asynchronous and synchronous functions.
    """
    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            func_name = func.__name__

            # Initialize the log data structure
            log_data = {
                "function": func_name,
                "args": [],
                "kwargs": {}
            }

            # Determine if the first argument is 'self' (i.e., a class instance)
            skip_indices = 0
            if args:
                first_arg = args[0]
                if hasattr(first_arg, '__class__') and not isinstance(first_arg, BaseModel):
                    skip_indices = 1  # Skip 'self'

            # Process positional arguments
            for i, arg in enumerate(args):
                if i < skip_indices:
                    continue  # Skip 'self'
                # Exclude WebSocket objects
                if isinstance(arg, WebSocket):
                    continue
                processed_arg = _process_value(arg)
                log_data["args"].append(processed_arg)

            # Process keyword arguments
            for key, value in kwargs.items():
                # Exclude WebSocket objects
                if isinstance(value, WebSocket):
                    continue
                processed_value = _process_value(value)
                log_data["kwargs"][key] = processed_value

            # Serialize log data to JSON string
            try:
                json_str = json.dumps(log_data, indent=4, sort_keys=True)
            except (TypeError, ValueError) as e:
                json_str = f"Failed to serialize log data: {e}"

            # Create a Syntax object with JSON highlighting
            syntax = Syntax(json_str, "json", theme="monokai",
                            line_numbers=True, word_wrap=True)

            # Create a Panel to contain the syntax-highlighted JSON
            call_panel = Panel(
                syntax,
                title=f"Function Call: {func_name}",
                subtitle="Arguments and Keyword Arguments",
                expand=False,
                border_style="green",
                padding=(1, 2)
            )

            # Print the call panel using Rich's print
            print(call_panel)

            # Call the actual function
            result = await func(*args, **kwargs)

            # Process and log the return value
            processed_result = _process_value(result)

            # Handle return value logging
            if processed_result is not None:
                try:
                    result_json_str = json.dumps(
                        {"return": processed_result}, indent=4, sort_keys=True)
                except (TypeError, ValueError) as e:
                    result_json_str = f"Failed to serialize return data: {e}"

                # Create a Syntax object for return value
                result_syntax = Syntax(
                    result_json_str, "json", theme="monokai", line_numbers=True, word_wrap=True)

                # Create a Panel for return value
                return_panel = Panel(
                    result_syntax,
                    title=f"Return Value: {func_name}",
                    subtitle="",
                    expand=False,
                    border_style="blue",
                    padding=(1, 2)
                )

                # Print the return value panel using Rich's print
                print(return_panel)
            else:
                # Log that the function returned None
                none_panel = Panel(
                    "return: null",
                    title=f"Return Value: {func_name}",
                    subtitle="",
                    expand=False,
                    border_style="blue",
                    padding=(1, 2)
                )
                print(none_panel)

            return result

        return async_wrapper
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            func_name = func.__name__

            # Initialize the log data structure
            log_data = {
                "function": func_name,
                "args": [],
                "kwargs": {}
            }

            # Determine if the first argument is 'self' (i.e., a class instance)
            skip_indices = 0
            if args:
                first_arg = args[0]
                if hasattr(first_arg, '__class__') and not isinstance(first_arg, BaseModel):
                    skip_indices = 1  # Skip 'self'

            # Process positional arguments
            for i, arg in enumerate(args):
                if i < skip_indices:
                    continue  # Skip 'self'
                # Exclude WebSocket objects
                if isinstance(arg, WebSocket):
                    # Convert WebSocket to string representation
                    arg = repr(arg)
                processed_arg = _process_value(arg)
                log_data["args"].append(processed_arg)

            # Process keyword arguments
            for key, value in kwargs.items():
                # Exclude WebSocket objects
                if isinstance(value, WebSocket):
                    # Convert WebSocket to string representation
                    value = repr(value)
                processed_value = _process_value(value)
                log_data["kwargs"][key] = processed_value

            # Serialize log data to JSON string
            try:
                json_str = json.dumps(log_data, indent=4, sort_keys=True)
            except (TypeError, ValueError) as e:
                json_str = f"Failed to serialize log data: {e}"

            # Create a Syntax object with JSON highlighting
            syntax = Syntax(json_str, "json", theme="monokai",
                            line_numbers=True, word_wrap=True)

            # Create a Panel to contain the syntax-highlighted JSON
            call_panel = Panel(
                syntax,
                title=f"Function Call: {func_name}",
                subtitle="Arguments and Keyword Arguments",
                expand=False,
                border_style="green",
                padding=(1, 2)
            )

            # Print the call panel using Rich's print
            print(call_panel)

            # Call the actual function
            result = func(*args, **kwargs)

            # Process and log the return value
            processed_result = _process_value(result)

            # Handle return value logging
            if processed_result is not None:
                try:
                    result_json_str = json.dumps(
                        {"return": processed_result}, indent=4, sort_keys=True)
                except (TypeError, ValueError) as e:
                    result_json_str = f"Failed to serialize return data: {e}"

                # Create a Syntax object for return value
                result_syntax = Syntax(
                    result_json_str, "json", theme="monokai", line_numbers=True, word_wrap=True)

                # Create a Panel for return value
                return_panel = Panel(
                    result_syntax,
                    title=f"Return Value: {func_name}",
                    subtitle="",
                    expand=False,
                    border_style="blue",
                    padding=(1, 2)
                )

                # Print the return value panel using Rich's print
                print(return_panel)
            else:
                # Log that the function returned None
                none_panel = Panel(
                    "return: null",
                    title=f"Return Value: {func_name}",
                    subtitle="",
                    expand=False,
                    border_style="blue",
                    padding=(1, 2)
                )
                print(none_panel)

            return result

        return sync_wrapper


def _process_value(value: Any):
    """
    Processes the value and returns a JSON-serializable object.
    Handles Pydantic models, dicts, lists/tuples, enums, and specific custom objects.
    Excludes specific fields like 'websocket' from Pydantic models.
    """
    # 0. Handle None explicitly
    if value is None:
        return None

    # 0.1 Handle primitive types
    if isinstance(value, (str, int, float, bool)):
        return value

    # 1. Pydantic Models
    if isinstance(value, BaseModel):
        dict_data = value.model_dump()  # Use .dict() if using Pydantic v1

        # Exclude 'websocket' field if present and convert specific fields to strings
        if dict_data.get('websocket') is not None:
            dict_data['websocket'] = str(dict_data['websocket'])

        if dict_data.get('client_id') is not None:
            dict_data['client_id'] = str(dict_data['client_id'])

        return dict_data

    # 2. Dictionaries
    if isinstance(value, dict):
        try:
            json.dumps(value)  # Ensure it's JSON-serializable
            # Optionally mask sensitive fields
            sensitive_keys = ['password', 'token', 'secret']
            for key in sensitive_keys:
                if key in value:
                    value[key] = '****'
            return value
        except (TypeError, ValueError):
            return str(value)

    # 3. Lists or Tuples
    if isinstance(value, (list, tuple)):
        try:
            json.dumps(value)  # Ensure it's JSON-serializable
            return value
        except (TypeError, ValueError):
            return [str(item) for item in value]

    # 4. Enums
    if isinstance(value, Enum):
        return {
            "type": value.__class__.__name__,
            "name": value.name,
            "value": value.value
        }

    # 5. Specific Custom Objects (excluding WebSocket)
    # Add handlers for other custom objects here if needed

    # 6. Attempt to use __dict__ as a fallback
    if hasattr(value, "__dict__"):
        try:
            dict_data = value.__dict__
            json.dumps(dict_data)  # Ensure it's serializable
            # Optionally exclude 'websocket' or other sensitive fields
            if 'websocket' in dict_data:
                del dict_data['websocket']
            return dict_data
        except (TypeError, ValueError):
            pass  # Serialization failed; proceed to fallback

    # 7. Fallback: Use a concise string representation
    return f"Not json {repr(value)}, type: {type(value)}"
