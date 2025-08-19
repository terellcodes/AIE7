from guardrails.hub import (
    RestrictToTopic,
    DetectJailbreak, 
    CompetitorCheck,
    LlmRagEvaluator,
    HallucinationPrompt,
    ProfanityFree,
    GuardrailsPII
)
from guardrails import Guard

print("🛡️ Setting up production Guardrails...")

# 1. Topic Restriction Guard - Keep conversations focused on student loans
def get_topic_guard():
    topic_guard = Guard().use(
        RestrictToTopic(
            valid_topics=["student loans", "financial aid", "education financing", "loan repayment"],
            invalid_topics=["investment advice", "crypto", "gambling", "politics"],
            disable_classifier=True,
            disable_llm=False,
            on_fail="exception"
        )
    )
    print("✓ Topic restriction guard configured")
    return topic_guard

def get_jailbreak_guard():

    jailbreak_guard = Guard().use(DetectJailbreak())
    print("✓ Jailbreak detection guard configured")
    return jailbreak_guard

def get_pii_guard():

    pii_guard = Guard().use(
        GuardrailsPII(
            entities=["CREDIT_CARD", "SSN", "PHONE_NUMBER", "EMAIL_ADDRESS"], 
            on_fail="fix"
        )
    )
    print("✓ PII protection guard configured")
    return pii_guard

def get_profanity_guard():
    profanity_guard = Guard().use(
    ProfanityFree(threshold=0.8, validation_method="sentence", on_fail="exception")
)
    print("✓ Content moderation guard configured")
    return profanity_guard

def get_factuality_guard():
    factuality_guard = Guard().use(
    LlmRagEvaluator(
        eval_llm_prompt_generator=HallucinationPrompt(prompt_name="hallucination_judge_llm"),
        llm_evaluator_fail_response="hallucinated",
        llm_evaluator_pass_response="factual", 
        llm_callable="gpt-4.1-mini",
        on_fail="exception",
        on="prompt"
    )
)
print("✓ Factuality guard configured")

print("\\n🎯 All Guardrails configured for production use!")