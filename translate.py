from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

model = M2M100ForConditionalGeneration.from_pretrained("danhsf/m2m100_418M-finetuned-kde4-en-to-pt_BR")
tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M", src_lang="en", tgt_lang="pt")

src_text = "Hello, my name is Bob, I like pasta and I'm happy."

model_inputs = tokenizer(src_text, return_tensors="pt")

loss = model(**model_inputs).loss  # forward pass

tokenizer.src_lang = "en"
encoded_hi = tokenizer(src_text, return_tensors="pt")
generated_tokens = model.generate(**encoded_hi, forced_bos_token_id=tokenizer.get_lang_id("pt"))
translation = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)

print(translation)

