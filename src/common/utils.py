from typing import List, Union

from common.constants import (
    PROD_ENV_REGIONS,
    PROD_ENVS,
    QA_ENV_REGIONS,
    QA_ENVS,
    ROOT_PATH,
    STG_ENV_REGIONS,
    STG_ENVS,
)


def clean_string(element):
    if isinstance(element, str):
        return element.lower().strip()
    return element


def is_subset(small_list: List, big_list: List) -> bool:
    return len(set(small_list) - set(big_list)) == 0


def is_qa_env(env: Union[str, List[str]]) -> bool:
    if isinstance(env, list):
        return is_subset(env, QA_ENVS)
    return env in QA_ENVS


def is_prod_env(env: Union[str, List[str]]) -> bool:
    if isinstance(env, list):
        return is_subset(env, PROD_ENVS)
    return env in PROD_ENVS


def is_stg_env(env: Union[str, List[str]]) -> bool:
    if isinstance(env, list):
        return is_subset(env, STG_ENVS)
    return env in STG_ENVS


def get_env_region(env: str) -> str:
    if is_qa_env(env):
        return QA_ENV_REGIONS[env]
    if is_prod_env(env):
        return PROD_ENV_REGIONS[env]
    if is_stg_env(env):
        return STG_ENV_REGIONS[env]


def remove_root_path(path: str) -> str:
    return path.replace(ROOT_PATH, "")


def is_promoting_qa_to_prod(src_env: str, dest_env: str) -> bool:
    return is_qa_env(src_env) and is_prod_env(dest_env)


def is_promoting_qa_to_stg(src_env: str, dest_env: str) -> bool:
    return is_qa_env(src_env) and is_stg_env(dest_env)
