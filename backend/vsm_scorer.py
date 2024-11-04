class VSMScorer:
    def __init__(self, title_weight=0.1, body_weight=0.9):
        self.title_weight = title_weight
        self.body_weight = body_weight

    def normalize_tfs(self, tfs, doc_lengths):
        for field, terms in tfs.items():
            length = doc_lengths.get(field, 1)
            for term in terms:
                terms[term] /= length

    def get_net_score(self, tfs, tf_query):
        score = 0.0
        tf_title = tfs.get("title", {})
        tf_body = tfs.get("body", {})

        for term, q_weight in tf_query.items():
            tf_d_t = tf_title.get(term, 0.0)
            tf_d_b = tf_body.get(term, 0.0)

            doc_weight = (self.title_weight * tf_d_t) + (self.body_weight * tf_d_b)
            score += q_weight * doc_weight

        return score

    def get_tf(self, text):
        if text is None:
            text = ""
        tf = {}
        for term in text.lower().split():
            tf[term] = tf.get(term, 0) + 1
        return tf

    def calculate_similarity(self, query, document):
        # Prepare term frequencies for query and document
        tf_query = self.get_tf(query)
        title_text = document.get("name", "") or ""
        body_text = document.get("categories", "") or ""
        
        # Extract term frequencies for title and body
        tfs = {
            "title": self.get_tf(title_text),
            "body": self.get_tf(body_text)
        }
        doc_lengths = {
            "title": len(title_text.split()),
            "body": len(body_text.split())
        }

        # Normalize term frequencies
        self.normalize_tfs(tfs, doc_lengths)

        # Calculate and return net score
        score = self.get_net_score(tfs, tf_query)
        
        return score
