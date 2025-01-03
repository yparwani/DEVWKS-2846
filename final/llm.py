from openai import AsyncAzureOpenAI

import ciscotools

# Azure OpenAI Configuration (Assumed client and deployment are configured)
client = AsyncAzureOpenAI(
    api_key="",
    api_version="2024-10-21",
    azure_endpoint="https://ciscolive25.openai.azure.com/",
)
deployment_name = "gpt-4o"


async def call_llm_stream(message_history: list):
    stream = await client.chat.completions.create(
        model=deployment_name,
        messages=message_history,
        tools=ciscotools.cisco_tools,
        tool_choice="auto",
        stream=True,
    )
    return stream
