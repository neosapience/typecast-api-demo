import requests
import time
import re
import xml.etree.ElementTree as ET
from io import BytesIO
from pydub import AudioSegment


API_TOKEN = 'your-api-token'
HEADERS = {'Authorization': f'Bearer {API_TOKEN}'}


def _get_synthesis_audio(line, actor_id):
    # request speech synthesis
    r = requests.post('https://typecast.ai/api/speak', headers=HEADERS, json={
        'lang': 'auto',
        'style_label_version': 'latest',
        'xapi_hd': True,
        'actor_id': actor_id,
        'text': line,
    })
    if r.status_code != 200:
        print('[ERRO]', 'synthesis request failed', r.text)
        return None
    
    speak_url = r.json()['result']['speak_v2_url']

    # polling the speech synthesis result
    for _ in range(120):
        r = requests.get(speak_url, headers=HEADERS)
        ret = r.json()['result']
        # audio is ready
        if ret['status'] == 'done':
            r = requests.get(ret['audio_download_url'])
            return BytesIO(r.content)
        # syntheis failed
        elif ret['status'] == 'failed':
            print('[ERRO]', 'synthesis wait request failed')
            return None
        else:
            print('[INFO]', f"synthesis status: {ret['status']}, waiting 1 second")
            time.sleep(1)
    
    return None


def _str2msec(timestr):
    # milliseconds
    r = re.match('(\d+)ms', timestr)
    if r:
        return int(r.group(1))
    
    # seconds
    r = re.match('(\d+)s', timestr)
    if r:
        return int(int(r.group(1)) * 1000)

    # exception 
    return 0


def _export_audio(out_audio_path, all_segments):
    output = all_segments[0]
    for a in all_segments[1:]:
        output += a
    output.export(out_audio_path, format='wav')


def _preprocess_text(line):
    line = re.sub(r'\(.*?\)', '', line)
    return line


def run(out_audio_path, script_path, actor_id):
    
    # get script each line
    with open(script_path) as f:
        lines = [line.strip() for line in f.readlines()]

    all_audio_segments = []
    for line in lines:
        print('[INFO]', f'-> source line: {line}')

        # add break
        try:
            tree = ET.fromstring(line)
            if tree.tag != 'break':
                print('[WARN]', f'ignore this tag: {tree.tag}')
                continue
            
            break_msec = _str2msec(tree.attrib['time'].strip())
            print('[INFO]', f'break: {break_msec} milliseconds')
            all_audio_segments.append(AudioSegment.silent(duration=break_msec))

        # add audio
        except Exception:
            line = _preprocess_text(line)
            print('[INFO]', f'preprocessed text: {line}')
            audio = _get_synthesis_audio(line, actor_id)
            if audio:
                all_audio_segments.append(AudioSegment.from_wav(audio))
            else:
                print('[ERRO]', 'failed to get audio')
                return None
    
    _export_audio(out_audio_path, all_audio_segments)


def main():
    # choose your voice actor
    r = requests.get('https://typecast.ai/api/actor', headers=HEADERS)
    if r.status_code != 200:
        print('[ERRO]', 'failed to get actor', r.text)
        return None
    my_actors = r.json()['result']
    my_first_actor = my_actors[0]
    my_first_actor_id = my_first_actor['actor_id']

    in_script_path = 'data/sample.txt'
    out_audio_path = '_out.wav'
    run(out_audio_path, in_script_path, my_first_actor_id)


if '__main__' == __name__:
    main()
