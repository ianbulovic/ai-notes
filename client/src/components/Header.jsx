import React, { useEffect, useState } from "react";
import { Navbar, Nav, NavDropdown } from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";
import { useNavigate } from "react-router-dom";

import { createNote, getHealth } from "../api";
import { APP_TITLE } from "../constants";

const Header = () => {
  let navigate = useNavigate();

  const [health, setHealth] = useState("connecting");

  useEffect(() => {
    const updateHealth = () => {
      getHealth().then((health) => {
        setHealth(health);
      });
    };
    updateHealth();
    const interval = setInterval(updateHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Navbar expand="lg" className="px-4 border-bottom">
      <LinkContainer to="/">
        <Navbar.Brand>{APP_TITLE}</Navbar.Brand>
      </LinkContainer>
      <Navbar.Toggle aria-controls="basic-navbar-nav" />
      <Navbar.Collapse id="basic-navbar-nav">
        <Nav className="ml-auto">
          <LinkContainer to="/">
            <Nav.Link>Home</Nav.Link>
          </LinkContainer>
          <NavDropdown title="New Note" id="basic-nav-dropdown">
            <NavDropdown.Item
              onClick={() => {
                createNote().then((note) => navigate(`/note/${note.id}`));
              }}
            >
              New Text Note
            </NavDropdown.Item>
            <LinkContainer to="/record">
              <NavDropdown.Item>New Audio Note</NavDropdown.Item>
            </LinkContainer>
          </NavDropdown>
          <LinkContainer to="/settings">
            <Nav.Link>Settings</Nav.Link>
          </LinkContainer>
        </Nav>
      </Navbar.Collapse>
      <Nav>
        {health ? (
          health !== "connecting" && (
            <span className="text-success">Connected</span>
          )
        ) : (
          <span className="text-danger">Disconnected</span>
        )}
      </Nav>
    </Navbar>
  );
};

export default Header;
