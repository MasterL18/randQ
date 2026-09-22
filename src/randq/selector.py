import random

def rand_draw(n_list, q_list, rng=None, excluded_pairs=None):
  rng = rng or random
  excluded_pairs = excluded_pairs or set()
  available_pairs = [
      (name, question)
      for name in n_list
      for question in q_list
      if (name, question) not in excluded_pairs
  ]
  if not available_pairs:
    raise ValueError("No name/question pairs are available")

  return rng.choice(available_pairs)