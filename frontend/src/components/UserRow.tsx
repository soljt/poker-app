import { useState } from "react";
import { admin_api } from "../services/api";
import { UserRowData, Roles } from "../types";
import { Button, Form, Row, Col, Card, ButtonGroup } from "react-bootstrap";

export default function UserRow({
  user,
  onChange,
}: {
  user: UserRowData;
  onChange: () => void;
}) {
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState<UserRowData>({ ...user });

  const handleSave = () => {
    admin_api.put(`users/${user.id}`, formData).then(() => {
      setEditing(false);
      onChange();
    });
  };

  const handleCancel = () => {
    setFormData({ ...user });
    setEditing(false);
  };

  const handleDelete = () => {
    admin_api.delete(`users/${user.id}`).then(onChange);
  };

  return (
    <Card className="mb-3 shadow-sm">
      <Card.Body>
        <Row className="align-items-center">
          <Col md={2}>
            <strong>{user.username}</strong>
          </Col>
          <Col md={3}>
            {editing ? (
              <Form.Select
                value={formData.role}
                onChange={(e) =>
                  setFormData({ ...formData, role: e.target.value as Roles })
                }
              >
                {Object.values(Roles).map((role, i) => (
                  <option key={i} value={role}>
                    {role}
                  </option>
                ))}
              </Form.Select>
            ) : (
              <span>{user.role}</span>
            )}
          </Col>
          <Col md={2}>
            {editing ? (
              <Form.Control
                type="number"
                value={formData.chips}
                step={100}
                onChange={(e) =>
                  setFormData({ ...formData, chips: +e.target.value })
                }
              />
            ) : (
              <span>{user.chips}</span>
            )}
          </Col>
          <Col md="auto">
            <ButtonGroup>
              {editing ? (
                <>
                  <Button variant="success" size="sm" onClick={handleSave}>
                    Confirm
                  </Button>
                  <Button variant="secondary" size="sm" onClick={handleCancel}>
                    Cancel
                  </Button>
                </>
              ) : (
                <Button
                  variant="outline-primary"
                  size="sm"
                  onClick={() => setEditing(true)}
                >
                  Edit
                </Button>
              )}
              <Button variant="outline-danger" size="sm" onClick={handleDelete}>
                Delete
              </Button>
            </ButtonGroup>
          </Col>
        </Row>
      </Card.Body>
    </Card>
  );
}
