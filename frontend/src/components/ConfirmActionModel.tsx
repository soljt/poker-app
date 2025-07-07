// components/ConfirmActionModal.tsx
import React from "react";
import { Modal, Button } from "react-bootstrap";

interface ConfirmActionModalProps {
  show: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title?: string;
  message: string;
  confirmText?: string;
}

const ConfirmActionModal: React.FC<ConfirmActionModalProps> = ({
  show,
  onClose,
  onConfirm,
  title = "Confirm Action",
  message,
  confirmText = "Yes",
}) => {
  return (
    <Modal show={show} onHide={onClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>{title}</Modal.Title>
      </Modal.Header>

      <Modal.Body>
        <p>{message}</p>
      </Modal.Body>

      <Modal.Footer>
        <Button variant="secondary" onClick={onClose}>
          No
        </Button>
        <Button variant="danger" onClick={onConfirm}>
          {confirmText}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ConfirmActionModal;
