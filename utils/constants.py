# ----------------------------------------------------------------------------- #
#                                      定数                                     #
# ----------------------------------------------------------------------------- #

from typing import Final

# --------------------------------- メッセージ --------------------------------- #


class MessageText:
    """
    MessageText定数
    """

    WELCOME_MESSAGE: Final[
        str
    ] = """\
ようこそ！**{display_name}** さん 👏
"""
    LEAVE_MESSAGE: Final[
        str
    ] = """\
さようなら、**{display_name}** さん 👋
"""


# ----------------------------------------------------------------------------- #


# --------------------------- 埋め込みオブジェクト 色 --------------------------- #


class EmbedColor:
    """\
    EmbedColor定数
    """

    SUCCESS: Final[int] = 0x5CB85C
    INFO: Final[int] = 0x0275D8
    WARN: Final[int] = 0xF0AD4E
    ERROR: Final[int] = 0xD9534F


# ----------------------------------------------------------------------------- #