import ast
import chainlit as cl

import llm
import ciscotools

MAX_ITER = 2


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Get PSIRTs released in January 2025",
            message="Get me all the psirts released in the January 2025",
            icon="https://img.icons8.com/color/48/warning-shield.png",
        ),
        cl.Starter(
            label="Get bugs related to Catalyst 9800",
            message="Cisco Catalyst 9800 bugs",
            icon="https://img.icons8.com/color/48/ladybird.png",
        ),
    ]


@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [
            {
                "role": "system",
                "content": "You are a helpful assistant for information on Cisco Defects and PSIRTs. For queries on PSIRT you can use get_security_advisories and for defects you can use get_bugs_by_keyword.",
            }
        ],
    )


@cl.on_message
async def on_message(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    cur_iter = 0
    # Allow for limited number tool calls before exiting
    while cur_iter < MAX_ITER:
        stream = await llm.call_llm_stream(message_history)
        tool_call_id = await stream_response(stream, message_history)
        # if no tool was called, its likely the conversation is over and response has been sent
        if not tool_call_id:
            break
        cur_iter += 1

    # Update message history for followup messages
    cl.user_session.set("message_history", message_history)


async def stream_response(stream, message_history: list):
    final_answer = cl.Message(content="", author="Answer")
    function_data = {"name": "", "arguments": ""}
    tool_call_id = None

    async for part in stream:
        if part.choices:
            new_delta = part.choices[0].delta
            # Check if tool is being called - in stream mode, tool name and arguments are streamed chunk by chunk
            tool_call = new_delta.tool_calls and new_delta.tool_calls[0]
            function = tool_call and tool_call.function
            if tool_call and tool_call.id:
                tool_call_id = tool_call.id

            if function:
                if function.name:
                    function_data["name"] = function.name
                else:
                    function_data["arguments"] += function.arguments

            if new_delta.content:
                if not final_answer.content:
                    await final_answer.send()
                await final_answer.stream_token(new_delta.content)

    if tool_call_id:
        await call_tool(
            message_history,
            tool_call_id,
            **function_data,
        )

    if final_answer.content:
        await final_answer.update()
        message_history.append({"role": "assistant", "content": final_answer.content})

    return tool_call_id


@cl.step(type="tool")
async def call_tool(message_history: list, tool_call_id: str, name: str, arguments: str):
    arguments = ast.literal_eval(arguments)

    current_step = cl.context.current_step
    current_step.name = name
    current_step.input = arguments

    tool_function = getattr(ciscotools, name, None)
    if tool_function:
        try:
            function_response = await tool_function(**arguments)
        except Exception as e:
            function_response = {"error": str(e)}

    current_step.output = function_response
    current_step.language = "json"

    message_history.append(
        {
            "role": "function",
            "name": name,
            "content": function_response,
            "tool_call_id": tool_call_id,
        }
    )
