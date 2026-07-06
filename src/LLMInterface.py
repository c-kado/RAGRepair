import datetime
import argparse
import json
import torch
from torch import cuda,bfloat16
import transformers
from transformers import AutoTokenizer,AutoModelForCausalLM,AutoModelForSeq2SeqLM

from openai import OpenAI

class CodeLlama:

    def __init__(self, model):
        self.output = ''
        match model:
            case 'codellama' | 'codellama-7b':
                # default('codellama') -> codellama-7b
                self.model_id = 'CodeLlama-7b-Instruct-hf'
            case 'codellama-13b':
                self.model_id = 'CodeLlama-13b-Instruct-hf'

        

    def install_model(self):
        print('quantize')
        # 量子化
        '''
        quant_config = transformers.BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type='nf4',
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=bfloat16
        )
        '''
        quant_config = transformers.BitsAndBytesConfig(load_in_8bit=True)

        print('download model from_pretrained')
        self.model = AutoModelForCausalLM.from_pretrained(
            f'codellama/{self.model_id}',
            trust_remote_code=True,
            quantization_config=quant_config,
            device_map="auto"
        )

        print('download tokenizer from_pretrained')
        self.tokenizer = AutoTokenizer.from_pretrained(f'codellama/{self.model_id}')

        return 


    # def load_model(self, save_directory):
        # self.model = AutoModelForCausalLM.from_pretrained(save_directory)
        # self.tokenizer = AutoTOkenizer.from_pretrained(save_directory)


    def run_inference(self, system_prompt, task_prompt, contract_code):
        prompt = f'<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{task_prompt}[/INST]'

        pipeline = transformers.pipeline(
            task = "text-generation",
            model = self.model,
            tokenizer = self.tokenizer,
            device_map = 'auto'
        )

        print(f'Run CodeLlama')
        # self.save_log(f'repair: {vul}/{file}\t{target_version}')
        start_dt = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        # print('\tinference start: ' + start_dt.strftime('%m/%d %X'))
        # self.save_log(f'{start_dt.strftime("%m/%d %X")}: inference start')

        sequences = pipeline(
            prompt,
            do_sample=True,
            temperature=0.2,
            top_p=0.95,
            eos_token_id=self.tokenizer.eos_token_id,
            truncation=True,
            max_new_tokens=len(self.tokenizer(contract_code)['input_ids'])*1.1
        )

        end_dt = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        self.exec_time = str(end_dt - start_dt)[:-7]
        # self.save_log(f'{end_dt.strftime("%m/%d %X")}: end inference')
        # self.save_log(f'execution time: {self.exec_time}')
        print('\texec time: '+ self.exec_time)
        # extract only output from sequences
        self.output = sequences[0]['generated_text'][len(prompt):]


    def save_output(self, save_file):
        with open(save_file, 'w') as f:
            f.write(self.output)


    def save_log(self, log):
        with open('./run_codellama.log', 'a') as f:
            f.write(f'[{self.model}]\t{log}\n')


# Not Working
# TODO: Introduce CodeT5p
class CodeT5p:

    def __init__(self, model):
        self.output = ''
        match model:
            case 'codet5p' | 'codet5p-2b':
                self.model_id = 'codet5p-2b'
            case 'codet5p-770m':
                self.model_id = 'codet5p-770m'

        

    def install_model(self):

        checkpoint = f'Salesforce/{self.model_id}'
        device = 'cuda' # for GPU usage or "cpu" for CPU usage

        self.tokenizer = AutoTokenizer.from_pretrained(checkpoint)
        match self.model_id:
            case 'codet5p-2b':
                self.model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint,
                                              torch_dtype=torch.float16,
                                              trust_remote_code=True).to(device)
            case 'codet5p-770m':
                self.model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint).to(device)

        return 


    # def load_model(self, save_directory):
        # self.model = AutoModelForCausalLM.from_pretrained(save_directory)
        # self.tokenizer = AutoTOkenizer.from_pretrained(save_directory)


    def run_inference(self, system_prompt, task_prompt, contract_code, vul, file, target_version):

        prompt = f'{task_prompt}'
        inputs = tokenizer.encode(prompt, return_tensors="pt").to(device)
        input_tokens = tokens.input_ids.shape[1]

        print(f'Run CodeT5p: {vul}/{file}\t{target_version}')
        self.save_log(f'repair: {vul}/{file}\t{target_version}')
        start_dt = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        print('\tinference start: ' + start_dt.strftime('%m/%d %X'))
        self.save_log(f'{start_dt.strftime("%m/%d %X")}: inference start')

        outputs = model.generate(
            **inputs,
            max_new_tokens=input_tokens,
            do_sample=True,
            temperature=0.2,
            top_p=0.95,
            length_penalty=1.0, # default=1.0
        )

        end_dt = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        self.exec_time = str(end_dt - start_dt)[:-7]
        self.save_log(f'{end_dt.strftime("%m/%d %X")}: end inference')
        self.save_log(f'execution time: {self.exec_time}')
        print('\texec time: '+ self.exec_time)
        self.output = tokenizer.decode(outputs[0], skip_special_tokens=True)


    def save_output(self, save_file):
        with open(save_file, 'w') as f:
            f.write(self.output)


    def save_log(self, log):
        with open('./run_codellama.log', 'a') as f:
            f.write(f'[{self.model}]\t{log}\n')



