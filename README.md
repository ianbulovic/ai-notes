# AI Notes

## Description

AI Notes is an AI-powered note-taking application. 

### Server

The server for AI Notes is a RESTful API built in Python using the Flask framework. The API manages a database of notes, and provides endpoints for CRUD operations on notes, as well as endpoints for LLM chat and audio transcription.

Currently, the server is configured to use Ollama for LLM chat, and whisper.cpp for transcription, so it can be run completely locally. Future versions will include support for cloud-based services such as OpenAI.

### Client

The client for AI Notes is a React application that provides a simple user interface to interact with the backend API. Currently supported features include:

- Creating, editing, and deleting notes
- Markdown formatting for notes
- Tagging notes
- Searching and sorting notes
- Chatting with an LLM about a note
- Recording and transcribing voice notes

## Table of Contents

- [AI Notes](#ai-notes)
  - [Description](#description)
    - [Server](#server)
    - [Client](#client)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
    - [Server](#server-1)
    - [Client](#client-1)
  - [Usage](#usage)

## Installation

1. Clone the repository:

    ```bash
    git clone --recurse-submodules https://github.com/ianbulovic/ai-notes.git
    cd ai-notes
    ```

### Server

2. Install [Ollama](https://ollama.com/).

3. Create a virtual environment for the server (optional but recommended, example uses conda):

    ```bash
    cd server
    conda create -y -n ai-notes python=3.12
    conda activate ai-notes
    ```

4. Install the server dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Download a whisper model and compile whisper.cpp. Instructions can be found [here](https://github.com/ggerganov/whisper.cpp), optimal settings will vary depending on your system. On my Macbook Pro, I used the following command (this can actually be further optimized with [coreml support](https://github.com/ggerganov/whisper.cpp?tab=readme-ov-file#core-ml-support), but I haven't tested it yet):
    
    ```bash
    cd whisper.cpp
    ./models/download-ggml-model.sh base.en
    make
    cd ..
    ```

6. Modify the configuration in `config.toml` as necessary. Make sure that the whisper model path matches the model you downloaded in the previous step, and that the Ollama executable path is correct (you can find this by running `where ollama`).

### Client

7. Navigate to the client directory and install the client dependencies:

    ```bash
    cd client
    npm install
    ```

## Usage

If both the server and client are running on the same machine, you can start them both with the following commands:

1. Start the server:

    ```bash
    cd server
    conda activate ai-notes
    python run.py
    ```

2. In a separate terminal, start the client:

    ```bash
    cd client
    npm start
    ```

Alternatively, you can run the server and client on different machines by modifying the `host` and `port` settings in `server/config.toml`, and the `API_HOST` and `API_PORT` settings in `client/src/constants.js`.
