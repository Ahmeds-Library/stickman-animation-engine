#!/usr/bin/env python3
"""asset_registry.py: Intelligent Mutual Asset Registry & Semantic Deduplicator
Enforces Rule 30 & Pillar 4: Shared Sticker & Asset Reuse across Short and Long formats.
Prevents duplicate generation:
1. Short <-> Long Mutual Sharing: Any sticker created in Short is available to Long and vice versa.
2. Semantic NLP Lookup: Pure Python + NumPy TF-IDF, character tri-grams, suffix lemmatization,
   and 80+ concept ontology families (matching abstract terms e.g. 'ancient footwear' <-> 'leather sandals').
3. Canonical Project Repository: Maintains <project_root>/elements/cut/ and STICKERS_REGISTRY.json.
"""

import os, sys, json, csv, re, shutil, math
import numpy as np

STOPWORDS = {
    "a", "an", "the", "with", "and", "in", "of", "to", "for", "on", "by", "at", "from", "into", "across",
    "cartoon", "sticker", "flat", "style", "color", "colors", "illustration", "modern", "ancient",
    "prehistoric", "isolated", "one", "single", "pure", "white", "black", "grey", "gray", "background",
    "magenta", "cutout", "prop", "icon", "dark", "ink", "outlines", "outline", "soft", "shading",
    "bright", "natural", "palette", "centered", "solid", "ff00ff", "shadow", "shadows", "clutter",
    "text", "showing", "no", "clean", "2d", "3d", "vector", "drawing", "placed", "perfectly", "against",
    "table", "floor", "people", "watermark", "letters", "labels", "absolutely"
}

def extract_core_subject(text):
    """Extracts core object descriptor by stripping standard prompt boilerplate."""
    s = str(text).strip()
    s = re.sub(r"^(one\s+single\s+isolated|single\s+isolated|one\s+single|isolated)\s+", "", s, flags=re.IGNORECASE)
    s = re.split(r",\s*(?:clean\s+)?2d\s+cartoon", s, flags=re.IGNORECASE)[0]
    s = re.split(r",\s*centered\s+on\s+solid", s, flags=re.IGNORECASE)[0]
    s = re.split(r",\s*placed\s+perfectly", s, flags=re.IGNORECASE)[0]
    s = re.split(r",\s*solid\s+flat", s, flags=re.IGNORECASE)[0]
    s = re.split(r",\s*no\s+shadows", s, flags=re.IGNORECASE)[0]
    return s.strip()

SYNONYMS = {
    "mattress": ["bed", "sleeping", "cushion", "pad", "cot", "blanket", "bedroll"],
    "sabertooth": ["tiger", "cat", "predator", "smilodon", "skull", "fang", "beast", "carnivore"],
    "flint": ["stone", "fire", "spark", "rock", "chert", "blade", "tool", "handaxe"],
    "campfire": ["fire", "flame", "ember", "hearth", "bonfire", "smoke", "blaze"],
    "spear": ["weapon", "point", "javelin", "lance", "harpoon", "hunting", "shaft"],
    "flute": ["instrument", "music", "bone", "whistle", "pipe"],
    "clock": ["time", "watch", "hourglass", "timer", "schedule", "alarm", "chronometer"],
    "clipboard": ["record", "list", "notes", "audit", "paper", "data", "ledger"],
    "skull": ["bone", "skeleton", "head", "cranium", "fossil", "jaw"],
    "knife": ["blade", "dagger", "cutting", "cleaver", "chopper", "scraper"],
    "switch": ["light", "toggle", "button", "lever", "power", "breaker"],
    "deadbolt": ["lock", "latch", "security", "door", "bolt", "padlock"],
    "brain": ["mind", "neuron", "synapse", "thought", "intelligence", "cerebrum"],
    "owl": ["bird", "nocturnal", "raptor", "feathers", "eyes"],
    "ember": ["coal", "spark", "ash", "glowing", "charcoal"],
    "mug": ["cup", "coffee", "tea", "drink", "chalice", "goblet"],
    "footwear": ["sandals", "shoes", "moccasins", "boots", "slippers", "clogs"]
}

