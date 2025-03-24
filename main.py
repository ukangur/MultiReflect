from consistency import consistency
from eval_check import eval_check
from retrieval import text_retrieval, image_retrieval
from filtering import filtering_text, filtering_image
from ranking import combined
from verification import verify2
from utils import *

from openai import OpenAI
import pandas as pd
import os
import re
from PIL import Image


config = load_config()
client = None
if config["client"] == "llama":
    client = LlamaImageTextToTextModel(config["model_id"])
elif config["client"] == "deepseek":
    client = DeepSeekImageTextToTextModel(config["model_id"])
else:
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key, timeout=100)


def consistency_response(image_path, caption, idx):
    response = consistency.get_response(image_path, caption, client)
    verdict = 0
    if not os.path.exists(f"{config['output_path']}/generated/{idx}/"):
        os.makedirs(f"{config['output_path']}/generated/{idx}/")
    save_json(
        {"consistency_response": response},
        f"{config['output_path']}/generated/{idx}/consistency_response.json",
    )
    if "<verdict>TRUE</verdict>" in response:
        verdict = 1
    elif "<verdict>FALSE</verdict>" in response:
        verdict = 0
    else:
        if "TRUE" in response:
            verdict = 1
        elif "FALSE" in response:
            verdict = 0
        else:
            if "true" in response.lower():
                verdict = 1
            elif "false" in response.lower():
                verdict = 0
            else:
                verdict = 0
    score = re.findall(r"(?<![a-zA-Z:])[-+]?\d*\.?\d+", response)
    if len(score) == 0:
        score = 0
    else:
        score = float(score[0])
    return verdict, score


def eval_check_response(
    image_path, caption, text_evidences, image_evidences, idx, first
):
    if first:
        response = eval_check.get_response_first(image_path, caption, client)
        if not os.path.exists(f"{config['output_path']}/generated/{idx}/"):
            os.makedirs(f"{config['output_path']}/generated/{idx}/")
        append_jsonl(
            {"eval_check_response": response, "check": "first"},
            f"{config['output_path']}/generated/{idx}/eval_check_response.jsonl",
        )
        response_lines = response.split("\n")
        needs_retrieval = True
        if "Yes" in response_lines[0] or "yes" in response_lines[0].lower():
            needs_retrieval = True
        elif "No" in response_lines[0] or "no" in response_lines[0].lower():
            needs_retrieval = False
        else:
            if "Yes" in response or "yes" in response.lower():
                needs_retrieval = True
            elif "No" in response or "no" in response.lower():
                needs_retrieval = False
            else:
                needs_retrieval = True
        return needs_retrieval
    else:
        response = eval_check.get_response_subs(
            image_path, caption, text_evidences, image_evidences, client
        )
        if not os.path.exists(f"{config['output_path']}/generated/{idx}/"):
            os.makedirs(f"{config['output_path']}/generated/{idx}/")
        append_jsonl(
            {"eval_check_response": response, "check": "subsequent"},
            f"{config['output_path']}/generated/{idx}/eval_check_response.json",
        )
        response_lines = response.split("\n")
        needs_retrieval = True
        if "[Continue to Use Evidence]" in response_lines[0]:
            needs_retrieval = False
        elif "[No Retrieval]" in response_lines[0]:
            needs_retrieval = False
        elif "[Retrieval]" in response_lines[0]:
            needs_retrieval = True
        else:
            if "[Continue to Use Evidence]" in response or "[No Retrieval]" in response:
                needs_retrieval = False
            elif "[Retrieval]" in response:
                needs_retrieval = True
            else:
                needs_retrieval = True
        return needs_retrieval


def get_evidences(image_path, caption, idx):
    with open(image_path, "rb") as f:
        image_content = f.read()
    (
        wikipedia_search,
        google_search,
        bing_search,
        inverse_google_search,
        inverse_bing_search,
        inverse_google_data,
        inverse_bing_data,
    ) = text_retrieval.get_data(caption, image_content)
    if not os.path.exists(f"{config['output_path']}/retrieved/{idx}/text_data"):
        os.makedirs(f"{config['output_path']}/retrieved/{idx}/text_data")
    save_json(
        wikipedia_search,
        f"{config['output_path']}/retrieved/{idx}/text_data/wikipedia_search.json",
    )
    save_json(
        google_search,
        f"{config['output_path']}/retrieved/{idx}/text_data/google_search.json",
    )
    save_json(
        bing_search,
        f"{config['output_path']}/retrieved/{idx}/text_data/bing_search.json",
    )
    save_json(
        inverse_google_search,
        f"{config['output_path']}/retrieved/{idx}/text_data/inverse_google_search.json",
    )
    save_json(
        inverse_bing_search,
        f"{config['output_path']}/retrieved/{idx}/text_data/inverse_bing_search.json",
    )
    save_json(
        inverse_google_data,
        f"{config['output_path']}/retrieved/{idx}/text_data/inverse_google_data.json",
    )
    save_json(
        inverse_bing_data,
        f"{config['output_path']}/retrieved/{idx}/text_data/inverse_bing_data.json",
    )
    google_image_data, bing_image_data, commons_data = image_retrieval.get_image_data(
        caption, idx
    )
    if not os.path.exists(f"{config['output_path']}/retrieved/{idx}/image_data"):
        os.makedirs(f"{config['output_path']}/retrieved/{idx}/image_data")
    save_json(
        google_image_data,
        f"{config['output_path']}/retrieved/{idx}/image_data/google_image_data.json",
    )
    save_json(
        bing_image_data,
        f"{config['output_path']}/retrieved/{idx}/image_data/bing_image_data.json",
    )
    save_json(
        commons_data,
        f"{config['output_path']}/retrieved/{idx}/image_data/commons_data.json",
    )


