import websocket
import json


def on_message(ws, message):
    try:
        message_data = json.loads(message)
        print(f"Received message: {message_data}")
    except json.JSONDecodeError:
        print(f"Received message: {message}")


def on_error(ws, error):
    print(f"Error: {error}")


def on_close(ws):
    print("WebSocket closed")


def on_open(ws):
    print("WebSocket connected")


if __name__ == "__main__":
    websocket.enableTrace(True)  # 디버그 메시지 활성화

    story_id = 1  # 연결할 스토리 ID 설정

    ws_url = f"ws://127.0.0.1:8000/ws/chat/{story_id}/"

    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
