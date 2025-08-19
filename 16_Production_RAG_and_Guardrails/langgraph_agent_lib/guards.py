
"""Production guardrails for LangGraph agents using the official guardrails library."""

import logging
import re
import os
from typing import Dict, Any, Optional

# Import from the official guardrails-ai package
try:
    import guardrails as gr
    from guardrails.hub import (
        RestrictToTopic,
        DetectJailbreak,
        ProfanityFree,
        GuardrailsPII,
        LlmRagEvaluator,
        HallucinationPrompt,
    )
    Guard = gr.Guard
    
    # Configure guardrails to use local-only processing to avoid 500 errors from remote API
    gr.settings.rc.use_remote_inferencing = False
    print("Guardrails configured for local-only processing")
    
except ImportError as e:
    print(f"Error importing guardrails library: {e}")
    print("Please install with: pip install guardrails-ai")
    raise

topic_guard = Guard().use(
    RestrictToTopic(
        valid_topics=["student loans", "financial aid", "education financing", "loan repayment"],
        invalid_topics=["investment advice", "crypto", "gambling", "politics"],
        disable_classifier=True,
        disable_llm=False,
        on_fail="noop"
    )
)

jailbreak_guard = Guard().use(DetectJailbreak(on_fail="noop"))

profanity_guard = Guard().use(
    ProfanityFree(threshold=0.8, validation_method="sentence", on_fail="noop")
)

factuality_guard = Guard().use(
    LlmRagEvaluator(
        eval_llm_prompt_generator=HallucinationPrompt(prompt_name="hallucination_judge_llm"),
        llm_evaluator_fail_response="hallucinated",
        llm_evaluator_pass_response="factual", 
        llm_callable="gpt-4.1-mini",
        on_fail="noop",
        on="prompt"
    )
)

pii_guard = Guard().use(
    GuardrailsPII(
        entities=["CREDIT_CARD", "SSN", "PHONE_NUMBER", "EMAIL_ADDRESS"],
        on_fail="fix"  # This will mask/fix PII instead of failing
    )
)

# Configure logging for security events
logging.basicConfig(level=logging.INFO)
security_logger = logging.getLogger("guardrails.security")

class GuardResult:
    """Result of a guardrail check."""
    def __init__(self, passed: bool, reason: str = "", confidence: float = 1.0, fixed_output: str = None):
        self.passed = passed
        self.reason = reason
        self.confidence = confidence
        self.fixed_output = fixed_output  # For guards that fix content (like PII)
        
    def __bool__(self):
        return self.passed

# Input Guardrails using official guardrails library

def restrict_to_topic(input_text: str, allowed_topics: list = None) -> GuardResult:
    """Restrict input to allowed topics using predefined guard instance."""
    if allowed_topics is None:
        allowed_topics = ["student loans", "financial aid", "education financing", "loan repayment"]
    
    try:
        # Use the predefined topic_guard instance
        result = topic_guard.validate(input_text)
        
        if result.validation_passed:
            return GuardResult(True, "Input is on-topic")
        else:
            security_logger.warning(f"Off-topic input detected: {input_text[:100]}...")
            return GuardResult(False, f"Input not related to allowed topics: {', '.join(allowed_topics)}")
            
    except Exception as e:
        # Fallback to simple keyword-based check if guardrails fails
        security_logger.warning(f"Topic restriction using guardrails failed, using fallback: {e}")
        input_lower = input_text.lower()
        for topic in allowed_topics:
            if any(word in input_lower for word in topic.lower().split()):
                return GuardResult(True, "Input appears on-topic (fallback check)")
        
        # Check for obviously off-topic content
        off_topic_keywords = ["weather", "cooking", "jokes", "cats", "celebrity", "vacation", "car", "stock", "investment"]
        for keyword in off_topic_keywords:
            if keyword in input_lower:
                return GuardResult(False, f"Input not related to allowed topics: {', '.join(allowed_topics)}")
        
        # Check for dangerous/prohibited content
        dangerous_keywords = [
            "weapons", "guns", "bombs", "explosives", "violence", "attack", "kill", "murder",
            "hack", "hacking", "crack", "exploit", "vulnerability", "malware", "virus",
            "illegal", "drugs", "trafficking", "fraud", "scam", "theft", "robbery",
            "terrorism", "extremist", "radical", "suicide", "self-harm", "harm others"
        ]
        for keyword in dangerous_keywords:
            if keyword in input_lower:
                security_logger.critical(f"Dangerous content detected: {keyword} in input: {input_text[:100]}...")
                return GuardResult(False, "Request contains prohibited content")
        
        # If unclear, be restrictive for security (changed from permissive)
        return GuardResult(False, "Topic unclear - defaulting to block for security")