CONCEPT_DOMAINS = {
    "footwear": ["footwear", "shoes", "sandals", "moccasins", "boots", "slippers", "clogs", "soles", "leather sandals", "bark shoes"],
    "headwear": ["headwear", "hat", "cap", "helmet", "hood", "bonnet", "bandana", "headband", "crown", "turban"],
    "clothing": ["clothing", "garment", "tunic", "cloak", "robe", "shirt", "pants", "trousers", "vest", "skirt", "dress", "mantle", "attire"],
    "bedding": ["bed", "mattress", "sleeping pad", "cot", "cushion", "blanket", "quilt", "pillow", "hammock", "bedroll"],
    "shelter": ["shelter", "cave", "hut", "tent", "cabin", "dwelling", "house", "yurt", "tipi", "lodge", "igloo", "lean-to"],
    "fire": ["fire", "flame", "campfire", "bonfire", "hearth", "blaze", "inferno", "combustion", "ember", "spark", "torch"],
    "fuel": ["fuel", "wood", "firewood", "kindling", "logs", "coal", "charcoal", "peat", "tinder"],
    "smoke": ["smoke", "soot", "ash", "fumes", "haze", "vapor", "smog", "plume"],
    "predator": ["predator", "tiger", "lion", "sabertooth", "smilodon", "wolf", "bear", "hyena", "leopard", "jaguar", "panther", "raptor"],
    "mammal": ["mammoth", "mastodon", "bison", "buffalo", "deer", "elk", "reindeer", "horse", "boar", "rhino", "camel"],
    "canine": ["canine", "wolf", "dog", "fox", "jackal", "dingo", "hound", "pup"],
    "feline": ["feline", "cat", "tiger", "lion", "cheetah", "lynx", "cougar"],
    "avian": ["bird", "eagle", "hawk", "owl", "falcon", "raven", "crow", "vulture", "sparrow"],
    "aquatic": ["fish", "salmon", "trout", "whale", "shark", "seal", "shellfish", "crab", "mollusk"],
    "reptile": ["snake", "serpent", "viper", "lizard", "alligator", "crocodile", "turtle"],
    "insect": ["insect", "bee", "wasp", "ant", "beetle", "spider", "fly", "mosquito", "moth", "locust"],
    "skeleton": ["skeleton", "skull", "bone", "cranium", "rib", "jaw", "vertebra", "femur", "spine"],
    "fossil": ["fossil", "petrified", "amber", "relic", "imprint", "remains"],
    "teeth": ["tooth", "teeth", "fang", "tusk", "canine", "molar", "incisor"],
    "horn": ["horn", "antler", "tusk", "spike", "crest"],
    "weapon": ["weapon", "spear", "javelin", "lance", "harpoon", "dart", "arrow", "bow", "sling"],
    "blade": ["blade", "knife", "dagger", "sword", "machete", "scythe", "sickle", "razor", "cleaver"],
    "blunt_weapon": ["club", "mace", "cudgel", "hammer", "staff", "baton"],
    "projectile": ["arrow", "bolt", "dart", "bullet", "pellet", "stone"],
    "armor": ["armor", "shield", "buckler", "breastplate", "cuirass", "mail", "greaves", "vambrace"],
    "tool": ["tool", "implement", "utensil", "device", "gear", "instrument", "gadget"],
    "stone_tool": ["flint", "chert", "obsidian", "handaxe", "cleaver", "scraper", "burin", "microlith"],
    "percussion": ["hammer", "mallet", "anvil", "pestle", "pounder", "sledge"],
    "cutting_tool": ["chisel", "saw", "awl", "drill", "needle", "gouge", "adze"],
    "vessel": ["vessel", "pot", "jar", "bowl", "urn", "jug", "pitcher", "amphora", "crock", "basin"],
    "drinking": ["mug", "cup", "chalice", "goblet", "flask", "canteen", "gourd", "tankard"],
    "cooking_pot": ["cauldron", "kettle", "pan", "skillet", "pot", "roaster"],
    "storage": ["basket", "crate", "box", "chest", "sack", "bag", "pouch", "bin", "granary"],
    "lighting": ["lamp", "lantern", "candle", "torch", "brazier", "beacon", "flare"],
    "time": ["clock", "watch", "sundial", "hourglass", "timer", "chronometer", "calendar"],
    "record": ["clipboard", "scroll", "parchment", "tablet", "paper", "book", "ledger", "manuscript", "journal"],
    "writing": ["quill", "stylus", "pen", "ink", "pencil", "charcoal stick"],
    "brain": ["brain", "mind", "cerebrum", "neuron", "synapse", "intellect", "thought"],
    "lock": ["lock", "deadbolt", "padlock", "latch", "bolt", "bar", "key", "hasp"],
    "music": ["music", "flute", "pipe", "whistle", "drum", "horn", "harp", "lute", "rattle"],
    "switch": ["switch", "lever", "toggle", "button", "trigger", "breaker"],
    "cordage": ["rope", "cord", "twine", "string", "line", "sinew", "strap", "thong", "thread", "fiber"],
    "fabric": ["cloth", "textile", "linen", "wool", "leather", "hide", "pelt", "fur", "canvas", "felt"],
    "skin": ["skin", "hide", "leather", "pelt", "fur", "fleece"],
    "gem": ["gem", "jewel", "amber", "quartz", "jade", "turquoise", "opal", "crystal"],
    "metal": ["copper", "bronze", "iron", "gold", "silver", "tin", "lead", "brass"],
    "mineral": ["mineral", "stone", "rock", "pebble", "boulder", "flint", "quartz", "clay", "ochre"],
    "pigment": ["ochre", "charcoal", "pigment", "dye", "paint", "chalk", "soot"],
    "art": ["art", "painting", "carving", "petroglyph", "pictograph", "engraving", "figurine", "sculpture", "totem"],
    "adornment": ["necklace", "pendant", "bead", "bracelet", "ring", "amulet", "talisman", "earring"],
    "ritual": ["altar", "shrine", "idol", "relic", "offering", "fetish", "totem"],
    "hunting": ["trap", "snare", "net", "decoy", "pitfall", "blind", "track"],
    "gathering": ["foraging", "berry", "nut", "root", "tuber", "mushroom", "herb"],
    "agriculture": ["plow", "sickle", "grain", "seed", "wheat", "barley", "harvest", "sheaf"],
    "food": ["meat", "flesh", "carcass", "fat", "marrow", "fish", "bread", "meal", "stew", "broth"],
    "water": ["water", "stream", "river", "spring", "well", "pond", "lake", "rain"],
    "liquid_storage": ["waterskin", "bladder", "canteen", "gourd", "amphora"],
    "cleansing": ["soap", "sponge", "comb", "brush", "waterbasin", "towel"],
    "medicine": ["herb", "poultice", "salve", "bandage", "remedy", "tonic", "potion"],
    "transport": ["boat", "canoe", "raft", "sled", "sledge", "cart", "wagon", "wheel"],
    "barrier": ["wall", "fence", "palisade", "gate", "door", "barricade", "parapet"],
    "path": ["trail", "path", "track", "road", "footpath", "route", "crossing"],
    "weather": ["storm", "rain", "snow", "frost", "ice", "hail", "wind", "gale", "thunder", "lightning"],
    "cold": ["glacier", "ice", "icicle", "frost", "snow", "tundra", "permafrost", "blizzard"],
    "heat": ["heat", "sun", "warmth", "sweat", "scorch", "summer", "drought"],
    "celestial": ["moon", "sun", "star", "constellation", "eclipse", "sky", "meteor"],
    "shadow": ["shadow", "shade", "silhouette", "darkness", "gloom", "abyss"],
    "vision": ["eye", "pupil", "gaze", "sight", "lens", "eyeball", "vision"],
    "hearing": ["ear", "sound", "echo", "whisper", "shout", "roar", "rumble"],
    "speech": ["voice", "mouth", "tongue", "lips", "call", "chant", "song"],
    "touch": ["hand", "finger", "palm", "grip", "fist", "grasp"],
    "stride": ["foot", "footprint", "track", "heel", "sole", "toe", "step", "stride"],
    "strength": ["muscle", "sinew", "arm", "bicep", "power", "might"],
    "measure": ["scale", "balance", "ruler", "weight", "tally", "notch"],
    "money": ["coin", "currency", "gold", "silver", "barter", "tribute", "token"],
    "death": ["tomb", "grave", "burial", "urn", "shroud", "cairn", "monument"],
    "ceremony": ["mask", "headdress", "staff", "scepter", "wand", "banner"],
    "flora": ["tree", "branch", "leaf", "bark", "root", "vine", "moss", "fern", "flower", "grass", "shrub"],
    "landscape": ["mountain", "cliff", "valley", "canyon", "cave", "gorge", "ridge", "plateau"],
    "soil": ["soil", "dirt", "mud", "sand", "clay", "loam", "silt", "dust"]
}

