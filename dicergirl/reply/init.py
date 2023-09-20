"""
初始化DGI_PROVIDERS与CUSTOM_PROVIDERS数组
"""
import os
import re

from multilogging import multilogger

from dicergirl.common import const
from dicergirl.common.response import GenericResponse, ConditionResponse
from dicergirl.reply.data import GenericData, ConditionData
from dicergirl.reply.manager import manager
from dicergirl.reply.parsers import templates
from dicergirl.reply.parsers.matcher import MatchType

logger = multilogger(name="DicerGirl", payload="ReplyModuleInit")


def init():
    """
    初始化方法
    """
    if not os.path.exists(const.REPLY_FOLDER_PATH):
        os.makedirs(const.REPLY_FOLDER_PATH)
    _load_template_methods()
    _init_reply_config()
    _init_default_template_file()


def _load_template_methods():
    """
    获取 templates.py 中的所有方法
    """
    for name, method in vars(templates).items():
        if callable(method):
            manager.register_method(method)


def _init_reply_config():
    """
    加载reply文件数组中
    """
    try:
        for filename in os.listdir(const.REPLY_FOLDER_PATH):
            filepath = os.path.join(const.REPLY_FOLDER_PATH, filename)
            logger.info(f"载入文件: [{filepath}]")
            if os.path.isfile(filepath):
                _load_custom_generic_reply_file(filename, filepath)
                _load_condition_specific_reply_file(filename, filepath)
    except KeyError as e:
        logger.error(
            f"请确保您的回复配置文件包含了正确的键和相应的值。如果您不确定如何正确配置文件，请参考文档或向管理员寻求帮助。")
        logger.error(f"Error: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")


def _init_default_template_file():
    """
    默认模板文件初始化
    """
    try:
        if not os.path.exists(const.EXAMPLE_REPLY_FILE_PATH):
            with open(file=const.EXAMPLE_REPLY_FILE_PATH, mode='wb') as drf:
                raw_data = const.REPLY_YAML.load(const.CONDITION_SPECIFIC_TEMPLATE)
                const.REPLY_YAML.dump(data=raw_data, stream=drf)
    except Exception as e:
        logger.error(f"{type(e)}:e")


def _load_custom_generic_reply_file(filename, filepath):
    pattern = re.compile(r'^dg-.*\.yml$')
    if pattern.match(filename):
        with (open(filepath, "rb") as file):
            data = const.REPLY_YAML.load(file)
            group_name = filename.removeprefix("dg-").removesuffix(".yml")
            version = data["version"]
            author = data["author"]
            description = data["description"]
            enable = data["enable"]
            container = GenericData(group_name, version, author, description, enable)
            items = data["items"]
            logger.debug(items)
            for item in items:
                for event_name, send_text, enable in item.items():
                    container.add(GenericResponse(event_name, send_text))
            manager.register_container(container)


def _load_condition_specific_reply_file(filename, filepath):
    if filename.endswith(".yml"):
        with (open(filepath, "rb") as file):
            data = const.REPLY_YAML.load(file)
            group_name = filename.removesuffix(".yml")
            version = data["version"]
            author = data["author"]
            description = data["description"]
            enable = data["enable"]
            container = ConditionData(group_name, version, author, description, enable)
            items = data["items"]
            logger.debug(items)
            for item in items:
                for event_name, event_content in item.items():
                    container.add(ConditionResponse(event_name,
                                                    event_content["send_text"],
                                                    event_content["match_field"],
                                                    MatchType[event_content["match_type"]],
                                                    event_content["enable"],
                                                    ))
            manager.register_container(container)
