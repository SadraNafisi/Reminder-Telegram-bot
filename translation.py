from deep_translator import GoogleTranslator
import re
def translate(text,selected_language='en'):

    translated_text = GoogleTranslator(source='auto', target=selected_language).translate(text)
    if translated_text:
        return translated_text
    else:
        return ''
def translate_with_regex(text,selected_language='en'):
    placeholder='^&*&^#$@'
    non_trans_phrase = re.findall(r'\^\*(.*?)\*\^',text)
    if non_trans_phrase:
        for phrase in non_trans_phrase:
            text=text.replace(f'^*{phrase}*^', placeholder)

        translated_text=''
        for phrase in non_trans_phrase:
            start_index=text.find(placeholder)
            if start_index != -1:
                before_phrase=translate(text[:start_index],selected_language)
                translated_text += before_phrase + phrase
                text = text[len(text[:start_index]) + len(placeholder):]
        return translated_text+(translate(text,selected_language))
    else:
        return translate(text,selected_language)