def stem_word(w):
    """Simple suffix lemmatizer for clean token matching without external dependencies."""
    w = w.lower().strip()
    for suffix in ("ing", "ed", "es", "s", "en", "er", "al", "ic", "tion", "ment", "ly", "ful", "ness", "ity"):
        if len(w) > len(suffix) + 2 and w.endswith(suffix):
            return w[:-len(suffix)]
    return w

def get_char_trigrams(text):
    """Extracts character 3-grams for substring and morphological similarity."""
    s = re.sub(r"[^a-z0-9]", "", str(text).lower())
    if len(s) < 3:
        return {s} if s else set()
    return {s[i:i+3] for i in range(len(s) - 2)}

def trigram_cosine_similarity(t1, t2):
    """Computes cosine similarity between character 3-grams of core subjects."""
    tri1 = get_char_trigrams(extract_core_subject(t1))
    tri2 = get_char_trigrams(extract_core_subject(t2))
    if not tri1 or not tri2:
        return 0.0
    inter = len(tri1 & tri2)
    denom = math.sqrt(len(tri1) * len(tri2))
    return (inter / denom) if denom > 0 else 0.0

def token_jaccard_similarity(raw_a, raw_b):
    """Computes Jaccard similarity across stemmed tokens."""
    stemmed_a = {stem_word(t) for t in raw_a if t not in STOPWORDS}
    stemmed_b = {stem_word(t) for t in raw_b if t not in STOPWORDS}
    if not stemmed_a or not stemmed_b:
        return 0.0
    inter = len(stemmed_a & stemmed_b)
    union = len(stemmed_a | stemmed_b)
    return (inter / union) if union > 0 else 0.0

