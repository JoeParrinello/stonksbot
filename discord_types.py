"""Module providing helpful discord types"""
from enum import IntEnum

class ApplicationCommandType(IntEnum):
    """Types of Commands to register a bot for."""
    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3

class ApplicationCommandOptionType(IntEnum):
    """Types of input values to commands."""
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENTIONABLE	= 9
    NUMBER = 10
    ATTACHMENT = 11

class InteractionType(IntEnum):
    """Types of messages received on the Discord Webhook."""
    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5

class InteractionCallbackType(IntEnum):
    """Types of callbacks used to respond to discord commands."""
    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7
    APPLICATION_COMMAND_AUTOCOMPLETE_RESULT = 8
    MODAL = 9

