import React from "react";
import ReactDOM from "react-dom/client";

import { createBrowserRouter, RouterProvider } from "react-router-dom";
import ErrorPage from "./error-page";
import RootPage from "./routes/RootPage";
import NotePage, { loader as noteLoader } from "./routes/NotePage";
import RecordingPage from "./routes/RecordingPage";
import SettingsPage from "./routes/SettingsPage";

import { APP_TITLE } from "./constants";

import "./index.css";
import "bootstrap/dist/css/bootstrap.css";

const router = createBrowserRouter([
  {
    path: "/",
    element: <RootPage />,
    errorElement: <ErrorPage />,
  },
  {
    path: "/note/:id",
    loader: noteLoader,
    element: <NotePage />,
    errorElement: <ErrorPage />,
  },
  {
    path: "/record",
    element: <RecordingPage />,
    errorElement: <ErrorPage />,
  },
  {
    path: "/settings",
    element: <SettingsPage />,
    errorElement: <ErrorPage />,
  },
]);

document.title = APP_TITLE;

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