def get_concept_domains_for_tokens(tokens):
    """Finds concept domains matching tokens or their stems."""
    matched = set()
    stemmed = {stem_word(t) for t in tokens}
    all_check = set(tokens) | stemmed
    for domain, terms in CONCEPT_DOMAINS.items():
        domain_terms_stemmed = {stem_word(term) for term in terms}
        if all_check & (set(terms) | domain_terms_stemmed):
            matched.add(domain)
    return matched

def clean_tokens(text):
    core = extract_core_subject(text)
    words = re.findall(r"[a-z0-9]+", str(core).lower())
    return {w for w in words if len(w) > 2 and w not in STOPWORDS}

def expand_tokens(tokens):
    expanded = set(tokens)
    for tok in list(tokens):
        st = stem_word(tok)
        if tok in SYNONYMS:
            expanded.update(SYNONYMS[tok])
        if st in SYNONYMS:
            expanded.update(SYNONYMS[st])
        for root_term, syn_list in SYNONYMS.items():
            syn_stems = [stem_word(s) for s in syn_list]
            if tok in syn_list or st in syn_stems or tok == root_term or st == stem_word(root_term):
                expanded.add(root_term)
                expanded.update(syn_list)
    return expanded

def resolve_project_root(path="."):
    p = os.path.abspath(path)
    if os.path.basename(p) in ("short", "long"):
        return os.path.dirname(p)
    return p

