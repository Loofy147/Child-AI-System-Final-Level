from .logic_engine import LogicEngine
from .knowledge_integration import KnowledgeIntegrator
from .learning_module import LearningModule

logic_engine = LogicEngine()
knowledge_integrator = KnowledgeIntegrator(logic_engine)
learning_module = LearningModule(logic_engine)
