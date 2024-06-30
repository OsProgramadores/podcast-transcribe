import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import torch

# Read the file content
with open('E75/transcribe-en.srt', 'r', encoding='utf-8') as file:
    content = file.read()

# Tokenize the content into sentences
sentences = sent_tokenize(content)

# Configure the model
model = M2M100ForConditionalGeneration.from_pretrained("danhsf/m2m100_418M-finetuned-kde4-en-to-pt_BR")

# Check if a GPU is available and move the model to GPU
device = torch.device('cuda:0')
if torch.cuda.is_available():
    model = model.to(device)

tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
tokenizer.src_lang = "en"

# Print the sentences
for sentence in sentences:
    cleanSentence = sentence.replace('\n', ' ')

    encoded_hi = tokenizer(cleanSentence, return_tensors="pt").to(device)
    generated_tokens = model.generate(**encoded_hi, forced_bos_token_id=tokenizer.get_lang_id("pt"))
    translation = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

    print(cleanSentence + ' -> ' + translation)
