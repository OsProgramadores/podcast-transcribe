from transformers import MBartForConditionalGeneration, MBart50TokenizerFast

# Load model and tokenizer
model_name = "facebook/mbart-large-50-many-to-many-mmt"
tokenizer = MBart50TokenizerFast.from_pretrained(model_name)
model = MBartForConditionalGeneration.from_pretrained(model_name)

# Example: Translate English text to French
text = "Hello, how are you?"
# MBart uses language codes, here 'en_XX' for English and 'fr_XX' for French
tokenizer.src_lang = "en_US"
encoded_text = tokenizer(text, return_tensors="pt")
translated_tokens = model.generate(**encoded_text, forced_bos_token_id=tokenizer.lang_code_to_id["pt_XX"])
translation = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)

print(translation)