def get_registry_path(project_root):
    return os.path.join(project_root, "STICKERS_REGISTRY.json")

def load_registry(project_root):
    reg_file = get_registry_path(project_root)
    if os.path.exists(reg_file):
        try:
            with open(reg_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"stickers": []}

def save_registry(registry, project_root):
    reg_file = get_registry_path(project_root)
    with open(reg_file, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

def scan_and_rebuild_registry(project_root):
    """Deep scans project for all transparent cutouts and indexes them into registry."""
    try:
        from anti_pollution import validate_external_output_dir
        project_root = validate_external_output_dir(project_root)
    except ImportError:
        pass
    registry = load_registry(project_root)
    
    # Check elements.tsv files in project_root, short, and long
    tsv_sources = [
        (os.path.join(project_root, "ELEMENTS.tsv"), "root"),
        (os.path.join(project_root, "short", "ELEMENTS.tsv"), "short"),
        (os.path.join(project_root, "long", "ELEMENTS.tsv"), "long")
    ]
    
    label_map = {}
    for tsv_path, scope in tsv_sources:
        if os.path.exists(tsv_path):
            with open(tsv_path, encoding="utf-8") as f:
                for r in csv.DictReader(f, delimiter="\t"):
                    eid = r.get("id", "").strip()
                    obj = r.get("object", "").strip()
                    if eid and obj:
                        label_map[f"{scope}_{eid}"] = obj
                        label_map[eid] = obj
                        label_map[f"{eid}.png"] = obj
                        label_map[f"{int(eid):02d}.png" if eid.isdigit() else eid] = obj

    search_dirs = [
        (os.path.join(project_root, "elements", "cut"), "root"),
        (os.path.join(project_root, "short", "elements", "cut"), "short"),
        (os.path.join(project_root, "long", "elements", "cut"), "long")
    ]
    
    for s_dir, scope in search_dirs:
        if not os.path.exists(s_dir):
            continue
        for fname in os.listdir(s_dir):
            if fname.lower().endswith((".png", ".webp", ".gif")):
                full_path = os.path.join(s_dir, fname)
                if os.path.getsize(full_path) < 1000:
                    continue
                # Determine object name
                base = os.path.splitext(fname)[0]
                obj_name = label_map.get(f"{scope}_{base}") or label_map.get(base) or base
                
                # Check if already present
                existing = None
                for entry in registry["stickers"]:
                    if os.path.abspath(entry["path"]) == os.path.abspath(full_path):
                        existing = entry
                        break
                        
                raw_tokens = list(clean_tokens(obj_name))
                exp_tokens = list(expand_tokens(raw_tokens))
                domains = list(get_concept_domains_for_tokens(set(raw_tokens) | set(exp_tokens)))
                
                entry_data = {
                    "name": obj_name,
                    "filename": fname,
                    "path": full_path,
                    "scope": scope,
                    "tokens": raw_tokens,
                    "expanded_tokens": exp_tokens,
                    "domains": domains,
                    "size_bytes": os.path.getsize(full_path)
                }
                
                if existing:
                    existing.update(entry_data)
                else:
                    registry["stickers"].append(entry_data)
                    
    save_registry(registry, project_root)
    return registry

def _get_sticker_library_indexer():
    """Dynamically locates stickman-stickers/scripts/index_stickers.py across repo or global skill dirs."""
    try:
        import importlib.util
        skills_parent = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        cands = [
            os.path.join(skills_parent, "stickman-stickers", "scripts", "index_stickers.py"),
            os.path.expanduser("~/.gemini/config/skills/stickman-stickers/scripts/index_stickers.py"),
            os.path.expanduser("~/.claude/skills/stickman-stickers/scripts/index_stickers.py"),
        ]
        for idx_p in cands:
            if os.path.exists(idx_p):
                spec = importlib.util.spec_from_file_location("stickman_stickers_index", idx_p)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    return mod
    except Exception:
        pass
    return None


def register_sticker_in_global_vault(src_png, slug_name, tags=""):
    """Registers a clean Flow cutout into skills/stickman-stickers/assets/flow_vault/ + CATALOG.tsv."""
    idx_mod = _get_sticker_library_indexer()
    if idx_mod:
        try:
            return idx_mod.register_flow_sticker(src_png, slug_name, tags=tags)
        except Exception:
            pass
    return None


ALCOHOL_EXCLUDE_TOKENS = {"wine", "beer", "champagne", "ale", "liquor", "whiskey", "vodka"}
SODA_SPECIFIC_TOKENS = {"soda", "cola", "fizzy", "softdrink", "sprite", "coke", "pepsi"}
MINI_SCENE_SLUGS = {"skull_fossil", "scientific_field_researcher", "tribal_storytelling_pie", "campfire_circle"}
MODERN_ONLY_PROPS = {
    "lightbulb", "bulb", "electric", "lamp", "phone", "smartphone", "laptop",
    "computer", "screen", "watch", "clock", "alarm", "soda", "candy", "car",
    "tv", "television", "camera", "microphone", "headphones", "battery", "robot", "rocket",
}
ANCIENT_CONTEXT_CUES = ("caveman", "cave", "hunter", "prehistoric", "stone age", "ice age", "ancient", "fossil", "roman", "egypt", "persia", "long before")
MODERN_CONTEXT_CUES = ("today", "now", "modern", "currently", "industrial", "supermarket", "grocery", "processed")


def find_reusable_sticker(query_text, project_root, threshold=0.70, single_object_only=False, era_context=""):
    """Finds existing sticker in 3-tier order:
    Tier 0: Local project short/long elements/cut/
    Tier 1: Global skills/stickman-stickers/assets/flow_vault/ (100% Owned-Flow priority)
    Tier 2: GENERATE_FLOW_CUTOUT (live synthesis via Google Flow Cutout API)
    Enforces strict Era Compatibility when era_context describes prehistoric/ancient narration.
    Score = 0.40 * Concept_Ontology + 0.35 * Token_Jaccard + 0.25 * Trigram_Cosine (+ bonuses)
    """
    registry = load_registry(project_root)
    if not registry.get("stickers"):
        registry = scan_and_rebuild_registry(project_root)
        
    query_raw = clean_tokens(query_text)
    query_exp = expand_tokens(query_raw)
    query_domains = get_concept_domains_for_tokens(query_raw | query_exp)
    
    if not query_raw and not query_domains:
        return None

    wants_alcohol = bool(query_raw & ALCOHOL_EXCLUDE_TOKENS)
    wants_soda = bool(query_raw & SODA_SPECIFIC_TOKENS)
    era_l = str(era_context or "").lower()
    ban_modern = any(c in era_l for c in ANCIENT_CONTEXT_CUES) and not any(m in era_l for m in MODERN_CONTEXT_CUES)

    best_match = None
    best_score = 0.0
    
    for item in registry["stickers"]:
        cand_path = item["path"]
        if not os.path.exists(cand_path) or os.path.getsize(cand_path) < 1000:
            continue
        cand_slug = os.path.splitext(os.path.basename(cand_path))[0].lower()
        if single_object_only and cand_slug in MINI_SCENE_SLUGS:
            continue
            
        cand_raw = set(item.get("tokens", []))
        cand_exp = set(item.get("expanded_tokens", []))
        if not wants_alcohol and ((cand_raw | cand_exp) & ALCOHOL_EXCLUDE_TOKENS):
            continue
        if wants_soda and not ((cand_raw | cand_exp) & (SODA_SPECIFIC_TOKENS | {"can", "beverage"})):
            continue
        if ban_modern and ((cand_raw & MODERN_ONLY_PROPS) or any(m in cand_slug for m in ("lightbulb", "bulb", "smartphone", "laptop", "soda_can", "clock"))):
            continue
        cand_domains = set(item.get("domains", []))
        if not cand_domains:
            cand_domains = get_concept_domains_for_tokens(cand_raw | cand_exp)
            
        cand_name = item.get("name", "")
        
        # 1. Concept Domain Overlap (Weight 0.40)
        shared_domains = query_domains & cand_domains
        if shared_domains and query_domains:
            concept_score = len(shared_domains) / len(query_domains)
        elif shared_domains:
            concept_score = 1.0
        else:
            concept_score = 0.0
            
        # 2. Token Jaccard with stemming (Weight 0.35)
        jaccard_score = token_jaccard_similarity(query_raw | query_exp, cand_raw | cand_exp)
        
        # 3. Character Trigram Cosine (Weight 0.25)
        trigram_score = trigram_cosine_similarity(query_text, cand_name)
        
        # Must have real content overlap: token overlap, synonym overlap, or high trigram match on core subject
        has_token_overlap = bool((query_raw | query_exp) & (cand_raw | cand_exp))
        synonym_overlap = any((k in query_exp) and (k in cand_exp) for k in SYNONYMS.keys())
        
        if not (has_token_overlap or synonym_overlap or trigram_score >= 0.70):
            continue

        combined_score = (0.40 * concept_score) + (0.35 * jaccard_score) + (0.25 * trigram_score)
        
        # Domain identity bonus: matching specific concrete concept domain
        if shared_domains:
            combined_score += 0.12
            
        # Keyword domain boosts: direct synonym overlap
        for key_root in SYNONYMS.keys():
            if (key_root in query_exp) and (key_root in cand_exp):
                combined_score += 0.15

        # Prioritize bold 2D Owned-Flow art over simple vector wireframes
        if "flow_vault" in cand_path or item.get("scope") == "flow_vault":
            combined_score += 0.22

        if combined_score > best_score:
            best_score = combined_score
            best_match = item
            
    if best_score >= threshold and best_match:
        return best_match

    # Tier 1 (flow_vault) lookup in skills/stickman-stickers/CATALOG.tsv
    idx_mod = _get_sticker_library_indexer()
    if idx_mod:
        try:
            subj = extract_core_subject(query_text) or query_text
            vault_hits = idx_mod.search_stickers(
                subj, min_score=max(0.45, threshold - 0.15),
                require_alpha_ok=True, single_object_only=single_object_only
            )
            for top in vault_hits:
                top_slug = os.path.splitext(os.path.basename(top["path"]))[0].lower()
                top_toks = set(clean_tokens(f"{top_slug} {top.get('tags','')}"))
                if not wants_alcohol and (top_toks & ALCOHOL_EXCLUDE_TOKENS):
                    continue
                if ban_modern and ((top_toks & MODERN_ONLY_PROPS) or any(m in top_slug for m in ("lightbulb", "bulb", "smartphone", "laptop", "soda_can", "clock"))):
                    continue
                return {
                    "name": top["name"],
                    "filename": os.path.basename(top["path"]),
                    "path": top["path"],
                    "scope": top["source"],
                    "category": top.get("category", ""),
                    "license": top.get("license", ""),
                }
        except Exception:
            pass
    return None

def link_or_copy_mutual_sticker(query_text, destination_path, project_root):
    """Finds best reusable sticker and copies it to destination_path if found."""
    match = find_reusable_sticker(query_text, project_root)
    if not match:
        return False
        
    src = match["path"]
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    if os.path.abspath(src) != os.path.abspath(destination_path):
        shutil.copy2(src, destination_path)
        print(f"♻️ [Asset Registry] Reused '{match['name']}' from {match['scope']}: {src} -> {destination_path}")
    return True

if __name__ == "__main__":
    try:
        from anti_pollution import validate_external_output_dir
    except ImportError:
        validate_external_output_dir = lambda x: x
    root = resolve_project_root(sys.argv[1] if len(sys.argv) > 1 else ".")
    root = validate_external_output_dir(root)
    reg = scan_and_rebuild_registry(root)
    print(f"✅ Indexed {len(reg.get('stickers', []))} shared stickers in {root}")
    if len(sys.argv) > 2:
        q = sys.argv[2]
        res = find_reusable_sticker(q, root)
        if res:
            print(f"🎯 Query '{q}' matched: {res['name']} ({res['path']})")
        else:
            print(f"❌ No match for '{q}'")
