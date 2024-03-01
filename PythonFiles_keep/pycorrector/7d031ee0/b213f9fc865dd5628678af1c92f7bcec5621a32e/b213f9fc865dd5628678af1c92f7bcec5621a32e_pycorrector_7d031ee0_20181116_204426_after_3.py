# -*- coding: utf-8 -*-
"""
@author:XuMing（xuming624@qq.com)
@description: Inference
"""
import sys

sys.path.append('../..')
import torch
from torch import optim

from pycorrector.deep_context import config
from pycorrector.deep_context.data_util import read_config, load_vocab
from pycorrector.deep_context.network import Context2vec


def inference(model_path,
              emb_path,
              gpu_id):
    def return_split_sentence(sentence):
        if ' ' not in sentence:
            print('sentence should contain white space to split it into tokens')
            raise SyntaxError
        elif '[]' not in sentence:
            print('sentence should contain `[]` that notes the target')
            raise SyntaxError
        else:
            tokens = sentence.lower().strip().split()
            target_pos = tokens.index('[]')
            return tokens, target_pos

    # device
    use_cuda = torch.cuda.is_available() and gpu_id > -1
    if use_cuda:
        device = torch.device('cuda:{}'.format(gpu_id))
        torch.cuda.set_device(gpu_id)
    else:
        device = torch.device('cpu')

    # load model
    model, config_dict = read_model(model_path)
    unk_token = config_dict['unk_token']
    bos_token = config_dict['bos_token']
    eos_token = config_dict['eos_token']

    # read vocab from word_emb path
    itos, stoi = load_vocab(emb_path)

    # norm weight
    model.norm_embedding_weight(model.criterion.W)

    while True:
        sentence = input('>> ')
        try:
            tokens, target_pos = return_split_sentence(sentence)
        except SyntaxError:
            continue
        tokens[target_pos] = unk_token
        tokens = [bos_token] + tokens + [eos_token]
        indexed_sentence = [stoi[token] if token in stoi else stoi[unk_token] for token in tokens]
        input_tokens = torch.tensor(indexed_sentence, dtype=torch.long, device=device).unsqueeze(0)
        topv, topi = model.run_inference(input_tokens, target=None, target_pos=target_pos)
        for value, key in zip(topv, topi):
            print(value.item(), itos[key.item()])


def read_model(model_path):
    config_file = model_path + '.config.json'
    config_dict = read_config(config_file)
    model = torch.load(model_path)
    return model, config_dict


if __name__ == "__main__":
    inference(config.model_path,
              config.emb_path,
              config.gpu_id)