def detect_jailbreak(input_text: str) -> GuardResult:
    """Detect jailbreak and prompt injection attempts using predefined guard instance + local patterns."""
    
    # First, run our own pattern-based detection (more reliable than guardrails for basic patterns)
    jailbreak_patterns = [
        # Instruction manipulation
        r"ignore\s+(all\s+)?(previous\s+)?instructions",
        r"forget\s+(all\s+)?(previous\s+)?instructions",
        r"disregard\s+(all\s+)?(previous\s+)?instructions",
        r"override\s+(all\s+)?(previous\s+)?instructions",
        
        # Role manipulation
        r"act\s+as\s+(if\s+you\s+are\s+)?a\s+different",
        r"pretend\s+(to\s+be|you\s+are)",
        r"roleplay\s+as",
        r"play\s+the\s+role\s+of",
        r"assume\s+the\s+role\s+of",
        
        # System manipulation
        r"system\s*:\s*you\s+are",
        r"developer\s+mode",
        r"admin\s+mode",
        r"jailbreak",
        r"DAN\s+mode",
        r"evil\s+ai",
        
        # Restriction bypass
        r"bypass\s+(your\s+)?restrictions",
        r"ignore\s+(your\s+)?safety",
        r"remove\s+(your\s+)?limitations",
        r"disable\s+(your\s+)?safety",
        r"without\s+restrictions",
        r"no\s+moral\s+constraints",
        
        # Dangerous content requests
        r"tell\s+me\s+about\s+(weapons|bombs|explosives)",
        r"how\s+to\s+(hack|break\s+into|attack)",
        r"instructions\s+for\s+(illegal|harmful)",
        r"bypass\s+security",
        r"exploit\s+(vulnerability|weakness)",
    ]
    
    input_lower = input_text.lower()
    for pattern in jailbreak_patterns:
        if re.search(pattern, input_lower):
            security_logger.critical(f"Jailbreak attempt detected (pattern match): {input_text[:100]}...")
            return GuardResult(False, "Jailbreak or prompt injection detected")
    
    # Additional safety check for suspicious phrases
    suspicious_phrases = [
        "tell me a secret", "reveal", "bypass", "circumvent", "workaround",
        "trick you", "fool you", "deceive", "manipulate", "exploit",
        "override", "overwrite", "modify", "change your", "alter your"
    ]
    
    for phrase in suspicious_phrases:
        if phrase in input_lower:
            security_logger.warning(f"Suspicious phrase detected: {phrase} in input: {input_text[:100]}...")
            return GuardResult(False, "Input contains suspicious content")
    
    # Then try predefined jailbreak_guard as additional check (but don't rely on it exclusively)
    try:
        result = jailbreak_guard.validate(input_text)
        
        if not result.validation_passed:
            security_logger.critical(f"Jailbreak attempt detected by guardrails: {input_text[:100]}...")
            return GuardResult(False, "Jailbreak or prompt injection detected by guardrails")
            
    except Exception as e:
        security_logger.warning(f"Jailbreak detection using guardrails failed: {e}")
        # Continue with local validation (already done above)
    
    return GuardResult(True, "Input appears safe")

def profanity_free(input_text: str, threshold: float = 0.8) -> GuardResult:
    """Check for profanity and inappropriate content using predefined guard instance."""
    
    try:
        # Use the predefined profanity_guard instance
        result = profanity_guard.validate(input_text)
        
        if result.validation_passed:
            return GuardResult(True, "Input is appropriate")
        else:
            security_logger.info(f"Profanity detected in input: {input_text[:50]}...")
            return GuardResult(False, "Input contains inappropriate language")
            
    except Exception as e:
        # Fallback to basic profanity filter
        security_logger.warning(f"Profanity check using guardrails failed, using fallback: {e}")
        
        profanity_words = [
            "damn", "hell", "crap", "shit", "fuck", "bitch", "asshole", 
            "bastard", "piss", "dickhead", "motherfucker", "cocksucker"
        ]
        
        input_lower = input_text.lower()
        for word in profanity_words:
            if word in input_lower:
                security_logger.info(f"Profanity detected (fallback): {word}")
                return GuardResult(False, "Input contains inappropriate language")
        
        return GuardResult(True, "Input is appropriate (fallback check)")

