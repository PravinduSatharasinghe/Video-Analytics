import os
from aiohttp import web
from livekit import api
from dotenv import load_dotenv

load_dotenv(".env")


async def handle_index(request):
    with open("index.html", "r", encoding="utf-8") as f:
        return web.Response(text=f.read(), content_type="text/html")


async def handle_token(request):
    room_name = request.query.get("room", "analytics-room")
    identity = "console-" + os.urandom(4).hex()

    token = (
        api.AccessToken(os.getenv("LIVEKIT_API_KEY"), os.getenv("LIVEKIT_API_SECRET"))
        .with_identity(identity)
        .with_name("Console User")
        .with_grants(api.VideoGrants(room_join=True, room=room_name))
    )

    # Create the room and dispatch the agent
    try:
        async with api.LiveKitAPI() as lkapi:
            await lkapi.room.create_room(api.CreateRoomRequest(name=room_name))
            await lkapi.agent_dispatch.create_dispatch(
                api.CreateAgentDispatchRequest(
                    agent_name="vision_analyze",
                    room=room_name,
                )
            )
    except Exception as e:
        print(f"Agent dispatch note: {e}")

    return web.json_response({"token": token.to_jwt(), "url": os.getenv("LIVEKIT_URL")})


app = web.Application()
app.add_routes([web.get("/", handle_index), web.get("/token", handle_token)])

if __name__ == "__main__":
    print("Video Analytics Console → http://localhost:8080")
    web.run_app(app, port=8080)
