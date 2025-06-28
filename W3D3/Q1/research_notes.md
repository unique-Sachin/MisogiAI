# Research Notes: LLM Inference Fundamentals

This document provides an overview of the key concepts behind Large Language Model (LLM) inference and a comparison between different model sizes.

---

## 1. LLM Inference Basics

LLM inference is the process of using a trained language model to generate text based on a given input (a "prompt"). Unlike training, which is computationally intensive and done beforehand, inference is optimized for speed and efficiency to provide real-time responses.

### Key Metrics in LLM Inference:

*   **Latency**: The time it takes to get a response from the model.
    *   **Time to First Token (TTFT)**: How quickly the first word of the response appears. Crucial for real-time applications like chatbots.
    *   **Time Per Output Token (TPOT)**: The time taken to generate each subsequent token. This determines the overall "speed" of the streaming response.
*   **Throughput**: The number of requests or output tokens the system can process in a given period (e.g., tokens per second). Higher throughput is essential for applications with many concurrent users.
*   **Memory Usage**: The amount of VRAM (GPU memory) required. This consists of:
    *   **Static Memory**: The memory needed to load the model's weights. This is fixed for a given model and precision.
    *   **Dynamic Memory (KV Cache)**: Memory used to store the context of the ongoing generation. It grows with the number of tokens in the input and the generated response.
*   **Cost**: The financial cost of running the model, which is a function of the hardware used, the time it's running, and energy consumption.

### Key Factors Influencing Performance:

*   **Model Size**: Larger models (more parameters) have greater capabilities but are slower, require more memory, and are more expensive to run.
*   **Quantization**: A technique to reduce the numerical precision of the model's weights (e.g., from 16-bit float to 8-bit integer). This reduces memory usage and can speed up inference, sometimes with a minor trade-off in accuracy.
*   **Batch Size**: Processing multiple input prompts simultaneously. A larger batch size can improve throughput but increases memory usage and can increase latency for individual requests.
*   **Hardware**: The choice of hardware (e.g., GPU, CPU, TPU) is the most critical factor. GPUs are preferred for their parallel processing capabilities, which are ideal for the matrix operations in LLMs.

---

## 2. Model Comparison: 7B vs. 13B vs. GPT-4

Here's a comparative look at three common model sizes.

| Feature               | **7B Model (e.g., Mistral 7B, Llama 2 7B)**                                   | **13B Model (e.g., Llama 2 13B)**                                            | **GPT-4 (Closed-Source Model)**                                                              |
| --------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| **Performance**       | Strong performance for its size, excellent for specific, fine-tuned tasks.      | A good balance between performance and resource requirements. More nuanced than 7B. | State-of-the-art reasoning, logic, and creativity. Can handle highly complex tasks.          |
| **Best For**          | Chatbots, summarization, language translation, sentiment analysis.            | Content creation, complex Q&A, more advanced chatbots, RAG systems.              | Demanding applications requiring deep understanding, multi-step reasoning, and code generation. |
| **Latency**           | Low. Well-suited for real-time, interactive applications.                     | Medium. Still usable for interactive apps but with a slight delay.               | High. Often not suitable for applications requiring immediate responses.                     |
| **Memory & Hardware** | ~14-16 GB of VRAM. Can run on consumer/pro-grade GPUs (e.g., NVIDIA T4, A10).  | ~26-30 GB of VRAM. Requires enterprise-grade GPUs (e.g., NVIDIA A100 40GB).      | Extremely high. Not feasible for self-hosting; accessed via API. Requires clusters of A100/H100 GPUs. |
| **Cost**              | Low. Cheapest to host and run among the three.                                | Medium. Represents a significant step up in hosting costs from 7B models.      | High. The most expensive option, typically billed per token used via an API.                 |
| **Customization**     | High. Open-source models can be extensively fine-tuned on custom datasets.    | High. Also open-source and highly customizable.                                  | Low. Limited to prompt engineering and some fine-tuning capabilities provided by the vendor. |

### Summary:

*   **Choose a 7B model** for efficiency, speed, and lower costs, especially when the task is well-defined.
*   **Choose a 13B model** for a good compromise between advanced capabilities and manageable resource needs.
*   **Choose GPT-4** when you need the highest possible quality and can tolerate higher latency and costs, without the need for deep customization. 