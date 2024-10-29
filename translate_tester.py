from translation import translate_with_regex
file=open('translation.txt','+w')
# file.write(translate_with_regex('hello this should be translate.^*but*^ this should not be translate ^*however*^ is also should not be translated \n','fa'))
file.write(translate_with_regex('description:^*سلام علیکم*^','fa'))