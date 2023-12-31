from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from llama_index.llms import MockLLM
from llama_index.llms.base import LLM
from llama_index.llms.llama_utils import completion_to_prompt, messages_to_prompt
from pydantic import BaseModel

from app.config.settings import AppSettings, get_app_settings
from app.paths import models_path


class LLMComponent:
    llm: LLM

    def __init__(
        self,
        app_settings: AppSettings = get_app_settings(),
    ) -> None:
        from llama_index.llms import LlamaCPP

        if app_settings.fastapi_env != "testing":
            self.llm = LlamaCPP(
                model_path=str(models_path / app_settings.llm_hf_model_file),
                temperature=0.1,
                # llama2 has a context window of 4096 tokens,
                # but we set it lower to allow for some wiggle room
                context_window=3900,
                generate_kwargs={},
                # All to GPU
                model_kwargs={"n_gpu_layers": -1},
                # transform inputs into Llama2 format
                messages_to_prompt=messages_to_prompt,
                completion_to_prompt=completion_to_prompt,
                verbose=True,
            )
        else:
            self.llm = MockLLM()


@lru_cache
def get_llm_component() -> LLMComponent:
    return LLMComponent()
