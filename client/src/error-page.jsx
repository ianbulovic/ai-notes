import { useRouteError } from "react-router-dom";
import Header from "./components/Header";

import { LinkContainer } from 'react-router-bootstrap'

export default function ErrorPage() {
  const error = useRouteError();
  console.error(error);

  return (
    <div id="error-page" className="vh-100">
        <Header />
        <div className="d-flex flex-column gap-2 py-4 align-items-center h-100">
            <h1>Oops! Something went wrong.</h1>
            <LinkContainer to="/">
                <button className="btn btn-primary">Go Home</button>
            </LinkContainer>
        </div>
    </div>
  );
}