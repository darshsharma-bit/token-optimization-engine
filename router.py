from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
import uvicorn

app = FastAPI(title="ATP Network Router")

class ConnectionManager:
    def __init__(self):
        # Stores active agent connections { "agent_id": WebSocket }
        self.active_connections: dict[str, WebSocket] = {}
        # Stores connections for our monitoring dashboard
        self.observers: list[WebSocket] = [] 

    async def connect(self, agent_id: str, websocket: WebSocket):
        await websocket.accept()
        if agent_id == "observer":
            self.observers.append(websocket)
            print("[NETWORK] Dashboard Observer connected.")
        else:
            self.active_connections[agent_id] = websocket
            print(f"[NETWORK] Agent '{agent_id}' connected.")

    def disconnect(self, agent_id: str, websocket: WebSocket):
        if agent_id == "observer":
            self.observers.remove(websocket)
        else:
            del self.active_connections[agent_id]
            print(f"[NETWORK] Agent '{agent_id}' disconnected.")

    async def route_packet(self, packet_dict: dict):
        sender = packet_dict['h']['s']
        receiver = packet_dict['h']['r']
        
        # 1. Forward to the intended receiver agent
        if receiver in self.active_connections:
            await self.active_connections[receiver].send_json(packet_dict)
            print(f"[ROUTER] Routed ATP packet from {sender} -> {receiver}")
        else:
            print(f"[ROUTER] Error: Receiver '{receiver}' is not online.")

        # 2. Broadcast a copy to our Streamlit dashboard so you can monitor the traffic
        for observer in self.observers:
            await observer.send_json(packet_dict)

manager = ConnectionManager()

@app.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    await manager.connect(agent_id, websocket)
    try:
        while True:
            # Wait for an ATP packet to arrive
            data = await websocket.receive_text()
            packet_dict = json.loads(data)
            
            # Instantly route it to the correct destination
            await manager.route_packet(packet_dict)
            
    except WebSocketDisconnect:
        manager.disconnect(agent_id, websocket)

if __name__ == "__main__":
    print("Starting ATP Router on ws://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)