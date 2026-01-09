from app.chatbot.conversationStates.ConversationState import ConversationState

"""State representing an ended conversation."""
class EndedConversationState(ConversationState):
    def handle(self, controller, user_input: str) -> str:
        return "Conversation is over, Goodbye!"