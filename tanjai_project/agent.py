import os
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.tools import google_search, agent_tool, VertexAiSearchTool

load_dotenv()

_dir = os.path.dirname(os.path.abspath(__file__))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(_dir, "credentials.json")

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
GCP_PROJECT_ID = "intnonprd-goog-tanjai"
DATASTORE_PATH = (
    f"projects/{GCP_PROJECT_ID}"
    "/locations/global/collections/default_collection"
    "/dataStores/tanjai-adk-test-internship_1776309751289"
)
# Credentials are set via GOOGLE_APPLICATION_CREDENTIALS env var

# ─────────────────────────────────────────────
# SPECIALIST 1: Internet Search (Google Search + Wikipedia)
# ─────────────────────────────────────────────
search_specialist = LlmAgent(
    name="SearchAgent",
    model="gemini-3-flash-preview",
    description="ค้นหาข้อมูลทันสมัยจากอินเทอร์เน็ต เช่น ข่าวสาร ราคา หรือข้อมูลทั่วไปที่อัปเดต",
    instruction="""
    You are an internet research specialist. 
    Use Google Search to find current, factual information.
    Always include source URLs in your response.
    Respond in the same language the user used.
    """,
    tools=[google_search],
)

# ─────────────────────────────────────────────
# SPECIALIST 2: Organization Knowledge (Vertex AI Search)
# Note: VertexAiSearchTool must be the ONLY tool on its agent
# ─────────────────────────────────────────────
org_knowledge_specialist = LlmAgent(
    name="OrgKnowledgeAgent",
    model="gemini-3-flash-preview",
    description="ค้นหาข้อมูลภายในองค์กร เช่น นโยบาย กระบวนการ คู่มือ หรือเอกสารภายใน",
    instruction="""
    You are an internal knowledge specialist for the organization.
    Use the Vertex AI Search tool to find information from internal documents, 
    policies, and organizational knowledge bases.
    Always cite which document or source the information came from.
    Respond in the same language the user used.
    """,
    tools=[VertexAiSearchTool(data_store_id=DATASTORE_PATH)],
)

# ─────────────────────────────────────────────
# SPECIALIST 3: Image Generation
# ─────────────────────────────────────────────
image_specialist = LlmAgent(
    name="ImageGenAgent",
    model="gemini-3-flash-preview",
    description="สร้างภาพจาก prompt ที่ผู้ใช้ระบุ",
    instruction="""
    Generate the requested image based on the user's description.
    Save the generated image as a session artifact named 'generated_image.png'.
    Confirm to the user that the image has been generated.
    """,
)

# ─────────────────────────────────────────────
# ROOT AGENT: TanjAI
# ─────────────────────────────────────────────
root_agent = LlmAgent(
    name="TanjAI",
    model="gemini-3-flash-preview",
    description="TanjAI ผู้ช่วยในที่ทำงานที่ฉลาดและรอบรู้",
    instruction="""
    คุณคือ TanjAI (แทนใจ) ผู้ช่วย AI สำหรับองค์กร ที่มีความสามารถดังนี้:

    1. **ตอบคำถามทั่วไป** — ใช้ความรู้ของตัวเอง (LLM base knowledge) ตอบได้เลย
    
    2. **ข้อมูลทันสมัยจากอินเทอร์เน็ต** — ถ้าต้องการข้อมูลปัจจุบัน ข่าว หรือข้อเท็จจริงที่อัปเดต 
       ให้ delegate ไปที่ 'SearchAgent'
    
    3. **เอกสารที่ผู้ใช้อัปโหลด** — คุณอ่านไฟล์ได้โดยตรง รองรับ:
       - PDF
       - Microsoft Office (Word, Excel, PowerPoint)
       - รูปภาพ (PNG, JPG, ฯลฯ)
       วิเคราะห์และสรุปเนื้อหาไฟล์ได้ทันที ไม่ต้อง delegate
    
    4. **ข้อมูลองค์กร (Knowledge Base)** — ถ้าถามเกี่ยวกับนโยบาย กระบวนการ หรือข้อมูลภายในองค์กร
       ให้ delegate ไปที่ 'OrgKnowledgeAgent'
    
    5. **สร้างภาพ** — ถ้าต้องการสร้างภาพหรือ visual
       ให้ delegate ไปที่ 'ImageGenAgent'

    **กฎการตอบ:**
    - ถ้าผู้ใช้พูดภาษาไทย → ตอบภาษาไทยอย่างเป็นทางการ (ลงท้ายด้วย ครับ/ค่ะ)
    - ถ้าผู้ใช้พูดภาษาอังกฤษ → ตอบภาษาอังกฤษ
    - อ้างอิงแหล่งที่มาเสมอเมื่อใช้ข้อมูลจาก Search หรือ Knowledge Base
    """,
    tools=[
        agent_tool.AgentTool(agent=search_specialist),
        agent_tool.AgentTool(agent=org_knowledge_specialist),
        agent_tool.AgentTool(agent=image_specialist),
    ],
)