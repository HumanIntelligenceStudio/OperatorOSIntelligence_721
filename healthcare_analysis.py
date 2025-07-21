"""
Healthcare Analysis Engine - Medical diagnosis, treatment recommendations, and health insights
Advanced medical AI capabilities with safety protocols
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class HealthcareAnalyzer:
    """Advanced healthcare analysis and medical AI assistant"""
    
    def __init__(self, ai_provider_manager):
        self.ai_provider = ai_provider_manager
        
        # Medical knowledge bases and drug interaction databases
        self.medical_disclaimer = """
        IMPORTANT MEDICAL DISCLAIMER: This AI assistant provides general health information for educational purposes only. 
        It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified 
        healthcare professionals for medical concerns. In emergencies, call 911 or go to the nearest emergency room immediately.
        """
        
        logger.info("Healthcare Analyzer initialized")
    
    def analyze_symptoms(self, query: str) -> str:
        """Analyze symptoms and provide medical insights"""
        try:
            # Extract symptoms and medical context
            symptoms = self._extract_symptoms(query)
            
            analysis_prompt = f"""
            {self.medical_disclaimer}
            
            Analyze the following symptoms and medical query:
            
            Query: {query}
            Identified Symptoms: {symptoms}
            
            Please provide a comprehensive analysis including:
            
            1. SYMPTOM ASSESSMENT:
            - Primary symptoms analysis
            - Severity indicators
            - Duration and progression patterns
            - Associated symptoms to monitor
            
            2. POSSIBLE CONDITIONS:
            - Common conditions that may cause these symptoms
            - More serious conditions to rule out
            - Risk factors and red flags
            - When to seek immediate medical attention
            
            3. RECOMMENDATIONS:
            - Next steps for diagnosis
            - Healthcare providers to consult
            - Diagnostic tests that may be helpful
            - Self-care measures (if appropriate)
            
            4. MONITORING GUIDELINES:
            - Symptoms that require immediate attention
            - Warning signs of complications
            - Follow-up timeline recommendations
            
            Always emphasize the importance of professional medical consultation and never provide definitive diagnoses.
            """
            
            response = self.ai_provider.get_completion(
                analysis_prompt,
                system_prompt="You are a medical AI assistant with advanced knowledge of clinical medicine, differential diagnosis, and patient care protocols. Always prioritize patient safety and emphasize the need for professional medical consultation.",
                temperature=0.2  # Low temperature for medical accuracy
            )
            
            return f"{self.medical_disclaimer}\n\n{response}"
            
        except Exception as e:
            logger.error(f"Error in symptom analysis: {e}")
            return f"{self.medical_disclaimer}\n\nI apologize, but I encountered an error while analyzing the symptoms. Please consult with a healthcare professional for proper medical evaluation."
    
    def medication_analysis(self, query: str) -> str:
        """Analyze medications, interactions, and pharmaceutical information"""
        try:
            medications = self._extract_medications(query)
            
            medication_prompt = f"""
            {self.medical_disclaimer}
            
            Provide comprehensive pharmaceutical analysis for the following query:
            
            Query: {query}
            Identified Medications: {medications}
            
            Please provide detailed information on:
            
            1. MEDICATION OVERVIEW:
            - Generic and brand names
            - Drug classification and mechanism of action
            - Primary indications and uses
            - Standard dosing guidelines
            
            2. SAFETY INFORMATION:
            - Common side effects and adverse reactions
            - Serious warnings and contraindications
            - Drug interaction potential
            - Special populations (pregnancy, elderly, etc.)
            
            3. INTERACTION ANALYSIS:
            - Drug-drug interactions
            - Drug-food interactions
            - Timing considerations
            - Monitoring requirements
            
            4. PATIENT COUNSELING POINTS:
            - Administration instructions
            - Storage requirements
            - What to do if doses are missed
            - When to contact healthcare providers
            
            5. MONITORING RECOMMENDATIONS:
            - Laboratory tests that may be needed
            - Signs and symptoms to watch for
            - Follow-up timeline
            
            Always emphasize the importance of following healthcare provider instructions and pharmacist guidance.
            """
            
            response = self.ai_provider.get_completion(
                medication_prompt,
                system_prompt="You are a clinical pharmacist AI with expertise in pharmacology, drug interactions, and medication therapy management. Always prioritize patient safety and medication adherence.",
                temperature=0.1  # Very low temperature for pharmaceutical accuracy
            )
            
            return f"{self.medical_disclaimer}\n\n{response}"
            
        except Exception as e:
            logger.error(f"Error in medication analysis: {e}")
            return f"{self.medical_disclaimer}\n\nI apologize, but I encountered an error while analyzing the medication information. Please consult with your pharmacist or healthcare provider."
    
    def insurance_navigation(self, query: str) -> str:
        """Help navigate healthcare insurance and coverage issues"""
        try:
            insurance_prompt = f"""
            Provide comprehensive healthcare insurance guidance based on the following query:
            
            Query: {query}
            
            Please address the following aspects:
            
            1. INSURANCE BASICS:
            - Coverage types and benefits
            - Deductibles, copays, and coinsurance
            - Network providers vs. out-of-network
            - Prior authorization requirements
            
            2. CLAIM PROCESSES:
            - How to file claims
            - Documentation requirements
            - Appeal processes
            - Common denial reasons and solutions
            
            3. COST OPTIMIZATION:
            - Ways to reduce healthcare costs
            - Generic vs. brand name medications
            - Preventive care benefits
            - Health Savings Accounts (HSA) and Flexible Spending Accounts (FSA)
            
            4. NAVIGATION STRATEGIES:
            - Working with insurance representatives
            - Understanding Explanation of Benefits (EOB)
            - Finding in-network providers
            - Emergency vs. urgent care decisions
            
            5. SPECIAL SITUATIONS:
            - Coverage for pre-existing conditions
            - Prescription assistance programs
            - Medical necessity documentation
            - Coordination of benefits
            
            Provide practical, actionable advice for navigating the healthcare insurance system effectively.
            """
            
            response = self.ai_provider.get_completion(
                insurance_prompt,
                system_prompt="You are a healthcare insurance specialist with expertise in insurance navigation, healthcare economics, and patient advocacy.",
                temperature=0.3
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in insurance navigation: {e}")
            return "I apologize, but I encountered an error while providing insurance navigation guidance. Please contact your insurance provider directly or speak with a healthcare advocate."
    
    def wellness_coaching(self, query: str) -> str:
        """Provide wellness and lifestyle coaching"""
        try:
            wellness_prompt = f"""
            Provide comprehensive wellness and lifestyle coaching based on the following query:
            
            Query: {query}
            
            Please provide guidance on:
            
            1. LIFESTYLE ASSESSMENT:
            - Current wellness status evaluation
            - Risk factors identification
            - Goal setting and prioritization
            - Motivation and readiness assessment
            
            2. NUTRITION GUIDANCE:
            - Dietary recommendations
            - Meal planning strategies
            - Nutritional supplementation
            - Healthy eating habits
            
            3. PHYSICAL ACTIVITY:
            - Exercise recommendations
            - Activity level progression
            - Injury prevention
            - Movement throughout the day
            
            4. STRESS MANAGEMENT:
            - Stress identification and assessment
            - Coping strategies and techniques
            - Mindfulness and relaxation methods
            - Work-life balance
            
            5. SLEEP OPTIMIZATION:
            - Sleep hygiene practices
            - Sleep environment optimization
            - Sleep disorder recognition
            - Recovery and restoration
            
            6. PREVENTIVE CARE:
            - Screening recommendations
            - Health monitoring strategies
            - Early detection practices
            - Healthcare maintenance schedules
            
            Provide evidence-based, practical recommendations that can be implemented gradually.
            """
            
            response = self.ai_provider.get_completion(
                wellness_prompt,
                system_prompt="You are a certified wellness coach with expertise in lifestyle medicine, nutrition, exercise physiology, and behavior change.",
                temperature=0.4
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in wellness coaching: {e}")
            return "I apologize, but I encountered an error while providing wellness guidance. Please consult with a certified wellness coach or healthcare provider."
    
    def general_health_advice(self, query: str) -> str:
        """Provide general health information and guidance"""
        try:
            health_prompt = f"""
            {self.medical_disclaimer}
            
            Provide comprehensive health information and guidance for the following query:
            
            Query: {query}
            
            Please provide educational information covering relevant aspects such as:
            - Health condition overview
            - Risk factors and prevention
            - Treatment options and approaches
            - Lifestyle modifications
            - When to seek professional care
            - Resources for additional support
            
            Ensure all information is evidence-based, current, and emphasizes the importance of professional medical consultation.
            """
            
            response = self.ai_provider.get_completion(
                health_prompt,
                system_prompt="You are a health educator with comprehensive medical knowledge, focused on providing accurate, evidence-based health information while emphasizing the importance of professional medical care.",
                temperature=0.3
            )
            
            return f"{self.medical_disclaimer}\n\n{response}"
            
        except Exception as e:
            logger.error(f"Error in general health advice: {e}")
            return f"{self.medical_disclaimer}\n\nI apologize, but I encountered an error while providing health information. Please consult with a healthcare professional."
    
    def _extract_symptoms(self, text: str) -> List[str]:
        """Extract potential symptoms from text"""
        # Common symptom keywords
        symptom_keywords = [
            'pain', 'ache', 'hurt', 'sore', 'tender', 'swollen', 'fever', 'chills',
            'nausea', 'vomiting', 'diarrhea', 'constipation', 'headache', 'dizzy',
            'fatigue', 'tired', 'weakness', 'shortness of breath', 'cough', 'chest pain',
            'abdominal pain', 'back pain', 'joint pain', 'muscle pain', 'rash', 'itchy',
            'burning', 'stinging', 'cramping', 'bloating', 'heartburn', 'indigestion',
            'congestion', 'runny nose', 'sneezing', 'watery eyes', 'blurred vision',
            'ringing ears', 'hearing loss', 'difficulty swallowing', 'hoarse voice'
        ]
        
        text_lower = text.lower()
        found_symptoms = []
        
        for symptom in symptom_keywords:
            if symptom in text_lower:
                found_symptoms.append(symptom)
        
        return found_symptoms
    
    def _extract_medications(self, text: str) -> List[str]:
        """Extract potential medication names from text"""
        # This is a simplified implementation
        # In a real system, you'd use a comprehensive drug database
        
        # Common medication patterns and examples
        medication_patterns = [
            r'\b\w+mycin\b',  # Antibiotics like amoxicillin
            r'\b\w+pril\b',   # ACE inhibitors like lisinopril
            r'\b\w+olol\b',   # Beta blockers like metoprolol
            r'\b\w+statin\b', # Statins like atorvastatin
        ]
        
        # Common generic drug names
        common_drugs = [
            'aspirin', 'ibuprofen', 'acetaminophen', 'tylenol', 'advil', 'aleve',
            'metformin', 'insulin', 'lisinopril', 'amlodipine', 'metoprolol',
            'atorvastatin', 'simvastatin', 'levothyroxine', 'omeprazole',
            'prednisone', 'albuterol', 'warfarin', 'clopidogrel', 'gabapentin'
        ]
        
        text_lower = text.lower()
        found_medications = []
        
        # Check for common drugs
        for drug in common_drugs:
            if drug in text_lower:
                found_medications.append(drug)
        
        # Check for pattern matches
        import re
        for pattern in medication_patterns:
            matches = re.findall(pattern, text_lower)
            found_medications.extend(matches)
        
        return list(set(found_medications))  # Remove duplicates
    
    def get_health_resources(self) -> Dict:
        """Get healthcare resources and emergency information"""
        return {
            'emergency': {
                'number': '911',
                'poison_control': '1-800-222-1222',
                'suicide_prevention': '988',
                'crisis_text_line': 'Text HOME to 741741'
            },
            'resources': {
                'cdc': 'https://www.cdc.gov',
                'nih': 'https://www.nih.gov',
                'mayo_clinic': 'https://www.mayoclinic.org',
                'webmd': 'https://www.webmd.com',
                'medline_plus': 'https://medlineplus.gov'
            },
            'professional_help': {
                'find_doctor': 'Contact your insurance provider or visit healthcare.gov',
                'mental_health': 'Psychology Today, NAMI, or your EAP program',
                'specialists': 'Ask for referrals from your primary care physician'
            }
        }
