import json
import tools
from openai import AzureOpenAI

# Azure OpenAI Configuration (Assumed client and deployment are configured)
client = AzureOpenAI(api_key="", api_version="2024-10-21", azure_endpoint="https://ciscolive25.openai.azure.com/")
deployment_name = "gpt-4o"


def run_conversation(user_message: str):
    # Initial user message
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant for information on Cisco Defects and PSIRTs. For queries on PSIRT you can use get_security_advisories and for defects you can use get_bugs_by_keyword.",
        },
        {"role": "user", "content": user_message},
    ]
    # First API call: Ask the model to use the function
    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        tools=tools.cisco_tools,
        tool_choice="auto",  # Let the model choose the appropriate tool
    )
    # Process the model's response
    response_message = response.choices[0].message
    messages.append(response_message)
    print("Model's response:")
    print(response_message)
    # Handle tool calls
    if response_message.tool_calls:
        for tool_call in response_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            print(f"Function arguments: {tool_args}")
            tool_function = getattr(tools, tool_name, None)
            # Call the appropriate tool function
            if tool_function:
                try:
                    tool_result = tool_function(**tool_args)
                    # Send the result back to the model
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_name,
                            "content": tool_result,
                        }
                    )
                except Exception as e:
                    print(f"Error while executing tool '{tool_name}': {e}")
            else:
                print(f"Tool '{tool_name}' is not recognized.")
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_name,
                        "content": "Information not available.",
                    }
                )
    # Second API call: Get the final response from the model
    final_response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
    )
    return final_response.choices[0].message.content


if __name__ == "__main__":
    print("Test 1 : PSIRT query")
    print(run_conversation("Get me the PSIRTs for Cisco for November 2024"))
    print("Test 2 : Defect query")
    print(run_conversation("Find bugs related to memory leaks for asr 9000"))
