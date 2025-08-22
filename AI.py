import json
import random
import os

BRAIN_FILE = "sam_brain.json"
MEMORY_FILE = "sam_memory.json"

class SamBrain:
    def __init__(self, order=5):
        self.order = order
        self.map = {}      # key: context tuple -> list of next words
        self.starts = []   # contexts that can start a sentence

    def feed(self, text):
        tokens = text.lower().split()
        if len(tokens) <= self.order:
            return
        self.starts.append(tuple(tokens[:self.order]))
        for i in range(len(tokens) - self.order):
            key = tuple(tokens[i:i+self.order])
            nxt = tokens[i+self.order]
            self.map.setdefault(key, []).append(nxt)

    def generate(self, prompt="", max_words=50):
        tokens = prompt.lower().split()
        if len(tokens) >= self.order:
            ctx = tuple(tokens[-self.order:])
        else:
            ctx = None

        out = tokens[:] if tokens else []

        for _ in range(max_words):
            key = ctx if ctx in self.map else random.choice(list(self.map.keys())) if self.map else None
            if not key:
                break
            nxt = random.choice(self.map[key])
            # avoid repeating same word twice in a row
            if out and nxt == out[-1]:
                continue
            out.append(nxt)
            ctx = tuple(out[-self.order:])
        return " ".join(out) if out else "I have nothing to say yet."

    def save(self, filename=BRAIN_FILE):
        data = {
            "order": self.order,
            "map": {str(k): v for k,v in self.map.items()},
            "starts": [list(s) for s in self.starts]
        }
        with open(filename, "w") as f:
            json.dump(data, f)

    @classmethod
    def load(cls, filename=BRAIN_FILE):
        if not os.path.exists(filename):
            return cls()
        with open(filename) as f:
            data = json.load(f)
        b = cls(order=data.get("order",5))
        b.map = {tuple(eval(k)): v for k,v in data.get("map",{}).items()}
        b.starts = [tuple(s) for s in data.get("starts",[])]
        return b

# ===== Memory for personal info =====
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE) as f:
        return json.load(f)

def save_memory(mem):
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f)

memory = load_memory()

# ===== Starter brain =====
starter_text = """
hello! hi there! hey! greetings! hi Sam! howdy! hey buddy! good morning! good afternoon! good evening!
how are you? how's it going? what's up? how do you do? nice to meet you! pleased to meet you!
I'm fine, thanks! I'm good! all well! doing great! doing well! not bad! can't complain!
what's your name? I am Sam. I am your AI friend. call me Sam. my name is Sam.
tell me a joke! why did the chicken cross the road? I don't know, why? just kidding! haha!
bye! see you later! goodbye! catch you later! take care!
"""

print("Sam: Hey! I'm Pro Sam, your upgraded AI. Type 'exit' to quit. I learn from everything you type.")
sam = SamBrain.load()
if not sam.map:
    sam.feed(starter_text)
    sam.save()

while True:
    user = input("You: ").strip()
    if not user:
        continue
    if user.lower() == "exit":
        print("Sam: Bye! See you later.")
        break

    # ==== Personal memory parsing (simple example) ====
    if "my name is " in user.lower():
        name = user.lower().split("my name is ")[-1].split()[0]
        memory["user_name"] = name.capitalize()
        save_memory(memory)
        print(f"Sam: Nice to meet you, {memory['user_name']}!")
        sam.feed(user)
        sam.save()
        continue

    # Auto-learn
    sam.feed(user)
    sam.save()

    response = sam.generate(user)

    # Insert known name if applicable
    if "user_name" in memory:
        response = response.replace("you", memory["user_name"])

    print("Sam:", response)