def init_pipeline(image_path, caption, idx):
    print("Checking Consistency for Sample", idx)
    try:
        consistency_verdict, consistency_score = consistency_response(
            image_path, caption, idx
        )
        print("Consistency Verdict:", consistency_verdict)
        print("Consistency Score:", consistency_score)
        print("-" * 50)
    except:
        consistency_verdict = 0
        print("Consistency Error for", idx)
        print("-" * 50)
    if consistency_verdict == 1:
        # Move to is retrieval needed
        print("Checking if Retrieval is Needed for Sample", idx)
        try:
            extra_evidence_need = eval_check_response(
                image_path, caption, [], [], idx, first=True
            )
            print("First Eval Check:", extra_evidence_need)
            print("-" * 50)
        except:
            extra_evidence_need = True
            print("First Eval Check Error for", idx)
            print("-" * 50)
        if extra_evidence_need:
            # return
            # Move to Retrieval
            print("Retrieval Needed for Sample", idx)
            get_evidences(image_path, caption, idx)
            print("Retrieval Done for Sample", idx)
            print("-" * 50)
            # Move to Filtering
            print("Filtering Text for Sample", idx)
            filtering_text.get_all_text_filtered(idx, caption)
            print("Text Filtering Done for Sample", idx)
            print("-" * 50)
            print("Filtering Image for Sample", idx)
            img = Image.open(image_path)
            filtering_image.get_similar_images(img, idx)
            print("Image Filtering Done for Sample", idx)
            print("-" * 50)
            # Move to Ranking
            print("Ranking Text and Image for Sample", idx)
            combined.get_text_scores(idx, caption, image_path, client)
            combined.get_image_scores(idx, caption, image_path, client)
            print("Ranking Done for Sample", idx)
            print("-" * 50)
            # Check for each evidence
            print("Checking for each Evidence for Sample", idx)
            text_evidences = pd.read_csv(
                f"{config['output_path']}/ranking_score/{idx}/text_data/final_scores.csv"
            )
            text_evidences = text_evidences[text_evidences["total"] > 0]
            if len(text_evidences) == 0:
                text_evidences = []
            else:
                text_evidences = text_evidences.sort_values(
                    by="total", ascending=False
                )["evidence"].tolist()
            image_evidences = pd.read_csv(
                f"{config['output_path']}/ranking_score/{idx}/image_data/final_scores.csv"
            )
            image_evidences = image_evidences[image_evidences["total"] > 0]
            if len(image_evidences) == 0:
                image_evidences = []
            else:
                image_evidences = image_evidences.sort_values(
                    by="total", ascending=False
                )["evidence"].tolist()
            selected_text_evidences = []
            selected_image_evidences = []
            curr_text_idx = 0
            curr_image_idx = 0
            while True:
                if curr_text_idx == len(text_evidences) and curr_image_idx == len(
                    image_evidences
                ):
                    break
                if curr_text_idx < len(text_evidences):
                    selected_text_evidences.append(text_evidences[curr_text_idx])
                    curr_text_idx += 1
                if curr_image_idx < len(image_evidences):
                    selected_image_evidences.append(
                        f"{config['output_path']}/filtered/{idx}/image_data/"
                        + image_evidences[curr_image_idx]
                    )
                    curr_image_idx += 1
                if not eval_check_response(
                    image_path,
                    caption,
                    selected_text_evidences,
                    selected_image_evidences,
                    idx,
                    first=False,
                ):
                    break
            print("Checking for each Evidence Done for Sample", idx)
            print("-" * 50)
            # Move to Verification
            print("Verifying for Sample", idx)
            verify2.get_response_subs(
                idx,
                image_path,
                caption,
                selected_text_evidences,
                selected_image_evidences,
                client,
            )
            print("Verification Done for Sample", idx)
            print("-" * 50)
            print("-" * 50)
        else:
            print("No Retrieval Needed for Sample", idx)
            print("-" * 50)
            print("Verifying for Sample", idx)
            verify2.get_response_subs(idx, image_path, caption, [], [], client)
            print("Verification Done for Sample", idx)
            print("-" * 50)
            print("-" * 50)
    else:
        print("Consistency Verdict is False for Sample", idx)
        print("-" * 50)
        print("Verifying for Sample", idx)
        verify2.get_response_subs(idx, image_path, caption, [], [], client)
        print("Verification Done for Sample", idx)
        print("-" * 50)
        print("-" * 50)


df = pd.read_csv(f"{config['data_path']}/VERITE.csv")
for idx in range(len(df)):
    try:
        caption = df.iloc[idx]["caption"]
        image_path = f"{config['data_path']}/{df.iloc[idx]['image_path']}"
        init_pipeline(image_path, caption, idx)
    except Exception as e:
        print(e, idx)
        continue
