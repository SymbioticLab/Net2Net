from modelkeeper.config import modelkeeper_config
from modelkeeper.matchingopt import ModelKeeper

import argparse
import logging
import pickle
import torch
import time
import os, sys

log_path = './modelkeeper_log'
logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)s %(message)s',
                datefmt='%H:%M:%S',
                level=logging.INFO,
                handlers=[
                    logging.FileHandler(log_path, mode='a'),
                    logging.StreamHandler()
                ])

def mapper_model(model_export):
  zoo_path = f'{os.environ["HOME"]}/experiment/data/my_zoo'
  modelkeeper_config.zoo_path = zoo_path
  mapper = ModelKeeper(modelkeeper_config)

  model_folders = os.listdir(zoo_path)
  models = []
  for idx, model_path in enumerate(model_folders):
      if os.path.isdir(os.path.join(zoo_path, model_path)):
          model_name = [x for x in os.listdir(os.path.join(zoo_path, model_path)) if '.onnx' in x]
          if len(model_name) == 1:
              models.append(os.path.join(zoo_path, model_path, model_name[0]))
              mapper.add_to_zoo(models[-1])

  weights, meta_info = mapper.map_for_onnx(model_export, set([]), model_export.split('/')[-1])

  with open(f"{model_export}_keeper.pkl", 'wb') as fout:
    pickle.dump(weights, fout)
    pickle.dump(meta_info, fout)

mapper_model(sys.argv[1])

