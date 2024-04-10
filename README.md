# AI Notes

## Setup
1. Clone this repository and navigate to it in a terminal.
2. Create a new virtual environment and install the required packages. This assumes you have conda installed.

```bash
conda create -n ai-notes python=3.12
conda activate ai-notes
python -m pip install -r requirements.txt
```

3. Build the custom streamlit components. This requires npm.
   
```bash
cd components/streamlit-audiorecorder/audiorecorder/frontend
npm install
npm run build
cd ../../streamlit-autosize-textarea/autosize_textarea/frontend
npm install
npm run build
cd ../../../../
```

4. Install the custom streamlit components.

```bash
python -m pip install -e components/streamlit-audiorecorder
python -m pip install -e components/streamlit-autosize-textarea
```

## Running the server
```bash
python server.py
```

## Running the client
```bash
python client.py
```
