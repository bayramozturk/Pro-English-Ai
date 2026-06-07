# Data Sources

## CEFR-SP

This project uses the CEFR-SP corpus for model training and independent
evaluation. CEFR-SP contains English sentences annotated by two
English-education professionals.

- Yuki Arase, Satoru Uchida, and Tomoyuki Kajiwara. 2022.
  "CEFR-Based Sentence-Difficulty Annotation and Assessment."
  EMNLP 2022.
- Source: https://github.com/yukiar/CEFR-SP
- Wiki-Auto portion: CC BY-SA 3.0
- SCoRE portion: CC BY-NC-SA 4.0

The original train, development, and test separation is preserved during
evaluation. The displayed exact agreement counts a prediction as correct
when it agrees with either expert annotation.
