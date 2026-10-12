import re
import math
from typing import Dict, Any, List
import logging

logger = logging.getLogger("stealthdoc.detector")

class AIDetector:
    """
    Local AI Text Detector supporting Hugging Face models (e.g. roberta-base-openai-detector)
    with statistical perplexity and burstiness analysis.
    """

    def __init__(self, model_name: str = "roberta-base-openai-detector"):
        self.model_name = model_name
        self.hf_pipeline = None
        self._initialized = False

    def _lazy_init_hf(self):
        """Initializes Hugging Face pipeline if torch and transformers are available."""
        if self._initialized:
            return
        try:
            import torch
            from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

            device = 0 if torch.cuda.is_available() else -1
            self.hf_pipeline = pipeline(
                "text-classification",
                model=self.model_name,
                device=device,
                truncation=True,
                max_length=512
            )
            logger.info(f"Loaded Hugging Face detector model: {self.model_name}")
        except Exception as e:
            logger.warning(f"Could not load HF model '{self.model_name}' locally ({e}). Using statistical fallback engine.")
            self.hf_pipeline = None
        finally:
            self._initialized = True

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        """Splits text into meaningful sentences."""
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if len(s.strip()) > 3]

    @staticmethod
    def _calculate_statistical_metrics(text: str) -> Dict[str, float]:
        """
        Calculates linguistic perplexity and burstiness signals:
        - Sentence length variation (burstiness)
        - Lexical diversity (Type-Token Ratio)
        - Punctuation & transition rhythm
        - Repetition entropy
        """
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        if not words:
            return {"ai_score": 0.0, "human_score": 100.0, "mixed_score": 0.0, "burstiness": 0.0}

        total_words = len(words)
        unique_words = len(set(words))
        ttr = unique_words / total_words  # Type-Token Ratio

        # Burstiness: Standard deviation of sentence lengths
        sentences = re.split(r'[.!?]+', text)
        sentence_lengths = [len(re.findall(r'\b\w+\b', s)) for s in sentences if s.strip()]

        if len(sentence_lengths) > 1:
            mean_len = sum(sentence_lengths) / len(sentence_lengths)
            variance = sum((l - mean_len) ** 2 for l in sentence_lengths) / len(sentence_lengths)
            std_dev = math.sqrt(variance)
            burstiness = std_dev / (mean_len + 1e-5)
        else:
            burstiness = 0.2

        # AI buzzwords checklist that inflate AI detection score
        ai_markers = [
            "delve", "harness", "leverage", "testament", "intricate", "robust",
            "paradigm", "dynamic", "crucial", "multifaceted", "underscores",
            "fostering", "tapestry", "in summary", "moreover", "furthermore"
        ]
        marker_hits = sum(1 for m in ai_markers if m in text.lower())

        # Low burstiness (monotonous sentence lengths) + low TTR + AI markers = higher AI probability
        ai_prob = 0.5
        if burstiness < 0.35:
            ai_prob += 0.20
        elif burstiness > 0.65:
            ai_prob -= 0.20

        if ttr < 0.45:
            ai_prob += 0.15
        elif ttr > 0.65:
            ai_prob -= 0.15

        ai_prob += min(0.30, marker_hits * 0.06)
        ai_prob = max(0.02, min(0.98, ai_prob))

        ai_percent = round(ai_prob * 100, 1)
        mixed_percent = round(min(ai_percent, 100 - ai_percent) * 0.35, 1)
        human_percent = round(max(0.0, 100.0 - ai_percent - mixed_percent), 1)

        # Normalize to exactly 100%
        total = ai_percent + human_percent + mixed_percent
        if total > 0:
            ai_percent = round((ai_percent / total) * 100, 1)
            human_percent = round((human_percent / total) * 100, 1)
            mixed_percent = round(100.0 - ai_percent - human_percent, 1)

        return {
            "ai_percent": ai_percent,
            "human_percent": human_percent,
            "mixed_percent": mixed_percent,
            "burstiness": round(burstiness, 2),
            "lexical_diversity": round(ttr, 2)
        }

    def detect_text(self, text: str) -> Dict[str, Any]:
        """Scans input text and returns probability distribution and sentence breakdown."""
        if not text or not text.strip():
            return {
                "ai_percentage": 0.0,
                "human_percentage": 100.0,
                "mixed_percentage": 0.0,
                "sentences": [],
                "engine": "empty_input"
            }

        self._lazy_init_hf()

        # If HF model is loaded, compute batch probabilities
        if self.hf_pipeline is not None:
            try:
                sentences = self._split_sentences(text)
                sentence_scores = []
                fake_scores = []

                # Analyze chunks
                chunks = [text[i:i + 1500] for i in range(0, min(len(text), 6000), 1500)]
                chunk_results = self.hf_pipeline(chunks)
                for res in chunk_results:
                    label = res.get("label", "").lower()
                    score = float(res.get("score", 0.5))
                    # 'fake' or 'label_1' represents AI
                    if "fake" in label or "1" in label or "ai" in label:
                        fake_scores.append(score)
                    else:
                        fake_scores.append(1.0 - score)

                ai_mean = sum(fake_scores) / len(fake_scores) if fake_scores else 0.5
                ai_percent = round(ai_mean * 100, 1)
                mixed_percent = round(min(ai_percent, 100 - ai_percent) * 0.3, 1)
                human_percent = round(100.0 - ai_percent - mixed_percent, 1)

                # Sentence-level tagging
                for s in sentences[:15]:
                    s_stat = self._calculate_statistical_metrics(s)
                    sentence_scores.append({
                        "text": s,
                        "ai_score": s_stat["ai_percent"]
                    })

                return {
                    "ai_percentage": ai_percent,
                    "human_percentage": human_percent,
                    "mixed_percentage": mixed_percent,
                    "engine": "huggingface_model",
                    "model_name": self.model_name,
                    "sentences": sentence_scores
                }
            except Exception as e:
                logger.warning(f"Inference error with HF model ({e}). Using statistical analyzer.")

        # Statistical fallback engine
        metrics = self._calculate_statistical_metrics(text)
        sentences = self._split_sentences(text)
        sentence_scores = []
        for s in sentences[:15]:
            s_stat = self._calculate_statistical_metrics(s)
            sentence_scores.append({
                "text": s,
                "ai_score": s_stat["ai_percent"]
            })

        return {
            "ai_percentage": metrics["ai_percent"],
            "human_percentage": metrics["human_percent"],
            "mixed_percentage": metrics["mixed_percent"],
            "engine": "statistical_burstiness_engine",
            "burstiness": metrics["burstiness"],
            "lexical_diversity": metrics["lexical_diversity"],
            "sentences": sentence_scores
        }
