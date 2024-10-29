from deep_translator import GoogleTranslator
import re
def translate(text,seletcted_language='en'):
    return GoogleTranslator(source='auto', target=seletcted_language).translate(text)

def translate_with_regex(text,seletcted_language='en'):
    placeholder='^&*&^#$@'
    non_trans_phrase = re.findall(r'\^\*(.*?)\*\^',text)
    if non_trans_phrase:
        for phrase in non_trans_phrase:
            text=text.replace(f'^*{phrase}*^', placeholder)

        translated_text=''
        for phrase in non_trans_phrase:
            start_index=text.find(placeholder)
            if start_index != -1:
                before_phrase=translate(text[:start_index],seletcted_language)
                translated_text += before_phrase + phrase 
                text = text[len(text[:start_index]) + len(placeholder):]
        return translated_text+translate(text,seletcted_language)
    else:
        return translate(text,seletcted_language)