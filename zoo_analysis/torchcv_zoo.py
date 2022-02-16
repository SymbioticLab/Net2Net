import os
import sys

sys.path.insert(0, '../ray_tune/models/')

# Imgclsmob zoo
from torchcv.model_provider import _models as model_zoo
from torchcv.model_provider import get_model as ptcv_get_model

# Cifar zoo
from cifarmodels import *

import torch
from torch.autograd import Variable
import pickle
import string

def export_onnx():
    size = 224

    dummy_input = torch.rand(2, 3, size, size) #  batch:32; 3 channels; 32 x 32 size
    path = f'{os.environ["HOME"]}/experiments/zoo'
    os.makedirs(path, exist_ok=True)

    cnt = 0
    params_set = set()
    name_list = ['_cifar10', '_cifar100', '_svhn', '_cub', '_voc', '_coco', '_ade20k', '_cityscapes', '_celebamaskhq']
    # cifar_first = [m for m in model_zoo if 'cifar10' in m]
    # cifar_first += [x for x in model_zoo if x not in cifar_first]
    models = []
    for m in model_zoo:
        is_small = False
        for n in name_list:
            if n in m:
                is_small = True
                break
        if not is_small:
            models.append(m)

    for model_name in models:
        try:
            model = ptcv_get_model(model_name, pretrained=False, num_classes=103)
            num_params = sum(p.numel() for p in model.parameters())

            if num_params in params_set:
                print(f"{model_name} is repeated")
                continue
            output = model(dummy_input)
            torch.onnx.export(model, dummy_input, os.path.join(path, model_name+".onnx"),
                              export_params=False, verbose=0, training=1)

            print(f"Successfully generate {model_name}, # of params {num_params}")
            with open(f"{os.path.join(path, model_name)}", 'wb') as fout:
                pickle.dump(model, fout)

            params_set.add(num_params)
            cnt += 1

        except Exception as e:
            print(f"{model_name} failed due to {e}")

    print("============")
    print(f"Generate {cnt} models in total, failed {len(model_zoo)-cnt} models")

def polish_name(model_name):
    updated_name = ''
    for c in model_name:
        if c in string.punctuation:
            updated_name += '_'
        else:
            updated_name += c

    return updated_name.replace('__', '')

def validate_list():
    size = 32
    num_classes = 100

    dummy_input = torch.rand(2, 3, size, size) #  batch:32; 3 channels; 32 x 32 size
    modellist = 'modellist'
    path = '/mnt/zoo/modellist'
    cnt = 0
    params_set = set()
    model_list = [x.strip() for x in open(modellist).readlines()]

    for model_name in model_list:
        try:
            if '(' in model_name:
                if '()' in model_name:
                    eval_func = model_name.replace(')', f'num_classes={num_classes})')
                else:
                    eval_func = model_name.replace(')', f', num_classes={num_classes})')
                model = eval(eval_func)
            else:
                model = ptcv_get_model(model_name, pretrained=False, num_classes=num_classes)

            num_params = sum(p.numel() for p in model.parameters())

            updated_name = polish_name(model_name)
            if num_params in params_set:
                print(f"{updated_name} is repeated")
                continue
            output = model(dummy_input)
            torch.onnx.export(model, dummy_input, os.path.join(path, updated_name+".onnx"),
                              export_params=False, verbose=0, training=1)

            print(f"Successfully generate {updated_name}, # of params {num_params}")
            # with open(f"{os.path.join(path, model_name)}", 'wb') as fout:
            #     pickle.dump(model, fout)

            params_set.add(num_params)
            cnt += 1

        except Exception as e:
            print(f"{model_name} failed due to {e}")

    print("============")
    print(f"Generate {cnt} models in total, failed {len(model_zoo)-cnt} models")

def clean_up_logs(file):
    with open(file) as f:
        lines = [x for x in f.readlines() if 'Successfully' in x]

    with open('model-zoo', 'w') as fout:
        for line in lines:
            fout.writelines(line.split()[2].strip()[:-1] + '\n')

#export_onnx()
clean_up_logs('model-export-list')
#validate_list()
