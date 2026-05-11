import logging
from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,  # <-- Import AutoSubscribe
    JobContext, 
    JobProcess, 
    Agent, 
    AgentSession, 
    AgentServer, 
    cli, 
    room_io
)
from livekit.plugins import silero, google

load_dotenv()

logger = logging.getLogger("gemini-live-vision")
logger.setLevel(logging.INFO)


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful voice AI assistant that can see the world around you.")


server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="my-agent")
async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    # 1. CONNECT FIRST!
    # By default, agents connect with AUDIO_ONLY. You MUST explicitly tell it to subscribe to Video.
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)

    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            model="gemini-2.5-flash-native-audio-preview-12-2025", # (See note below)
            proactivity=True,
            enable_affective_dialog=True
        ),
        vad=ctx.proc.userdata["vad"],
    )

    # 2. START THE SESSION AFTER THE ROOM IS CONNECTED
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            video_input=True, # You correctly had this!
        )
    )

    await session.generate_reply()


if __name__ == "__main__":
    cli.run_app(server)