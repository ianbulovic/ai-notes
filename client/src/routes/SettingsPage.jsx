import React from "react";

import Header from "../components/Header";
import { Stack, Tabs, Tab } from "react-bootstrap";
import TagManager from "../components/TagManager";

export default function SettingsPage() {
  return (
    <div className="vh-100">
      <Header />
      <Stack className="col-md-6 mx-auto p-4">
        <Tabs defaultActiveKey="tags" id="justify-tab-example" className="mb-3">
          <Tab eventKey="tags" title="Manage Tags">
            <TagManager />
          </Tab>
          <Tab eventKey="other" title="Other Settings?">
            <h3>Coming soon!</h3>
          </Tab>
        </Tabs>
      </Stack>
    </div>
  );
}
