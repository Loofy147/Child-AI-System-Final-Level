from child_ai.logic_engine import Predicate, Constant, Variable, Rule, LogicEngine

def test_add_fact():
    engine = LogicEngine()
    fact = Predicate("Human", (Constant("Socrates"),))
    engine.add_fact(fact)
    assert fact in engine.get_all_facts()

def test_add_rule_and_query():
    engine = LogicEngine()
    x = Variable("x")
    engine.add_fact(Predicate("Human", (Constant("Socrates"),)))
    engine.add_rule(Rule(Predicate("Human", (x,)), Predicate("Mortal", (x,))))
    assert engine.query(Predicate("Mortal", (Constant("Socrates"),))) == True

def test_query():
    engine = LogicEngine()
    x = Variable("x")
    engine.add_fact(Predicate("Human", (Constant("Socrates"),)))
    engine.add_rule(Rule(Predicate("Human", (x,)), Predicate("Mortal", (x,))))
    assert engine.query(Predicate("Mortal", (Constant("Socrates"),))) == True
    assert engine.query(Predicate("Mortal", (Constant("Plato"),))) == False
