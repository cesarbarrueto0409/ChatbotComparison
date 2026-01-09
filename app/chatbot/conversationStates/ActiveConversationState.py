from app.chatbot.conversationStates.ConversationState import ConversationState

"""State representing an active conversation with the AI agent."""
class ActiveConversationState(ConversationState):
    def handle(self, controller, history: list[dict]) -> str: # takes controller and history as parameters

        response = controller.agent.respond(history) # get response from the controller'sAI agent

        history.append({"role": "ai", "content": response}) # append AI response to history
        controller.redis.save_history(controller.session_id, history) # save updated history to Redis
        controller.mongo.save_message(controller.session_id, "ai", response) # save AI response to MongoDB
        
        return response # return the AI response