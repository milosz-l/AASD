from chains.chatbot_chain import ChatbotChain
from chains.knowledge_chain import KnowledgeChain
from chains.aggregation_chain import AggregationChain
from chains.logging_chain import LoggingChain

from langgraph.graph import END, StateGraph
from typing import Annotated, TypedDict, List
from operator import add

class MedicalState(TypedDict):
    user_request: str
    rephrased_request: str
    source_knowledge_pairs: Annotated[List[tuple[str, str]], add]
    aggregated_knowledge: str
    answer: str
    conversation_id: str
    location: str
    conversation_history: List[dict]
    summary: str
    symptoms_categories: List[str]
    datetime: str

class MedicalGraph:
    def _request_answered_routing(self, state: MedicalState):
        if state["answer"] == "":
            return ["knowledge_agent_wikipedia", "knowledge_agent_nhs"]
        else:
            return "logging_agent"

    def create(self):
        graph = StateGraph(MedicalState)

        graph.add_node("chatbot_agent", ChatbotChain().create())
        graph.add_node("knowledge_agent_wikipedia", KnowledgeChain("https://www.wikipedia.org/").invoke)
        graph.add_node("knowledge_agent_nhs", KnowledgeChain("https://www.nhs.uk/conditions/").invoke)
        graph.add_node("aggregation_agent", AggregationChain().create())
        graph.add_node("logging_agent", LoggingChain().create())

        graph.add_conditional_edges("chatbot_agent", self._request_answered_routing)
        graph.add_edge(["knowledge_agent_wikipedia", "knowledge_agent_nhs"], "aggregation_agent")
        graph.add_edge("aggregation_agent", "chatbot_agent")
        graph.add_edge("logging_agent", END)

        graph.set_entry_point("chatbot_agent")

        return graph.compile()