import anthropic
import os
import json
import time
import multiprocessing
import sys
import os.path

class CaptionGenerator:
    def __init__(self, api_key, model_id):
        self.api_key = api_key
        self.model_id = model_id
        self.client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
            )
        self.prompt_base = "generate captions from prompt\n"

    def set_prompt_base(self, prompt_base):
        self.prompt_base = prompt_base
        if self.prompt_base[-1] != '\n':
            self.prompt_base += '\n'

    def create_prompt(self, keywords):
        prompt = self.prompt_base
        prompt += str(keywords)
        return prompt

    def generate_caption(self, prompt):
        try:
            response = self.client.messages.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        }
                    ],
                model=self.model_id,
                max_tokens=4000,
                temperature=0,
                )
            caption = response.content[0].text
            print(f'usage: {response.usage}')
        except anthropic.APIStatusError as e:
            print("Another non-200-range status code was received")
            print(e.response)
            caption = 'exceeding liimt'
        except Exception as e:
            print('some error happened')
            print(e)
            caption = 'some error'
        return caption

def process_item(line):
    agent = CaptionGenerator('XXXXXXX', 'claude-3-opus-20240229')
    flag = 0
    response = {}
    prompt = line['tags']
    location = line['location']
    out_f = f'/home/abhinaba_roy/midicaps/caption_output/{location}.json'
    if os.path.exists(out_f):
        with open(out_f,'r') as f:
            cont = json.load(f)
            if(cont['caption'] == 'exceeding liimt'):
                flag = 0
            elif(cont['caption']=='some error'):
                flag = 0
            else:
                flag = 1
        f.close()
    if flag == 0:
        print(f'processing {location}')
        response['location'] = location
        response['caption'] = agent.generate_caption(prompt)
        with open(out_f,'w') as f:
            json.dump(response,f)
        f.close()
    else:
        print(f'file processed already: {location}')
    del agent
    return 1
    
def get_captions(file='test17_all.json'):
    test_ = [json.loads(line) for line in open(file)]
    num_processes = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=2)
    t_0 = time.time()
    results = pool.map(process_item, test_)
    t_1 = time.time()
    pool.close()
    pool.join()
    print(f'time_taken in multiprocessing: {t_1 - t_0}')

if __name__ =='__main__':
    get_captions('test17_all.json')