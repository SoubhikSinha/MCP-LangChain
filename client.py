from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

from dotenv import load_dotenv
load_dotenv()

import os
import time
import asyncio
import subprocess

async def main():
    # Start the weather HTTP server automatically (streamable-http needs a running server)
    weather_proc = subprocess.Popen(
        ["python", "weather.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(3)  # Wait for server to be ready

    # Initialize MCP Client
    mcp_client = MultiServerMCPClient(
        {
          "math":{
            "command" : "python", # This is the command to start the server
            "args" : ["mathServer.py"], # These are the arguments to start the server
            "transport" : "stdio" # stdio is used for the CLI tool mcp
          },
          "weather":{
            "url" : "http://localhost:8000/mcp", # This is the url of the server
            "transport" : "streamable-http" # streamable-http connects to a running HTTP server
          }
        })

    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

    # Calling the LLM
    tools = await mcp_client.get_tools()
    model = ChatGroq(model = "qwen/qwen3-32b")
    agent = create_react_agent(
        model,
        tools,
        prompt = "You are a helpful assistant. Only use the tools explicitly provided to you. Call one tool at a time with plain integer or string arguments only — never nest tool calls or pass a function as an argument. Solve multi-step problems by calling tools sequentially."
    )

    math_response = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": "Use the calculate tool to compute: (10 + 4) * 67"}
        ]
    })

    print("Math Response : ", math_response["messages"][-1].content)

    weather_response = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": "What is the weather in Dallas?"}
        ]
    })

    print("Weather Response : ", weather_response["messages"][-1].content)

    # Stop the weather server when done
    weather_proc.terminate()


# run the async main function
asyncio.run(main())
