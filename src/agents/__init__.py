# agents/__init__.py
from .therapist_agent import therapist_agent
from .psychologist_agent import psychologist_agent
from .neurologist_agent import neurologist_agent
from .mindcoach_agent import mindcoach_agent
from .learning_agent import learning_agent
from .facts_agent import facts_agent
from .games_agent import games_agent
from .cognitive_neuroscientist_agent import neuroscientist_agent
from .neuropsychologist_agent import neuropsychologist_agent
from .psychiatrist_agent import psychiatrist_agent

AGENT_REGISTRY = {
    "therapist_agent": therapist_agent,
    "therapist": therapist_agent,
    "psychologist_agent": psychologist_agent,
    "psychologist": psychologist_agent,
    "neuroscientist_agent": neuroscientist_agent,
    "neuroscientist": neuroscientist_agent,
    "neurologist_agent": neurologist_agent,
    "neurologist": neurologist_agent,
    "mindcoach_agent": mindcoach_agent,
    "mindcoach": mindcoach_agent,
    "learning_agent": learning_agent,
    "learning": learning_agent,
    "facts_agent": facts_agent,
    "facts": facts_agent,
    "games_agent": games_agent,
    "games": games_agent,
    "neuropsychologist_agent": neuropsychologist_agent,
    "neuropsychologist": neuropsychologist_agent,
    "psychiatrist_agent": psychiatrist_agent,
    "psychiatrist": psychiatrist_agent,
}