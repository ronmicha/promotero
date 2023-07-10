import sys
from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from typing import List, Tuple, Union

from common.constants import ALL_ENVS, MODULES_ARG_DEFAULT_VALUE, PROD_ENVS, QA_ENVS
from common.utils import clean_string, is_qa_env

Args = Tuple[str, List[str], List[str], List[str], bool, bool]


def _create_parser() -> ArgumentParser:
    return ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        description="This script automatically copies specific configuration files between environments - useful for promoting a feature to multiple environments",
    )


def _create_args(parser: ArgumentParser) -> Namespace:
    parser.add_argument(
        "-se",
        "--src-env",
        required=True,
        nargs=1,
        help="""\tSource environment to copy the configuration from
        Usage example: -se qa-web-1""",
        metavar="env",
    )

    parser.add_argument(
        "-de",
        "--dest-envs",
        nargs="*",
        action="append",
        help="""\tDestination environment(s) to copy the configuration to, separated by spaces. The source environment will be filtered out
        Usage example: -de qa-atlas-1 qa-nova-1
        Default: all QA/PROD envs, based on the source environment""",
        metavar="env",
    )

    parser.add_argument(
        "-s",
        "--services",
        nargs="*",
        action="append",
        default=[],
        help="""\tNames of the services to copy from the source environment, separated by spaces
        Usage example: -s viz-web dicomweb-provider""",
        metavar="service_name",
    )

    parser.add_argument(
        "-m",
        "--modules",
        nargs="*",
        action="append",
        default=[MODULES_ARG_DEFAULT_VALUE],
        help="""\tService modules (or SSM) to copy, separated by spaces
        Usage example: -m ecs-service alb ssm
        Default: all modules""",
        metavar="module",
    )

    parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help="""\tOverwrite files and sub-folders in the destination environment(s)
        Default: False""",
    )

    parser.add_argument(
        "-a",
        "--apply",
        action="store_true",
        help="""\tActually copy the configuration. Omitting it runs the operation in "dry-run" mode. Use after review the dry-run output
        Default: False""",
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return parser.parse_args()


def _parse_arg(arg) -> Union[str, List[str], bool]:
    parsed_arg = arg
    if isinstance(arg, list):
        filtered_arg = list(filter(None, arg))
        parsed_arg = filtered_arg if len(filtered_arg) == 0 else filtered_arg.pop()
    return [clean_string(x) for x in parsed_arg] if isinstance(parsed_arg, list) else clean_string(parsed_arg)


def _validate_args(args: Args) -> None:
    src_env, dest_envs, services, modules, overwrite, apply = args

    if not src_env:
        raise Exception("Source environment must be a non-empty string")

    formatted_all_envs = "\n\t" + "\n\t".join(ALL_ENVS)

    if src_env not in ALL_ENVS:
        raise Exception(f"Unrecognized source environment '{src_env}'. An environment must be one of: {formatted_all_envs}")

    for dest_env in dest_envs:
        if dest_env not in ALL_ENVS:
            raise Exception(f"Unrecognized destination environment '{dest_env}'. An environment must be one of: {formatted_all_envs}")


def get_args() -> Args:
    parser = _create_parser()
    raw_args = _create_args(parser)

    parsed_src_env = _parse_arg(raw_args.src_env)
    parsed_dest_envs = _parse_arg(raw_args.dest_envs)

    if not parsed_dest_envs:
        parsed_dest_envs = QA_ENVS if is_qa_env(parsed_src_env) else PROD_ENVS

    parsed_dest_envs = [env for env in parsed_dest_envs if env != parsed_src_env]

    args: Args = (
        parsed_src_env,
        parsed_dest_envs,
        _parse_arg(raw_args.services),
        _parse_arg(raw_args.modules),
        _parse_arg(raw_args.overwrite),
        _parse_arg(raw_args.apply),
    )

    _validate_args(args)

    return args