class GPT:
    def __init__(self, model_id='gpt-5', api_key=''):
        # GPT-5.1 is our flagship model for coding and agentic tasks with configurable reasoning and non-reasoning effort.
        # https://platform.openai.com/docs/models/gpt-5
        self.model_id = model_id
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)

        match model_id:
            case 'gpt' | 'gpt-5':
                # default('gpt') -> gpt-5
                self.model_id = 'gpt-5'

    def install_model(self):
        return


    def run_inference(self, system_prompt, task_prompt, contract_code=None):
        print(f'Run GPT')
        # self.save_log(f'repair: {vul}/{file}\t{target_version}')
        start_dt = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        print('\tinference start: ' + start_dt.strftime('%m/%d %X'))
        # self.save_log(f'{start_dt.strftime("%m/%d %X")}: inference start')

        completion = self.client.chat.completions.create(
            model = self.model_id,
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task_prompt}
            ]
        )

        end_dt = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        self.exec_time = str(end_dt - start_dt)[:-7]
        # self.save_log(f'{end_dt.strftime("%m/%d %X")}: end inference')
        # self.save_log(f'execution time: {self.exec_time}')
        print('\texec time: '+ self.exec_time)
        self.output = completion.choices[0].message.content



    def save_output(self, save_file):
        with open(save_file, 'w') as f:
            f.write(self.output)


    def save_log(self, log):
        with open('./run_gpt.log', 'a') as f:
            f.write(f'{log}\n')



def argument_processing(args):
    model_list = {'gpt': ['gpt-5'],
                  'codellama': ['codellama-7b', 'codellama-13b'],
                  'codet5p': ['codet5p-770m', 'codet5p-2b', 'codet5p-6b']}
    if args.model in model_list['gpt']:
        with open('api_key.txt', 'r') as f:
            key = f.read()
        model = GPT(args.model, key)
    elif args.model in model_list['codellama']:
        model = CodeLlama(args.model)
        model.install_model()
    elif args.model in model_list['codet5p']:
        model = CodeT5p(args.model)
        model.install_model()
    else:
        raise 

   

    return model, args.prompt, args.output


def get_args():
    print()
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', choices=['gpt', 'gpt-5', 'codellama', 'codellama-7b', 'codellama-13b', 'codet5p-770m', 'codet5p-2b', 'codet5p-6b'], required=True)
    parser.add_argument('-p', '--prompt', default='')
    parser.add_argument('-o', '--output', default='')
    args = parser.parse_args()

    return args


def main(model, prompt_file, output_file):
    if prompt_file != '':
        with open(prompt, 'r') as f:
            prompt = json.load(f)
        sys_prompt = prompt['system_prompt']
        user_prompt = prompt['user_prompt']
    else:
        print('System Prompt >>')
        sys_prompt = input()
        print('Prompt >>')
        user_prompt = input()

    model.install_model()
    model.run_inference(sys_prompt, user_prompt)

    if output_file != '':
        with open(output_file, 'w') as f:
            f.write(model.output)
    else:
        os.makedirs('output/', exist_ok=True)
        with open('output/gpt_output.txt', 'w') as f:
            f.write(model.output)


if __name__ == '__main__':
    model, prompt_file, output_file = argument_processing(get_args())
    main(model)
