import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib"
import React, { ReactNode } from "react"

interface State {
  recorder: MediaRecorder | null
}

function BlobToDataURL(blob: Blob) {
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.addEventListener("loadend", () => resolve(reader.result as string))
    reader.readAsDataURL(blob)
  }) as Promise<string>
}

class AudioRecorder extends StreamlitComponentBase<State> {
  public state: State = {
    recorder: null,
  }

  public componentDidMount(): void {
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then((mediaStreamObj) => {
        const recorder = new MediaRecorder(mediaStreamObj)
        this.setState({ recorder })

        recorder.ondataavailable = async ({ data }) => {
          const audioData_str = (await BlobToDataURL(data)).replace(
            /^data:.+?base64,/,
            ""
          )
          Streamlit.setComponentValue(audioData_str)
        }
      })
  }

  public render = (): ReactNode => {
    const { recording } = this.props.args
    const recorder = this.state.recorder as MediaRecorder

    if (recording && this.state.recorder?.state !== "recording") {
      recorder.start()
      this.forceUpdate()
    } else if (!recording && this.state.recorder?.state === "recording") {
      recorder.stop()
      this.forceUpdate()
    }

    return <div id="audiorecorder"></div>
  }
}

export default withStreamlitConnection(AudioRecorder)
