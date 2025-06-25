# RLHF Pipeline

🌖 **Reinforcement Learning from Human Feedback (RLHF) with Llama 3.1 8B Instruct**

---

## Overview
This project demonstrates how to fine-tune a large language model (Llama 3.1 8B Instruct) using Reinforcement Learning from Human Feedback (RLHF) to reduce harmful or toxic outputs. The workflow includes training a reward model, running PPO-based RLHF, and evaluating toxicity reduction.

## Requirements
- **Google Colab** (Pro/Pro+ recommended)
- **A100 GPU** (Required for model size and speed)
- **Hugging Face Account & Access Token** (for model and dataset downloads)
- **Weights & Biases (wandb) Account & API Key** (for experiment tracking)

## Quickstart
1. **Open the Notebook**
   - Use the provided notebook: `Reward_Model_and_PPO_Training_RLHF_in_Practice.ipynb`
   - [Open in Colab](https://colab.research.google.com/drive/1h6XUz36PW85ZgcyCxRk_ddBtkaTKuR07?usp=sharing)

2. **Set Up Your Environment**
   - In Colab, select `Runtime > Change runtime type > GPU > A100`.
   - Install required packages (the notebook will do this automatically):
     ```python
     !pip install -qU transformers==4.45.2 accelerate bitsandbytes peft trl==0.11 datasets tqdm
     ```

3. **Authenticate**
   - **Hugging Face**: Run the cell with `notebook_login()` and paste your HF token.
   - **Weights & Biases**: When prompted, paste your wandb API key.

4. **Workflow Steps**
   - **Load Pretrained Model**: Llama 3.1 8B Instruct in 4-bit quantized mode.
   - **Prepare Datasets**: Use Anthropic's `hh-rlhf` for reward modeling and AllenAI's `real-toxicity-prompts` for PPO training.
   - **Train Reward Model**: Fine-tune a `distilroberta-base` classifier to distinguish between helpful and harmful completions.
   - **Train with PPO**: Use the reward model to guide RLHF training of the Llama model.
   - **Evaluate**: Generate outputs for toxic prompts and score them with a toxicity metric.

5. **Tips**
   - Training is memory and compute intensive. Use small dataset subsets for experimentation.
   - The notebook is designed for Colab; local runs may require significant hardware and setup.
   - For best results, ensure your tokens are kept private and not shared in public notebooks.

## References
- [Hugging Face TRL Documentation](https://huggingface.co/docs/trl/main/en/reward_trainer)
- [Anthropic hh-rlhf Dataset](https://huggingface.co/datasets/Anthropic/hh-rlhf)
- [AllenAI Real Toxicity Prompts](https://huggingface.co/datasets/allenai/real-toxicity-prompts)

---

For more details, see the notebook and code comments.
