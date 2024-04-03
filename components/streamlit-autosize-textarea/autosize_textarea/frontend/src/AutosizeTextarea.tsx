import {
  Streamlit,
  StreamlitComponentBase,
  Theme,
  withStreamlitConnection,
} from "streamlit-component-lib"
import React, { ReactNode } from "react"
import TextareaAutosize from "react-textarea-autosize"

interface State {
  dirty: boolean
  value: string
  focused: boolean
}

class AutosizeTextarea extends StreamlitComponentBase<State> {
  public state: State = {
    dirty: false,
    value: this.props.args["value"] || this.props.args["default"] || "",
    focused: false,
  }

  private onFocus = (): void => {
    this.setState({ focused: true })
  }

  private onBlur = (): void => {
    this.setState({ focused: false })
    if (this.state.dirty) {
      Streamlit.setComponentValue(this.state.value)
      this.setState({ dirty: false })
    }
  }

  public render = (): ReactNode => {
    const theme: Theme = this.props.theme || {
      base: "light",
      primaryColor: "black",
      backgroundColor: "white",
      secondaryBackgroundColor: "#f4f2f2",
      textColor: "black",
      font: "sans-serif",
    }

    const style: React.CSSProperties = {
      fontFamily: theme.font,
      color: theme.textColor,
      backgroundColor: theme.secondaryBackgroundColor,
      padding: "0.5rem",

      border: `1px solid ${
        this.state.focused ? theme.primaryColor : theme.secondaryBackgroundColor
      }`,
      transition: "border 200ms",
      transitionTimingFunction: "cubic-bezier(0.2, 0.8, 0.4, 1)",
      borderRadius: "0.5rem",
      width: "100%",
      resize: "none",
      outline: "none",
    }

    const value = this.state.value

    return (
      <TextareaAutosize
        value={value}
        onChange={this.onTextChanged}
        disabled={this.props.disabled}
        onFocus={this.onFocus}
        onBlur={this.onBlur}
        style={{ ...style, height: 100 }}
        minRows={10}
      />
    )
  }

  private onTextChanged = (e: React.ChangeEvent<HTMLTextAreaElement>): void => {
    this.setState({ value: e.target.value, dirty: true })
    Streamlit.setFrameHeight()
  }

  // Listen for cmd+enter or ctrl+enter to save the value
  public componentDidMount = (): void => {
    Streamlit.setFrameHeight()
    document.addEventListener("keydown", this.onKeyDown)
  }

  public componentWillUnmount = (): void => {
    document.removeEventListener("keydown", this.onKeyDown)
  }

  private onKeyDown = (e: KeyboardEvent): void => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey) && this.state.dirty) {
      Streamlit.setComponentValue(this.state.value)
      this.setState({ dirty: false })
    }
  }
}

// "withStreamlitConnection" is a wrapper function. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
//
// You don't need to edit withStreamlitConnection (but you're welcome to!).
export default withStreamlitConnection(AutosizeTextarea)
