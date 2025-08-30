#!/usr/bin/env python3
"""
Web interface for LangGraph Table Agent
Provides a simple web UI to interact with the agent
"""

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
from pathlib import Path
from agents.graph_agent import build_graph
from langchain_core.messages import HumanMessage, AIMessage
import os

app = FastAPI(title="LangGraph Table Agent")

# Build the agent graph once
print("Initializing LangGraph agent...")
graph = None
try:
    graph = build_graph()
    print("Agent initialized successfully")
except Exception as e:
    print(f"Warning: Could not initialize agent: {e}")

# Serve output files
if os.path.exists("outputs"):
    app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

@app.get("/")
async def home():
    """Serve the web interface"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <title>LangGraph Table Agent</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            width: 90%;
            max-width: 800px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 { font-size: 24px; margin-bottom: 5px; }
        .header p { opacity: 0.9; font-size: 14px; }
        .chat-container {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        .message {
            margin: 10px 0;
            padding: 12px 16px;
            border-radius: 12px;
            max-width: 70%;
            word-wrap: break-word;
        }
        .user-message {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .agent-message {
            background: white;
            border: 1px solid #e0e0e0;
            margin-right: auto;
        }
        .agent-message pre {
            background: #f5f5f5;
            padding: 8px;
            border-radius: 4px;
            overflow-x: auto;
            margin: 8px 0;
        }
        .agent-message img {
            max-width: 100%;
            margin: 8px 0;
            border-radius: 8px;
        }
        .input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
        }
        input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s;
        }
        input:focus { border-color: #667eea; }
        button {
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s;
        }
        button:hover { transform: scale(1.05); }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        .status {
            padding: 10px 20px;
            background: #fff3cd;
            color: #856404;
            text-align: center;
            font-size: 14px;
        }
        .examples {
            padding: 10px 20px;
            background: #e8f4f8;
            font-size: 13px;
            color: #666;
        }
        .examples strong { color: #333; }
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 LangGraph Table Agent</h1>
            <p>AI-powered data analysis and visualization</p>
        </div>
        
        <div class="examples">
            <strong>Try:</strong> 
            "What data files are available?" | 
            "Analyze the sales data" | 
            "Create a chart showing trends"
        </div>
        
        <div id="status" class="status" style="display: none;"></div>
        
        <div id="chat" class="chat-container"></div>
        
        <div class="input-container">
            <input type="text" id="message" placeholder="Ask about your data..." 
                   onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()" id="sendBtn">Send</button>
        </div>
    </div>

    <script>
        let ws = null;
        let isConnected = false;
        
        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onopen = () => {
                isConnected = true;
                setStatus('Connected to agent', 'success');
                document.getElementById('sendBtn').disabled = false;
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                if (data.type === 'response') {
                    addMessage(data.content, 'agent');
                } else if (data.type === 'error') {
                    setStatus('Error: ' + data.content, 'error');
                    addMessage('Error: ' + data.content, 'agent');
                } else if (data.type === 'status') {
                    setStatus(data.content, 'info');
                }
                
                document.getElementById('sendBtn').disabled = false;
                document.getElementById('sendBtn').innerHTML = 'Send';
            };
            
            ws.onerror = (error) => {
                setStatus('Connection error', 'error');
                isConnected = false;
            };
            
            ws.onclose = () => {
                setStatus('Disconnected. Reconnecting...', 'warning');
                isConnected = false;
                setTimeout(connect, 3000);
            };
        }
        
        function sendMessage() {
            const input = document.getElementById('message');
            const message = input.value.trim();
            
            if (!message || !isConnected) return;
            
            addMessage(message, 'user');
            
            document.getElementById('sendBtn').disabled = true;
            document.getElementById('sendBtn').innerHTML = '<span class="spinner"></span>Processing...';
            
            ws.send(JSON.stringify({
                type: 'message',
                content: message
            }));
            
            input.value = '';
        }
        
        function addMessage(content, sender) {
            const chat = document.getElementById('chat');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            
            // Convert markdown-like formatting
            content = content.replace(/```(.*?)```/gs, '<pre>$1</pre>');
            content = content.replace(/`([^`]+)`/g, '<code>$1</code>');
            
            // Check for image references
            if (content.includes('.png') || content.includes('.jpg')) {
                content = content.replace(/(outputs\/[^\s]+\.(png|jpg|jpeg))/g, 
                    '<br><img src="/$1" alt="Generated chart"><br>');
            }
            
            messageDiv.innerHTML = content;
            chat.appendChild(messageDiv);
            chat.scrollTop = chat.scrollHeight;
        }
        
        function setStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.style.display = 'block';
            
            if (type === 'success') {
                status.style.background = '#d4edda';
                status.style.color = '#155724';
            } else if (type === 'error') {
                status.style.background = '#f8d7da';
                status.style.color = '#721c24';
            } else if (type === 'warning') {
                status.style.background = '#fff3cd';
                status.style.color = '#856404';
            }
            
            if (type === 'success') {
                setTimeout(() => {
                    status.style.display = 'none';
                }, 3000);
            }
        }
        
        // Connect on load
        connect();
        
        // Add some welcome messages
        setTimeout(() => {
            addMessage("Hello! I'm your data analysis assistant. I can help you analyze CSV files and create visualizations. What would you like to know?", 'agent');
        }, 500);
    </script>
</body>
</html>
    """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    if not graph:
        await websocket.send_json({
            "type": "error",
            "content": "Agent not initialized. Please check LLM configuration."
        })
        return
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            if data["type"] == "message":
                user_message = data["content"]
                
                # Send status
                await websocket.send_json({
                    "type": "status",
                    "content": "Processing your request..."
                })
                
                try:
                    # Process with agent
                    messages = [HumanMessage(content=user_message)]
                    result = graph.invoke({"messages": messages})
                    
                    # Extract response
                    if result and "messages" in result:
                        last_message = result["messages"][-1]
                        
                        if isinstance(last_message, AIMessage):
                            response = last_message.content
                        else:
                            response = str(last_message.content)
                        
                        # Check if any files were created
                        if "outputs" in response or ".png" in response or ".jpg" in response:
                            response += "\n\n📊 Chart saved to outputs folder."
                    else:
                        response = "I processed your request but couldn't generate a response."
                    
                    # Send response
                    await websocket.send_json({
                        "type": "response",
                        "content": response
                    })
                    
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "content": f"Error processing request: {str(e)}"
                    })
    
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_initialized": graph is not None
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting LangGraph Table Agent Web UI...")
    print("Access the interface at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)