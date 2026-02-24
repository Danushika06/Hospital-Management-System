from flask import jsonify
import json
import re
from groq import Groq
from config import Config

# Configure Groq API
client = Groq(api_key=Config.GROQ_API_KEY)

# Hospital System Prompt - Curated for medical assistance
HOSPITAL_SYSTEM_PROMPT = """You are MediBot, an AI medical assistant for City General Hospital Management System. Your role is to help patients, doctors, and staff with hospital-related queries.

**Your Capabilities:**
1. **Symptom Assessment**: Provide preliminary symptom analysis with appropriate medical advice
2. **Medicine Information**: Explain medications, dosages, uses, and side effects
3. **Appointment Guidance**: Help book, cancel, or reschedule appointments
4. **Hospital Information**: Answer questions about services, hours, and procedures
5. **Emergency Detection**: Identify critical situations requiring immediate medical attention

**Important Guidelines:**
- Always prioritize patient safety and well-being
- Provide clear, accurate, and compassionate responses
- Include disclaimers that you're not replacing professional medical diagnosis
- Detect emergency situations (chest pain, severe bleeding, difficulty breathing, etc.) and advise calling 911
- Be professional yet friendly and approachable
- Keep responses concise but informative (2-4 sentences typically)
- Use medical terminology appropriately but explain complex terms
- Respect patient privacy and confidentiality
- Direct users to appropriate resources (doctors, pharmacists, receptionists)

**Hospital Details:**
- Name: City General Hospital
- Address: 123 Medical Center Drive, Healthcare City
- Phone: +1 (555) 123-4567
- Emergency: 911
- Hours: Emergency 24/7, OPD 8 AM - 6 PM (Mon-Sat)

**Emergency Keywords to Watch:**
If user mentions: heart attack, chest pain, can't breathe, severe bleeding, stroke, unconscious, suicide, overdose - IMMEDIATELY advise calling 911 and going to ER.

**Response Format:**
- Use emojis appropriately (🏥 💊 📋 ⚠️ 🚨) to make information clearer
- Structure responses with bullet points when listing information
- End with an offer to help further or suggest next steps

Remember: You provide guidance and information, but always emphasize consulting healthcare professionals for diagnosis and treatment."""

class ChatbotService:
    """AI Chatbot service powered by Google Gemini"""
    
    def __init__(self):
        # Emergency keywords for quick detection
        self.emergency_keywords = [
            'heart attack', 'chest pain', 'can\'t breathe', 'cannot breathe',
            'suicide', 'kill myself', 'overdose', 'severe bleeding', 
            'unconscious', 'stroke', 'choking', 'seizure'
        ]
    
    def check_emergency(self, message):
        """Quick check if message contains emergency keywords"""
        message_lower = message.lower()
        for keyword in self.emergency_keywords:
            if keyword in message_lower:
                return True
        return False
    
    def get_response(self, message, message_type='general', role='patient'):
        """Get AI response from Gemini"""
        try:
            # Quick emergency check
            if self.check_emergency(message):
                return {
                    'emergency': True,
                    'message': '🚨 **EMERGENCY DETECTED!**\n\n**CALL 911 IMMEDIATELY** if you are experiencing:\n• Chest pain or pressure\n• Difficulty breathing\n• Severe bleeding\n• Loss of consciousness\n• Stroke symptoms\n• Any life-threatening condition\n\n**Emergency Contacts:**\n• Ambulance: **911**\n• Hospital Emergency: +1 (555) 123-4567\n\nDo not wait - seek immediate medical attention!',
                    'emergency_number': '911'
                }
            
            # Build context-aware prompt
            system_context = HOSPITAL_SYSTEM_PROMPT + f"\n\n**Current Context:**\nUser Role: {role.title()}\nQuery Type: {message_type}\n\n"
            
            if message_type == 'symptom':
                system_context += "The user is describing symptoms. Provide a thoughtful symptom assessment with possible conditions and advice. Always include medical disclaimer.\n\n"
            elif message_type == 'medicine':
                system_context += "The user is asking about medication. Provide medicine information including uses, dosage guidelines, and side effects. Include warning about consulting doctor.\n\n"
            elif message_type == 'appointment':
                system_context += "The user needs help with appointments. Explain the process step-by-step for booking/canceling/rescheduling.\n\n"
            elif message_type == 'faq':
                system_context += "The user wants general hospital information. Provide FAQs relevant to their role (patient/doctor/admin/etc).\n\n"
            elif message_type == 'emergency':
                return {
                    'message': '🚨 **EMERGENCY CONTACTS**\n\n• **Ambulance:** 911\n• **Hospital Emergency:** +1 (555) 123-4567\n• **Poison Control:** 1-800-222-1222\n\nFor **life-threatening emergencies**, call **911** immediately!\n\nOur emergency department is **open 24/7**.',
                    'emergency_contacts': {
                        'ambulance': '911',
                        'hospital': '+1 (555) 123-4567',
                        'poison_control': '1-800-222-1222'
                    }
                }
            
            # Get response from Groq API
            user_prompt = f"User Question: {message}\n\nProvide a helpful, concise response:"
            
            # Generate response using Groq API with Llama model
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_context
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=800
            )
            
            # Extract response
            response_text = chat_completion.choices[0].message.content
            
            if response_text:
                return {
                    'message': response_text.strip(),
                    'success': True
                }
            else:
                return {
                    'message': 'I apologize, but I could not generate a response at this time. Please try rephrasing your question or contact support.',
                    'success': False
                }
            
        except Exception as e:
            # Fallback response if API fails
            return {
                'message': f'I apologize, but I\'m having trouble processing your request right now. Please try again or contact our support team at +1 (555) 123-4567.\n\nError: {str(e)}',
                'success': False,
                'error': str(e)
            }


# Initialize chatbot service
chatbot_service = ChatbotService()


def process_chatbot_message(message, message_type='general', role='patient'):
    """Process chatbot message and return response"""
    return chatbot_service.get_response(message, message_type, role)
