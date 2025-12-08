from child_ai.logic_engine import Predicate, Constant, Variable, Rule, DefaultRule, LogicEngine

def test_default_reasoning():
    engine = LogicEngine()
    x = Variable("x")
    engine.add_fact(Predicate("Bird", (Constant("Tweety"),)))
    engine.add_default_rule(DefaultRule(Predicate("Bird", (x,)), Predicate("Flies", (x,))))
    assert engine.query(Predicate("Flies", (Constant("Tweety"),))) == True

def test_default_reasoning_with_exception():
    engine = LogicEngine()
    x = Variable("x")
    engine.add_fact(Predicate("Penguin", (Constant("Tux"),)))
    engine.add_rule(Rule(Predicate("Penguin", (x,)), Predicate("Bird", (x,))))
    engine.add_fact(Predicate("NotFlies", (Constant("Tux"),)))
    engine.add_default_rule(DefaultRule(Predicate("Bird", (x,)), Predicate("Flies", (x,))))
    assert engine.query(Predicate("Flies", (Constant("Tux"),))) == False
