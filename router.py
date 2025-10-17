from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- Define training phrases for each route ---
faq_texts = [
    "vision of the institute",
    "mission of BNMIT",
    "faculty information",
    "who are the faculty members",
    "training and placement process",
    "facilities in the college",
    "message from HOD",
    "students corner",
    "recruiters corner",
]

sql_texts = [
    "average salary",
    "average package",
    "placements",
    "total students placed",
    "highest package",
    "companies that visited",
    "number of students placed",
    "total placements",
]

# --- Fit TF-IDF model ---
corpus = faq_texts + sql_texts
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(corpus)

def router(query: str):
    """Return a route object with .name ('faq', 'sql', or 'other') and .score"""
    q_vec = vectorizer.transform([query])
    sims = cosine_similarity(q_vec, X)[0]

    faq_score = max(sims[:len(faq_texts)])
    sql_score = max(sims[len(faq_texts):])
    best_score = max(faq_score, sql_score)

    class R:
        pass

    R.score = float(best_score)
    if best_score < 0.15:  # low similarity threshold
        R.name = "other"
    else:
        R.name = "faq" if faq_score >= sql_score else "sql"

    return R()
    

# --- Quick test ---
if __name__ == "__main__":
    print(router("tell me about mission").name)        # faq
    print(router("average package in 2023").name)      # sql
    print(router("how's the weather").name)            # other
