import streamlit as st
from PIL import Image
import openai
import io

st.set_page_config(page_title="Forex Vision Wizard", layout="centered")
st.title("🧠 Forex Vision Wizard – AI Chart Analysis")

# Get API Key
openai.api_key = st.text_input("Enter your OpenAI API Key:", type="password")

uploaded_file = st.file_uploader("Upload market chart screenshot (PNG/JPG)", type=["png", "jpg", "jpeg"])
prompt = st.text_area("Enter your strategy prompt (e.g. 'Should I buy or sell using support & resistance?')")

if st.button("🔍 Analyze"):

    if not openai.api_key or not uploaded_file or not prompt.strip():
        st.error("🔴 Please provide API key, chart image, and a prompt.")
    else:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Chart", use_column_width=True)

        with st.spinner("Sending to AI..."):
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_bytes = buffered.getvalue()

            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",  # or "gpt-4o" if available
                messages=[
                    {"role": "system", "content": "You are an expert forex analyst."},
                    {"role": "user", "content": prompt}
                ],
                functions=[{
                    "name": "analyze_chart",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "trend": {"type": "string"},
                            "entry_price": {"type": "number"},
                            "take_profit": {"type": "number"},
                            "stop_loss": {"type": "number"},
                            "confidence": {"type": "number"}
                        },
                        "required": ["trend", "entry_price", "take_profit", "stop_loss"]
                    }
                }],
                function_call={"name": "analyze_chart"},
                user=img_bytes
            )

        msg = response.choices[0].message
        data = msg.function_call["arguments"]

        st.markdown("## 📊 AI Analysis Result")
        st.markdown(f"""
- Trend: {data["trend"]}
- Entry Price: {data["entry_price"]}
- Take Profit (TP): {data["take_profit"]}
- Stop Loss (SL): {data["stop_loss"]}
- Confidence: {data.get("confidence", 0)*100:.0f}%  
        """)
