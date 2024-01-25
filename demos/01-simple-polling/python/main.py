import requests
import time

API_TOKEN = {{your token here}}
HEADERS = {'Authorization': f'Bearer {API_TOKEN}'}

# get my actor
r = requests.get('https://typecast.ai/api/actor', headers=HEADERS)
my_actors = r.json()['result']
my_first_actor = my_actors[0]
my_first_actor_id = my_first_actor['actor_id']

# request speech synthesis
r = requests.post('https://typecast.ai/api/speak', headers=HEADERS, json={
    'text': 'hello typecast',
    'lang': 'auto',
    'actor_id': my_first_actor_id,
    'xapi_hd': True,
    'model_version': 'latest'
})
speak_url = r.json()['result']['speak_v2_url']

# polling the speech synthesis result
for _ in range(120):
    r = requests.get(speak_url, headers=HEADERS)
    ret = r.json()['result']
    # audio is ready
    if ret['status'] == 'done':
        # download audio file
        r = requests.get(ret['audio_download_url'])
        with open('out.wav', 'wb') as f:
            f.write(r.content)
        break
    else:
        print(f"status: {ret['status']}, waiting 1 second")
        time.sleep(1)
