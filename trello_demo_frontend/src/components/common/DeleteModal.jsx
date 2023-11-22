import React, { useState } from "react";
import { Modal } from "antd";

const DeleteModal = ({ open, onClose, onOk, title, okText }) => {
  const [loading, setLoading] = useState(false);

  const handleOk = async () => {
    try {
      setLoading(true);
      await onOk();
      setLoading(false);
    } catch (error) {
      setLoading(false);
    }
  };

  return (
    <Modal
      title={title}
      open={open}
      onOk={handleOk}
      onCancel={onClose}
      okText={okText}
      confirmLoading={loading}
    >
      <div className="task-delete-modal-wrapper">
        <div className="description">Are you sure you want to delete?</div>
      </div>
    </Modal>
  );
};

export default DeleteModal;
