import { useCallback, useEffect, useState } from "react";
import UserRow from "../components/UserRow";
import UserForm from "../components/UserForm";
import Pagination from "../components/Pagination";
import { UserRowData } from "../types";
import { admin_api } from "../services/api";
import { Container } from "react-bootstrap";

export default function Admin() {
  const [users, setUsers] = useState<UserRowData[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const fetchUsers = useCallback(() => {
    admin_api.get(`users?page=${page}`).then((res) => {
      const data = res.data;
      setUsers(data.users);
      setTotalPages(data.totalPages);
    });
  }, [page]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  return (
    <Container>
      <div className="container my-4">
        <h2 className="text-center mb-4">Admin Dashboard</h2>
      </div>

      <UserForm onUserCreated={fetchUsers} />

      {users.map((u) => (
        <UserRow key={u.id} user={u} onChange={fetchUsers} />
      ))}

      <Pagination current={page} total={totalPages} onChange={setPage} />
    </Container>
  );
}
