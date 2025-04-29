from transformers import pipeline

# Initialize the Hugging Face pipeline
qa_pipeline = pipeline(
    "text2text-generation",
    model="google/flan-t5-small"  # Free, lightweight model
)

def generate_answer(prompt):
    response = qa_pipeline(prompt, max_length=256, truncation=True)
    return response[0]['generated_text']

if __name__ == "__main__":
    sample_prompt = "What is Vedic Astrology?"
    answer = generate_answer(sample_prompt)
    print(f"Sample Answer: {answer}")
