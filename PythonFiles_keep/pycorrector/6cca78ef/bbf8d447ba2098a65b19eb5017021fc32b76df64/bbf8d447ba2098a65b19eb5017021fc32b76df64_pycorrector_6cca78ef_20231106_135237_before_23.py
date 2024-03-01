# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: 
"""
import argparse
import sys

sys.path.append('../..')

from pycorrector.deepcontext.deepcontext_model import DeepContextModel


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_dir", default="outputs/deepcontext_model/", type=str, help="Dir for model save.")
    parser.add_argument("--max_length", default=128, type=int, help="The maximum total input sequence length")
    parser.add_argument("--embed_size", default=128, type=int, help="Embedding size.")
    parser.add_argument("--hidden_size", default=128, type=int, help="Hidden size.")
    parser.add_argument("--dropout", default=0.25, type=float, help="Dropout rate.")

    args = parser.parse_args()
    print(args)

    m = DeepContextModel(
        args.model_dir,
        embed_size=args.embed_size,
        hidden_size=args.hidden_size,
        dropout=args.dropout,
        max_length=args.max_length
    )
    inputs = [
        '老是较书。',
        '感谢等五分以后，碰到一位很棒的奴生跟我可聊。',
        '遇到一位很棒的奴生跟我聊天。',
        '遇到一位很美的女生跟我疗天。',
        '他们只能有两个选择：接受降新或自动离职。',
        '王天华开心得一直说话。'
    ]
    outputs, details = m.correct_batch(inputs)
    for a, b, c in zip(inputs, outputs, details):
        print('input  :', a)
        print('predict:', b, c)
        print()
    # result:
    # input  : 老是较书。
    # predict: 老师教书。 [('是', '师', 1, 2), ('较', '教', 2, 3)]
    #
    # input  : 感谢等五分以后，碰到一位很棒的奴生跟我可聊。
    # predict: 感谢等五分以后，碰到一位很棒的女生跟我可聊。 [('奴', '女', 15, 16)]


if __name__ == "__main__":
    main()