# Output Guardrails using official guardrails library

def detect_pii_leakage(output_text: str, entities: list = None) -> GuardResult:
    """Detect and optionally fix PII leakage in output using predefined guard instance."""
    if entities is None:
        entities = ["CREDIT_CARD", "SSN", "PHONE_NUMBER", "EMAIL_ADDRESS"]
    
    try:
        # Use the predefined pii_guard instance
        result = pii_guard.validate(output_text)
        
        if result.validation_passed:
            return GuardResult(True, "No PII detected")
        else:
            # If validation failed but we got fixed output, use it
            if hasattr(result, 'validated_output') and result.validated_output:
                security_logger.warning(f"PII detected and fixed in output: {output_text[:100]}...")
                return GuardResult(True, "PII detected and fixed", fixed_output=result.validated_output)
            else:
                security_logger.critical(f"PII detected in output: {output_text[:100]}...")
                return GuardResult(False, "Output contains PII that could not be fixed")
            
    except Exception as e:
        security_logger.error(f"PII detection failed: {e}")
        return GuardResult(True, "PII detection failed, allowing output")

def content_moderation(output_text: str) -> GuardResult:
    """Basic content moderation - we'll use profanity check as a proxy for now."""
    return profanity_free(output_text, threshold=0.5)

def factuality_check(output_text: str) -> GuardResult:
    """Check factuality using predefined guard instance with fallback."""
    try:
        # Use the predefined factuality_guard instance
        result = factuality_guard.validate(output_text)
        
        if result.validation_passed:
            return GuardResult(True, "Output appears factually sound")
        else:
            security_logger.warning(f"Factuality issues detected: {output_text[:100]}...")
            return GuardResult(False, "Output may contain factual inaccuracies")
            
    except Exception as e:
        # Fallback to simple heuristics for obviously false claims
        security_logger.warning(f"Factuality check using guardrails failed, using fallback: {e}")
        
        suspicious_phrases = [
            "500% interest rate", "1000% annual rate", "free money", 
            "never pay back", "ignore your loans", "lie on fafsa"
        ]
        
        output_lower = output_text.lower()
        for phrase in suspicious_phrases:
            if phrase in output_lower:
                security_logger.info(f"Potentially inaccurate output detected: {output_text[:100]}...")
                return GuardResult(False, "Output may contain factual inaccuracies")
        
        return GuardResult(True, "Output appears factually sound (fallback check)")

# Utility functions to create guards

def create_input_guard_chain():
    """Create a combined guard for all input validation."""
    try:
        combined_guard = Guard().use_many(
            RestrictToTopic(
                valid_topics=["student loans", "financial aid", "education financing", "loan repayment"],
                invalid_topics=["investment advice", "crypto", "gambling", "politics", "weather", "cooking"],
                disable_classifier=False,
                disable_llm=True,
                on_fail="exception"
            ),
            DetectJailbreak(on_fail="exception"),
            ProfanityFree(threshold=0.8, validation_method="sentence", on_fail="exception")
        )
        return combined_guard
    except Exception as e:
        security_logger.error(f"Failed to create input guard chain: {e}")
        return None

def create_output_guard_chain():
    """Create a combined guard for all output validation."""
    try:
        combined_guard = Guard().use_many(
            GuardrailsPII(
                entities=["CREDIT_CARD", "SSN", "PHONE_NUMBER", "EMAIL_ADDRESS"],
                on_fail="fix"
            ),
            ProfanityFree(threshold=0.5, validation_method="sentence", on_fail="exception")
        )
        return combined_guard
    except Exception as e:
        security_logger.error(f"Failed to create output guard chain: {e}")
        return None

# Legacy functions for backward compatibility
def check_inputs(input: str) -> bool:
    """Legacy function - use comprehensive input guards instead."""
    return True

def check_outputs(output: str) -> bool:
    """Legacy function - use comprehensive output guards instead."""
    return True