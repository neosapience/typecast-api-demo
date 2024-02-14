import re
import csv


def _cvt_digit_to_korean(elements):
    converter = {
        '0': '공',
        '1': '일',
        '2': '이',
        '3': '삼',
        '4': '사',
        '5': '오',
        '6': '육',
        '7': '칠',
        '8': '팔',
        '9': '구',
    }
    output = ''
    for elem in elements:
        output += converter[elem]
    return output


def _cvt_alphabet_to_korean(elements):
    converter = {
        'a': '에이',
        'b': '비',
        'c': '씨',
        'd': '디',
        'e': '이',
        'f': '에프',
        'g': '지',
        'h': '에이치',
        'i': '아이',
        'j': '제이',
        'k': '케이',
        'l': '엘',
        'm': '엠',
        'n': '엔',
        'o': '오',
        'p': '피',
        'q': '큐',
        'r': '알',
        's': '에스',
        't': '티',
        'u': '유',
        'v': '브이',
        'w': '떠블유',
        'x': '엑스',
        'y': '와이',
        'z': '지',
        '-': '대쉬',
        '.': '쩜',
    }
    output = ''
    for elem in elements:
        output += converter[elem]
        if elem == '.':
            output += ' '
    return output


def _cvt_pmhour_to_korean(elements):
    converter = {
        '12': '십이',
        '13': '십삼',
        '14': '십사',
        '15': '십오',
        '16': '십육',
        '17': '십칠',
        '18': '십팔',
        '19': '십구',
        '20': '이십',
        '21': '이십일',
        '22': '이십이',
        '23': '이십삼',
        '24': '이십사',
    }
    output = ''
    for start_idx in range(0, len(elements), 2):
        output += converter[elements[start_idx:start_idx+2]]
    return output


def _prep_mydict(text, mydict):
    for key, value in mydict.items():
        text = text.replace(key, value)
    return text


def _prep_hour_with_fromto(text):
    pattern = re.compile(r'(\d+시)~(\d+시까지)')
    return pattern.sub(r'\1에서 \2', text)


def _prep_date(text):
    pattern = re.compile(r'(\d+)/(\d+)일')
    return pattern.sub(r'\1월 \2일', text)


def _prep_email(text):
    pattern = re.compile(r'([\w\-\.]+)@([\w\-]+\.+[\w\-])')
    return pattern.sub(r'\1골뱅이\2', text)


def _prep_korea_phone_number(text):
    pattern = re.compile(r'(\d\d)-(\d\d\d\d)-(\d\d\d\d)')
    text = pattern.sub(lambda x: f"{_cvt_digit_to_korean(x.group(1))} {_cvt_digit_to_korean(x.group(2))} {_cvt_digit_to_korean(x.group(3))}", text)
    return text


def _prep_www(text):
    pattern = re.compile(r'(www\.)([\w\-]+)\.([\w\-\.]+)')
    text = pattern.sub(lambda x: f"떠블유 떠블유 떠블유 쩜 {_cvt_alphabet_to_korean(x.group(2))} 쩜 {_cvt_alphabet_to_korean(x.group(3))}", text)
    return text


def _prep_pmhour(text):
    pattern = re.compile(r'(\d\d)시')
    text = pattern.sub(lambda x: f"{_cvt_pmhour_to_korean(x.group(1))}시", text)
    return text


def preprocess(text, mydict):
    text = _prep_mydict(text, mydict)
    text = _prep_hour_with_fromto(text)
    text = _prep_korea_phone_number(text)
    text = _prep_date(text)
    text = _prep_email(text)
    text = _prep_www(text)

    # final process
    text = _prep_pmhour(text)
    return text


def main():
    # load my dictionary
    mydict = {}
    with open('data/dic.csv') as f:
        rows = csv.reader(f, delimiter='|')
        for cols in rows:
            mydict[cols[0]] = cols[1]

    # test sample dataset
    with open('data/sample.csv') as f:
        samples = csv.reader(f, delimiter='|')
        for sample in samples:
            src = sample[0]
            expected = sample[1]
            
            ########################################################
            # core logic
            ########################################################
            test = preprocess(src, mydict)
            ########################################################
            
            if expected != test:
                print('[ERRO]', src, '=>', test)
                print(' src:', src)
                print(' expected:', expected.encode('utf-8'))
                print(' test:', test.encode('utf-8'))
            else:
                print('[OK]', src, '=>', test)



if '__main__' == __name__:
    main()
