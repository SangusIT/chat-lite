from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from datetime import datetime

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Time</title>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
    </head>
    <body>
        <h1>Time</h1>
        <p id="time"></p>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                $("#time").text(event.data)
            };
            setInterval(() => {
                var dateTime = new Date();
                // $("#test-form").submit()
                // console.log(dateTime)
                ws.send('test')
            }, 1000)
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    while True:
        data = await websocket.receive_text()
        test = datetime.now().isoformat()
        await websocket.send_text(f"Time is now: {test}")