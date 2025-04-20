from verification import verify_noevi
from utils import *

from openai import OpenAI
import pandas as pd

# import os
# import re
from PIL import Image

config = load_config()
client = GptImagetextToTextModel(config["model_api_key"])


def init_pipeline(image_path, caption, idx):
    verify_noevi.get_response_subs(idx, image_path, caption, client)


df = pd.read_csv("./data/original/VERITE.csv")
for idx in [576, 822]:
    try:
        with open(f"./data/generated/{idx}/verification_noevi.json", "r") as f:
            data = json.load(f)
        if (
            "OUT-OF-CONTEXT" in data["response"]
            or "TRUE" in data["response"]
            or "FALSE" in data["response"]
        ):
            continue
        else:
            print(data["response"], idx)
        # image_path = f"./data/original/{df.iloc[idx]['image_path']}"
        # caption = df["caption"][idx]
        # init_pipeline(image_path, caption, idx)
        # print("Done", idx)
    except Exception as e:
        print(e, idx)
        continue
