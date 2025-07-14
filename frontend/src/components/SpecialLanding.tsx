import React, { useEffect, useState } from "react";
import { Card, Container } from "react-bootstrap";

const SpecialLanding: React.FC = () => {
  const [messageHtml, setMessageHtml] = useState<string>("");

  useEffect(() => {
    fetch("/message.html")
      .then((res) => res.text())
      .then(setMessageHtml)
      .catch((err) => console.error("Failed to load message:", err));
  }, []);
  return (
    <Container className="py-5 text-center big-handmade-hearts">
      <Card
        style={{ backgroundColor: "#fff0f6", color: "#912f56" }}
        className="h-100 shadow-sm mb-3"
      >
        <Card.Body>
          <Card.Title>
            <h1 className="display-3 text-danger">Hi sweetheart 💕</h1>
          </Card.Title>
          <Card.Text className="fs-4 fw-bold mt-4 mb-5">
            I made this special page just for you. Nobody else can even see it
            at all!!! I also custom-made the background on iPadmé 😎. I hope
            you're loving me! Mwah 😘
          </Card.Text>
        </Card.Body>
      </Card>
      {messageHtml && (
        <Card
          style={{ backgroundColor: "#fff0f6", color: "#912f56" }}
          className="h-100 shadow-sm"
        >
          <Card.Body>
            <Card.Title>
              <h2 className="display-3 text-danger">
                A little extra <strong>secret</strong> note 💛
              </h2>
            </Card.Title>
            <div
              className="fs-4 fw-bold mt-4 mb-5"
              dangerouslySetInnerHTML={{ __html: messageHtml }}
            />
          </Card.Body>
        </Card>
      )}
    </Container>
  );
};

export default SpecialLanding;
