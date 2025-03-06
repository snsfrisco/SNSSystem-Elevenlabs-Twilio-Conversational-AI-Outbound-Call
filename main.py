
import uvicorn
import os, time
import json, traceback
from dotenv import load_dotenv
from twilio.rest import Client
from elevenlabs import ElevenLabs
from fastapi.responses import HTMLResponse
from database import (CallRecord, get_call)
from fastapi import FastAPI, Request, WebSocket
from starlette.websockets import WebSocketDisconnect
from twilio_audio_interface import TwilioAudioInterface
from twilio.twiml.voice_response import VoiceResponse, Connect
from elevenlabs.conversational_ai.conversation import Conversation, ConversationInitiationData
# Load environment variables
load_dotenv()

# Twilio Credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# ElevenLabs Credentials
ELEVENLABS_API_KEY = os.getenv("ELEVENLABSAPI_KEY", None)
ELEVEN_LABS_AGENT_ID = os.getenv("ELEVENLABSAGENT_ID", None)

# Initialize FastAPI app
app = FastAPI()

# Initialize Twilio Client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def on_agent_say_goodbye(text, call_sid):
    print(f"Agent: {text}")
    time.sleep(8)
    if "Have a great day".lower() in text.lower() or "Goodbye".lower() in text.lower():
        twilio_client.calls(call_sid).update(status="completed") 
        raise Exception("Call Ended!!!")
        
### **🎙️ WebSocket Route: Handles Audio Streaming**
@app.websocket("/media-stream/{call_sid}")
async def handle_media_stream(websocket: WebSocket, call_sid: str):
    """Manages Twilio WebSocket connection"""
    await websocket.accept()

    # uncomment if you need to pass your custom configuration to elevenlabs agent.
    # Fetch call record using call_sid from URL
    # call_record = get_call(call_sid)  
    # You can use your call data for the user details to be pass on elevenlabs

    # uncomment if you need to pass your custom configuration to elevenlabs agent.
    # Step 1: Set dynamic configuration based on call record
    # if call_record:
    #     dynamic_vars = {
    #         "user_name": call_record.first_name,
    #     }
    # else:
    #     dynamic_vars = {
    #         "user_name": "Unknown",
    #     }
    
    # uncomment if you need to pass your custom configuration to elevenlabs agent.
    # config = ConversationInitiationData(dynamic_variables=dynamic_vars)
    
    audio_interface = TwilioAudioInterface(websocket)
    
    eleven_labs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

    try:
        conversation = Conversation(
            # config=config, # uncomment if you need to pass your custom configuration to elevenlabs agent.
            requires_auth=True,
            client=eleven_labs_client,
            agent_id=ELEVEN_LABS_AGENT_ID,
            audio_interface=audio_interface,
            callback_agent_response=lambda text: on_agent_say_goodbye(text, call_sid),
            callback_user_transcript=lambda text: print(f"User: {text}"),
        )
        conversation.start_session()
        print("Conversation started")
        async for message in websocket.iter_text():
            if not message:
                continue
            await audio_interface.handle_twilio_message(json.loads(message))
            

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception:
        print("Error occurred in WebSocket handler:")
        traceback.print_exc()
    finally:
        try:
            if not websocket.client_state.name == "DISCONNECTED": 
                print("❌ Closing WebSocket...")
                await websocket.close()
            print("Conversation getting end...")
            conversation.end_session()
            conversation.wait_for_session_end()
            print("Conversation ended.")
        except Exception:
            print("Error ending conversation session:")
            traceback.print_exc()

### **📞 Twilio Webhook: Handles Outgoing Call Status**
@app.post("/twilio/call-status")
async def call_status_webhook(request: Request):
    """
    ✅ Handles Twilio call status updates and detects if a VoIP call was auto-answered.
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "")
    call_status = form_data.get("CallStatus", "")
    answered_by = form_data.get("AnsweredBy", "unknown")  # ✅ Detect human vs machine
    print(f"📞 CallSid: {call_sid} | Status: {call_status} | AnsweredBy: {answered_by}")
    if call_status == "ringing":
        print("🔔 Phone is ringing!")
    elif call_status == "in-progress" and answered_by == "machine":
        print("⚠️ VoIP Call was auto-answered by a machine!")
        print("❌ Hanging up VoIP auto-answered call.")
        twilio_client.calls(call_sid).update(status="completed")
    elif call_status == "no-answer":
        print("⚠️ The user did not pick up the call!")
    elif call_status == "busy":
        print("🚫 User is on another call!")
    elif call_status == "completed":
        print("✅ Call completed successfully.")
    elif call_status == "failed":
        print("❌ Call failed. Wrong number?")
    return {"message": "Status received"}
    
### **📞 Twilio Webhook: Handles Outgoing Call**
@app.post("/twilio/outbound_call")
async def handle_outbound_call(request: Request):
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "Unknown")
    from_number = form_data.get("From", "Unknown")
    response = VoiceResponse()
    connect = Connect()
    connect.stream(url=f"wss://{request.url.hostname}/media-stream/{call_sid}")
    response.append(connect)
    print(f"Incoming call: CallSid={call_sid}, From={from_number}")
    return HTMLResponse(content=str(response), media_type="application/xml")

### 📞 Main API: Handle Outbound Calls & Store Data**
@app.post("/make-outbound-call")
async def make_outbound_call(request: Request):
    """
    1️⃣ Receive API request payload.
    2️⃣ Store the call details in the database.
    3️⃣ Initiate the outbound call via Twilio.
    4️⃣ Respond back with call details.
    """ 
    data = await request.json()
    
    phone_number = data.get("phone_number")  # Destination phone number
    
    first_name = data.get("first_name")  # User name (if provided)
    
    last_name = data.get("last_name")  # User name (if provided)
    
    name = first_name +" "+ last_name    # User name (if provided)
    
    email = data.get("email", None)  # Email (if provided)
    
    if not phone_number:
        return {"error": "Missing 'to' phone number."}
    
    if not first_name:
        return {"error": "Missing 'to' first name."}
    
    if not last_name:
        return {"error": "Missing 'to' last name."}
    
    if not email:
        return {"error": "Missing 'to' email."}
    
    # Initiate Twilio Call
    try:
        call = twilio_client.calls.create(
            to=phone_number,
            from_=TWILIO_PHONE_NUMBER,
            url=f"https://{request.headers['host']}/twilio/outbound_call",
            status_callback=f"https://{request.headers['host']}/twilio/call-status",
            status_callback_event=["initiated", "ringing", "answered", "completed"],
            machine_detection="DetectMessageEnd",
            timeout=15
        )
        callRecord = CallRecord()
        callRecord.call_sid =  call.sid
        callRecord.name =  name
        callRecord.first_name =  first_name
        callRecord.last_name =  last_name
        callRecord.email =  email
        callRecord.phone_number =  phone_number
        callRecord.call_type =  "outbound"
        callRecord.save()
        print(f"[Twilio] Outbound call initiated: {call.sid} for {phone_number}")
        return {"message": f"Call initiated for {name} ({phone_number}) with email {email}.", "callSid": call.sid}
    except Exception as error:
        print("[Twilio] Error initiating call:", error)
        return {"error": "Failed to initiate call"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8082)
