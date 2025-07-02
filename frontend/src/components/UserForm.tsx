import { FormEvent } from "react";
import { Roles } from "../types";
import { admin_api } from "../services/api";
import { Form, Button, Card } from "react-bootstrap";

export default function UserForm({
  onUserCreated,
}: {
  onUserCreated: () => void;
}) {
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const data = Object.fromEntries(new FormData(form));
    admin_api.post("/users", data).then(() => {
      form.reset();
      onUserCreated();
    });
  };

  return (
    <Card className="mb-4">
      <Card.Body>
        <Form onSubmit={handleSubmit} className="row g-3">
          <Form.Group className="col-md-3">
            <Form.Control name="username" placeholder="Username" required />
          </Form.Group>
          <Form.Group className="col-md-3">
            <Form.Control
              name="password"
              type="password"
              placeholder="Password"
              required
            />
          </Form.Group>
          <Form.Group className="col-md-2">
            <Form.Select name="role" defaultValue="user">
              {Object.values(Roles).map((role, i) => (
                <option key={i} value={role}>
                  {role}
                </option>
              ))}
            </Form.Select>
          </Form.Group>
          <Form.Group className="col-md-2">
            <Form.Control
              name="chips"
              type="number"
              placeholder="Chips"
              required
            />
          </Form.Group>
          <div className="col-md-2">
            <Button type="submit" variant="primary" className="w-100">
              Create
            </Button>
          </div>
        </Form>
      </Card.Body>
    </Card>
  );
}
