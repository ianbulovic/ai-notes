import React, { useState } from "react";

import Header from "../components/Header";
import {
  Stack,
  Tabs,
  Tab,
  FormControl,
  FloatingLabel,
  Form,
} from "react-bootstrap";
import TagManager from "../components/TagManager";
import { API_URL } from "../constants";

export default function SettingsPage() {
  const [darkMode, setDarkMode] = useState(
    localStorage.getItem("darkMode") === "true"
  );
  return (
    <div className="vh-100">
      <Header />
      <Stack className="col-md-6 mx-auto p-4">
        <Tabs
          defaultActiveKey="general"
          id="justify-tab-example"
          className="mb-3"
        >
          <Tab eventKey="general" title="General Settings">
            <FloatingLabel controlId="apiUrl" label="API URL">
              <FormControl value={API_URL} disabled />
            </FloatingLabel>
            <h6 className="mt-3 mb-1">Dark Mode</h6>
            <Form.Switch
              id="darkMode"
              checked={darkMode}
              className="h5"
              onChange={(e) => {
                // toggle dark mode by setting the "data-bs-theme" attribute on the <html> element
                // and saving the preference to localStorage
                const html = document.querySelector("html");
                if (e.target.checked) {
                  html.setAttribute("data-bs-theme", "dark");
                  localStorage.setItem("darkMode", "true");
                  setDarkMode(true);
                } else {
                  html.removeAttribute("data-bs-theme");
                  localStorage.removeItem("darkMode");
                  setDarkMode(false);
                }
              }}
            />
          </Tab>
          <Tab eventKey="tags" title="Manage Tags">
            <TagManager />
          </Tab>
        </Tabs>
      </Stack>
    </div>
  );
}
