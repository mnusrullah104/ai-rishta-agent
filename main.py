import os
import google.generativeai as genai
import requests
import chainlit as cl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ULTRAMSG_INSTANCE_ID = os.getenv("ULTRAMSG_INSTANCE_ID")
ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Chat Start
@cl.on_chat_start
async def start():
    cl.user_session.set("step", "name")
    await cl.Message("🧕 Welcome to AI Rishta Finder!\n\nWhat is your full name?").send()

# Handle incoming messages
@cl.on_message
async def handle_message(message: cl.Message):
    step = cl.user_session.get("step")
    content = message.content.strip()

    if step == "name":
        cl.user_session.set("name", content)
        cl.user_session.set("step", "age")
        await cl.Message("🎂 What is your age?").send()

    elif step == "age":
        cl.user_session.set("age", content)
        cl.user_session.set("step", "gender")
        await cl.Message("🚻 Gender (M/F)?").send()

    elif step == "gender":
        cl.user_session.set("gender", content)
        cl.user_session.set("step", "education")
        await cl.Message("🎓 Your education?").send()

    elif step == "education":
        cl.user_session.set("education", content)
        cl.user_session.set("step", "preferences")
        await cl.Message("💬 Any partner preferences?").send()

    elif step == "preferences":
        cl.user_session.set("preferences", content)
        cl.user_session.set("step", "phone")
        await cl.Message("📞 Your WhatsApp number (e.g. 923001234567)?").send()

    elif step == "phone":
        cl.user_session.set("phone", content)
        cl.user_session.set("step", "done")
        await cl.Message("⏳ Generating your rishta suggestion...").send()

        # Create profile dictionary
        profile = {
            "name": cl.user_session.get("name"),
            "age": cl.user_session.get("age"),
            "gender": cl.user_session.get("gender"),
            "education": cl.user_session.get("education"),
            "preferences": cl.user_session.get("preferences"),
            "contact": cl.user_session.get("phone"),
        }

        # Build prompt
        prompt = f"""
You are a Rishta agent. Write a respectful and warm WhatsApp message suggesting a rishta match using the following profile:

Name: {profile['name']}
Age: {profile['age']}
Gender: {profile['gender']}
Education: {profile['education']}
Partner Preferences: {profile['preferences']}

Tone: Respectful, family-oriented, cultural.
        """

        try:
            # ✅ Use correct Gemini model name
            model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")
            response = model.generate_content(prompt)
            message_text = response.text.strip()
        except Exception as e:
            await cl.Message(f"❌ Gemini Error: {e}").send()
            return

        await cl.Message(f"📩 Rishta Suggestion:\n\n{message_text}").send()

        # Send to WhatsApp using UltraMsg
        try:
            url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
            payload = {
                "token": ULTRAMSG_TOKEN,
                "to": profile["contact"],
                "body": message_text
            }
            r = requests.post(url, data=payload)
            if r.status_code == 200:
                await cl.Message("✅ Sent to WhatsApp via UltraMsg!").send()
            else:
                await cl.Message(f"❌ WhatsApp failed: {r.text}").send()
        except Exception as e:
            await cl.Message(f"❌ Error sending WhatsApp: {e}").send()

    else:
        await cl.Message("✅ You already submitted your profile.").send()
