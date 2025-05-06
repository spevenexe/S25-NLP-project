# S25-NLP-project — Self-Study QuizMaker
Semester Project for CS 6320 Natural Language Processing
## Contributors
Vimal Sebastian \
Terrence Li \
Nivedh Koya
## Project Overview
Our project is a web application interface that allows users to upload PDF files of whatever study material they want to familiarize themselves with, and our NLP application will parse the text and use a RAG-based approach integrated with an LLM to generate a specified number of random short-answer questions based on the material of varying question types (e.g. Application based, Conceptual Understanding, Compare and Contrast, etc.) and quiz the user on it. After the user answers the questions, our pipeline again uses an LLM to judge and assess how well the submitted responses, answers the asked questions based on information of the material, and evaluate it on a score of [0 to 5]. Our NLP agent not only returns the score for every question, but also gives additional feedback information and metrics, such as sifting through their responses and identifying categorical strengths and weaknesses in certain content areas of the material, aggregating their score into a total number, and stratifying their score based on question-type for user self-assessment. Another functionality of our application is that after an initial quiz run, our NLP agent can also prompt the user to ask if they want to regenerate a brand new quiz, whose questions are more relevant towards their weaknesses automatically, and redo the quiz distribution and result assessment pipeline, enabling a positive feedback loop for the user to keep improving on their study material. This unique approach, coupled with a modern, stylistic, and friendly User-Interface, makes our solution a viable value-proposition to learners around the globe to potentially accelerate their study workflow.
## Tech Stack
<div align="center">
	<code><img width="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/tailwind_css.png" alt="Tailwind CSS" title="Tailwind CSS"/></code>
	<code><img width="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/shadcn_ui.png" alt="ShadCn UI" title="ShadCn UI"/></code>
	<code><img width="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/react.png" alt="React" title="React"/></code>
	<code><img width="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/typescript.png" alt="TypeScript" title="TypeScript"/></code>
	<code><img width="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/vite.png" alt="Vite" title="Vite"/></code>
  <code><img width="50" src="https://github.com/user-attachments/assets/83efd3a3-6b45-45bb-90a9-b14f93389859" alt="FastAPI" title="FastAPI"/></code>
  <code><img width="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/python.png" alt="Python" title="Python"/></code>
  <code><img width="50" src="https://github.com/user-attachments/assets/6c9afc58-601c-4a99-861c-3a65c1e6a613" alt="PyTorch" title="PyTorch"/></code>
  <code><img width="50" src="https://heidloff.net/assets/img/2023/09/transformers.png" alt="Hugging Face Transformers" title="Hugging Face Transformers"/></code>
  <code><img width="50" src="https://brandlogos.net/wp-content/uploads/2025/03/langchain-logo_brandlogos.net_9zgaw.png" alt="LangChain" title="LangChain"/></code>
</div>

## YouTube Demo Link - https://youtu.be/4l5027PMe0E

## How to Run
You will need Node [`npm`](https://www.npmjs.com/) and Python [`pip`](https://pypi.org/project/pip/) configured on your device. As well as [NVIDIA's CUDA toolkit](https://developer.nvidia.com/cuda-toolkit) and a CUDA-capable graphics card.

#### Run backend:
1) `cd backend`
2) (Create and) Start your virtual environment if you have not already done so
3) Install packages in requirements.txt: `pip install -r requirements.txt` if you havbe not already done so
4) Run the server: `python main.py`

#### Run frontend:
1) `cd frontend`
2) `npm install` if you have not already installed the packages
3) Run web client: `npm run dev`

Check the output of your frontend for the `localhost` port on which it is running. You can find the app there.