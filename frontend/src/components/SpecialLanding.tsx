import React from "react";
import { Card, Container } from "react-bootstrap";

const SpecialLanding: React.FC = () => {
  return (
    <Container className="py-5 text-center big-handmade-hearts">
      <Card
        style={{ backgroundColor: "#fadadd", color: "#634d4fff" }}
        className="h-100 shadow-sm"
      >
        <Card.Body>
          <Card.Title>
            <h1 className="display-3 text-danger">Hi sweetheart 💕</h1>
          </Card.Title>
          <Card.Text>
            <p className="fs-4 fw-bold mt-4">
              I made this special page just for you. Nobody else can even see it
              at all!!! I also custom-made the background on iPadmé 😎. I hope
              you're loving me! Mwah 😘
            </p>
          </Card.Text>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default SpecialLanding;
