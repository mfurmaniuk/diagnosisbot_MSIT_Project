#------------------------#
# Test the Chatbot  #
#------------------------#

import pytest
from chatbot import Chatbot

@pytest.fixture
def chatbot():
    return Chatbot()




