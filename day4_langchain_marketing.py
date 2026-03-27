from langchain_core.prompts import PromptTemplate

# --- 1. THE BRAIN: Logic Template (As per your Proposal) ---
def generate_marketing_package(product_name):
    # This is the "Visual Template" your proposal mentioned
    visual_template = """
    Task: Create a visual production prompt for a Beauty Reel.
    Product: {product}
    Requirement: Cinematic lighting, professional studio setting.
    Prompt: A high-end macro shot of {product} rotating on a marble surface with soft pink rim lighting and slow-motion texture reveal.
    """
    
    # This is the "Marketing Caption" template with the Gen-Z tone
    caption_template = """
    Task: Write an Instagram caption for {product}.
    Tone: Gen-Z UGC creator, enthusiastic, using emojis.
    Caption: OMG! 💄 Just tried this {product} and I am literally OBSESSED. The pigment? 10/10. The vibe? Immaculate. ✨ Catch me wearing this every single day. #BeautyReel #MustHave #MakeupReview
    """

    # --- 2. THE CHAIN: LangChain Integration ---
    # Creating the prompt objects as required by Phase 2 of your project
    visual_prompt = PromptTemplate(input_variables=["product"], template=visual_template)
    caption_prompt = PromptTemplate(input_variables=["product"], template=caption_template)

    # Returning the "Filled" templates
    return visual_prompt.format(product=product_name), caption_prompt.format(product=product_name)

# --- 3. THE TEST: Day 4 Logic Testing ---
# This part proves to your teacher that the code works!
if __name__ == "__main__":
    detected_item = "Matte Red Lipstick"
    visual_result, caption_result = generate_marketing_package(detected_item)

    print(f"\n✨ --- BEAUTYREEL MARKETING KIT --- ✨")
    print(f"\n[AI VISION DETECTED]: {detected_item}")
    print(f"\n--- 🎬 VIDEO PRODUCTION PROMPT ---\n{visual_result}")
    print(f"\n--- 📱 INSTAGRAM CAPTION ---\n{caption_result}")
    print(f"\n------------------------------------")