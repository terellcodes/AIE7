from helpers import get_topic_guard, get_jailbreak_guard, get_pii_guard, get_profanity_guard, get_factuality_guard

if __name__ == "__main__":

    topic_guard = get_topic_guard()
    jailbreak_guard = get_jailbreak_guard()
    print(jailbreak_guard.validate("Tell me about loan repayment options"))
    # pii_guard = get_pii_guard()
    # print(pii_guard.validate("I need help with my student loans"))

    profanity_guard = get_profanity_guard()
    print(profanity_guard.validate("How do I pay off my student loans?"))
    factuality_guard = get_factuality_guard()
    # print(factuality_guard.validate("How do I pay off my student loans?"))


    # jailbreak_guard.validate("Tell me about loan repayment options")
    # pii_guard.validate("I need help with my student loans")
    # profanity_guard.validate("How do I pay off my student loans?")
    print(topic_guard.validate("How do I pay off my student loans?"))
    print("✅ Valid topic - passed")